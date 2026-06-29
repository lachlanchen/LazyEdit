from __future__ import annotations

import json
import os
import subprocess
from typing import Any


DEFAULT_PORTRAIT_BLURFILL: dict[str, Any] = {
    "enabled": False,
    "mode": "lalachan",
    "width": 1080,
    "height": 1920,
    "foregroundWidth": 1080,
    "foregroundY": 240,
    "centerShiftRatio": 0.1,
    "blur": 36.0,
    "backgroundDim": -0.08,
    "backgroundSaturation": 1.08,
    "crf": 12,
    "preset": "slow",
    "scaleFlags": "lanczos",
    "audioMode": "copy",
}


def _bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _float(value: Any, fallback: float, minimum: float, maximum: float) -> float:
    try:
        parsed = float(value)
    except Exception:
        parsed = fallback
    return min(max(parsed, minimum), maximum)


def _int(value: Any, fallback: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(round(float(value)))
    except Exception:
        parsed = fallback
    return min(max(parsed, minimum), maximum)


def sanitize_portrait_blurfill(payload: Any) -> dict[str, Any]:
    base = dict(DEFAULT_PORTRAIT_BLURFILL)
    if not isinstance(payload, dict):
        return base

    mode = str(payload.get("mode") or payload.get("alignment") or base["mode"]).strip().lower()
    if mode not in {"lalachan", "center", "custom"}:
        mode = base["mode"]

    preset = str(payload.get("preset") or base["preset"]).strip().lower()
    if preset not in {"ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"}:
        preset = base["preset"]

    scale_flags = str(payload.get("scaleFlags") or payload.get("scale_flags") or base["scaleFlags"]).strip().lower()
    if scale_flags not in {"lanczos", "bicubic", "bilinear"}:
        scale_flags = base["scaleFlags"]

    audio_mode = str(payload.get("audioMode") or payload.get("audio_mode") or base["audioMode"]).strip().lower()
    if audio_mode not in {"copy", "aac"}:
        audio_mode = base["audioMode"]

    width = _int(payload.get("width"), base["width"], 360, 4320)
    height = _int(payload.get("height"), base["height"], 640, 7680)
    if width % 2:
        width += 1
    if height % 2:
        height += 1

    foreground_width = _int(
        payload.get("foregroundWidth", payload.get("foreground_width")),
        base["foregroundWidth"],
        160,
        width,
    )
    if foreground_width % 2:
        foreground_width -= 1

    return {
        "enabled": _bool(payload.get("enabled"), default=base["enabled"]),
        "mode": mode,
        "width": width,
        "height": height,
        "foregroundWidth": max(2, foreground_width),
        "foregroundY": _int(
            payload.get("foregroundY", payload.get("foreground_y")),
            base["foregroundY"],
            0,
            height,
        ),
        "centerShiftRatio": _float(
            payload.get(
                "centerShiftRatio",
                payload.get("center_shift_ratio", payload.get("shiftRatio", payload.get("shift_ratio"))),
            ),
            base["centerShiftRatio"],
            0.0,
            0.45,
        ),
        "blur": _float(payload.get("blur"), base["blur"], 0.0, 96.0),
        "backgroundDim": _float(
            payload.get("backgroundDim", payload.get("background_dim")),
            base["backgroundDim"],
            -1.0,
            1.0,
        ),
        "backgroundSaturation": _float(
            payload.get("backgroundSaturation", payload.get("backgroundSat", payload.get("background_saturation"))),
            base["backgroundSaturation"],
            0.0,
            3.0,
        ),
        "crf": _int(payload.get("crf"), base["crf"], 0, 35),
        "preset": preset,
        "scaleFlags": scale_flags,
        "audioMode": audio_mode,
    }


def is_portrait_blurfill_enabled(config: Any) -> bool:
    return bool(sanitize_portrait_blurfill(config).get("enabled"))


def _probe_resolution(video_path: str) -> tuple[int, int]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "json",
            video_path,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    payload = json.loads(result.stdout or "{}")
    streams = payload.get("streams") or []
    if not streams:
        raise RuntimeError(f"video stream missing: {video_path}")
    width = int(streams[0].get("width") or 0)
    height = int(streams[0].get("height") or 0)
    if width <= 0 or height <= 0:
        raise RuntimeError(f"invalid video resolution: {video_path}")
    return width, height


def _foreground_y(input_path: str, config: dict[str, Any]) -> int:
    source_w, source_h = _probe_resolution(input_path)
    output_h = int(config["height"])
    fg_w = int(config["foregroundWidth"])
    scaled_h = int(round(source_h * (fg_w / max(source_w, 1))))
    if scaled_h % 2:
        scaled_h += 1
    max_y = max(0, output_h - scaled_h)
    center_y = max_y // 2
    if config.get("mode") == "center":
        return center_y
    if config.get("mode") == "lalachan":
        shift_ratio = float(config.get("centerShiftRatio") or 0.0)
        return min(max(int(round(center_y * (1.0 - shift_ratio))), 0), max_y)
    return min(max(int(config.get("foregroundY") or 0), 0), max_y)


def _ffmpeg_command(input_path: str, output_path: str, config: dict[str, Any], audio_mode: str) -> list[str]:
    width = int(config["width"])
    height = int(config["height"])
    fg_width = int(config["foregroundWidth"])
    fg_y = _foreground_y(input_path, config)
    scale_flags = str(config["scaleFlags"])
    filter_complex = (
        "[0:v]split=2[fgsrc][bgsrc];"
        f"[bgsrc]scale={width}:{height}:force_original_aspect_ratio=increase:flags={scale_flags},"
        f"crop={width}:{height},gblur=sigma={float(config['blur'])},"
        f"eq=brightness={float(config['backgroundDim'])}:saturation={float(config['backgroundSaturation'])}[bg];"
        f"[fgsrc]scale={fg_width}:-2:flags={scale_flags}[fg];"
        f"[bg][fg]overlay=(W-w)/2:{fg_y},setsar=1,format=yuv420p[v]"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-preset",
        str(config["preset"]),
        "-crf",
        str(int(config["crf"])),
        "-pix_fmt",
        "yuv420p",
    ]
    if audio_mode == "copy":
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    cmd += ["-movflags", "+faststart", output_path]
    return cmd


def apply_portrait_blurfill(input_path: str, output_path: str, settings: Any) -> str:
    config = sanitize_portrait_blurfill(settings)
    if not config.get("enabled"):
        return input_path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    audio_mode = str(config.get("audioMode") or "copy")
    cmd = _ffmpeg_command(input_path, output_path, config, audio_mode)
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        if audio_mode != "copy":
            raise
        fallback = _ffmpeg_command(input_path, output_path, config, "aac")
        subprocess.run(fallback, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path
