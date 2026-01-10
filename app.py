import os
import hashlib

os.environ["CUDA_VISIBLE_DEVICES"]="1"


from lazyedit.openai_version_check import OpenAI
from config import UPLOAD_FOLDER, PORT, AUTOPUBLISH_URL, AUTOPUBLISH_TIMEOUT



import shlex
import threading
import subprocess

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import tornado.ioloop
import tornado.web
from tornado import gen
import tornado.autoreload
from tornado.concurrent import run_on_executor
import tornado.httpclient


import zipfile  # for creating zip files

from lazyedit.autocut_processor import AutocutProcessor

from lazyedit.subtitle_metadata import Subtitle2Metadata
from lazyedit.words_card import VideoAddWordsCard, overlay_word_card_on_cover
from lazyedit.subtitle_translate import SubtitlesTranslator
from lazyedit.video_prompt_generator import VideoPromptGenerator
from lazyedit.utils import find_font_size
from lazyedit.video_captioner import VideoCaptioner
from lazyedit.chinese_simplify import convert_items_to_simplified, convert_traditional_to_simplified
from lazyedit.subtitles_burner import BurnSlotConfig, burn_video_with_slots

from pprint import pprint
import json5
import json

import subprocess
from urllib.parse import quote
from pathlib import Path
import re

import cjkwrap
from moviepy.editor import VideoFileClip

import requests
import base64
import os
import subprocess

import cv2
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

import os
import subprocess
import traceback  # Import traceback for detailed error logging


import json
from datetime import datetime, timedelta

import shutil
import glob

from lingua import Language, LanguageDetectorBuilder

import os

from moviepy.editor import VideoFileClip
import moviepy.editor as mp

from lazyedit.handbrake import preprocess_video
from lazyedit.video_utils import preprocess_if_needed
from lazyedit import db as ldb
from lazyedit.plugins.languages import list_languages
from agi.video_requests import create_poll_and_download


GRAMMAR_PALETTE_DIR = os.path.join(
    os.path.dirname(__file__),
    "lazyedit",
    "templates",
    "grammar_palettes",
)
METADATA_TEMPLATE_DIR = os.path.join(
    os.path.dirname(__file__),
    "lazyedit",
    "templates",
)
METADATA_TEMPLATE_MAP = {
    "zh": "metadata_zh",
    "en": "metadata_en",
}
VIDEO_PROMPT_TEMPLATE_DIR = os.path.join(METADATA_TEMPLATE_DIR, "video_prompt")
VIDEO_SPEC_TEMPLATE_DIR = os.path.join(METADATA_TEMPLATE_DIR, "video_spec")

DEFAULT_TRANSLATION_STYLE = {
    "outlineEnabled": True,
    "shadowEnabled": True,
    "outlineThickness": 10.0,
    "outlineStrength": 0.85,
    "outlineColor": "#000000",
    "paletteMode": "base",
    "bgColor": "#000000",
    "bgOpacity": 0.5,
}
DEFAULT_TRANSLATION_LANGUAGES = ["ja", "en", "zh-Hant", "fr"]
DEFAULT_VIDEO_PROMPT_SPEC = {
    "autoTitle": False,
    "title": "Epic Vision",
    "subject": "A fictional protagonist in a vast imagined world",
    "action": "They confront a revelation that changes their journey",
    "environment": "An epic, timeless setting (mythic history or distant planet) with sweeping scale",
    "camera": "Cinematic movement that reveals scale and detail",
    "lighting": "Atmospheric, dramatic lighting with soft volumetric depth",
    "mood": "Epic, awe-inspiring, contemplative",
    "style": "Cinematic, richly detailed, timeless tone",
    "model": "sora-2",
    "aspectRatio": "16:9",
    "durationSeconds": "12",
    "audioLanguage": "auto",
    "sceneCount": "",
    "spokenWords": "Include a short original philosophical line of dialogue.",
    "extraRequirements": "Let the model invent distinct moments and symbolism while keeping a coherent arc.",
    "negative": "no text, no logos, no gore, no real people",
}
DEFAULT_VIDEO_PROMPT_HISTORY = {
    "title": [],
    "subject": [],
    "action": [],
    "environment": [],
    "camera": [],
    "lighting": [],
    "mood": [],
    "style": [],
    "model": [],
    "audioLanguage": [],
    "sceneCount": [],
    "spokenWords": [],
    "extraRequirements": [],
    "negative": [],
}
DEFAULT_BURN_LAYOUT = {
    "heightRatio": 0.5,
    "rows": 4,
    "cols": 1,
    "liftRatio": 0.1,
    "liftSlots": 0,
    "rubySpacing": 0.1,
    "slots": [
        {
            "slot": 1,
            "language": "en",
            "romaji": True,
            "pinyin": True,
            "ipa": True,
            "jyutping": False,
            "romaja": False,
            "arabicTranslit": False,
        },
        {
            "slot": 2,
            "language": "ja",
            "romaji": True,
            "pinyin": True,
            "ipa": True,
            "jyutping": False,
            "romaja": False,
            "arabicTranslit": False,
        },
        {
            "slot": 3,
            "language": "zh-Hant",
            "romaji": True,
            "pinyin": True,
            "ipa": True,
            "jyutping": False,
            "romaja": False,
            "arabicTranslit": False,
        },
        {
            "slot": 4,
            "language": "fr",
            "romaji": True,
            "pinyin": True,
            "ipa": True,
            "jyutping": False,
            "romaja": False,
            "arabicTranslit": False,
        },
    ]
}

BURN_EXECUTOR = ThreadPoolExecutor(max_workers=1)
PROXY_EXECUTOR = ThreadPoolExecutor(max_workers=1)


def _should_create_preview_proxy(file_path: str) -> bool:
    if not file_path:
        return False
    _, ext = os.path.splitext(file_path)
    ext = (ext or "").lower()
    if ext in {".mov"}:
        return True
    # Best-effort detection for HEVC/HDR in MP4/etc.
    try:
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name,color_transfer",
                "-of",
                "json",
                file_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload = json.loads(probe.stdout.decode("utf-8", errors="replace") or "{}")
        streams = payload.get("streams") or []
        stream = streams[0] if streams else {}
        codec = str(stream.get("codec_name") or "").lower()
        transfer = str(stream.get("color_transfer") or "").lower()
        if codec in {"hevc", "h265"}:
            return True
        if transfer in {"smpte2084", "arib-std-b67"}:
            return True
    except Exception:
        pass
    return False


def _create_preview_proxy(video_id: int, input_path: str) -> str | None:
    if not input_path or not os.path.exists(input_path):
        return None
    proxies_dir = os.path.join(UPLOAD_FOLDER, "proxy_previews")
    os.makedirs(proxies_dir, exist_ok=True)
    output_path = os.path.join(proxies_dir, f"video_{video_id}_proxy.mp4")

    try:
        if os.path.exists(output_path) and os.path.getmtime(output_path) >= os.path.getmtime(input_path):
            return output_path
    except Exception:
        pass

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "22",
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        output_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path


def _enqueue_preview_proxy(video_id: int, input_path: str) -> None:
    if not _should_create_preview_proxy(input_path):
        return

    def _run() -> None:
        try:
            _create_preview_proxy(video_id, input_path)
        except Exception as exc:
            print(f"Proxy transcode failed for video {video_id}: {exc}")

    PROXY_EXECUTOR.submit(_run)


def load_grammar_palette(lang):
    safe_lang = re.sub(r"[^a-zA-Z0-9_-]", "", lang or "").strip() or "default"
    for candidate in (safe_lang, "default"):
        path = os.path.join(GRAMMAR_PALETTE_DIR, f"{candidate}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
    return None


def _normalize_metadata_language(value: str | None) -> str | None:
    if not value:
        return None
    lowered = str(value).strip().lower()
    if lowered in {"zh", "zh-cn", "zh-hans", "chinese", "cn"}:
        return "zh"
    if lowered in {"en", "english"}:
        return "en"
    return None


def _normalize_video_source(value: str | None) -> str | None:
    if not value:
        return None
    lowered = str(value).strip().lower()
    if lowered in {"upload", "generate", "remix", "api"}:
        return lowered
    return None


def _read_text_file(path: str | None, max_chars: int = 12000) -> str:
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            content = handle.read()
        return content[:max_chars]
    except Exception:
        return ""


def _parse_bool(value, default=True):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    value_str = str(value).strip().lower()
    if value_str in {"1", "true", "yes", "y", "on"}:
        return True
    if value_str in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value or "").strip("-").lower()
    return cleaned or "generated"


def _sanitize_title(value: str) -> str:
    cleaned = re.sub(r"[\r\n\t]+", " ", value or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "Generated video"


def _load_metadata_templates(lang_code: str) -> tuple[dict, dict]:
    template_key = METADATA_TEMPLATE_MAP.get(lang_code)
    if not template_key:
        raise ValueError(f"unsupported metadata language: {lang_code}")
    template_dir = os.path.join(METADATA_TEMPLATE_DIR, template_key)
    prompt_path = os.path.join(template_dir, "prompt.json")
    schema_path = os.path.join(template_dir, "schema.json")
    if not os.path.exists(prompt_path) or not os.path.exists(schema_path):
        raise FileNotFoundError(f"metadata template missing for {lang_code}")
    with open(prompt_path, "r", encoding="utf-8") as handle:
        prompt_payload = json.load(handle)
    with open(schema_path, "r", encoding="utf-8") as handle:
        schema_payload = json.load(handle)
    return prompt_payload, schema_payload


def _sanitize_translation_style(payload: dict | None) -> dict:
    if not isinstance(payload, dict):
        return DEFAULT_TRANSLATION_STYLE.copy()

    palette_mode = str(payload.get("paletteMode") or DEFAULT_TRANSLATION_STYLE["paletteMode"])
    if palette_mode not in {"base", "deep", "soft", "mono"}:
        palette_mode = DEFAULT_TRANSLATION_STYLE["paletteMode"]

    bg_color = str(payload.get("bgColor") or DEFAULT_TRANSLATION_STYLE["bgColor"]).strip()
    if not bg_color.startswith("#") or len(bg_color) not in {4, 7}:
        bg_color = DEFAULT_TRANSLATION_STYLE["bgColor"]

    try:
        bg_opacity = float(payload.get("bgOpacity", DEFAULT_TRANSLATION_STYLE["bgOpacity"]))
    except Exception:
        bg_opacity = DEFAULT_TRANSLATION_STYLE["bgOpacity"]
    bg_opacity = min(max(bg_opacity, 0.0), 1.0)

    try:
        outline_thickness = float(payload.get("outlineThickness", DEFAULT_TRANSLATION_STYLE["outlineThickness"]))
    except Exception:
        outline_thickness = DEFAULT_TRANSLATION_STYLE["outlineThickness"]
    outline_thickness = min(max(outline_thickness, 0.0), 20.0)

    try:
        outline_strength = float(payload.get("outlineStrength", DEFAULT_TRANSLATION_STYLE["outlineStrength"]))
    except Exception:
        outline_strength = DEFAULT_TRANSLATION_STYLE["outlineStrength"]
    outline_strength = min(max(outline_strength, 0.0), 1.0)

    outline_color = str(payload.get("outlineColor") or DEFAULT_TRANSLATION_STYLE["outlineColor"]).strip()
    if not outline_color.startswith("#") or len(outline_color) not in {4, 7}:
        outline_color = DEFAULT_TRANSLATION_STYLE["outlineColor"]

    return {
        "outlineEnabled": bool(payload.get("outlineEnabled", DEFAULT_TRANSLATION_STYLE["outlineEnabled"])),
        "shadowEnabled": bool(payload.get("shadowEnabled", DEFAULT_TRANSLATION_STYLE["shadowEnabled"])),
        "outlineThickness": outline_thickness,
        "outlineStrength": outline_strength,
        "outlineColor": outline_color,
        "paletteMode": palette_mode,
        "bgColor": bg_color,
        "bgOpacity": bg_opacity,
    }


def _normalize_translation_language(value: object | None) -> str | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    lowered = raw.lower()
    if lowered == "ja":
        return "ja"
    if lowered == "en":
        return "en"
    if lowered in {"ar", "arabic"}:
        return "ar"
    if lowered in {"vi", "vietnamese"}:
        return "vi"
    if lowered in {"ko", "korean"}:
        return "ko"
    if lowered in {"es", "spanish"}:
        return "es"
    if lowered in {"fr", "french"}:
        return "fr"
    if lowered in {"ru", "russian"}:
        return "ru"
    if lowered in {"yue", "cantonese", "zh-yue", "zh-yue-hk"}:
        return "yue"
    if lowered in {"zh", "zh-hant", "zh_hant", "zh-tw", "zh-hk", "zh-mo"}:
        return "zh-Hant"
    if lowered in {"zh-hans", "zh_hans", "zh-cn"}:
        return "zh-Hans"
    return None


def _sanitize_translation_languages(payload) -> list[str]:
    if not isinstance(payload, (list, tuple)):
        return DEFAULT_TRANSLATION_LANGUAGES.copy()
    cleaned = []
    for item in payload:
        code = _normalize_translation_language(item)
        if code and code not in cleaned:
            cleaned.append(code)
    return cleaned or DEFAULT_TRANSLATION_LANGUAGES.copy()


def _load_translation_languages_setting() -> list[str]:
    saved = ldb.get_ui_preference("translation_languages")
    if saved is None:
        return DEFAULT_TRANSLATION_LANGUAGES.copy()
    return _sanitize_translation_languages(saved)


def _load_burn_layout_setting() -> dict:
    saved = ldb.get_ui_preference("burn_layout")
    if saved is None:
        return DEFAULT_BURN_LAYOUT.copy()
    return _sanitize_burn_layout(saved)


def _sanitize_video_prompt_spec(payload: dict | None) -> dict:
    if not isinstance(payload, dict):
        return DEFAULT_VIDEO_PROMPT_SPEC.copy()

    def _string(key: str, fallback: str) -> str:
        value = payload.get(key, fallback)
        if value is None:
            return fallback
        text = str(value).strip()
        return text or fallback

    auto_title = payload.get("autoTitle")
    auto_title = bool(auto_title) if isinstance(auto_title, bool) else DEFAULT_VIDEO_PROMPT_SPEC["autoTitle"]

    aspect_ratio = str(payload.get("aspectRatio") or DEFAULT_VIDEO_PROMPT_SPEC["aspectRatio"])
    if aspect_ratio not in {"16:9", "9:16", "auto"}:
        aspect_ratio = DEFAULT_VIDEO_PROMPT_SPEC["aspectRatio"]

    model_provided = "model" in payload and payload.get("model") is not None
    model_value = str(payload.get("model") or DEFAULT_VIDEO_PROMPT_SPEC["model"])
    if model_value not in {"sora-2", "sora-2-pro"}:
        model_value = DEFAULT_VIDEO_PROMPT_SPEC["model"]

    duration_value = str(payload.get("durationSeconds") or DEFAULT_VIDEO_PROMPT_SPEC["durationSeconds"])
    duration_value = "".join(ch for ch in duration_value if ch.isdigit())
    if duration_value:
        try:
            duration_int = int(duration_value)
        except Exception:
            duration_int = int(DEFAULT_VIDEO_PROMPT_SPEC["durationSeconds"])
    else:
        duration_int = int(DEFAULT_VIDEO_PROMPT_SPEC["durationSeconds"])
    max_seconds = 25 if (model_provided and model_value == "sora-2-pro") or not model_provided else 12
    duration_int = min(max(duration_int, 4), max_seconds)
    duration_value = str(duration_int)

    audio_language = str(payload.get("audioLanguage") or DEFAULT_VIDEO_PROMPT_SPEC["audioLanguage"])
    if audio_language not in {"auto", "en", "zh", "ja", "ko", "vi", "ar", "fr", "es"}:
        audio_language = DEFAULT_VIDEO_PROMPT_SPEC["audioLanguage"]

    scene_count = str(payload.get("sceneCount") or "").strip()
    scene_count = "".join(ch for ch in scene_count if ch.isdigit())

    return {
        "autoTitle": auto_title,
        "title": _string("title", DEFAULT_VIDEO_PROMPT_SPEC["title"]),
        "subject": _string("subject", DEFAULT_VIDEO_PROMPT_SPEC["subject"]),
        "action": _string("action", DEFAULT_VIDEO_PROMPT_SPEC["action"]),
        "environment": _string("environment", DEFAULT_VIDEO_PROMPT_SPEC["environment"]),
        "camera": _string("camera", DEFAULT_VIDEO_PROMPT_SPEC["camera"]),
        "lighting": _string("lighting", DEFAULT_VIDEO_PROMPT_SPEC["lighting"]),
        "mood": _string("mood", DEFAULT_VIDEO_PROMPT_SPEC["mood"]),
        "style": _string("style", DEFAULT_VIDEO_PROMPT_SPEC["style"]),
        "model": model_value,
        "aspectRatio": aspect_ratio,
        "durationSeconds": duration_value,
        "audioLanguage": audio_language,
        "sceneCount": scene_count,
        "spokenWords": _string("spokenWords", DEFAULT_VIDEO_PROMPT_SPEC["spokenWords"]),
        "extraRequirements": _string("extraRequirements", DEFAULT_VIDEO_PROMPT_SPEC["extraRequirements"]),
        "negative": _string("negative", DEFAULT_VIDEO_PROMPT_SPEC["negative"]),
    }


def _sanitize_history_list(payload) -> list[str]:
    if not isinstance(payload, (list, tuple)):
        return []
    cleaned: list[str] = []
    for item in payload:
        if item is None:
            continue
        text = str(item).strip()
        if not text:
            continue
        if text in cleaned:
            continue
        cleaned.append(text)
    return cleaned[:50]


def _sanitize_video_prompt_history(payload: dict | None) -> dict:
    if not isinstance(payload, dict):
        return DEFAULT_VIDEO_PROMPT_HISTORY.copy()

    def _clean_list(value) -> list[str]:
        if not isinstance(value, (list, tuple)):
            return []
        cleaned = []
        for item in value:
            text = str(item).strip()
            if not text or text in cleaned:
                continue
            cleaned.append(text)
        return cleaned[:20]

    return {
        "title": _clean_list(payload.get("title")),
        "subject": _clean_list(payload.get("subject")),
        "action": _clean_list(payload.get("action")),
        "environment": _clean_list(payload.get("environment")),
        "camera": _clean_list(payload.get("camera")),
        "lighting": _clean_list(payload.get("lighting")),
        "mood": _clean_list(payload.get("mood")),
        "style": _clean_list(payload.get("style")),
        "audioLanguage": _clean_list(payload.get("audioLanguage")),
        "sceneCount": _clean_list(payload.get("sceneCount")),
        "spokenWords": _clean_list(payload.get("spokenWords")),
        "extraRequirements": _clean_list(payload.get("extraRequirements")),
        "negative": _clean_list(payload.get("negative")),
    }


def _sanitize_burn_layout(payload: dict | list | None) -> dict:
    if payload is None:
        return DEFAULT_BURN_LAYOUT.copy()

    slots_payload = None
    height_ratio = DEFAULT_BURN_LAYOUT.get("heightRatio", 0.5)
    rows = DEFAULT_BURN_LAYOUT.get("rows", 4)
    cols = DEFAULT_BURN_LAYOUT.get("cols", 1)
    lift_ratio = DEFAULT_BURN_LAYOUT.get("liftRatio", 0.1)
    lift_slots = DEFAULT_BURN_LAYOUT.get("liftSlots", 0)
    ruby_spacing = DEFAULT_BURN_LAYOUT.get("rubySpacing", 0.1)
    romaji_default = DEFAULT_BURN_LAYOUT.get("romajiEnabled", True)
    pinyin_default = DEFAULT_BURN_LAYOUT.get("pinyinEnabled", True)
    if isinstance(payload, dict):
        slots_payload = payload.get("slots")
        if "heightRatio" in payload:
            try:
                height_ratio = float(payload.get("heightRatio"))
            except Exception:
                height_ratio = DEFAULT_BURN_LAYOUT.get("heightRatio", 0.5)
        if "rows" in payload:
            try:
                rows = int(payload.get("rows"))
            except Exception:
                rows = DEFAULT_BURN_LAYOUT.get("rows", 4)
        if "cols" in payload:
            try:
                cols = int(payload.get("cols"))
            except Exception:
                cols = DEFAULT_BURN_LAYOUT.get("cols", 1)
        if "liftRatio" in payload:
            try:
                lift_ratio = float(payload.get("liftRatio"))
            except Exception:
                lift_ratio = DEFAULT_BURN_LAYOUT.get("liftRatio", 0.1)
        if "liftSlots" in payload:
            try:
                lift_slots = int(payload.get("liftSlots"))
            except Exception:
                lift_slots = DEFAULT_BURN_LAYOUT.get("liftSlots", 0)
        if "rubySpacing" in payload:
            try:
                ruby_spacing = float(payload.get("rubySpacing"))
            except Exception:
                ruby_spacing = DEFAULT_BURN_LAYOUT.get("rubySpacing", 0.1)
        if "romajiEnabled" in payload:
            value = payload.get("romajiEnabled")
            if isinstance(value, bool):
                romaji_default = value
        if "pinyinEnabled" in payload:
            value = payload.get("pinyinEnabled")
            if isinstance(value, bool):
                pinyin_default = value
    elif isinstance(payload, list):
        slots_payload = payload

    if not isinstance(slots_payload, list):
        return DEFAULT_BURN_LAYOUT.copy()

    height_ratio = min(max(height_ratio, 0.2), 0.6)
    rows = min(max(rows, 1), 10)
    cols = min(max(cols, 1), 4)
    lift_slots = min(max(lift_slots, 0), rows)
    if lift_ratio is None:
        lift_ratio = DEFAULT_BURN_LAYOUT.get("liftRatio", 0.1)
    if not isinstance(lift_ratio, (int, float)):
        lift_ratio = DEFAULT_BURN_LAYOUT.get("liftRatio", 0.1)
    if "liftRatio" not in (payload or {}) and lift_slots:
        lift_ratio = (height_ratio / max(rows, 1)) * lift_slots
    lift_ratio = min(max(float(lift_ratio), 0.0), 0.4)
    ruby_spacing = min(max(float(ruby_spacing), 0.0), 0.2)
    slot_count = rows * cols

    slot_map: dict[int, dict[str, object]] = {}
    for idx, entry in enumerate(slots_payload):
        slot_id = idx + 1
        language = None
        font_scale = 1.0
        romaji = romaji_default
        pinyin = pinyin_default
        ipa = False
        jyutping = False
        romaja = False
        arabic_translit = False
        if isinstance(entry, dict):
            try:
                slot_id = int(entry.get("slot") or slot_id)
            except Exception:
                slot_id = idx + 1
            language = entry.get("language")
            try:
                font_scale = float(entry.get("fontScale", 1.0))
            except Exception:
                font_scale = 1.0
            if isinstance(entry.get("romaji"), bool):
                romaji = entry.get("romaji")
            if isinstance(entry.get("pinyin"), bool):
                pinyin = entry.get("pinyin")
            if isinstance(entry.get("ipa"), bool):
                ipa = entry.get("ipa")
            if isinstance(entry.get("jyutping"), bool):
                jyutping = entry.get("jyutping")
            if isinstance(entry.get("romaja"), bool):
                romaja = entry.get("romaja")
            if isinstance(entry.get("arabicTranslit"), bool):
                arabic_translit = entry.get("arabicTranslit")
        else:
            language = entry
        if slot_id < 1 or slot_id > slot_count:
            continue
        normalized = _normalize_translation_language(language) if language else None
        font_scale = min(max(font_scale, 0.6), 2.5)
        slot_map[slot_id] = {
            "language": normalized,
            "fontScale": font_scale,
            "romaji": romaji,
            "pinyin": pinyin,
            "ipa": ipa,
            "jyutping": jyutping,
            "romaja": romaja,
            "arabicTranslit": arabic_translit,
        }

    normalized_slots = []
    for slot_id in range(1, slot_count + 1):
        entry = slot_map.get(
            slot_id,
            {
                "language": None,
                "fontScale": 1.0,
                "romaji": romaji_default,
                "pinyin": pinyin_default,
                "ipa": False,
                "jyutping": False,
                "romaja": False,
                "arabicTranslit": False,
            },
        )
        normalized_slots.append(
            {
                "slot": slot_id,
                "language": entry.get("language"),
                "fontScale": entry.get("fontScale", 1.0),
                "romaji": entry.get("romaji", romaji_default),
                "pinyin": entry.get("pinyin", pinyin_default),
                "ipa": entry.get("ipa", False),
                "jyutping": entry.get("jyutping", False),
                "romaja": entry.get("romaja", False),
                "arabicTranslit": entry.get("arabicTranslit", False),
            }
        )

    return {
        "slots": normalized_slots,
        "heightRatio": height_ratio,
        "rows": rows,
        "cols": cols,
        "liftRatio": lift_ratio,
        "liftSlots": lift_slots,
        "rubySpacing": ruby_spacing,
        "romajiEnabled": romaji_default,
        "pinyinEnabled": pinyin_default,
    }



def detect_language_with_lingua(text, detector):
    """
    Detects the language of a given text using Lingua.
    Returns the ISO 639-1 code of the detected language if detection is confident; otherwise, returns None.
    """
    try:
        language = detector.detect_language_of(text)
        return language.iso_code_639_1.name.lower()  # Use .name to get the ISO code as a string
    except Exception as e:
        print(f"Language detection failed: {e}")
        return 'und'

def get_seconds(timestamp):
    print("timestamp: ", timestamp)
    # Split by ';' and take the last timestamp (if multiple timestamps are present)
    last_timestamp = timestamp.split(';')[0].strip()
    # Convert HH:MM:SS,mmm to HH:MM:SS.mmm and then to seconds
    h, m, s = last_timestamp.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)




# def extract_cover(video_path, image_path, time):
#     # Replace comma with dot for milliseconds
#     time = time.replace(',', '.')
#     ffmpeg_command = f"ffmpeg -y -ss {time} -i \"{video_path}\" -frames:v 1 \"{image_path}\""
#     subprocess.run(ffmpeg_command, shell=True, check=True)

def extract_cover(video_path, image_path, time):
    """
    Extracts a frame from a video at the specified time and saves it as an image.
    Compatible with newer FFmpeg versions that require additional flags for single image output.
    
    Args:
        video_path (str): Path to the input video file
        image_path (str): Path where the extracted frame will be saved
        time (str): Timestamp for the frame to extract (in format HH:MM:SS.ms)
    """
    import subprocess
    import os
    import shutil
    
    # Replace comma with dot for milliseconds
    time = time.replace(',', '.')
    
    # Try different approaches to extract the frame
    methods = [
        # Method 1: Use -update flag as suggested in the error message
        f"ffmpeg -y -ss {time} -i \"{video_path}\" -frames:v 1 -update 1 \"{image_path}\"",
        
        # Method 2: Explicitly specify the format
        f"ffmpeg -y -ss {time} -i \"{video_path}\" -frames:v 1 -f image2 -update 1 \"{image_path}\"",
        
        # Method 3: Use vframes instead of frames:v
        f"ffmpeg -y -ss {time} -i \"{video_path}\" -vframes 1 \"{image_path}\"",
        
        # Method 4: Use a temporary pattern filename and then rename
        f"ffmpeg -y -ss {time} -i \"{video_path}\" -vframes 1 \"{os.path.dirname(image_path)}/temp%03d.jpg\""
    ]
    
    success = False
    
    for i, method in enumerate(methods):
        try:
            print(f"Trying method {i+1} to extract cover frame...")
            subprocess.run(method, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            
            # If using Method 4 (temp filename with pattern), rename the file
            if i == 3:
                temp_file = f"{os.path.dirname(image_path)}/temp001.jpg"
                if os.path.exists(temp_file):
                    shutil.move(temp_file, image_path)
            
            success = True
            print(f"Successfully extracted cover frame using method {i+1}")
            break
            
        except subprocess.CalledProcessError as e:
            print(f"Method {i+1} failed: {e.stderr.decode() if e.stderr else str(e)}")
            continue
    
    if not success:
        print("Failed to extract cover frame using all methods. Attempting fallback...")
        try:
            # Fallback method: Use OpenCV to extract a frame
            import cv2
            
            cap = cv2.VideoCapture(video_path)
            # Convert time string to seconds
            time_parts = time.split(':')
            if len(time_parts) == 3:
                seconds = float(time_parts[0]) * 3600 + float(time_parts[1]) * 60 + float(time_parts[2])
            else:
                seconds = float(time)
                
            # Set position and read frame
            cap.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
            ret, frame = cap.read()
            
            if ret:
                cv2.imwrite(image_path, frame)
                print("Successfully extracted cover frame using OpenCV fallback")
                success = True
            
            cap.release()
            
        except Exception as e:
            print(f"OpenCV fallback failed: {str(e)}")
            
    if not success:
        raise RuntimeError("Failed to extract cover frame using all available methods")


def escape_ffmpeg_text(text):
    # Escaping single quotes and other special characters for FFmpeg drawtext filter
    return text.replace("'", "\\'").replace(":", "\\:")








def get_seconds_from_timestamp(timestamp):
    try:
        h, m, s = timestamp.split(':')
        s, ms = s.split(',')
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    except ValueError:
        # Return 0 if the timestamp is not parseable
        return 0

def format_timestamp(seconds):
    # Helper function to format seconds back to a timestamp string
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

# def get_time_range(time_range):
#     timestamps = time_range.split(' --> ')
#     if len(timestamps) == 2:
#         start_timestamp, end_timestamp = timestamps
#     elif len(timestamps) == 1:
#         # If there's only one timestamp, use it as the start and add 1 second for the end
#         start_timestamp = timestamps[0]
#         end_timestamp = format_timestamp(get_seconds_from_timestamp(start_timestamp) + 1)
#     else:
#         # Handle unexpected format by setting both start and end to 0
#         start_timestamp, end_timestamp = '00:00:00,000', '00:00:00,000'

#     start_seconds = get_seconds_from_timestamp(start_timestamp)
#     end_seconds = get_seconds_from_timestamp(end_timestamp)
    
#     # Add 1 second to end_timestamp if there's an error in parsing either timestamp
#     if start_seconds == 0 or end_seconds == 0:
#         end_seconds = start_seconds + 1
#         end_timestamp = format_timestamp(end_seconds)

#     return start_seconds, end_seconds


def get_time_range(time_range):
    """
    Updated to handle both old string format and new object format
    """
    if isinstance(time_range, dict):
        # New format: {"start": "HH:MM:SS,mmm", "end": "HH:MM:SS,mmm"}
        start_timestamp = time_range.get("start", "00:00:00,000")
        end_timestamp = time_range.get("end", "00:00:01,000")
    else:
        # Old format: "HH:MM:SS,mmm --> HH:MM:SS,mmm"
        timestamps = time_range.split(' --> ')
        if len(timestamps) == 2:
            start_timestamp, end_timestamp = timestamps
        elif len(timestamps) == 1:
            # If there's only one timestamp, use it as the start and add 1 second for the end
            start_timestamp = timestamps[0]
            end_timestamp = format_timestamp(get_seconds_from_timestamp(start_timestamp) + 1)
        else:
            # Handle unexpected format by setting both start and end to 0
            start_timestamp, end_timestamp = '00:00:00,000', '00:00:01,000'

    start_seconds = get_seconds_from_timestamp(start_timestamp)
    end_seconds = get_seconds_from_timestamp(end_timestamp)
    
    # Add 1 second to end_timestamp if there's an error in parsing either timestamp
    if start_seconds == 0 or end_seconds == 0:
        end_seconds = start_seconds + 1
        end_timestamp = format_timestamp(end_seconds)

    return start_seconds, end_seconds


def get_video_length_alternative(filename):
    from moviepy.editor import VideoFileClip
    import moviepy.editor as mp
    """Returns the length of the video in seconds using moviepy. Returns -1 if unable to determine."""
    try:
        with VideoFileClip(filename) as video:
            return video.duration
    except Exception as e:
        print(f"Warning: Failed to get video length for {filename}. Error: {e}")
        return -1



def get_video_length(filename):
    """Returns the length of the video in seconds or None if unable to determine."""
    try:
        cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{filename}\""
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        video_length = float(output)
        return video_length
    except Exception as e:
        print(f"Warning: Failed to get video length for {filename}. Error: {e}")
        # return None
        return get_video_length_alternative(filename)


def get_video_resolution(video_path):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height


def has_audio_stream(video_path):
    command = (
        f"ffprobe -v error -select_streams a "
        f"-show_entries stream=codec_type -of csv=p=0 \"{video_path}\""
    )
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        check=False,
    )
    return bool(result.stdout.strip())


def write_empty_transcription_files(output_json_path, output_srt_path, output_md_path, message):
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump([], json_file)
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write("")
    with open(output_md_path, "w", encoding="utf-8") as md_file:
        md_file.write(f"{message}\n")


def write_markdown_from_srt(srt_path, md_path, empty_message="No transcription available."):
    if not os.path.exists(srt_path):
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(f"{empty_message}\n")
        return
    entries = []
    current_time = None
    current_text = []
    with open(srt_path, "r", encoding="utf-8", errors="ignore") as srt_file:
        for line in srt_file:
            stripped = line.strip()
            if not stripped:
                if current_time and current_text:
                    entries.append(f"- {current_time}: {' '.join(current_text)}")
                current_time = None
                current_text = []
                continue
            if stripped.isdigit():
                continue
            if "-->" in stripped:
                current_time = stripped
                current_text = []
                continue
            current_text.append(stripped)
    if current_time and current_text:
        entries.append(f"- {current_time}: {' '.join(current_text)}")
    if not entries:
        entries.append(empty_message)
    with open(md_path, "w", encoding="utf-8") as md_file:
        md_file.write("\n".join(entries) + "\n")


def build_transcription_preview(md_path=None, srt_path=None, max_lines=6):
    def read_lines(path):
        if not path or not os.path.exists(path):
            return None
        lines = []
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                lines.append(stripped)
                if len(lines) >= max_lines:
                    break
        return "\n".join(lines) if lines else None

    md_preview = read_lines(md_path)
    if md_preview:
        return md_preview

    if not srt_path or not os.path.exists(srt_path):
        return None
    lines = []
    with open(srt_path, "r", encoding="utf-8", errors="ignore") as srt_file:
        for line in srt_file:
            stripped = line.strip()
            if not stripped or stripped.isdigit() or "-->" in stripped:
                continue
            lines.append(stripped)
            if len(lines) >= max_lines:
                break
    return "\n".join(lines) if lines else None


def find_latest_caption_outputs(output_folder, base_name):
    srt_pattern = os.path.join(output_folder, f"{base_name}_caption_*.srt")
    json_pattern = os.path.join(output_folder, f"{base_name}_caption_*.json")
    srt_files = glob.glob(srt_pattern)
    json_files = glob.glob(json_pattern)
    latest_srt = max(srt_files, key=os.path.getmtime) if srt_files else None
    latest_json = max(json_files, key=os.path.getmtime) if json_files else None
    return latest_srt, latest_json


def find_latest_transcription_outputs(output_folder, base_name):
    if not output_folder or not base_name:
        return None, None
    default_json = os.path.join(output_folder, f"{base_name}_mixed.json")
    default_srt = os.path.join(output_folder, f"{base_name}_mixed.srt")
    if os.path.exists(default_json) and os.path.exists(default_srt):
        return default_json, default_srt
    json_pattern = os.path.join(output_folder, f"{base_name}_mixed*.json")
    srt_pattern = os.path.join(output_folder, f"{base_name}_mixed*.srt")
    json_files = glob.glob(json_pattern)
    srt_files = glob.glob(srt_pattern)
    latest_json = max(json_files, key=os.path.getmtime) if json_files else None
    latest_srt = max(srt_files, key=os.path.getmtime) if srt_files else None
    return latest_json, latest_srt


def _normalize_transcription_language(value: object | None) -> str | None:
    if value is None:
        return None
    raw = str(value).strip().lower()
    if not raw:
        return None
    if raw in {"yue", "zh-yue", "yue-hk", "zh-yue-hk"}:
        return "yue"
    if raw in {"zh", "zho", "cmn", "zh-cn", "zh-tw", "zh-hk", "zh-mo", "zh-hans", "zh-hant"}:
        return "zh"
    if raw in {"en", "ja", "ko", "vi", "ar", "fr", "es", "ru"}:
        return raw
    return raw


def _summarize_transcription_languages(json_path: str | None) -> tuple[str | None, list[dict[str, int]]]:
    if not json_path or not os.path.exists(json_path):
        return None, []
    try:
        with open(json_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return None, []

    if isinstance(payload, dict):
        items = payload.get("items") or payload.get("subtitles") or payload.get("segments") or []
    elif isinstance(payload, list):
        items = payload
    else:
        items = []

    counts: dict[str, int] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        lang = _normalize_transcription_language(item.get("lang") or item.get("language"))
        if not lang:
            continue
        counts[lang] = counts.get(lang, 0) + 1

    if not counts:
        return None, []

    primary = max(counts.items(), key=lambda pair: pair[1])[0]
    summary = [
        {"language": lang, "count": count}
        for lang, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    ]
    return primary, summary


def _build_transcription_language_map(json_path: str | None) -> dict[tuple[str, str], str]:
    if not json_path or not os.path.exists(json_path):
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return {}

    if isinstance(payload, dict):
        items = payload.get("items") or payload.get("subtitles") or payload.get("segments") or []
    elif isinstance(payload, list):
        items = payload
    else:
        items = []

    mapping: dict[tuple[str, str], str] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        start = item.get("start")
        end = item.get("end")
        if not start or not end:
            continue
        lang = _normalize_transcription_language(item.get("lang") or item.get("language"))
        if not lang:
            continue
        mapping[(str(start), str(end))] = lang
    return mapping


def _speaker_lang_key(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip().lower()
    if raw in {"zh", "zh-hant", "zh_hant", "zh-hans", "zh_hans", "zh-cn", "zh-tw", "zh-hk", "zh-mo"}:
        return "zh"
    if raw in {"yue", "zh-yue", "yue-hk", "zh-yue-hk"}:
        return "yue"
    return raw


def _prepare_speaker_json(
    json_path: str,
    output_dir: str,
    slot_language: str,
    text_key: str | None,
    speaker_map: dict[tuple[str, str], str],
    icon: str = "🔊",
) -> str:
    if not speaker_map or not json_path or not os.path.exists(json_path):
        return json_path
    try:
        with open(json_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return json_path

    if isinstance(payload, dict):
        items = payload.get("items") or payload.get("subtitles") or payload.get("segments") or []
        container = payload
    elif isinstance(payload, list):
        items = payload
        container = None
    else:
        return json_path

    slot_key = _speaker_lang_key(slot_language)
    if not slot_key:
        return json_path

    modified = False
    for item in items:
        if not isinstance(item, dict):
            continue
        start = item.get("start")
        end = item.get("end")
        if not start or not end:
            continue
        original_lang = _speaker_lang_key(speaker_map.get((str(start), str(end))))
        if not original_lang or original_lang != slot_key:
            continue

        tokens = item.get("tokens")
        if isinstance(tokens, list):
            if tokens and isinstance(tokens[0], dict) and tokens[0].get("type") == "speaker":
                # Ensure the speaker token carries a non-empty glyph so downstream
                # token normalization (e.g. kana-affix splitting) doesn't drop it.
                if not tokens[0].get("text"):
                    tokens[0]["text"] = icon
                    modified = True
                continue
            item["tokens"] = [{"text": icon, "type": "speaker"}] + tokens
            modified = True
            continue

        key = text_key or "text"
        text_value = None
        if key in item and isinstance(item[key], str):
            text_value = item[key]
        elif "text" in item and isinstance(item["text"], str):
            text_value = item["text"]

        if text_value:
            item["tokens"] = [
                {"text": icon, "type": "speaker"},
                {"text": text_value},
            ]
            modified = True
            continue

    if not modified:
        return json_path

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(json_path))[0]
    safe_lang = slot_language.replace("/", "_")
    output_path = os.path.join(output_dir, f"{base_name}_speaker_{safe_lang}.json")
    try:
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(container if container is not None else items, handle, ensure_ascii=False, indent=2)
    except Exception:
        return json_path
    return output_path


def build_srt_preview_with_timestamps(srt_path, max_entries=6):
    if not srt_path or not os.path.exists(srt_path):
        return None
    preview_lines = []
    with open(srt_path, "r", encoding="utf-8", errors="ignore") as handle:
        block = []
        for raw in handle:
            line = raw.strip()
            if not line:
                if block:
                    preview_lines.append(block)
                    block = []
                continue
            block.append(line)
        if block:
            preview_lines.append(block)

    lines = []
    for block in preview_lines:
        if not block:
            continue
        time_line = next((b for b in block if "-->" in b), None)
        if not time_line:
            continue
        parts = [p.strip() for p in time_line.split("-->")]
        if len(parts) != 2:
            continue
        text_lines = [b for b in block if b != time_line and not b.isdigit()]
        text = " ".join(text_lines).strip()
        if not text:
            continue
        lines.append(f"- {parts[0]} --> {parts[1]}: {text}")
        if len(lines) >= max_entries:
            break
    return "\n".join(lines) if lines else None


def find_latest_caption_frames_dir(output_folder, base_name):
    if not output_folder or not base_name:
        return None
    candidates = []
    default_dir = os.path.join(output_folder, f"{base_name}_captioning_frames")
    if os.path.isdir(default_dir):
        candidates.append(default_dir)
    pattern = os.path.join(output_folder, f"{base_name}_captioning_frames_*")
    for path in glob.glob(pattern):
        if os.path.isdir(path):
            candidates.append(path)
    if not candidates:
        return None
    scored = []
    for path in candidates:
        files = list_caption_frame_files(path)
        if files:
            scored.append((len(files), os.path.getmtime(path), path))
    if scored:
        scored.sort(reverse=True)
        return scored[0][2]
    return max(candidates, key=os.path.getmtime)


def list_caption_frame_files(output_dir):
    if not output_dir or not os.path.isdir(output_dir):
        return []
    files = [
        os.path.join(output_dir, name)
        for name in os.listdir(output_dir)
        if name.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    files = sorted(files)
    preferred = [path for path in files if "-R" not in os.path.basename(path)]
    return preferred or files


def load_caption_entries(json_path, srt_path):
    if json_path and os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            entries = []
            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    text = item.get("text") or item.get("caption")
                    if not text:
                        continue
                    entries.append({
                        "start": item.get("start"),
                        "end": item.get("end"),
                        "text": text,
                    })
            if entries:
                return entries
        except Exception:
            pass
    if not srt_path or not os.path.exists(srt_path):
        return []
    entries = []
    current = None
    buffer = []
    with open(srt_path, "r", encoding="utf-8", errors="ignore") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                if current:
                    current["text"] = " ".join(buffer).strip()
                    entries.append(current)
                current = None
                buffer = []
                continue
            if line.isdigit():
                continue
            if "-->" in line:
                parts = [part.strip() for part in line.split("-->")]
                if len(parts) == 2:
                    current = {"start": parts[0], "end": parts[1], "text": ""}
                continue
            if current is not None:
                buffer.append(line)
    if current:
        current["text"] = " ".join(buffer).strip()
        entries.append(current)
    return entries


def build_caption_frame_payload(output_folder, base_name, json_path, srt_path):
    frames_dir = find_latest_caption_frames_dir(output_folder, base_name)
    frame_files = list_caption_frame_files(frames_dir)
    entries = load_caption_entries(json_path, srt_path)
    payload = []
    for idx, path in enumerate(frame_files):
        url = media_url_for_path(path)
        if not url:
            continue
        entry = entries[idx] if idx < len(entries) else {}
        payload.append({
            "url": url,
            "text": entry.get("text"),
            "start": entry.get("start"),
            "end": entry.get("end"),
        })
    return payload


def list_keyframe_files(output_dir):
    if not output_dir or not os.path.isdir(output_dir):
        return []
    files = [
        os.path.join(output_dir, name)
        for name in os.listdir(output_dir)
        if name.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    return sorted(files)


def clean_keyframe_dir(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for name in os.listdir(output_dir):
        if name.lower().endswith((".jpg", ".jpeg", ".png")):
            os.remove(os.path.join(output_dir, name))


def extract_keyframes_scene(input_file, output_dir, scene_threshold=0.35):
    command = (
        f'ffmpeg -y -i "{input_file}" '
        f'-vf "select=\'gt(scene,{scene_threshold})\',scale=480:-2" '
        f'-vsync vfr -q:v 3 "{output_dir}/scene_%03d.jpg"'
    )
    subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)


def extract_keyframes_uniform(input_file, output_dir, target_count=8, duration=None):
    if not duration or duration <= 0:
        duration = None
    if duration:
        fps = target_count / duration
        fps = max(min(fps, 8.0), 0.2)
    else:
        fps = 1.0
    command = (
        f'ffmpeg -y -i "{input_file}" '
        f'-vf "fps={fps},scale=480:-2" '
        f'-frames:v {target_count} -q:v 3 "{output_dir}/uniform_%03d.jpg"'
    )
    subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)


def extract_keyframes_opencv(input_file, output_dir, target_count=8):
    cap = cv2.VideoCapture(input_file)
    if not cap.isOpened():
        raise RuntimeError("Failed to open video for keyframe extraction.")
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = None
    if fps and fps > 0 and total_frames and total_frames > 0:
        duration = total_frames / fps
    if duration and duration > 0:
        times = [(i + 0.5) * duration / target_count for i in range(target_count)]
        for idx, t in enumerate(times):
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ret, frame = cap.read()
            if not ret:
                continue
            cv2.imwrite(os.path.join(output_dir, f"cv_{idx:03d}.jpg"), frame)
    elif total_frames and total_frames > 0:
        indices = [int((i + 0.5) * total_frames / target_count) for i in range(target_count)]
        for idx, frame_idx in enumerate(indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                continue
            cv2.imwrite(os.path.join(output_dir, f"cv_{idx:03d}.jpg"), frame)
    else:
        cap.release()
        raise RuntimeError("Unable to determine video duration for keyframes.")
    cap.release()


def extract_keyframes(input_file, output_dir, target_count=8):
    clean_keyframe_dir(output_dir)
    duration = get_video_length(input_file)

    try:
        extract_keyframes_scene(input_file, output_dir)
        frames = list_keyframe_files(output_dir)
        if len(frames) >= max(3, min(target_count, 6)):
            return frames, "scene"
    except Exception:
        frames = []

    clean_keyframe_dir(output_dir)
    try:
        extract_keyframes_uniform(input_file, output_dir, target_count=target_count, duration=duration)
        frames = list_keyframe_files(output_dir)
        if frames:
            return frames, "uniform"
    except Exception:
        frames = []

    clean_keyframe_dir(output_dir)
    extract_keyframes_opencv(input_file, output_dir, target_count=target_count)
    frames = list_keyframe_files(output_dir)
    return frames, "opencv"




def convert_time_to_seconds(time_str):
    """
    Convert a timestamp from "HH:MM:SS,mmm" format to seconds.
    """
    hours, minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split(',')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000



# def adjust_teaser_range(teaser_start, teaser_end, subtitles, video_length, max_length=4, min_length=2):
#     """
#     Adjust the teaser range based on subtitle timings, treating start and end as equivalent time points.
#     """
#     print("Adjusting teaser range...")

#     teaser_start_td = timedelta(seconds=teaser_start)
#     teaser_end_td = timedelta(seconds=teaser_end)
#     video_length_td = timedelta(seconds=video_length)

#     # Get all subtitle boundaries (start and end) as a sorted list of time points
#     subtitle_boundaries = sorted({timedelta(seconds=s['start']) for s in subtitles} | {timedelta(seconds=s['end']) for s in subtitles})

#     # Function to find closest subtitle boundary for adjustment
#     def find_adjustment(time, adjust_end=True, increase=True):
#         if adjust_end:
#             if increase:
#                 # Extend end: find the next boundary after current end
#                 return next((t for t in subtitle_boundaries if t > time), None)
#             else:
#                 # Reduce end: find the last boundary before current end
#                 return next((t for t in reversed(subtitle_boundaries) if t < time), None)
#         else:
#             if increase:
#                 # Extend start: find the last boundary before current start
#                 return next((t for t in reversed(subtitle_boundaries) if t < time), None)
#             else:
#                 # Reduce start: find the next boundary after current start
#                 return next((t for t in subtitle_boundaries if t > time), None)
    

#     # Adjusting for too long teaser
#     while teaser_end_td - teaser_start_td > timedelta(seconds=max_length):
#         new_end = find_adjustment(teaser_end_td, adjust_end=True, increase=False)
#         if new_end and new_end - teaser_start_td >= timedelta(seconds=min_length):
#             teaser_end_td = new_end
#         else:
#             new_start = find_adjustment(teaser_start_td, adjust_end=False, increase=False)
#             if new_start and teaser_end_td - new_start >= timedelta(seconds=min_length):
#                 teaser_start_td = new_start
#             else:
#                 break

#     # Adjusting for too short teaser
#     while teaser_end_td - teaser_start_td < timedelta(seconds=min_length):
#         new_end = find_adjustment(teaser_end_td, adjust_end=True, increase=True)
#         if new_end and new_end - teaser_start_td <= timedelta(seconds=max_length) and new_end <= video_length_td:
#             teaser_end_td = new_end
#         else:
#             new_start = find_adjustment(teaser_start_td, adjust_end=False, increase=True)
#             if new_start and teaser_end_td - new_start <= timedelta(seconds=max_length) and new_start >= 0:
#                 teaser_start_td = new_start
#             else:
#                 break  # No suitable adjustment found

#     return teaser_start_td.total_seconds(), teaser_end_td.total_seconds()

def adjust_teaser_range(teaser_start, teaser_end, subtitles, video_length, max_length=4, min_length=2):
    """
    Adjust the teaser range based on subtitle timings, treating start and end as equivalent time points.
    """
    teaser_start_td = timedelta(seconds=teaser_start)
    teaser_end_td = timedelta(seconds=teaser_end)
    video_length_td = timedelta(seconds=video_length)

    subtitle_boundaries = sorted({timedelta(seconds=s['start']) for s in subtitles} | {timedelta(seconds=s['end']) for s in subtitles})

    def find_adjustment(time, adjust_end=True, increase=True):
        if adjust_end:
            if increase:
                return next((t for t in subtitle_boundaries if t > time), None)
            else:
                return next((t for t in reversed(subtitle_boundaries) if t < time), None)
        else:
            if increase:
                return next((t for t in reversed(subtitle_boundaries) if t < time), None)
            else:
                return next((t for t in subtitle_boundaries if t > time), None)
    
    while teaser_end_td - teaser_start_td > timedelta(seconds=max_length):
        new_end = find_adjustment(teaser_end_td, adjust_end=True, increase=False)
        if new_end and new_end - teaser_start_td >= timedelta(seconds=min_length):
            teaser_end_td = new_end
        else:
            new_start = find_adjustment(teaser_start_td, adjust_end=False, increase=False)
            if new_start and teaser_end_td - new_start >= timedelta(seconds=min_length):
                teaser_start_td = new_start
            else:
                break

    while teaser_end_td - teaser_start_td < timedelta(seconds=min_length):
        new_end = find_adjustment(teaser_end_td, adjust_end=True, increase=True)
        if new_end and new_end - teaser_start_td <= timedelta(seconds=max_length) and new_end <= video_length_td:
            teaser_end_td = new_end
        else:
            new_start = find_adjustment(teaser_start_td, adjust_end=False, increase=True)
            if new_start and teaser_end_td - new_start <= timedelta(seconds=max_length) and new_start >= timedelta(seconds=0):
                teaser_start_td = new_start
            else:
                break

    return teaser_start_td.total_seconds(), teaser_end_td.total_seconds()


# def calculate_optimal_teaser_range(metadata_path, subtitle_json_path, video_length):
#     """
#     Calculate an optimized teaser range based on the video's metadata and subtitle timings.
#     """

#     print("Calculating optimal teaser time...")
#     try:
#         with open(metadata_path, 'r') as meta_file:
#             metadata = json.load(meta_file)
#             teaser = metadata["teaser"].split(" --> ")
#             teaser_start, teaser_end = convert_time_to_seconds(teaser[0]), convert_time_to_seconds(teaser[1])
            
#             teaser_start = max(teaser_start, 0)
#             teaser_end = min(teaser_end, video_length)

#         with open(subtitle_json_path, 'r') as sub_file:
#             subtitles = json.load(sub_file)
#             subtitles = [{'start': convert_time_to_seconds(sub['start']), 'end': convert_time_to_seconds(sub['end'])} for sub in subtitles]

#         adjusted_start, adjusted_end = adjust_teaser_range(teaser_start, teaser_end, subtitles, video_length)

#         return adjusted_start, adjusted_end
#     except Exception as e:
#         print(f"Error adjusting teaser range: {e}")
#         # Return default range if there's an error
#         default_start, default_end = 0, calculate_optimal_repeat_sec(subtitle_json_path)
#         return default_start, default_end

def calculate_optimal_teaser_range(metadata_path, subtitle_json_path, video_length):
    """
    Calculate an optimized teaser range based on the video's metadata and subtitle timings.
    Updated to handle new JSON format.
    """
    print("Calculating optimal teaser time...")
    try:
        with open(metadata_path, 'r') as meta_file:
            metadata = json.load(meta_file)
            teaser = metadata["teaser"]
            
            # Handle both old and new format
            if isinstance(teaser, dict):
                # New format: {"start": "HH:MM:SS,mmm", "end": "HH:MM:SS,mmm"}
                teaser_start = convert_time_to_seconds(teaser["start"])
                teaser_end = convert_time_to_seconds(teaser["end"])
            else:
                # Old format: "HH:MM:SS,mmm --> HH:MM:SS,mmm"
                teaser_parts = teaser.split(" --> ")
                teaser_start = convert_time_to_seconds(teaser_parts[0])
                teaser_end = convert_time_to_seconds(teaser_parts[1])
            
            teaser_start = max(teaser_start, 0)
            teaser_end = min(teaser_end, video_length)

        with open(subtitle_json_path, 'r') as sub_file:
            subtitles = json.load(sub_file)
            subtitles = [{'start': convert_time_to_seconds(sub['start']), 'end': convert_time_to_seconds(sub['end'])} for sub in subtitles]

        adjusted_start, adjusted_end = adjust_teaser_range(teaser_start, teaser_end, subtitles, video_length)

        return adjusted_start, adjusted_end
    except Exception as e:
        print(f"Error adjusting teaser range: {e}")
        # Return default range if there's an error
        default_start, default_end = 0, calculate_optimal_repeat_sec(subtitle_json_path)
        return default_start, default_end

def calculate_optimal_repeat_sec(subtitle_json_path):
    with open(subtitle_json_path, 'r') as file:
        subtitles = json.load(file)

    # Initialize thresholds
    min_threshold = timedelta(seconds=2)
    optimal_threshold = timedelta(seconds=3)
    max_threshold = timedelta(seconds=4)
    
    video_start = datetime.strptime("00:00:00,000", "%H:%M:%S,%f")
    optimal_duration = 0
    min_duration_over_two = 0  # Track if we have a duration over 2 seconds

    print("Calculating optimal repeat time...")
    for subtitle in subtitles:
        start_time = datetime.strptime(subtitle["start"], "%H:%M:%S,%f")
        end_time = datetime.strptime(subtitle["end"], "%H:%M:%S,%f")
        current_duration = (end_time - video_start).total_seconds()

        if optimal_threshold.total_seconds() < current_duration <= max_threshold.total_seconds():
            return current_duration  # Return this duration if it's within the optimal range (over 3 but not over 4)

        if min_threshold.total_seconds() < current_duration <= optimal_threshold.total_seconds():
            min_duration_over_two = max(min_duration_over_two, current_duration)  # Update if this is the largest duration over 2 but under 3

    # If we found a duration over 2 but under 3 seconds, return it
    if min_duration_over_two > 0:
        return min_duration_over_two

    # If no duration is found within the optimal or acceptable range, default to 2 seconds
    return 3.0

def repeat_start_of_video(video_path, repeat_sec, output_path):
    # repeat_command = [
    #     "ffmpeg", "-y", "-i", video_path, "-filter_complex",
    #     f"[0:v]trim=0:{repeat_sec},setpts=PTS-STARTPTS[first3v];[0:a]atrim=0:{repeat_sec},asetpts=PTS-STARTPTS[first3a];"
    #     f"[first3v][0:v]concat=n=2:v=1:a=0[finalv];[first3a][0:a]concat=n=2:v=0:a=1[finala]",
    #     "-map", "[finalv]", "-map", "[finala]", output_path
    # ]
    # subprocess.run(repeat_command, check=True)
    repeat_command = [
        "ffmpeg", "-y", "-i", video_path, "-filter_complex",
        f"[0:v]trim=0:{repeat_sec},setpts=PTS-STARTPTS[first3v];[0:a]atrim=0:{repeat_sec},asetpts=PTS-STARTPTS[first3a];"
        f"[first3v][0:v]concat=n=2:v=1:a=0[finalv];[first3a][0:a]concat=n=2:v=0:a=1[finala]",
        "-map", "[finalv]", "-map", "[finala]", "-movflags", "+faststart", output_path  # Add here
    ]

# def insert_video_segment_at_start(video_path, start_time, end_time, output_path):
#     """
#     Inserts a specific segment of a video at the beginning of the original video.

#     Args:
#     - video_path: Path to the input video file.
#     - start_time: Start time of the segment to insert (in seconds).
#     - end_time: End time of the segment to insert (in seconds).
#     - output_path: Path to save the output video with the segment inserted at the start.
#     """

#     print("Adding teaser...")

#     # Correctly format the ffmpeg command
#     ffmpeg_command = (
#         f'ffmpeg -y -i "{video_path}" -filter_complex '
#         f'"[0:v]trim=start={start_time}:end={end_time},setpts=PTS-STARTPTS[firstv];'
#         f'[0:a]atrim=start={start_time}:end={end_time},asetpts=PTS-STARTPTS[firsta];'
#         f'[firstv][0:v]concat=n=2:v=1:a=0[finalv];'
#         f'[firsta][0:a]concat=n=2:v=0:a=1[finala]" '
#         f'-map "[finalv]" -map "[finala]" "{output_path}"'
#     )

#     try:
#         # Execute the ffmpeg command
#         subprocess.run(ffmpeg_command, check=True, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
#         print("Segment successfully inserted at the start of the video.")
#     except subprocess.CalledProcessError as e:
#         print(f"An error occurred: {e.stderr.decode()}\nReturning the original file.")
#         # Use shutil.copy2 to copy the original file to the output path, preserving metadata
#         shutil.copy2(video_path, output_path)
#         # return output_path  # Return the path to the copied original file

#         # return video_path

#     return output_path

def insert_video_segment_at_start(video_path, start_time, end_time, output_path):
    """
    Inserts a specific segment of a video at the beginning of the original video.
    
    Args:
    - video_path: Path to the input video file.
    - start_time: Start time of the segment to insert (in seconds).
    - end_time: End time of the segment to insert (in seconds).
    - output_path: Path to save the output video with the segment inserted at the start.
    """
    import os
    import subprocess
    import shutil
    import tempfile

    print("Adding teaser...")
    
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        # First extract the segment to a separate file with the same codec
        segment_path = os.path.join(temp_dir, "segment.mp4")
        extract_cmd = (
            f'ffmpeg -y -i "{video_path}" -ss {start_time} -to {end_time} '
            f'-c:v libx264 -c:a aac -strict experimental "{segment_path}"'
        )
        
        try:
            # Extract the segment
            subprocess.run(extract_cmd, check=True, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            
            # Now concatenate the segment with the original video using the concat demuxer
            concat_list_path = os.path.join(temp_dir, "concat_list.txt")
            
            # Write the concat list file with absolute paths
            with open(concat_list_path, 'w') as f:
                f.write(f"file '{os.path.abspath(segment_path)}'\n")
                f.write(f"file '{os.path.abspath(video_path)}'\n")
            
            # Use the concat demuxer for more reliable concatenation
            concat_cmd = (
                f'ffmpeg -y -f concat -safe 0 -i "{concat_list_path}" '
                f'-c copy "{output_path}"'
            )
            
            subprocess.run(concat_cmd, check=True, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            print("Segment successfully inserted at the start of the video.")
            
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr.decode()}")
            print("Trying alternative method...")
            
            try:
                # Alternative method using the concat filter with explicit codec specification
                alt_concat_cmd = (
                    f'ffmpeg -y -i "{segment_path}" -i "{video_path}" -filter_complex '
                    f'"[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]" '
                    f'-map "[outv]" -map "[outa]" -c:v libx264 -c:a aac -strict experimental "{output_path}"'
                )
                
                subprocess.run(alt_concat_cmd, check=True, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                print("Segment successfully inserted using alternative method.")
                
            except subprocess.CalledProcessError as e2:
                print(f"Alternative method also failed: {e2.stderr.decode()}")
                print("Returning the original file.")
                shutil.copy2(video_path, output_path)
    
    return output_path

def insert_video_segment_at_start_with_temp(video_path, start_time, end_time, output_path):
    """
    Inserts a specific segment of a video at the beginning of the original video.
    
    Args:
    - video_path: Path to the input video file (can be relative or absolute).
    - start_time: Start time of the segment to insert (in seconds).
    - end_time: End time of the segment to insert (in seconds).
    - output_path: Path to save the output video with the segment inserted at the start (can be relative or absolute).
    """

    # Convert paths to absolute paths to avoid confusion
    video_path = os.path.abspath(video_path)
    output_path = os.path.abspath(output_path)
    directory = os.path.dirname(video_path)
    basename = os.path.splitext(os.path.basename(video_path))[0]
    temp_segment_path = os.path.join(directory, f"{basename}_temp_segment.mp4")
    concat_list_path = os.path.join(directory, f"{basename}_concat_list.txt")

    print("Adding teaser...")

    try:
        # Step 1: Extract the segment
        subprocess.run(
            ['ffmpeg', '-y', '-i', video_path,
             '-ss', str(start_time), '-to', str(end_time),
             '-c:v', 'libx264', '-c:a', 'aac', temp_segment_path],
            check=True
        )

        # Step 2: Create a concat list file with absolute paths
        with open(concat_list_path, 'w') as f:
            f.writelines([f"file '{temp_segment_path}'\n", f"file '{video_path}'\n"])

        # Step 3: Concatenate using the concat list
        subprocess.run(
            ['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
             '-i', concat_list_path, '-c:v', 'libx264', '-c:a', 'aac',
             '-strict', 'experimental', output_path],
            check=True
        )

        print(f"Segment successfully inserted. Output saved to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}\nReturning the original file.")
        shutil.copy2(video_path, output_path)
        # return video_path
    finally:
        # Clean up temporary files
        os.remove(temp_segment_path)
        os.remove(concat_list_path)

    return output_path

def get_word_card_image(word, output_folder):
    # URL of the API
    url = 'http://lazyingart:8082/get_words_card'
    # url = 'http://lazyingart:7788/get_word_etymology/'
    data = {"word": word}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        content = response.json()
        image_data = base64.b64decode(content['image'])

        # Construct file path
        image_path = os.path.join(output_folder, f"{word}.jpeg")
        with open(image_path, 'wb') as file:
            file.write(image_data)
        print(f'Image for word "{word}" saved as {image_path}')
        return image_path
    else:
        print(f'Error fetching image for word "{word}": {response.status_code}')
        return None

def get_etymology_image(word, output_folder):
    # URL of the API
    # url = 'http://lazyingart:8082/get_words_card'
    url = 'http://lazyingart:7788/get_word_etymology/'
    data = {"word": word}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        content = response.json()
        image_data = base64.b64decode(content['image'])

        # Construct file path
        image_path = os.path.join(output_folder, f"{word}-etymology.jpeg")
        with open(image_path, 'wb') as file:
            file.write(image_data)
        print(f'Image for word "{word}" saved as {image_path}')
        return image_path
    else:
        print(f'Error fetching image for word "{word}": {response.status_code}')
        return None


# def add_first_word_card_to_video(video_path, english_words_to_learn, output_folder, duration=3):
#     if not english_words_to_learn:
#         print("No words to learn provided.")
#         return video_path, english_words_to_learn, None  # No word card to add

#     first_word_info = english_words_to_learn[0]
#     english_words_to_learn = english_words_to_learn[1:]  # Exclude the first word for further processing

#     try:
#         word_card_image_path = get_word_card_image(first_word_info["word"], output_folder)
#     except:
#         print("Failed to request word: ", first_word_info["word"])
#         word_card_image_path = get_word_card_image("hello", output_folder)

#     # filename, file_extension = os.path.splitext(os.path.basename(video_path))
#     # output_path = os.path.join(self.output_dir, f"{filename}_with_words_card{file_extension}")

#     if word_card_image_path:
#         video_add_words_card = VideoAddWordsCard(video_path, word_card_image_path, duration=duration)
#         try:
#             video_with_first_word_card_path, _ = video_add_words_card.add_image_to_video()
#             return video_with_first_word_card_path, english_words_to_learn, word_card_image_path
#         except Exception as e:
#             print("Error in adding cover word: ", str(e))
#             # shutil.copy2(video_path, video_with_first_word_card_path)
#             # return video_with_first_word_card_path, english_words_to_learn, word_card_image_path
#             return video_path, english_words_to_learn, word_card_image_path
#     else:
#         print(f"Failed to obtain word card for '{first_word_info['word']}'. Proceeding without adding word card.")
#         # shutil.copy2(video_path, video_with_first_word_card_path)
#         # return video_with_first_word_card_path, english_words_to_learn, None
#         return video_path, english_words_to_learn, None

#     # return video_path, english_words_to_learn, None

def add_first_word_card_to_video(video_path, english_words_to_learn, output_folder, duration=3):
    if not english_words_to_learn:
        print("No words to learn provided.")
        return video_path, english_words_to_learn, None  # No word card to add if the list is empty.

    remaining_words = english_words_to_learn[:]  # Make a copy of the word list to modify it without affecting the original.
    used_word = None  # Initialize to track which word was successfully used to create a word card.
    fallback_word = "Lazying Art"  # Define a fallback word in case all words in the list fail.

    # Try each word in the list until one succeeds in creating a word card and adding it to the video.
    for first_word_info in remaining_words:
        try:
            # Attempt to get a word card image for the current word.
            word_card_image_path = get_word_card_image(first_word_info["word"], output_folder)
            # Create a video adder object and add the word card to the video.
            video_add_words_card = VideoAddWordsCard(video_path, word_card_image_path, duration=duration)
            # Process the video to add the word card, capturing the new video path.
            video_with_first_word_card_path, _ = video_add_words_card.add_image_to_video()
            used_word = first_word_info  # Update the used word on success.
            break  # Exit loop on successful video processing.
        except Exception as e:
            traceback.print_exc()
            print("Failed to request word or add to video: ", first_word_info["word"], "Error:", str(e))
            continue  # Skip to the next word on failure.

    # If a word card was successfully added, update the remaining words list by removing the used word.
    if used_word:
        remaining_words.remove(used_word)
        return video_with_first_word_card_path, remaining_words, word_card_image_path

    # If no word from the list leads to a successful word card, try the fallback word.
    try:
        word_card_image_path = get_word_card_image(fallback_word, output_folder)
        video_add_words_card = VideoAddWordsCard(video_path, word_card_image_path, duration=duration)
        video_with_first_word_card_path, _ = video_add_words_card.add_image_to_video()
        # On fallback success, return the path of the modified video, the unchanged word list, and the fallback image path.
        return video_with_first_word_card_path, remaining_words, word_card_image_path
    except Exception as e:
        traceback.print_exc()
        print("Failed to use fallback word 'lazying art':", str(e))
        # If even the fallback fails, return the original video path, the unchanged word list, and no image path.
        return video_path, remaining_words, None





# def highlight_words(video_path, english_words_to_learn, output_path, delay=3):
#     # Get the length of the video
#     video_length = get_video_length(video_path)
#     video_width, video_height = get_video_resolution(video_path)

#     # is_video_landscape = video_width > video_height

#     # rescale = 4  # Scaling factor

#     # # Adjust base font sizes
#     # base_font_size = 24 * rescale if is_video_landscape else 20 * rescale  # Larger for landscape
#     # furigana_font_size = 20 * rescale if is_video_landscape else 18 * rescale
#     # arabic_font_size = 26 * rescale if is_video_landscape else 22 * rescale  # Specific for Arabic



#     # Sort english_words_to_learn by start time
#     english_words_to_learn.sort(key=lambda x: get_time_range(x['timestamp_range'])[0])

#     # Initialize variables
#     temp_output_path = output_path + ".temp.mp4"
#     final_output_path = output_path
#     current_input_path = video_path
#     successful = False
#     last_end_time = delay  # Initialize last end time with the optional delay parameter

#     font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

#     # Process each word
#     for i, word_info in enumerate(english_words_to_learn):
#         try:
#             # Get time range
#             start_seconds, end_seconds = get_time_range(word_info['timestamp_range'])

#             # Ignore words that start beyond the video length or before the last end time
#             if start_seconds >= video_length or start_seconds < last_end_time:
#                 continue

#             # Ensure end time is at least 1 second after the start time and does not exceed video length
#             end_seconds = min(max(end_seconds, start_seconds + 1), video_length)

#             # Update last end time for the next iteration
#             last_end_time = end_seconds

#             word_text = word_info['word']
#             font_size = find_font_size(word_text, font_path, video_width * 0.5, video_height * 0.5)

#             # drawtext_filter = (
#             #     f"drawtext=text='{word_text}':"
#             #     f"x=(w-text_w)/2:y=(h-text_h)/2:"
#             #     f"fontsize={font_size}:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:"
#             #     f"enable='between(t,{start_seconds},{end_seconds})'"
#             # )

#             drawtext_filter = (
#                 f"drawtext=text='{word_text}':"
#                 f"x=(w-text_w)/2:y=text_h/2:"
#                 # f"fontsize={font_size}:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:"
#                 f"fontsize={font_size}:fontcolor=white:box=1:boxcolor=crimson@0.5:boxborderw=5:"
#                 f"enable='between(t,{start_seconds},{end_seconds})'"
#             )

#             # command = (
#             #     f"ffmpeg -y -i \"{current_input_path}\" -vf \"{drawtext_filter}\" "
#             #     f"-c:a copy \"{temp_output_path}\""
#             # )
#             command = (
#                 f"ffmpeg -y -i \"{current_input_path}\" -vf \"{drawtext_filter}\" "
#                 f"-c:a copy -movflags +faststart \"{temp_output_path}\""  # Add here
#             )

#             subprocess.run(command, shell=True, check=True)

#             # Prepare for next iteration
#             if i < len(english_words_to_learn) - 1 or current_input_path != final_output_path:
#                 os.rename(temp_output_path, final_output_path)
#                 current_input_path = final_output_path
#             successful = True
#         except subprocess.CalledProcessError as e:
#             print(f"Error processing word '{word_text}': {e}")
#             continue

#     # Check if any word was successfully processed
#     if not successful:
#         # Check if output_path already exists, remove it before creating a new link
#         if os.path.exists(output_path):
#             os.remove(output_path)
#         try:
#             os.link(video_path, output_path)  # Attempt to create a hard link again
#         except Exception as e:
#             print(f"Error linking files: {e}")
#             traceback.print_exc()  # Print detailed traceback
#             # If os.link fails, consider using shutil.copy as a fallback
#             # import shutil
#             # shutil.copy(video_path, output_path)

#     return None  # Since word_card_image_path logic was removed


def highlight_words(video_path, english_words_to_learn, output_path, delay=3):
    # Get the length of the video
    video_length = get_video_length(video_path)
    video_width, video_height = get_video_resolution(video_path)

    # Sort english_words_to_learn by start time
    english_words_to_learn.sort(key=lambda x: get_time_range(x['timestamp_range'])[0])

    # Initialize variables
    temp_output_path = output_path + ".temp.mp4"
    final_output_path = output_path
    current_input_path = video_path
    successful = False
    last_end_time = delay  # Initialize last end time with the optional delay parameter

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    # Process each word
    for i, word_info in enumerate(english_words_to_learn):
        try:
            # Get time range - now handles both old and new format
            start_seconds, end_seconds = get_time_range(word_info['timestamp_range'])

            # Ignore words that start beyond the video length or before the last end time
            if start_seconds >= video_length or start_seconds < last_end_time:
                continue

            # Ensure end time is at least 1 second after the start time and does not exceed video length
            end_seconds = min(max(end_seconds, start_seconds + 1), video_length)

            # Update last end time for the next iteration
            last_end_time = end_seconds

            word_text = word_info['word']
            font_size = find_font_size(word_text, font_path, video_width * 0.5, video_height * 0.5)

            drawtext_filter = (
                f"drawtext=text='{word_text}':"
                f"x=(w-text_w)/2:y=text_h/2:"
                f"fontsize={font_size}:fontcolor=white:box=1:boxcolor=crimson@0.5:boxborderw=5:"
                f"enable='between(t,{start_seconds},{end_seconds})'"
            )

            command = (
                f"ffmpeg -y -i \"{current_input_path}\" -vf \"{drawtext_filter}\" "
                f"-c:a copy -movflags +faststart \"{temp_output_path}\""
            )

            subprocess.run(command, shell=True, check=True)

            # Prepare for next iteration
            if i < len(english_words_to_learn) - 1 or current_input_path != final_output_path:
                os.rename(temp_output_path, final_output_path)
                current_input_path = final_output_path
            successful = True
        except subprocess.CalledProcessError as e:
            print(f"Error processing word '{word_text}': {e}")
            continue

    # Check if any word was successfully processed
    if not successful:
        # Check if output_path already exists, remove it before creating a new link
        if os.path.exists(output_path):
            os.remove(output_path)
        try:
            os.link(video_path, output_path)  # Attempt to create a hard link again
        except Exception as e:
            print(f"Error linking files: {e}")
            traceback.print_exc()  # Print detailed traceback

    return None  # Since word_card_image_path logic was removed



def highlight_words_dummy(video_path, english_words_to_learn, output_path, delay=3):
    """
    Dummy implementation of highlight_words that simply copies the input video to output path.
    This function skips the word highlighting process to avoid system freezes.
    
    Args:
        video_path (str): Path to the input video file
        english_words_to_learn (list): List of words to highlight (ignored in this implementation)
        output_path (str): Path where the output video will be saved
        delay (int, optional): Delay parameter (ignored in this implementation). Defaults to 3.
    
    Returns:
        None
    """
    print("Using dummy highlight_words function - skipping word highlighting")
    
    # Simply copy the input video to the output path to maintain workflow
    try:
        # Check if output_path already exists, remove it before creating a new link
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Try to create a hard link (fast, doesn't duplicate file data)
        try:
            os.link(video_path, output_path)
            print(f"Created hard link from {video_path} to {output_path}")
        except OSError:
            # If hard link fails (e.g., different filesystems), copy the file
            import shutil
            shutil.copy2(video_path, output_path)
            print(f"Copied {video_path} to {output_path}")
    
    except Exception as e:
        print(f"Error in dummy highlight_words function: {e}")
        traceback.print_exc()
    
    return None

def select_font_path(detected_language):
    """
    Selects the font path based on the detected language's ISO 639-1 code.
    Adjust paths as necessary based on the actual installation paths of the fonts.
    """
    noto_base = "/usr/share/fonts/truetype/noto/"
    language_font_map = {
        'zh': "NotoSansCJK-Regular.ttc",  # Chinese; adjust for Simplified/Traditional as needed
        'ja': "NotoSansCJK-Regular.ttc",  # Japanese
        'ko': "NotoSansCJK-Regular.ttc",  # Korean
        'ar': "NotoSansArabic-Regular.ttf",  # Arabic
        'hi': "NotoSansDevanagari-Regular.ttf",  # Hindi
        'es': "NotoSans-Regular.ttf",  # Spanish
        'en': "NotoSans-Regular.ttf",  # English
        'pt': "NotoSans-Regular.ttf",  # Portuguese
        'ru': "NotoSansCyrillic-Regular.ttf",  # Russian
        'bn': "NotoSansBengali-Regular.ttf",  # Bengali
        'fr': "NotoSans-Regular.ttf",  # French
        'ms': "NotoSans-Regular.ttf",  # Malay
        'de': "NotoSans-Regular.ttf",  # German
        'it': "NotoSans-Regular.ttf",  # Italian
        'tr': "NotoSans-Regular.ttf",  # Turkish
        'fa': "NotoSansArabic-Regular.ttf",  # Persian (Farsi), using Arabic script
        'pl': "NotoSans-Regular.ttf",  # Polish
        'uk': "NotoSansCyrillic-Regular.ttf",  # Ukrainian
        'ro': "NotoSans-Regular.ttf",  # Romanian
        'nl': "NotoSans-Regular.ttf",  # Dutch
        'el': "NotoSansGreek-Regular.ttf",  # Greek
        'sv': "NotoSans-Regular.ttf",  # Swedish
        'da': "NotoSans-Regular.ttf",  # Danish
        'he': "NotoSansHebrew-Regular.ttf",  # Hebrew
        'th': "NotoSansThai-Regular.ttf",  # Thai
        'id': "NotoSans-Regular.ttf",  # Indonesian
        # Add more mappings as needed
    }

    # Default font for languages not explicitly mapped above
    default_font = "NotoSans-Regular.ttf"

    # Select font based on detected language, defaulting to NotoSans-Regular if not mapped
    font_name = language_font_map.get(detected_language, default_font)
    font_path = os.path.join(noto_base, font_name)

    return font_path


# def highlight_words(video_path, english_words_to_learn, output_path, delay=3):
#     # Assuming get_video_length, get_video_resolution, get_time_range, find_font_size are defined elsewhere
#     video_length = get_video_length(video_path)
#     video_width, video_height = get_video_resolution(video_path)

#     english_words_to_learn.sort(key=lambda x: get_time_range(x['timestamp_range'])[0])

#     temp_output_path = output_path + ".temp.mp4"
#     final_output_path = output_path
#     current_input_path = video_path
#     successful = False
#     last_end_time = delay

#     # Initialize the language detector
#     detector = LanguageDetectorBuilder.from_all_languages().build()

#     for i, word_info in enumerate(english_words_to_learn):
#         try:
#             start_seconds, end_seconds = get_time_range(word_info['timestamp_range'])
#             if start_seconds >= video_length or start_seconds < last_end_time:
#                 continue
#             end_seconds = min(max(end_seconds, start_seconds + 1), video_length)
#             last_end_time = end_seconds

#             word_text = word_info['word']
#             detected_language = detect_language_with_lingua(word_text, detector)

#             # Select font based on detected language
#             font_path = select_font_path(detected_language)

#             font_size = find_font_size(word_text, font_path, video_width * 0.8, video_height * 0.8)
#             drawtext_filter = (
#                 f"drawtext=text='{word_text}':"
#                 f"x=(w-text_w)/2:y=(h-text_h)/2:"
#                 f"fontsize={font_size}:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:"
#                 f"fontfile='{font_path}':"
#                 f"enable='between(t,{start_seconds},{end_seconds})'"
#             )
#             command = (
#                 f"ffmpeg -y -i \"{current_input_path}\" -vf \"{drawtext_filter}\" "
#                 f"-c:a copy \"{temp_output_path}\""
#             )
#             subprocess.run(command, shell=True, check=True)

#             if i < len(english_words_to_learn) - 1 or current_input_path != final_output_path:
#                 os.rename(temp_output_path, final_output_path)
#                 current_input_path = final_output_path
#             successful = True
#         except subprocess.CalledProcessError as e:
#             print(f"Error processing word '{word_text}': {e}")
#             continue

#     if not successful:
#         if os.path.exists(output_path):
#             os.remove(output_path)
#         try:
#             os.link(video_path, output_path)
#         except Exception as e:
#             print(f"Error linking files: {e}")
#             traceback.print_exc()




# def highlight_words(video_path, english_words_to_learn, output_path):
#     # Get the length of the video
#     video_length = get_video_length(video_path)
#     video_width, video_height = get_video_resolution(video_path)

#     # Sort english_words_to_learn by start time
#     first_word_info = english_words_to_learn[0]
#     english_words_to_learn = english_words_to_learn[1:]
#     english_words_to_learn.sort(key=lambda x: get_time_range(x['timestamp_range'])[0])

#     # Initialize variables
#     temp_output_path = output_path + ".temp.mp4"
#     final_output_path = output_path
#     current_input_path = video_path
#     successful = False
#     last_end_time = 3  # Initialize last end time

#     word_card_image_path = None
#     # Fetch the image for the first word and add to video
#     if english_words_to_learn:
        
#         first_word = first_word_info["word"]  # Get the first word from the first dictionary
#         output_folder = os.path.dirname(video_path)
#         word_card_image_path = get_word_card_image(first_word, output_folder)  # Function to fetch and save the word card image
#         if word_card_image_path:
#             video_add_words_card = VideoAddWordsCard(video_path, word_card_image_path)
#             video_with_first_word_card_path, _ = video_add_words_card.add_image_to_video()
#             current_input_path = video_with_first_word_card_path
#         else:
#             print(f"Failed to obtain word card for '{first_word}'. Proceeding without adding word card.")
#             current_input_path = video_path
#     else:
#         current_input_path = video_path


#     # font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"  # Update this to the actual path of your font file
#     font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

#     # Process each word
#     for i, word_info in enumerate(english_words_to_learn):
#         try:
#             # Get time range
#             start_seconds, end_seconds = get_time_range(word_info['timestamp_range'])

#             # Ignore words that start beyond the video length
#             if start_seconds >= video_length:
#                 break



#             # Update start time if it overlaps with the end time of the previous word
#             start_seconds = max(start_seconds, last_end_time)

#             # Ensure end time is at least 1 second after the start time and does not exceed video length
#             end_seconds = min(max(end_seconds, start_seconds + 1), video_length)



#             # Update last end time for the next iteration
#             last_end_time = end_seconds


#             word_text = word_info['word']

#             # Find the optimal font size using the find_font_size method for the video resolution
#             font_size = find_font_size(word_text, font_path, video_width*0.8, video_height*0.8)

#             # Set box width dynamically based on the actual video width and the length of the text
#             max_box_width = int(video_width * 0.8)  # The box can occupy up to 80% of the video width
#             box_width = min(max_box_width, font_size * len(word_text) / 2)
#             box_width += font_size / 2


#             drawtext_filter = (
#                 f"drawtext=text='{word_text}':"
#                 f"x=(w-text_w)/2: "
#                 f"y=(h-text_h)/2: "
#                 f"fontsize={font_size}: "
#                 f"fontcolor=white@1.0: "
#                 f"box=1: "
#                 f"boxcolor=black@0.5: "
#                 f"boxborderw=5: "
#                 # f"boxw={box_width}: "
#                 f"enable='between(t,{start_seconds},{end_seconds})'"
#             )

#             # Construct ffmpeg command
#             command = (
#                 f"ffmpeg -y -i \"{current_input_path}\" -vf \"{drawtext_filter}\" "
#                 f"-c:a copy \"{temp_output_path}\""
#             )

#             # Execute ffmpeg command
#             subprocess.run(command, shell=True, check=True)

#             # If successful, prepare for next iteration
#             if i < len(english_words_to_learn) - 1:
#                 os.rename(temp_output_path, final_output_path)
#                 current_input_path = final_output_path
#             successful = True
#         except subprocess.CalledProcessError as e:
#             # Log error and skip to the next word
#             print(f"Error processing word '{word_info['word']}': {e}")
#             continue

#     # Finalize output
#     if not successful:
#         # If no text was successfully drawn, copy the original video to the output
#         os.link(video_path, final_output_path)
#     else:
#         if current_input_path != final_output_path:
#             os.rename(current_input_path, final_output_path)

#     return word_card_image_path




def parse_subtitles(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    subtitles = []
    i = 0
    while i < len(lines):
        if '-->' in lines[i]:
            start, end = lines[i].strip().split(' --> ')
            text = lines[i + 1].strip()
            subtitles.append({'start': start, 'end': end, 'text': text})
            i += 2  # Skip the next line as it's part of the current subtitle
        i += 1
    return subtitles




def merge_subtitles(subtitles_en, subtitles_zh, output_path):
    merged_subtitles = []
    used_zh_subs = set()  # Keep track of used Chinese subtitles to avoid duplicates

    # Iterate through English subtitles
    for sub_en in subtitles_en:
        # Find overlapping Chinese subtitles
        overlaps = [sub_zh for sub_zh in subtitles_zh if sub_zh['start'] <= sub_en['end'] and sub_zh['end'] >= sub_en['start']]
        
        # Combine overlapping subtitles or keep English subtitle as is
        if overlaps:
            combined_text = f"{overlaps[0]['text']}\n{sub_en['text']}"  # Assuming maximum one overlap
            used_zh_subs.add(overlaps[0]['start'])  # Mark this Chinese subtitle as used
        else:
            combined_text = sub_en['text']

        merged_subtitles.append({'start': sub_en['start'], 'end': sub_en['end'], 'text': combined_text})

    # Add remaining Chinese subtitles that didn't overlap with any English subtitle
    for sub_zh in subtitles_zh:
        if sub_zh['start'] not in used_zh_subs:
            merged_subtitles.append({'start': sub_zh['start'], 'end': sub_zh['end'], 'text': sub_zh['text']})

    # Sort by start time and re-index
    merged_subtitles.sort(key=lambda sub: sub['start'])
    with open(output_path, 'w', encoding='utf-8') as file:
        for index, sub in enumerate(merged_subtitles, 1):
            file.write(f"{index}\n{sub['start']} --> {sub['end']}\n{sub['text']}\n\n")

    print("Subtitles merged and re-indexed successfully.")



# def burn_subtitles(video_path, srt_path, output_path):
#         command = f"ffmpeg -y -i \"{video_path}\" -vf \"subtitles={srt_path}\" \"{output_path}\""
#         subprocess.run(command, shell=True, check=True)

def wrap_text(text, width, is_cjk):
    if is_cjk:
        # Use cjkwrap for CJK text
        return cjkwrap.wrap(text, width)
    else:
        # Use cjkwrap for non-CJK text as well, as it should handle both appropriately
        return cjkwrap.wrap(text, width)

# def get_video_dimensions(video_file):
#     video = VideoFileClip(video_file)
#     return video.size  # (width, height)

def get_video_dimensions(video_file):
        video = cv2.VideoCapture(video_file)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video.release()
        print("width: ", width, "height: ", height)
        return width, height

# def wrap_subtitles(video_file, input_subtitle_file, output_subtitle_file, max_width):
#     video_width, video_height = get_video_dimensions(video_file)
#     is_landscape = video_width > video_height

#     # if portrait
#     if not is_landscape:
#         max_width = int(max_width * 0.4)

#     with open(input_subtitle_file, 'r', encoding='utf-8') as f:
#         lines = f.readlines()

#     with open(output_subtitle_file, 'w', encoding='utf-8') as f:
#         for line in lines:
#             if '-->' in line:
#                 f.write(line)
#             else:
#                 is_cjk = any('\u4e00' <= char <= '\u9fff' for char in line)
#                 wrapped_lines = wrap_text(line, max_width, is_cjk=is_cjk)
#                 for wrapped_line in wrapped_lines:
#                     f.write(wrapped_line + '\n')

def wrap_subtitles(video_file, input_subtitle_file, output_subtitle_file, max_width):
    video_width, video_height = get_video_dimensions(video_file)
    is_landscape = video_width > video_height

    # Adjust max_width for portrait videos
    if not is_landscape:
        max_width = int(max_width * 0.5)

    with open(input_subtitle_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    subtitle_block = ""
    index = 1  # Initialize subtitle index
    with open(output_subtitle_file, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.strip().isdigit() and subtitle_block:  # Check if the line is a subtitle ID and a block exists
                # Write out the existing block and reset for the next
                f.write(f"{subtitle_block.strip()}\n\n")  # Ensure it's stripped and followed by two newlines
                subtitle_block = f"{index}\n"  # Start a new block with the next index
                index += 1  # Increment the subtitle index for the next block
            elif '-->' in line:
                subtitle_block += f"{line}"  # Add the time range line to the current block
            else:
                is_cjk = any('\u4e00' <= char <= '\u9fff' for char in line)
                wrapped_lines = wrap_text(line.strip(), max_width, is_cjk=is_cjk)
                for wrapped_line in wrapped_lines:
                    subtitle_block += f"{wrapped_line}\n"  # Add wrapped lines to the current block

        # Write out the last subtitle block, if it exists
        if subtitle_block:
            f.write(f"{subtitle_block.strip()}\n")  # Ensure the last block is stripped and followed by a newline


# def burn_subtitles(video_path, sub_path, output_path):
#     # # Determine the name for the processed subtitles
#     # wrapped_sub_path = sub_path.rsplit('.', 1)[0] + '_wrapped.srt'
#     wrapped_sub_path = sub_path
    
#     # # Adjust 'max_width' as needed
#     # max_width = 50  # You may want to dynamically set this based on the video dimensions
#     # wrap_subtitles(video_path, srt_path, wrapped_sub_path, max_width)
    
#     # Construct the FFmpeg command to burn the processed subtitles
#     # command = f"ffmpeg -y -i \"{video_path}\" -vf \"subtitles={wrapped_sub_path}\" \"{output_path}\""
#     command = f"ffmpeg -y -i \"{video_path}\" -vf \"ass={wrapped_sub_path}\" -c:a copy \"{output_path}\""
#     subprocess.run(command, shell=True, check=True)

def get_audio_bitrate(video_path):
    # Use ffprobe to get the audio bitrate of the original video
    command = f"ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 \"{video_path}\""
    result = subprocess.run(command, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=False)

    # Extract the bitrate from ffprobe output
    bitrate = result.stdout.strip()
    
    # Return the bitrate in kbps if found, else default to 192k
    return f"{int(bitrate)//1000}k" if bitrate.isdigit() else "192k"

# def burn_subtitles(video_path, sub_path, output_path):
#     # Determine the subtitle file extension
#     sub_extension = os.path.splitext(sub_path)[1].lower()
    
#     # Determine the appropriate subtitle filter based on the extension
#     if sub_extension in [".ass", ".ssa"]:
#         subtitle_filter = f"ass={sub_path}"
#     elif sub_extension == ".srt":
#         subtitle_filter = f"subtitles={sub_path}"
#     else:
#         raise ValueError(f"Unsupported subtitle format: {sub_extension}")
    
#     # Extract the original audio bitrate for use in conversion
#     audio_bitrate = get_audio_bitrate(video_path)
    
#     # Construct the FFmpeg command
#     command = f'ffmpeg -y -i "{video_path}" -vf "{subtitle_filter}" -c:a aac -b:a {audio_bitrate} "{output_path}"'
    
#     try:
#         subprocess.run(command, shell=True, check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Error executing FFmpeg command: {e}")


def burn_subtitles(video_path, sub_path, output_path):
    # Determine the subtitle file extension
    sub_extension = os.path.splitext(sub_path)[1].lower()
    
    # Choose the appropriate subtitle filter based on the extension.
    # ASS/SSA files use the ASS filter; SRT files use the subtitles filter.
    if sub_extension in [".ass", ".ssa"]:
        subtitle_filter = f"ass={sub_path}"
    elif sub_extension == ".srt":
        subtitle_filter = f"subtitles={sub_path}"
    else:
        raise ValueError(f"Unsupported subtitle format: {sub_extension}")
    
    # Extract the original audio bitrate from the input video.
    audio_bitrate = get_audio_bitrate(video_path)
    
    # Construct the FFmpeg command:
    # - The -y flag forces overwriting output if it exists.
    # - -vf applies the subtitle filter.
    # - -c:a aac and -b:a specify that AAC audio encoding with the extracted bitrate will be used.
    command = (
        f'ffmpeg -y -i "{video_path}" '
        f'-vf "{subtitle_filter}" '
        f'-c:a aac -b:a {audio_bitrate} -movflags +faststart '
        f'"{output_path}"'
    )
    
    print("Executing command:", command)
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing FFmpeg command: {e}")


def mux_audio(rendered_video_path: str, source_video_path: str, output_path: str):
    audio_bitrate = get_audio_bitrate(source_video_path)
    command = (
        f'ffmpeg -y -i "{rendered_video_path}" -i "{source_video_path}" '
        f'-c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium '
        f'-c:a aac -b:a {audio_bitrate} '
        f'-map 0:v:0 -map 1:a:0? -shortest '
        f'"{output_path}"'
    )
    print("Executing command:", command)
    subprocess.run(command, shell=True, check=True)


# def burn_subtitles(video_path, sub_path, output_path):
#     """
#     Burns subtitles into a video using MoviePy and FFmpeg.
#     This implementation uses a hybrid approach for maximum reliability.
#     """
#     from moviepy.editor import VideoFileClip
#     from moviepy.config import change_settings
#     import tempfile
#     import os
#     import subprocess
#     import shutil
#     import traceback
    
#     # Determine subtitle filter
#     sub_extension = os.path.splitext(sub_path)[1].lower()
#     if sub_extension in [".ass", ".ssa"]:
#         subtitle_filter = f"ass={sub_path}"
#     elif sub_extension == ".srt":
#         subtitle_filter = f"subtitles={sub_path}"
#     else:
#         raise ValueError(f"Unsupported subtitle format: {sub_extension}")
    
#     # Create temporary directory for processing
#     with tempfile.TemporaryDirectory() as temp_dir:
#         # Set MoviePy's temp directory to our controlled location
#         original_temp = change_settings({"TEMP_DIR": temp_dir})
        
#         try:
#             print(f"Processing video: {video_path}")
#             print(f"Using subtitle file: {sub_path}")
            
#             # Step 1: Analyze the video with MoviePy to get properties
#             video = VideoFileClip(video_path)
#             fps = video.fps if video.fps else 24
#             duration = video.duration
#             video.close()
            
#             # Step 2: Extract audio bitrate using ffprobe
#             audio_bitrate = "192k"  # Default
#             try:
#                 cmd = f"ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 \"{video_path}\""
#                 result = subprocess.run(cmd, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=False)
#                 bitrate = result.stdout.strip()
#                 if bitrate and bitrate.isdigit():
#                     audio_bitrate = f"{int(bitrate)//1000}k"
#             except Exception as e:
#                 print(f"Error getting audio bitrate: {e}")
            
#             # Step 3: Create intermediate file with subtitles
#             temp_subs = os.path.join(temp_dir, "with_subs.mp4")
            
#             # Use FFmpeg for subtitle burning (which MoviePy doesn't directly support)
#             subs_cmd = (
#                 f'ffmpeg -y -i "{video_path}" '
#                 f'-vf "{subtitle_filter}" '
#                 f'-c:v libx264 -preset medium -crf 23 '
#                 f'-c:a aac -b:a {audio_bitrate} '
#                 f'"{temp_subs}"'
#             )
            
#             print("Adding subtitles...")
#             subprocess.run(subs_cmd, shell=True, check=True)
            
#             # Step 4: Use MoviePy to process the final output with proper metadata
#             print("Finalizing video...")
#             final_video = VideoFileClip(temp_subs)
            
#             # Create the final output with movflags faststart
#             final_video.write_videofile(
#                 output_path,
#                 codec="libx264",
#                 audio_codec="aac",
#                 bitrate="0",  # Use CRF instead of bitrate control
#                 ffmpeg_params=[
#                     "-crf", "23",
#                     "-movflags", "+faststart",
#                     "-preset", "medium"
#                 ],
#                 fps=fps
#             )
            
#             final_video.close()
#             print(f"Successfully created {output_path}")
            
#         except Exception as e:
#             print(f"Error in MoviePy processing: {e}")
#             traceback.print_exc()
            
#             # Fallback to direct FFmpeg with a reliable two-step process
#             try:
#                 print("Using FFmpeg fallback method...")
                
#                 # Step 1: Create with subtitles
#                 temp_fallback = os.path.join(temp_dir, "fallback.mp4")
                
#                 step1_cmd = (
#                     f'ffmpeg -y -i "{video_path}" '
#                     f'-vf "{subtitle_filter}" '
#                     f'-c:v libx264 -preset fast -crf 23 '
#                     f'-c:a aac -b:a {audio_bitrate} '
#                     f'"{temp_fallback}"'
#                 )
                
#                 subprocess.run(step1_cmd, shell=True, check=True)
                
#                 # Step 2: Remux with faststart
#                 step2_cmd = (
#                     f'ffmpeg -y -i "{temp_fallback}" '
#                     f'-c copy -movflags +faststart '
#                     f'"{output_path}"'
#                 )
                
#                 subprocess.run(step2_cmd, shell=True, check=True)
#                 print("Fallback method successful")
                
#             except Exception as e2:
#                 print(f"All methods failed: {e2}")
#                 # Last resort - copy the original file
#                 print("Copying original video as last resort (without subtitles)")
#                 shutil.copy2(video_path, output_path)
        
#         finally:
#             # Restore original MoviePy settings
#             change_settings({"TEMP_DIR": original_temp})

# def validate_timestamp(timestamp):
#     try:
#         # Split the timestamp and check if it has the correct format
#         h, m, s = timestamp.split(':')
#         s, ms = s.split('.')
#         # Convert to integers to check if they are within the correct range
#         h, m, s, ms = int(h), int(m), int(s), int(ms)
#         seconds = h*3600 + m * 60 + s + ms/1000
#         # Check if hours, minutes, seconds, and milliseconds are in the correct range
#         if h >= 0 and m >= 0 and m < 60 and s >= 0 and s < 60 and ms >= 0 and ms < 1000:
#             return timestamp, seconds  # The timestamp is valid
#     except ValueError:
#         # Catch ValueError if the timestamp is not in the correct format
#         print("Format unrecognized for timestamp of cover: ", timestamp)
#         pass
#     # Return the default value if the timestamp is not valid
#     return '00:00:01,000', seconds

def validate_timestamp(timestamp):
    """
    Updated to handle new timestamp format and validate properly
    """
    try:
        # Handle both comma and dot as decimal separators
        if ',' in timestamp:
            timestamp = timestamp.replace(',', '.')
        
        # Split the timestamp and check if it has the correct format
        h, m, s = timestamp.split(':')
        s, ms = s.split('.')
        # Convert to integers to check if they are within the correct range
        h, m, s, ms = int(h), int(m), int(s), int(ms)
        seconds = h*3600 + m * 60 + s + ms/1000
        # Check if hours, minutes, seconds, and milliseconds are in the correct range
        if h >= 0 and m >= 0 and m < 60 and s >= 0 and s < 60 and ms >= 0 and ms < 1000:
            return timestamp.replace('.', ','), seconds  # Return in original format with comma
    except ValueError:
        # Catch ValueError if the timestamp is not in the correct format
        print("Format unrecognized for timestamp of cover: ", timestamp)
        pass
    # Return the default value if the timestamp is not valid
    return '00:00:01,000', 1.0


# Function to copy a folder to a new location with a new name
def copy_folder(output_folder, new_folder_name):
    # Copy the folder to the new location with the new name
    shutil.copytree(output_folder, new_folder_name)
    print(f"Folder '{output_folder}' was copied to '{new_folder_name}'")

def media_url_for_path(file_path: str | None) -> str | None:
    if not file_path:
        return None
    try:
        upload_root = Path(UPLOAD_FOLDER).resolve()
        resolved = Path(file_path).resolve()
        relative = resolved.relative_to(upload_root)
    except Exception:
        return None
    return f"/media/{quote(relative.as_posix())}"


def _load_json_payload(path: str | None) -> dict | None:
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return None


def _get_video_row(video_id: int) -> tuple | None:
    ldb.ensure_schema()
    with ldb.get_cursor() as cur:
        cur.execute("SELECT id, file_path, title, created_at FROM videos WHERE id = %s", (video_id,))
        return cur.fetchone()


def _get_latest_metadata_payload(video_id: int, lang: str) -> tuple[dict | None, str | None]:
    row = ldb.get_latest_video_metadata(video_id, lang)
    if not row:
        return None, None
    _, _, status, output_json_path, _, _ = row
    if status != "completed":
        return None, None
    payload = _load_json_payload(output_json_path)
    return payload, output_json_path


def _get_publish_dir(video_path: str) -> str:
    base_dir = os.path.dirname(video_path)
    publish_dir = os.path.join(base_dir, "publish")
    os.makedirs(publish_dir, exist_ok=True)
    return publish_dir


def _pick_publish_video_path(video_id: int, fallback_path: str) -> str:
    latest_burn = ldb.get_latest_subtitle_burn(video_id)
    if latest_burn:
        _, status, output_path, _, _, _, _ = latest_burn
        if status == "completed" and output_path and os.path.exists(output_path):
            return output_path
    return fallback_path


def _simplify_metadata_payload(metadata: dict) -> dict:
    simplified = dict(metadata or {})
    for key in ("title", "brief_description", "middle_description", "long_description"):
        if isinstance(simplified.get(key), str):
            simplified[key] = convert_traditional_to_simplified(simplified[key])
    tags = simplified.get("tags")
    if isinstance(tags, list):
        simplified["tags"] = [
            convert_traditional_to_simplified(tag) if isinstance(tag, str) else tag for tag in tags
        ]
    return simplified


class CorsMixin:
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS,PUT")
        self.set_header("Access-Control-Allow-Headers", "content-type")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()


class MediaHandler(tornado.web.StaticFileHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "content-type, range")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()


class FileUploaderHandler(CorsMixin, tornado.web.RequestHandler):
    def initialize(self, upload_folder):
        self.upload_folder = upload_folder

    @gen.coroutine
    def post(self):
        # Extract video file from the request
        video_files = self.request.files.get('video') or self.request.files.get('file')
        if not video_files:
            self.set_status(400)
            return self.write({"error": "video file missing"})
        video_file = video_files[0]
        original_fname = video_file['filename']
        requested_name = self.get_argument('filename', default=None) or original_fname
        safe_name = os.path.basename(requested_name) or original_fname
        print("Filename: ", safe_name)

        # Determine the basename (without extension) and create a subfolder
        base_name, _ = os.path.splitext(safe_name)
        output_folder = os.path.join(self.upload_folder, base_name)

        # Check if the folder already exists
        if os.path.exists(output_folder) and os.path.isdir(output_folder):
            # Get the folder creation time
            creation_time = os.path.getctime(output_folder)
            # Convert creation time to a readable format
            creation_time_formatted = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d_%H-%M-%S')
            # Define the new folder name with creation datetime appended
            new_folder_name = f"{output_folder}_{creation_time_formatted}"
            # Rename the existing folder
            # os.rename(output_folder, new_folder_name)
            copy_folder(output_folder, new_folder_name)
            print(f"Existing folder renamed to: {new_folder_name}")

        os.makedirs(output_folder, exist_ok=True)

        # Define the full path for the incoming video
        input_file = os.path.join(output_folder, safe_name)

        # Write the incoming video to the file system
        with open(input_file, 'wb') as f:
            f.write(video_file['body'])

        # Save a row in the database for the uploaded video
        title = self.get_argument("title", default=None) or base_name
        source = _normalize_video_source(self.get_argument("source", default=None)) or "upload"
        try:
            ldb.ensure_schema()
            video_id = ldb.add_video(input_file, title, source)
        except Exception as e:
            self.set_status(500)
            return self.write({
                "error": "failed to save video in database",
                "details": str(e),
            })

        _enqueue_preview_proxy(video_id, input_file)

        # Respond with the path of the saved file
        self.write({
            'status': 'success',
            'message': f'File {safe_name} uploaded successfully.',
            'file_path': input_file,
            'media_url': media_url_for_path(input_file),
            'video_id': video_id,
        })


class LanguagesHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self):
        self.write({"languages": list_languages()})


class GrammarPaletteHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, lang):
        palette = load_grammar_palette(lang)
        if not palette:
            self.set_status(404)
            return self.write({"error": "palette not found"})
        self.write(palette)


class UISettingsHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, key):
        ldb.ensure_schema()
        if key not in {
            "translation_style",
            "translation_languages",
            "burn_layout",
            "video_prompt",
            "video_prompt_history",
            "video_spec_history",
            "video_prompt_text_history",
            "video_prompt_result_history",
            "video_idea_history",
        }:
            self.set_status(404)
            return self.write({"error": "unknown settings key"})
        saved = ldb.get_ui_preference(key)
        if key == "translation_style":
            if not saved:
                return self.write({"key": key, "value": DEFAULT_TRANSLATION_STYLE})
            return self.write({"key": key, "value": _sanitize_translation_style(saved)})
        if key == "burn_layout":
            if not saved:
                return self.write({"key": key, "value": DEFAULT_BURN_LAYOUT})
            return self.write({"key": key, "value": _sanitize_burn_layout(saved)})
        if key == "video_prompt":
            if not saved:
                return self.write({"key": key, "value": DEFAULT_VIDEO_PROMPT_SPEC})
            return self.write({"key": key, "value": _sanitize_video_prompt_spec(saved)})
        if key == "video_prompt_history":
            if not saved:
                return self.write({"key": key, "value": DEFAULT_VIDEO_PROMPT_HISTORY})
            return self.write({"key": key, "value": _sanitize_video_prompt_history(saved)})
        if key in {"video_spec_history", "video_prompt_text_history", "video_prompt_result_history", "video_idea_history"}:
            return self.write({"key": key, "value": _sanitize_history_list(saved)})
        if not saved:
            return self.write({"key": key, "value": DEFAULT_TRANSLATION_LANGUAGES})
        return self.write({"key": key, "value": _sanitize_translation_languages(saved)})

    def post(self, key):
        ldb.ensure_schema()
        if key not in {
            "translation_style",
            "translation_languages",
            "burn_layout",
            "video_prompt",
            "video_prompt_history",
            "video_spec_history",
            "video_prompt_text_history",
            "video_prompt_result_history",
            "video_idea_history",
        }:
            self.set_status(404)
            return self.write({"error": "unknown settings key"})
        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}
        if key == "translation_style":
            cleaned = _sanitize_translation_style(data)
        elif key == "burn_layout":
            cleaned = _sanitize_burn_layout(data)
        elif key == "video_prompt":
            cleaned = _sanitize_video_prompt_spec(data)
        elif key == "video_prompt_history":
            cleaned = _sanitize_video_prompt_history(data)
        elif key in {"video_spec_history", "video_prompt_text_history", "video_prompt_result_history", "video_idea_history"}:
            cleaned = _sanitize_history_list(data)
        else:
            cleaned = _sanitize_translation_languages(data)
        ldb.set_ui_preference(key, cleaned)
        self.write({"key": key, "value": cleaned})


class VideosHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self):
        # Return recent videos from DB
        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute(
                "SELECT id, file_path, title, created_at, source FROM videos ORDER BY id DESC LIMIT 100"
            )
            rows = cur.fetchall()

        proxies_dir = os.path.join(UPLOAD_FOLDER, "proxy_previews")

        def preview_media_url(video_id: int, file_path: str) -> str | None:
            proxy_path = os.path.join(proxies_dir, f"video_{video_id}_proxy.mp4")
            if os.path.exists(proxy_path):
                return media_url_for_path(proxy_path)
            return media_url_for_path(file_path)

        videos = [
            {
                "id": r[0],
                "file_path": r[1],
                "media_url": media_url_for_path(r[1]),
                "preview_media_url": preview_media_url(r[0], r[1]),
                "title": r[2],
                "created_at": r[3].isoformat() if r[3] else None,
                "source": r[4],
            }
            for r in rows
        ]
        self.write({"videos": videos})

    def post(self):
        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid json"})
        file_path = data.get("file_path")
        title = data.get("title")
        source = _normalize_video_source(data.get("source"))
        if not file_path:
            self.set_status(400)
            return self.write({"error": "file_path required"})
        ldb.ensure_schema()
        vid = ldb.add_video(file_path, title, source)
        self.write({"id": vid})


class VideoDetailHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute(
                "SELECT id, file_path, title, created_at, source FROM videos WHERE id = %s",
                (video_id_i,),
            )
            row = cur.fetchone()
        if not row:
            self.set_status(404)
            return self.write({"error": "not found"})

        proxies_dir = os.path.join(UPLOAD_FOLDER, "proxy_previews")
        proxy_path = os.path.join(proxies_dir, f"video_{row[0]}_proxy.mp4")
        preview_url = media_url_for_path(proxy_path) if os.path.exists(proxy_path) else media_url_for_path(row[1])
        self.write({
            "id": row[0],
            "file_path": row[1],
            "media_url": media_url_for_path(row[1]),
            "preview_media_url": preview_url,
            "title": row[2],
            "created_at": row[3].isoformat() if row[3] else None,
            "source": row[4],
        })


class VideoProxyHandler(CorsMixin, tornado.web.RequestHandler):
    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})

        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute("SELECT file_path FROM videos WHERE id = %s", (video_id_i,))
            row = cur.fetchone()
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})

        input_path = row[0]
        if not input_path or not os.path.exists(input_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        proxies_dir = os.path.join(UPLOAD_FOLDER, "proxy_previews")
        os.makedirs(proxies_dir, exist_ok=True)
        output_path = os.path.join(proxies_dir, f"video_{video_id_i}_proxy.mp4")

        try:
            if os.path.exists(output_path) and os.path.getmtime(output_path) >= os.path.getmtime(input_path):
                return self.write({
                    "video_id": video_id_i,
                    "file_path": output_path,
                    "media_url": media_url_for_path(output_path),
                })
        except Exception:
            # If mtime checks fail, just regenerate.
            pass

        try:
            _create_preview_proxy(video_id_i, input_path)
        except subprocess.CalledProcessError as exc:
            err = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc)
            self.set_status(500)
            return self.write({"error": "proxy transcode failed", "details": err})
        except Exception as exc:
            self.set_status(500)
            return self.write({"error": "proxy transcode failed", "details": str(exc)})

        self.write({
            "video_id": video_id_i,
            "file_path": output_path,
            "media_url": media_url_for_path(output_path),
        })


class VideoTranscribeHandler(CorsMixin, tornado.web.RequestHandler):
    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute("SELECT file_path FROM videos WHERE id = %s", (video_id_i,))
            row = cur.fetchone()
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})
        file_path = row[0]
        if not file_path or not os.path.exists(file_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        input_file = preprocess_if_needed(file_path)
        base_name, extension = os.path.splitext(os.path.basename(input_file))
        output_folder = os.path.dirname(input_file)
        output_json_mixed = f"{output_folder}/{base_name}_mixed.json"
        output_srt_mixed = f"{output_folder}/{base_name}_mixed.srt"
        output_md_mixed = f"{output_folder}/{base_name}_mixed.md"

        if not has_audio_stream(input_file):
            message = "No audio stream detected in video."
            write_empty_transcription_files(output_json_mixed, output_srt_mixed, output_md_mixed, message)
            transcription_id = ldb.add_transcription(
                video_id_i,
                "mixed",
                "no_audio",
                output_json_mixed,
                output_srt_mixed,
                output_md_mixed,
                message,
            )
            primary_lang, language_summary = _summarize_transcription_languages(output_json_mixed)
            return self.write({
                "id": transcription_id,
                "video_id": video_id_i,
                "status": "no_audio",
                "error": message,
                "output_json_path": output_json_mixed,
                "output_srt_path": output_srt_mixed,
                "output_md_path": output_md_mixed,
                "json_url": media_url_for_path(output_json_mixed),
                "srt_url": media_url_for_path(output_srt_mixed),
                "md_url": media_url_for_path(output_md_mixed),
                "preview_text": build_transcription_preview(output_md_mixed, output_srt_mixed),
                "primary_language": primary_lang,
                "language_summary": language_summary,
            })

        # Clear stale outputs to avoid returning old data if transcription fails.
        for path in (output_json_mixed, output_srt_mixed, output_md_mixed):
            if os.path.exists(path):
                os.remove(path)

        try:
            autocut_processor = AutocutProcessor(input_file, output_folder, base_name, extension)
            autocut_processor.run_autocut("mixed", 1)

            if not os.path.exists(output_json_mixed) or not os.path.exists(output_srt_mixed):
                message = "Transcription completed but output files were not found."
                transcription_id = ldb.add_transcription(
                    video_id_i,
                    "mixed",
                    "failed",
                    None,
                    None,
                    None,
                    message,
                )
                self.set_status(500)
                return self.write({"error": message, "id": transcription_id})

            write_markdown_from_srt(output_srt_mixed, output_md_mixed)
            transcription_id = ldb.add_transcription(
                video_id_i,
                "mixed",
                "completed",
                output_json_mixed,
                output_srt_mixed,
                output_md_mixed,
                None,
            )
            primary_lang, language_summary = _summarize_transcription_languages(output_json_mixed)
            self.write({
                "id": transcription_id,
                "video_id": video_id_i,
                "status": "completed",
                "output_json_path": output_json_mixed,
                "output_srt_path": output_srt_mixed,
                "output_md_path": output_md_mixed,
                "json_url": media_url_for_path(output_json_mixed),
                "srt_url": media_url_for_path(output_srt_mixed),
                "md_url": media_url_for_path(output_md_mixed),
                "preview_text": build_transcription_preview(output_md_mixed, output_srt_mixed),
                "primary_language": primary_lang,
                "language_summary": language_summary,
            })
        except Exception as e:
            transcription_id = ldb.add_transcription(
                video_id_i,
                "mixed",
                "failed",
                None,
                None,
                None,
                str(e),
            )
            self.set_status(500)
            return self.write({"error": "transcription failed", "details": str(e), "id": transcription_id})


class VideoTranscriptionHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        ldb.ensure_schema()
        row = ldb.get_latest_transcription(video_id_i)
        if not row:
            self.set_status(404)
            return self.write({"error": "transcription not found"})
        (
            transcription_id,
            language_code,
            status,
            output_json_path,
            output_srt_path,
            output_md_path,
            error,
            created_at,
        ) = row
        primary_lang, language_summary = _summarize_transcription_languages(output_json_path)
        self.write({
            "id": transcription_id,
            "video_id": video_id_i,
            "language_code": language_code,
            "status": status,
            "output_json_path": output_json_path,
            "output_srt_path": output_srt_path,
            "output_md_path": output_md_path,
            "json_url": media_url_for_path(output_json_path),
            "srt_url": media_url_for_path(output_srt_path),
            "md_url": media_url_for_path(output_md_path),
            "error": error,
            "created_at": created_at.isoformat() if created_at else None,
            "preview_text": build_transcription_preview(output_md_path, output_srt_path),
            "primary_language": primary_lang,
            "language_summary": language_summary,
        })


class VideoCaptionHandler(CorsMixin, tornado.web.RequestHandler):
    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute("SELECT file_path FROM videos WHERE id = %s", (video_id_i,))
            row = cur.fetchone()
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})
        file_path = row[0]
        if not file_path or not os.path.exists(file_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        input_file = preprocess_if_needed(file_path)
        base_name, extension = os.path.splitext(os.path.basename(input_file))
        output_folder = os.path.dirname(input_file)
        output_json_caption = f"{output_folder}/{base_name}_caption.json"
        output_srt_caption = f"{output_folder}/{base_name}_caption.srt"
        output_md_caption = f"{output_folder}/{base_name}_caption.md"

        for path in (output_json_caption, output_srt_caption, output_md_caption):
            if os.path.exists(path):
                os.remove(path)

        num_frames_raw = self.get_argument("num_frames", default="7")
        try:
            num_frames = max(1, int(num_frames_raw))
        except Exception:
            num_frames = 7

        try:
            captioner = VideoCaptioner(input_file, output_folder, num_frames=num_frames)
            if not captioner.is_configured():
                message = "Captioner not configured. Set LAZYEDIT_CAPTION_PYTHON and script paths."
                caption_id = ldb.add_frame_caption(
                    video_id_i,
                    "not_configured",
                    None,
                    None,
                    None,
                    message,
                )
                return self.write({
                    "error": message,
                    "id": caption_id,
                    "status": "not_configured",
                    "preview_text": message,
                })
            captioner.run_captioning()

            if not os.path.exists(output_json_caption) or not os.path.exists(output_srt_caption):
                latest_srt, latest_json = find_latest_caption_outputs(output_folder, base_name)
                if latest_srt and not os.path.exists(output_srt_caption):
                    shutil.copy2(latest_srt, output_srt_caption)
                if latest_json and not os.path.exists(output_json_caption):
                    shutil.copy2(latest_json, output_json_caption)
                if not os.path.exists(output_json_caption) or not os.path.exists(output_srt_caption):
                    message = "Captioning completed but output files were not found."
                    caption_id = ldb.add_frame_caption(
                        video_id_i,
                        "failed",
                        None,
                        None,
                        None,
                        message,
                    )
                    self.set_status(500)
                    return self.write({"error": message, "id": caption_id})

            error_message = None
            if captioner.last_error:
                error_message = captioner.last_error
                with open(output_md_caption, "w", encoding="utf-8") as md_file:
                    md_file.write(f"Captioning failed: {error_message}\n")
                status = "failed"
            else:
                write_markdown_from_srt(
                    output_srt_caption,
                    output_md_caption,
                    empty_message="No captions generated for this video.",
                )
                status = "completed"
                if os.path.getsize(output_srt_caption) == 0:
                    status = "empty"
            caption_id = ldb.add_frame_caption(
                video_id_i,
                status,
                output_json_caption,
                output_srt_caption,
                output_md_caption,
                error_message,
            )
            frames_payload = build_caption_frame_payload(
                output_folder,
                base_name,
                output_json_caption,
                output_srt_caption,
            )
            self.write({
                "id": caption_id,
                "video_id": video_id_i,
                "status": status,
                "output_json_path": output_json_caption,
                "output_srt_path": output_srt_caption,
                "output_md_path": output_md_caption,
                "json_url": media_url_for_path(output_json_caption),
                "srt_url": media_url_for_path(output_srt_caption),
                "md_url": media_url_for_path(output_md_caption),
                "preview_text": build_transcription_preview(output_md_caption, output_srt_caption),
                "error": error_message,
                "method": captioner.last_method,
                "frames": frames_payload,
            })
        except Exception as e:
            caption_id = ldb.add_frame_caption(
                video_id_i,
                "failed",
                None,
                None,
                None,
                str(e),
            )
            self.set_status(500)
            return self.write({"error": "captioning failed", "details": str(e), "id": caption_id})

    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        ldb.ensure_schema()
        row = ldb.get_latest_frame_caption(video_id_i)
        if not row:
            self.set_status(404)
            return self.write({"error": "caption not found"})
        (
            caption_id,
            status,
            output_json_path,
            output_srt_path,
            output_md_path,
            error,
            created_at,
        ) = row
        output_folder = None
        base_name = None
        if output_srt_path:
            output_folder = os.path.dirname(output_srt_path)
            base_name = os.path.splitext(os.path.basename(output_srt_path))[0]
            if base_name.endswith("_caption"):
                base_name = base_name[: -len("_caption")]
        if not base_name:
            with ldb.get_cursor() as cur:
                cur.execute("SELECT file_path FROM videos WHERE id = %s", (video_id_i,))
                video_row = cur.fetchone()
            if video_row and video_row[0]:
                output_folder = os.path.dirname(video_row[0])
                base_name = os.path.splitext(os.path.basename(video_row[0]))[0]
        frames_payload = build_caption_frame_payload(
            output_folder,
            base_name,
            output_json_path,
            output_srt_path,
        )
        self.write({
            "id": caption_id,
            "video_id": video_id_i,
            "status": status,
            "output_json_path": output_json_path,
            "output_srt_path": output_srt_path,
            "output_md_path": output_md_path,
            "json_url": media_url_for_path(output_json_path),
            "srt_url": media_url_for_path(output_srt_path),
            "md_url": media_url_for_path(output_md_path),
            "error": error,
            "created_at": created_at.isoformat() if created_at else None,
            "preview_text": build_transcription_preview(output_md_path, output_srt_path),
            "frames": frames_payload,
        })


class VideoMetadataHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        lang = _normalize_metadata_language(self.get_argument("lang", default=None))
        if not lang:
            self.set_status(400)
            return self.write({"error": "lang required"})

        ldb.ensure_schema()
        row = ldb.get_latest_video_metadata(video_id_i, lang)
        if not row:
            self.set_status(404)
            return self.write({"error": "metadata not found"})

        metadata_id, language_code, status, output_json_path, error, created_at = row
        metadata_payload = None
        if output_json_path and os.path.exists(output_json_path):
            try:
                with open(output_json_path, "r", encoding="utf-8") as handle:
                    metadata_payload = json.load(handle)
            except Exception:
                metadata_payload = None

        self.write({
            "id": metadata_id,
            "video_id": video_id_i,
            "language_code": language_code,
            "status": status,
            "output_json_path": output_json_path,
            "json_url": media_url_for_path(output_json_path),
            "metadata": metadata_payload,
            "error": error,
            "created_at": created_at.isoformat() if created_at else None,
        })

    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})

        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}

        raw_lang = data.get("lang") or data.get("language") or self.get_argument("lang", default=None)
        lang = _normalize_metadata_language(raw_lang)
        if not lang:
            self.set_status(400)
            return self.write({"error": f"language '{raw_lang}' not supported"})

        def parse_bool(value, default=True):
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            value_str = str(value).strip().lower()
            if value_str in {"1", "true", "yes", "y", "on"}:
                return True
            if value_str in {"0", "false", "no", "n", "off"}:
                return False
            return default

        use_cache = parse_bool(data.get("use_cache", self.get_argument("use_cache", default=None)), default=True)
        custom_notes = data.get("notes") or data.get("custom_notes") or ""
        if not isinstance(custom_notes, str):
            custom_notes = str(custom_notes)

        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute("SELECT file_path FROM videos WHERE id = %s", (video_id_i,))
            row = cur.fetchone()
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})
        file_path = row[0]
        if not file_path or not os.path.exists(file_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        input_file = preprocess_if_needed(file_path)
        base_name, _ = os.path.splitext(os.path.basename(input_file))
        output_folder = os.path.dirname(input_file)

        transcription_row = ldb.get_latest_transcription(video_id_i)
        if not transcription_row:
            self.set_status(400)
            return self.write({"error": "transcription missing; run Transcribe first"})
        (
            _transcription_id,
            _language_code,
            transcription_status,
            _output_json_path,
            output_srt_path,
            output_md_path,
            _error,
            _created_at,
        ) = transcription_row
        if transcription_status == "failed":
            self.set_status(400)
            return self.write({"error": "transcription failed; run Transcribe again"})

        transcription_text = _read_text_file(output_md_path) or _read_text_file(output_srt_path)
        if not transcription_text:
            self.set_status(400)
            return self.write({"error": "transcription missing; run Transcribe first"})

        caption_text = ""
        caption_row = ldb.get_latest_frame_caption(video_id_i)
        if caption_row:
            _, caption_status, _, caption_srt_path, caption_md_path, _, _ = caption_row
            if caption_status != "failed":
                caption_text = _read_text_file(caption_md_path) or _read_text_file(caption_srt_path)

        metadata_dir = os.path.join(output_folder, "metadata", lang)
        os.makedirs(metadata_dir, exist_ok=True)
        output_json_path = os.path.join(metadata_dir, f"{base_name}_metadata_{lang}.json")
        if os.path.exists(output_json_path):
            os.remove(output_json_path)

        status = "completed"
        error_message = None
        metadata_payload = None
        try:
            template_dir = os.path.join(METADATA_TEMPLATE_DIR, METADATA_TEMPLATE_MAP.get(lang, ""))
            generator = Subtitle2Metadata(OpenAI(), use_cache=use_cache, cache_dir="cache/metadata")
            metadata_payload = generator.generate_metadata_from_template(
                template_dir=template_dir,
                transcription_text=transcription_text,
                caption_text=caption_text,
                custom_notes=custom_notes,
                output_path=output_json_path,
            )
            with open(output_json_path, "w", encoding="utf-8") as handle:
                json.dump(metadata_payload, handle, ensure_ascii=False, indent=2)
        except Exception as exc:
            status = "failed"
            error_message = str(exc)
            print(f"Metadata generation failed for {lang}: {error_message}")
            traceback.print_exc()

        metadata_id = ldb.add_video_metadata(
            video_id_i,
            lang,
            status,
            output_json_path if status == "completed" else None,
            error_message,
        )

        if status != "completed":
            self.set_status(500)
            return self.write({"error": "metadata generation failed", "details": error_message, "id": metadata_id})

        self.write({
            "id": metadata_id,
            "video_id": video_id_i,
            "language_code": lang,
            "status": status,
            "output_json_path": output_json_path,
            "json_url": media_url_for_path(output_json_path),
            "metadata": metadata_payload,
            "error": error_message,
        })


class VideoCoverHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})

        row = _get_video_row(video_id_i)
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})
        _, file_path, _, _ = row
        if not file_path or not os.path.exists(file_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        publish_dir = _get_publish_dir(file_path)
        cover_filename = f"{base_name}_cover.jpg"
        cover_path = os.path.join(publish_dir, cover_filename)
        legacy_cover_path = os.path.join(os.path.dirname(file_path), cover_filename)
        if not os.path.exists(cover_path) and os.path.exists(legacy_cover_path):
            shutil.copy2(legacy_cover_path, cover_path)

        if not os.path.exists(cover_path):
            self.set_status(404)
            return self.write({"error": "cover not found"})

        self.write({
            "status": "completed",
            "cover_path": cover_path,
            "cover_url": media_url_for_path(cover_path),
        })

    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})

        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}

        lang = _normalize_metadata_language(data.get("lang") or data.get("language") or "zh") or "zh"
        row = _get_video_row(video_id_i)
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})
        _, file_path, _, _ = row
        if not file_path or not os.path.exists(file_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        metadata_payload, _ = _get_latest_metadata_payload(video_id_i, lang)
        if not metadata_payload and lang != "en":
            metadata_payload, _ = _get_latest_metadata_payload(video_id_i, "en")
        if not metadata_payload:
            self.set_status(400)
            return self.write({"error": "metadata missing; generate metadata first"})

        cover_timestamp_raw = metadata_payload.get("cover")
        if not cover_timestamp_raw:
            self.set_status(400)
            return self.write({"error": "cover timestamp missing in metadata"})

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        publish_dir = _get_publish_dir(file_path)
        cover_filename = f"{base_name}_cover.jpg"
        cover_path = os.path.join(publish_dir, cover_filename)
        cover_timestamp, _ = validate_timestamp(str(cover_timestamp_raw))
        video_for_cover = _pick_publish_video_path(video_id_i, file_path)

        try:
            extract_cover(video_for_cover, cover_path, cover_timestamp)
        except Exception as exc:
            self.set_status(500)
            return self.write({"error": "cover extraction failed", "details": str(exc)})

        self.write({
            "status": "completed",
            "cover_path": cover_path,
            "cover_url": media_url_for_path(cover_path),
            "timestamp": cover_timestamp,
        })


class VideoPublishHandler(CorsMixin, tornado.web.RequestHandler):
    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})

        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}

        platforms_raw = data.get("platforms") or data.get("publish") or {}
        platform_flags: dict[str, bool] = {}
        if isinstance(platforms_raw, list):
            platform_flags = {str(item): True for item in platforms_raw}
        elif isinstance(platforms_raw, dict):
            platform_flags = {str(key): bool(value) for key, value in platforms_raw.items()}

        if not platform_flags:
            platform_flags = {
                "xiaohongshu": bool(data.get("publish_xhs")),
                "douyin": bool(data.get("publish_douyin")),
                "bilibili": bool(data.get("publish_bilibili")),
                "shipinhao": bool(data.get("publish_shipinhao")),
                "youtube": bool(data.get("publish_youtube")),
            }

        has_target = any(platform_flags.values())
        if not has_target:
            self.set_status(400)
            return self.write({"error": "no platforms selected"})

        test_mode = _parse_bool(data.get("test"), default=False)
        wait_for_result = _parse_bool(data.get("wait"), default=False)

        row = _get_video_row(video_id_i)
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})
        _, file_path, _, _ = row
        if not file_path or not os.path.exists(file_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        metadata_zh, _ = _get_latest_metadata_payload(video_id_i, "zh")
        if not metadata_zh:
            self.set_status(400)
            return self.write({"error": "Chinese metadata missing; generate metadata first"})

        metadata_en, _ = _get_latest_metadata_payload(video_id_i, "en")
        if not metadata_en:
            metadata_en = metadata_zh

        metadata_payload = _simplify_metadata_payload(metadata_zh)
        metadata_payload["english_version"] = metadata_en

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        publish_dir = _get_publish_dir(file_path)
        video_filename = f"{base_name}_highlighted.mp4"
        cover_filename = f"{base_name}_cover.jpg"
        metadata_filename = f"{base_name}_metadata.json"

        metadata_payload["video_filename"] = video_filename
        metadata_payload["cover_filename"] = cover_filename

        video_to_publish = _pick_publish_video_path(video_id_i, file_path)
        cover_path = os.path.join(publish_dir, cover_filename)
        if not os.path.exists(cover_path):
            cover_timestamp_raw = metadata_payload.get("cover") or "00:00:01,000"
            cover_timestamp, _ = validate_timestamp(str(cover_timestamp_raw))
            try:
                extract_cover(video_to_publish, cover_path, cover_timestamp)
            except Exception as exc:
                self.set_status(500)
                return self.write({"error": "cover extraction failed", "details": str(exc)})

        metadata_path = os.path.join(publish_dir, metadata_filename)
        with open(metadata_path, "w", encoding="utf-8") as handle:
            json.dump(metadata_payload, handle, ensure_ascii=False, indent=2)

        zip_path = os.path.join(publish_dir, f"{base_name}.zip")
        extra_files = [
            os.path.join(os.path.dirname(file_path), f"{base_name}_mixed.json"),
            os.path.join(os.path.dirname(file_path), f"{base_name}_mixed.srt"),
        ]
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(video_to_publish, arcname=video_filename)
            if os.path.exists(cover_path):
                zipf.write(cover_path, arcname=cover_filename)
            zipf.write(metadata_path, arcname=metadata_filename)
            for extra in extra_files:
                if os.path.exists(extra):
                    zipf.write(extra, arcname=os.path.basename(extra))

        zip_url = media_url_for_path(zip_path)
        response_payload = {
            "status": "ready",
            "zip_path": zip_path,
            "zip_url": zip_url,
            "metadata_path": metadata_path,
            "cover_path": cover_path if os.path.exists(cover_path) else None,
            "video_path": video_to_publish,
            "platforms": platform_flags,
        }

        if not AUTOPUBLISH_URL:
            response_payload["warning"] = "autopublish url not configured"
            return self.write(response_payload)

        params = {
            "filename": os.path.basename(zip_path),
            "publish_xhs": str(platform_flags.get("xiaohongshu", False)).lower(),
            "publish_douyin": str(platform_flags.get("douyin", False)).lower(),
            "publish_bilibili": str(platform_flags.get("bilibili", False)).lower(),
            "publish_shipinhao": str(platform_flags.get("shipinhao", False)).lower(),
            "publish_y2b": str(platform_flags.get("youtube", False)).lower(),
            "test": str(test_mode).lower(),
        }

        def _post_zip():
            with open(zip_path, "rb") as handle:
                resp = requests.post(
                    AUTOPUBLISH_URL,
                    params=params,
                    data=handle.read(),
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=AUTOPUBLISH_TIMEOUT,
                )
            return resp

        if wait_for_result:
            try:
                resp = _post_zip()
                response_payload["autopublish_status"] = resp.status_code
                response_payload["autopublish_response"] = resp.text
                response_payload["status"] = "published" if resp.ok else "failed"
            except Exception as exc:
                response_payload["status"] = "failed"
                response_payload["autopublish_error"] = str(exc)
            return self.write(response_payload)

        def _async_worker():
            try:
                resp = _post_zip()
                if not resp.ok:
                    print(f"Autopublish failed: {resp.status_code} {resp.text}")
            except Exception as exc:
                print(f"Autopublish request failed: {exc}")

        threading.Thread(target=_async_worker, daemon=True).start()
        response_payload["status"] = "queued"
        self.write(response_payload)


class VideoPromptHandler(CorsMixin, tornado.web.RequestHandler):
    def post(self):
        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}

        prompt_spec = data.get("prompt_spec") or data.get("spec") or data.get("input") or ""
        prompt_spec_obj = None
        if isinstance(prompt_spec, dict):
            prompt_spec_obj = prompt_spec
            prompt_spec_text = json.dumps(prompt_spec, ensure_ascii=False, indent=2)
        elif isinstance(prompt_spec, list):
            prompt_spec_text = json.dumps(prompt_spec, ensure_ascii=False, indent=2)
        else:
            prompt_spec_text = str(prompt_spec)
            try:
                parsed = json.loads(prompt_spec_text)
                if isinstance(parsed, dict):
                    prompt_spec_obj = parsed
            except Exception:
                prompt_spec_obj = None

        use_cache = _parse_bool(data.get("use_cache"), default=True)
        if not os.path.isdir(VIDEO_PROMPT_TEMPLATE_DIR):
            self.set_status(500)
            return self.write({"error": "video prompt template missing"})

        try:
            generator = VideoPromptGenerator(
                template_dir=VIDEO_PROMPT_TEMPLATE_DIR,
                use_cache=use_cache,
                cache_dir="cache/video_prompts",
            )
            result = generator.generate(prompt_spec_text)
        except Exception as exc:
            self.set_status(500)
            return self.write({"error": "prompt generation failed", "details": str(exc)})

        title = None
        if isinstance(prompt_spec_obj, dict):
            title = prompt_spec_obj.get("title") or prompt_spec_obj.get("name")

        self.write({
            "prompt_spec": prompt_spec_text,
            "title": result.get("title") or title,
            "prompt": result.get("prompt"),
            "negative_prompt": result.get("negative_prompt"),
            "model": result.get("model"),
            "size": result.get("size"),
            "seconds": result.get("seconds"),
            "result": result,
        })


class VideoSpecHandler(CorsMixin, tornado.web.RequestHandler):
    def post(self):
        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}

        idea_prompt = data.get("idea") or data.get("prompt") or ""
        if not isinstance(idea_prompt, str):
            idea_prompt = str(idea_prompt)
        idea_prompt = idea_prompt.strip() or "Create an evocative, cinematic short video spec."

        use_cache = _parse_bool(data.get("use_cache"), default=True)
        if not os.path.isdir(VIDEO_SPEC_TEMPLATE_DIR):
            self.set_status(500)
            return self.write({"error": "video spec template missing"})

        try:
            generator = VideoPromptGenerator(
                template_dir=VIDEO_SPEC_TEMPLATE_DIR,
                use_cache=use_cache,
                cache_dir="cache/video_specs",
            )
            result = generator.generate(idea_prompt, schema_name="video_spec")
        except Exception as exc:
            self.set_status(500)
            return self.write({"error": "spec generation failed", "details": str(exc)})

        spec = _sanitize_video_prompt_spec(result)
        self.write({"idea": idea_prompt, "spec": spec, "result": result})


class VideoGenerateHandler(CorsMixin, tornado.web.RequestHandler):
    def post(self):
        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}

        prompt = data.get("prompt") or ""
        if not isinstance(prompt, str) or not prompt.strip():
            self.set_status(400)
            return self.write({"error": "prompt required"})

        model = str(data.get("model") or "sora-2").strip()
        if model not in {"sora-2", "sora-2-pro"}:
            model = "sora-2"

        # OpenAI Sora size options are fixed; normalize legacy UI values.
        supported_sizes = {"720x1280", "1280x720", "1024x1792", "1792x1024"}
        legacy_size_map = {
            # Legacy 1080p selections (unsupported by Sora).
            "1920x1080": "1792x1024",
            "1080x1920": "1024x1792",
            # Legacy low-res 16:9.
            "1024x576": "1280x720",
        }
        size = str(data.get("size") or "1280x720").strip()
        size = legacy_size_map.get(size, size)
        if size not in supported_sizes:
            size = "1280x720"

        try:
            seconds = int(data.get("seconds") or 8)
        except Exception:
            seconds = 8

        # OpenAI Sora currently supports only fixed durations (regardless of model).
        allowed_seconds = (4, 8, 12)
        seconds = min(allowed_seconds, key=lambda v: abs(v - seconds))

        use_cache = _parse_bool(data.get("use_cache"), default=True)
        title_input = data.get("title") or data.get("name") or "Generated video"
        if not isinstance(title_input, str):
            title_input = str(title_input)

        title_base = _sanitize_title(title_input)
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
        title = f"{title_base} {prompt_hash}"
        output_dir = os.path.join(UPLOAD_FOLDER, "generated")
        os.makedirs(output_dir, exist_ok=True)
        slug = _slugify(title_base)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"{slug}_{timestamp}_{prompt_hash}.mp4")

        try:
            output_path = create_poll_and_download(
                prompt=prompt.strip(),
                model=model,
                size=size,
                seconds=seconds,
                output=output_path,
                use_cache=use_cache,
            )
        except Exception as exc:
            print("Video generation failed.")
            traceback.print_exc()
            self.set_status(500)
            return self.write({
                "error": "video generation failed",
                "details": str(exc),
                "requested": {"model": model, "size": size, "seconds": seconds},
            })

        if not output_path or not os.path.exists(output_path):
            self.set_status(500)
            return self.write({"error": "generated video missing", "path": output_path})

        if not media_url_for_path(output_path):
            dest_name = os.path.basename(output_path) or f"{slug}_{timestamp}_{prompt_hash}.mp4"
            dest_path = os.path.join(output_dir, dest_name)
            if os.path.abspath(output_path) != os.path.abspath(dest_path):
                shutil.copy2(output_path, dest_path)
            output_path = dest_path

        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute("SELECT id FROM videos WHERE file_path = %s", (output_path,))
            row = cur.fetchone()
        if row:
            video_id = row[0]
        else:
            video_id = ldb.add_video(output_path, title, "generate")

        self.write({
            "video_id": video_id,
            "file_path": output_path,
            "media_url": media_url_for_path(output_path),
            "title": title,
            "model": model,
            "size": size,
            "seconds": seconds,
        })


class VideoTranslateHandler(CorsMixin, tornado.web.RequestHandler):
    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})

        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}

        raw_lang = (
            data.get("language")
            or data.get("lang")
            or self.get_argument("lang", default=None)
            or "ja"
        )
        lang = _normalize_translation_language(raw_lang)
        if not lang:
            self.set_status(400)
            return self.write({"error": f"language '{raw_lang}' not supported yet"})

        def parse_bool(value, default=True):
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            value_str = str(value).strip().lower()
            if value_str in {"1", "true", "yes", "y", "on"}:
                return True
            if value_str in {"0", "false", "no", "n", "off"}:
                return False
            return default

        use_cache = parse_bool(
            data.get("use_cache", self.get_argument("use_cache", default=None)),
            default=True,
        )

        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute("SELECT file_path FROM videos WHERE id = %s", (video_id_i,))
            row = cur.fetchone()
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})
        file_path = row[0]
        if not file_path or not os.path.exists(file_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        input_file = preprocess_if_needed(file_path)
        base_name, _ = os.path.splitext(os.path.basename(input_file))
        output_folder = os.path.dirname(input_file)
        input_json, input_srt = find_latest_transcription_outputs(output_folder, base_name)
        if not input_json or not input_srt or not os.path.exists(input_json) or not os.path.exists(input_srt):
            self.set_status(400)
            return self.write({"error": "transcription missing; run Transcribe first"})

        translations_dir = os.path.join(output_folder, "translations", lang)
        os.makedirs(translations_dir, exist_ok=True)
        traditional_json_path = None
        if lang == "ja":
            output_json_path = os.path.join(translations_dir, f"{base_name}_ja_furigana.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_ja_furigana.srt")
            output_ass_path = os.path.join(translations_dir, f"{base_name}_ja_furigana.ass")
        elif lang == "en":
            output_json_path = os.path.join(translations_dir, f"{base_name}_en.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_en.srt")
            output_ass_path = None
        elif lang == "ar":
            output_json_path = os.path.join(translations_dir, f"{base_name}_ar.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_ar.srt")
            output_ass_path = None
        elif lang == "vi":
            output_json_path = os.path.join(translations_dir, f"{base_name}_vi.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_vi.srt")
            output_ass_path = None
        elif lang == "ko":
            output_json_path = os.path.join(translations_dir, f"{base_name}_ko.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_ko.srt")
            output_ass_path = None
        elif lang == "es":
            output_json_path = os.path.join(translations_dir, f"{base_name}_es.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_es.srt")
            output_ass_path = None
        elif lang == "fr":
            output_json_path = os.path.join(translations_dir, f"{base_name}_fr.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_fr.srt")
            output_ass_path = None
        elif lang == "ru":
            output_json_path = os.path.join(translations_dir, f"{base_name}_ru.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_ru.srt")
            output_ass_path = None
        elif lang == "yue":
            output_json_path = os.path.join(translations_dir, f"{base_name}_yue.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_yue.srt")
            output_ass_path = None
        elif lang == "zh-Hant":
            output_json_path = os.path.join(translations_dir, f"{base_name}_zh_hant.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_zh_hant.srt")
            output_ass_path = None
        else:
            output_json_path = os.path.join(translations_dir, f"{base_name}_zh_hans.json")
            output_srt_path = os.path.join(translations_dir, f"{base_name}_zh_hans.srt")
            output_ass_path = None
            traditional_dir = os.path.join(output_folder, "translations", "zh-Hant")
            traditional_json_path = os.path.join(traditional_dir, f"{base_name}_zh_hant.json")

        for path in (output_json_path, output_srt_path, output_ass_path):
            if path and os.path.exists(path):
                os.remove(path)

        try:
            video_length = get_video_length(input_file)
            video_width, video_height = get_video_resolution(input_file)
            translator = SubtitlesTranslator(
                OpenAI(),
                input_json_path=input_json,
                input_sub_path=input_srt,
                output_json_path=output_json_path,
                output_sub_path=output_srt_path,
                video_length=video_length,
                video_width=video_width,
                video_height=video_height,
                use_cache=use_cache,
            )
            json_items = []
            if lang == "ja":
                ruby_items, plain_items, json_items = translator.process_japanese_furigana_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
                translator.save_translated_subtitles_to_ass_path(ruby_items, output_ass_path)
            elif lang == "en":
                plain_items, json_items = translator.process_english_translation_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
            elif lang == "ar":
                plain_items, json_items = translator.process_arabic_translation_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
            elif lang == "vi":
                plain_items, json_items = translator.process_vietnamese_translation_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
            elif lang == "ko":
                plain_items, json_items = translator.process_korean_translation_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
            elif lang == "es":
                plain_items, json_items = translator.process_spanish_translation_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
            elif lang == "fr":
                plain_items, json_items = translator.process_french_translation_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
            elif lang == "ru":
                plain_items, json_items = translator.process_russian_translation_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
            elif lang == "yue":
                plain_items, json_items = translator.process_cantonese_translation_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
            elif lang == "zh-Hant":
                plain_items, json_items = translator.process_chinese_traditional_translation_single_pass()
                translator.save_translated_subtitles_to_json_path(json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(plain_items, output_srt_path)
            else:
                traditional_items = None
                if use_cache and traditional_json_path and os.path.exists(traditional_json_path):
                    try:
                        with open(traditional_json_path, "r", encoding="utf-8") as handle:
                            data = json.load(handle)
                        if isinstance(data, list):
                            traditional_items = data
                    except Exception:
                        traditional_items = None

                if traditional_items is None:
                    plain_items, json_items = translator.process_chinese_traditional_translation_single_pass()
                    traditional_items = json_items
                else:
                    plain_items = traditional_items
                    json_items = traditional_items

                simplified_plain_items = convert_items_to_simplified(plain_items)
                simplified_json_items = convert_items_to_simplified(json_items)
                translator.save_translated_subtitles_to_json_path(simplified_json_items, output_json_path)
                translator.save_translated_subtitles_to_srt_path(simplified_plain_items, output_srt_path)
                json_items = simplified_json_items

            status = "completed" if json_items else "empty"
            error_message = None
        except Exception as e:
            status = "failed"
            error_message = str(e)

        translation_id = ldb.add_subtitle_translation(
            video_id_i,
            lang,
            status,
            output_json_path if status != "failed" else None,
            output_srt_path if status != "failed" else None,
            output_ass_path if status != "failed" else None,
            error_message,
        )
        if status == "failed":
            self.set_status(500)
            return self.write({"error": "translation failed", "details": error_message, "id": translation_id})

        self.write({
            "id": translation_id,
            "video_id": video_id_i,
            "language_code": lang,
            "status": status,
            "output_json_path": output_json_path,
            "output_srt_path": output_srt_path,
            "output_ass_path": output_ass_path,
            "json_url": media_url_for_path(output_json_path),
            "srt_url": media_url_for_path(output_srt_path),
            "ass_url": media_url_for_path(output_ass_path),
            "preview_text": build_srt_preview_with_timestamps(output_srt_path),
            "error": error_message,
        })


class VideoTranslationsHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        ldb.ensure_schema()
        rows = ldb.get_subtitle_translations_for_video(video_id_i)
        seen_languages = set()
        translations = []
        for row in rows:
            (
                translation_id,
                language_code,
                status,
                output_json_path,
                output_srt_path,
                output_ass_path,
                error,
                created_at,
            ) = row
            if language_code in seen_languages:
                continue
            seen_languages.add(language_code)
            translations.append({
                "id": translation_id,
                "video_id": video_id_i,
                "language_code": language_code,
                "status": status,
                "output_json_path": output_json_path,
                "output_srt_path": output_srt_path,
                "output_ass_path": output_ass_path,
                "json_url": media_url_for_path(output_json_path),
                "srt_url": media_url_for_path(output_srt_path),
                "ass_url": media_url_for_path(output_ass_path),
                "error": error,
                "created_at": created_at.isoformat() if created_at else None,
                "preview_text": build_srt_preview_with_timestamps(output_srt_path),
            })
        self.write({"translations": translations})


class VideoTranslationHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        lang = self.get_argument("lang", default=None)
        if not lang:
            self.set_status(400)
            return self.write({"error": "lang required"})
        lang = _normalize_translation_language(lang)
        if not lang:
            self.set_status(400)
            return self.write({"error": "unsupported lang"})
        ldb.ensure_schema()
        row = ldb.get_latest_subtitle_translation(video_id_i, lang)
        if not row and lang == "zh-Hant":
            row = ldb.get_latest_subtitle_translation(video_id_i, "zh")
        if not row:
            self.set_status(404)
            return self.write({"error": "translation not found"})
        (
            translation_id,
            language_code,
            status,
            output_json_path,
            output_srt_path,
            output_ass_path,
            error,
            created_at,
        ) = row
        self.write({
            "id": translation_id,
            "video_id": video_id_i,
            "language_code": language_code,
            "status": status,
            "output_json_path": output_json_path,
            "output_srt_path": output_srt_path,
            "output_ass_path": output_ass_path,
            "json_url": media_url_for_path(output_json_path),
            "srt_url": media_url_for_path(output_srt_path),
            "ass_url": media_url_for_path(output_ass_path),
            "error": error,
            "created_at": created_at.isoformat() if created_at else None,
            "preview_text": build_srt_preview_with_timestamps(output_srt_path),
        })


class VideoSubtitleBurnHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})

        ldb.ensure_schema()
        row = ldb.get_latest_subtitle_burn(video_id_i)
        if not row:
            self.set_status(404)
            return self.write({"error": "burn not found"})
        burn_id, status, output_path, progress, config, error, created_at = row
        self.write({
            "id": burn_id,
            "video_id": video_id_i,
            "status": status,
            "output_path": output_path,
            "output_url": media_url_for_path(output_path),
            "progress": progress,
            "config": config,
            "error": error,
            "created_at": created_at.isoformat() if created_at else None,
        })

    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})

        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}

        layout_config = _sanitize_burn_layout(data.get("layout") or data.get("slots") or data)
        slots_config = layout_config.get("slots") or []
        romaji_enabled = bool(layout_config.get("romajiEnabled", True))
        pinyin_enabled = bool(layout_config.get("pinyinEnabled", True))

        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute("SELECT file_path FROM videos WHERE id = %s", (video_id_i,))
            row = cur.fetchone()
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})
        video_path = row[0]
        if not video_path or not os.path.exists(video_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        output_folder = os.path.dirname(video_path)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        speaker_output_dir = os.path.join(output_folder, "burn")
        transcription_row = ldb.get_latest_transcription(video_id_i)
        speaker_map: dict[tuple[str, str], str] = {}
        if transcription_row:
            transcription_json_path = transcription_row[3]
            speaker_map = _build_transcription_language_map(transcription_json_path)

        assignments: list[BurnSlotConfig] = []
        for slot in slots_config:
            if not isinstance(slot, dict):
                continue
            language = slot.get("language")
            slot_id = int(slot.get("slot") or 0)
            romaji = slot.get("romaji") if isinstance(slot.get("romaji"), bool) else True
            pinyin = slot.get("pinyin") if isinstance(slot.get("pinyin"), bool) else True
            ipa = slot.get("ipa") if isinstance(slot.get("ipa"), bool) else False
            jyutping = slot.get("jyutping") if isinstance(slot.get("jyutping"), bool) else False
            romaja = slot.get("romaja") if isinstance(slot.get("romaja"), bool) else False
            arabic_translit = slot.get("arabicTranslit") if isinstance(slot.get("arabicTranslit"), bool) else False
            try:
                font_scale = float(slot.get("fontScale", 1.0))
            except Exception:
                font_scale = 1.0
            font_scale = min(max(font_scale, 0.6), 2.5)
            if not language or slot_id <= 0:
                continue

            lang = _normalize_translation_language(language)
            if not lang:
                continue

            translation_row = ldb.get_latest_subtitle_translation(video_id_i, lang)
            if not translation_row and lang == "zh-Hant":
                translation_row = ldb.get_latest_subtitle_translation(video_id_i, "zh")
            if not translation_row:
                self.set_status(400)
                return self.write({"error": f"translation missing for {lang}"})
            _, _, status, output_json_path, _, _, error, _ = translation_row
            if status != "completed" or not output_json_path or not os.path.exists(output_json_path):
                self.set_status(400)
                return self.write({"error": f"translation not ready for {lang}", "details": error})

            if lang in {"zh-Hant", "zh-Hans"}:
                text_key = "zh"
            else:
                text_key = lang

            palette = load_grammar_palette(lang)
            auto_ruby = lang == "ja"
            speaker_json_path = _prepare_speaker_json(
                output_json_path,
                speaker_output_dir,
                lang,
                text_key,
                speaker_map,
            )
            assignments.append(
                BurnSlotConfig(
                    slot_id=slot_id,
                    language=lang,
                    json_path=speaker_json_path,
                    text_key=text_key,
                    ruby_key="ruby" if lang == "ja" else None,
                    palette=palette,
                    auto_ruby=auto_ruby,
                    strip_kana=lang == "ja",
                    font_scale=font_scale,
                    kana_romaji=romaji and lang == "ja",
                    pinyin=pinyin and lang in {"zh", "zh-Hant", "zh-Hans"},
                    ipa=ipa and lang in {"en", "fr"},
                    jyutping=jyutping and lang == "yue",
                    korean_romaja=romaja and lang == "ko",
                    arabic_translit=arabic_translit and lang == "ar",
                )
            )

        if not assignments:
            self.set_status(400)
            return self.write({"error": "no valid subtitle slots configured"})

        temp_output = os.path.join(output_folder, f"{base_name}_subtitles_render.avi")
        output_path = os.path.join(output_folder, f"{base_name}_subtitles.mp4")
        height_ratio = layout_config.get("heightRatio", DEFAULT_BURN_LAYOUT.get("heightRatio", 0.5))
        rows = layout_config.get("rows", DEFAULT_BURN_LAYOUT.get("rows", 4))
        cols = layout_config.get("cols", DEFAULT_BURN_LAYOUT.get("cols", 1))
        lift_ratio = layout_config.get("liftRatio", DEFAULT_BURN_LAYOUT.get("liftRatio", 0.1))
        lift_slots = layout_config.get("liftSlots", DEFAULT_BURN_LAYOUT.get("liftSlots", 0))
        ruby_spacing = layout_config.get("rubySpacing", DEFAULT_BURN_LAYOUT.get("rubySpacing", 0.1))

        burn_id = ldb.add_subtitle_burn(
            video_id_i,
            "processing",
            None,
            layout_config,
            None,
            progress=0,
        )

        def _update_progress(value: int) -> None:
            try:
                ldb.update_subtitle_burn_progress(burn_id, value)
            except Exception:
                pass

        def _run_burn() -> None:
            status = "completed"
            error_message = None
            try:
                burn_video_with_slots(
                    video_path,
                    temp_output,
                    assignments,
                    height_ratio=height_ratio,
                    rows=rows,
                    cols=cols,
                    lift_slots=lift_slots,
                    lift_ratio=lift_ratio,
                    ruby_spacing=ruby_spacing,
                    progress_callback=_update_progress,
                )
                mux_audio(temp_output, video_path, output_path)
            except Exception as exc:
                status = "failed"
                error_message = str(exc)
            finally:
                if os.path.exists(temp_output):
                    try:
                        os.remove(temp_output)
                    except Exception:
                        pass
            if status == "completed":
                ldb.finalize_subtitle_burn(burn_id, status, output_path, None, progress=100)
            else:
                ldb.finalize_subtitle_burn(burn_id, status, None, error_message, progress=0)

        BURN_EXECUTOR.submit(_run_burn)

        created_at = None
        try:
            latest = ldb.get_latest_subtitle_burn(video_id_i)
            if latest and latest[0] == burn_id:
                created_at = latest[-1]
        except Exception:
            created_at = None

        self.write({
            "id": burn_id,
            "video_id": video_id_i,
            "status": "processing",
            "progress": 0,
            "output_path": None,
            "output_url": None,
            "config": layout_config,
            "created_at": created_at.isoformat() if created_at else None,
        })


class VideoProcessHandler(CorsMixin, tornado.web.RequestHandler):
    async def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})

        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            data = {}

        steps_raw = data.get("steps")
        if isinstance(steps_raw, (list, tuple)):
            selected_steps = {str(step).lower() for step in steps_raw}
        else:
            selected_steps = set()

        def wants(step: str) -> bool:
            return not selected_steps or step in selected_steps

        needs_transcribe = wants("transcribe") or wants("translate") or wants("burn") or wants("metadata_zh") or wants("metadata_en")
        needs_translate = wants("translate") or wants("burn")
        needs_caption = wants("caption") or wants("metadata_zh") or wants("metadata_en")

        translation_languages = _load_translation_languages_setting()
        burn_layout = _load_burn_layout_setting()
        notes = data.get("notes") or data.get("custom_notes") or ""

        statuses: dict[str, dict] = {}

        async def call_json(method: str, path: str, payload: dict | None = None):
            url = f"http://localhost:{PORT}{path}"
            body = json.dumps(payload).encode("utf-8") if payload is not None else None
            headers = {"Content-Type": "application/json"} if payload is not None else None
            request = tornado.httpclient.HTTPRequest(
                url=url,
                method=method,
                body=body,
                headers=headers,
                request_timeout=7200,
            )
            response = await tornado.httpclient.AsyncHTTPClient().fetch(request, raise_error=False)
            try:
                data_out = json.loads(response.body or b"{}")
            except Exception:
                data_out = {}
            return response.code, data_out

        async def mark(step: str, status: str, detail: str | None = None):
            statuses[step] = {"status": status, "detail": detail}

        if needs_transcribe:
            await mark("transcribe", "working", "Transcribing")
            code, payload = await call_json("POST", f"/api/videos/{video_id_i}/transcribe")
            if code >= 400:
                await mark("transcribe", "error", payload.get("error") or payload.get("details") or "Failed")
                self.set_status(500)
                return self.write({"error": "transcription failed", "steps": statuses})
            await mark("transcribe", "done", "Completed")
        else:
            await mark("transcribe", "skipped", "Skipped")

        if needs_translate:
            if not translation_languages:
                await mark("translate", "skipped", "No languages selected")
            else:
                await mark("translate", "working", "Translating")
                for lang in translation_languages:
                    code, payload = await call_json(
                        "POST",
                        f"/api/videos/{video_id_i}/translate",
                        {"language": lang, "use_cache": True},
                    )
                    if code >= 400:
                        await mark(
                            "translate",
                            "error",
                            payload.get("error") or payload.get("details") or f"Failed: {lang}",
                        )
                        self.set_status(500)
                        return self.write({"error": "translation failed", "steps": statuses})
                await mark("translate", "done", "Completed")
        else:
            await mark("translate", "skipped", "Skipped")

        if wants("burn"):
            await mark("burn", "working", "Burning subtitles")
            code, payload = await call_json(
                "POST",
                f"/api/videos/{video_id_i}/burn-subtitles",
                {"layout": burn_layout},
            )
            if code >= 400:
                await mark("burn", "error", payload.get("error") or payload.get("details") or "Failed")
                self.set_status(500)
                return self.write({"error": "burn failed", "steps": statuses})

            while True:
                await gen.sleep(2)
                code, status_payload = await call_json("GET", f"/api/videos/{video_id_i}/burn-subtitles")
                if code >= 400:
                    await mark("burn", "error", status_payload.get("error") or "Failed")
                    self.set_status(500)
                    return self.write({"error": "burn failed", "steps": statuses})
                if status_payload.get("status") == "processing":
                    continue
                if status_payload.get("status") == "completed":
                    await mark("burn", "done", "Completed")
                    break
                await mark("burn", "error", status_payload.get("error") or "Failed")
                self.set_status(500)
                return self.write({"error": "burn failed", "steps": statuses})
        else:
            await mark("burn", "skipped", "Skipped")

        if wants("keyframes"):
            await mark("keyframes", "working", "Extracting")
            code, payload = await call_json("POST", f"/api/videos/{video_id_i}/keyframes")
            if code >= 400:
                await mark("keyframes", "error", payload.get("error") or payload.get("details") or "Failed")
                self.set_status(500)
                return self.write({"error": "keyframes failed", "steps": statuses})
            await mark("keyframes", "done", "Completed")
        else:
            await mark("keyframes", "skipped", "Skipped")

        if needs_caption:
            await mark("caption", "working", "Captioning")
            code, payload = await call_json("POST", f"/api/videos/{video_id_i}/caption")
            if code >= 400:
                await mark("caption", "error", payload.get("error") or payload.get("details") or "Failed")
                self.set_status(500)
                return self.write({"error": "caption failed", "steps": statuses})
            await mark("caption", "done", "Completed")
        else:
            await mark("caption", "skipped", "Skipped")

        if wants("metadata_zh"):
            await mark("metadata_zh", "working", "Generating")
            code, payload = await call_json(
                "POST",
                f"/api/videos/{video_id_i}/metadata",
                {"lang": "zh", "use_cache": True, "notes": notes},
            )
            if code >= 400:
                await mark("metadata_zh", "error", payload.get("error") or payload.get("details") or "Failed")
                self.set_status(500)
                return self.write({"error": "metadata zh failed", "steps": statuses})
            await mark("metadata_zh", "done", "Completed")
        else:
            await mark("metadata_zh", "skipped", "Skipped")

        if wants("metadata_en"):
            await mark("metadata_en", "working", "Generating")
            code, payload = await call_json(
                "POST",
                f"/api/videos/{video_id_i}/metadata",
                {"lang": "en", "use_cache": True, "notes": notes},
            )
            if code >= 400:
                await mark("metadata_en", "error", payload.get("error") or payload.get("details") or "Failed")
                self.set_status(500)
                return self.write({"error": "metadata en failed", "steps": statuses})
            await mark("metadata_en", "done", "Completed")
        else:
            await mark("metadata_en", "skipped", "Skipped")

        self.write({"video_id": video_id_i, "steps": statuses})

class VideoKeyframesHandler(CorsMixin, tornado.web.RequestHandler):
    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        ldb.ensure_schema()
        with ldb.get_cursor() as cur:
            cur.execute("SELECT file_path FROM videos WHERE id = %s", (video_id_i,))
            row = cur.fetchone()
        if not row:
            self.set_status(404)
            return self.write({"error": "video not found"})
        file_path = row[0]
        if not file_path or not os.path.exists(file_path):
            self.set_status(404)
            return self.write({"error": "video file missing"})

        input_file = preprocess_if_needed(file_path)
        base_name, _ = os.path.splitext(os.path.basename(input_file))
        output_folder = os.path.dirname(input_file)
        output_dir = os.path.join(output_folder, "keyframes")

        target_count_raw = self.get_argument("count", default="8")
        try:
            target_count = max(1, int(target_count_raw))
        except Exception:
            target_count = 8

        try:
            frames, method = extract_keyframes(input_file, output_dir, target_count=target_count)
            if not frames:
                message = "Keyframe extraction produced no frames."
                extract_id = ldb.add_keyframe_extraction(
                    video_id_i,
                    "failed",
                    output_dir,
                    0,
                    message,
                )
                self.set_status(500)
                return self.write({"error": message, "id": extract_id})

            frame_urls = [media_url_for_path(path) for path in frames if media_url_for_path(path)]
            extract_id = ldb.add_keyframe_extraction(
                video_id_i,
                "completed",
                output_dir,
                len(frame_urls),
                None,
            )
            self.write({
                "id": extract_id,
                "video_id": video_id_i,
                "status": "completed",
                "frame_count": len(frame_urls),
                "output_dir": output_dir,
                "frame_urls": frame_urls,
                "method": method,
            })
        except Exception as e:
            extract_id = ldb.add_keyframe_extraction(
                video_id_i,
                "failed",
                output_dir,
                0,
                str(e),
            )
            self.set_status(500)
            return self.write({"error": "keyframe extraction failed", "details": str(e), "id": extract_id})

    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        ldb.ensure_schema()
        row = ldb.get_latest_keyframe_extraction(video_id_i)
        if not row:
            self.set_status(404)
            return self.write({"error": "keyframes not found"})
        extract_id, status, output_dir, frame_count, error, created_at = row
        frames = list_keyframe_files(output_dir)
        frame_urls = [media_url_for_path(path) for path in frames if media_url_for_path(path)]
        self.write({
            "id": extract_id,
            "video_id": video_id_i,
            "status": status,
            "output_dir": output_dir,
            "frame_count": frame_count if frame_count is not None else len(frame_urls),
            "frame_urls": frame_urls,
            "error": error,
            "created_at": created_at.isoformat() if created_at else None,
        })


class CaptionsHandler(CorsMixin, tornado.web.RequestHandler):
    def get(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        rows = ldb.get_captions_for_video(video_id_i)
        caps = [{"id": r[0], "language_code": r[1], "subtitle_path": r[2]} for r in rows]
        self.write({"captions": caps})

    def post(self, video_id):
        try:
            video_id_i = int(video_id)
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid id"})
        try:
            data = json.loads(self.request.body or b"{}")
        except Exception:
            self.set_status(400)
            return self.write({"error": "invalid json"})
        lang = data.get("language_code")
        path = data.get("subtitle_path")
        if not (lang and path):
            self.set_status(400)
            return self.write({"error": "language_code and subtitle_path required"})
        ldb.ensure_schema()
        cid = ldb.add_caption(video_id_i, lang, path)
        self.write({"id": cid})




@tornado.web.stream_request_body
class FileUploadHandlerStream(CorsMixin, tornado.web.RequestHandler):
    def initialize(self, upload_folder):
        self.bytes_received = 0
        self.file = None
        self.file_path = None
        self.base_name = None
        self.title = None
        self.source = None
        self.upload_folder = upload_folder

    def prepare(self):
        filename = self.get_argument('filename', default='uploaded_file')
        base_name, _ = os.path.splitext(filename)
        self.base_name = base_name
        self.title = self.get_argument("title", default=None) or base_name
        self.source = _normalize_video_source(self.get_argument("source", default=None)) or "upload"
        output_folder = os.path.join(self.upload_folder, base_name)

        # Check if the folder already exists
        if os.path.exists(output_folder) and os.path.isdir(output_folder):
            # Get the folder creation time
            creation_time = os.path.getctime(output_folder)
            # Convert creation time to a readable format
            creation_time_formatted = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d_%H-%M-%S')
            # Define the new folder name with creation datetime appended
            new_folder_name = f"{output_folder}_{creation_time_formatted}"
            # Rename the existing folder
            # os.rename(output_folder, new_folder_name)
            copy_folder(output_folder, new_folder_name)
            print(f"Existing folder renamed to: {new_folder_name}")

        os.makedirs(output_folder, exist_ok=True)
        
        self.file_path = os.path.join(output_folder, filename)
        self.file = open(self.file_path, 'wb')

    def data_received(self, chunk):
        if self.file:
            self.file.write(chunk)
            self.bytes_received += len(chunk)

    def put(self):
        if self.file:
            self.file.close()
            self.file = None
            try:
                ldb.ensure_schema()
                video_id = ldb.add_video(self.file_path, self.title, self.source)
            except Exception as e:
                self.set_status(500)
                return self.write({
                    "error": "failed to save video in database",
                    "details": str(e),
                })
            _enqueue_preview_proxy(video_id, self.file_path)
            response = {
                'status': 'success',
                'message': f"Received {self.bytes_received} bytes.",
                'file_path': self.file_path,
                'media_url': media_url_for_path(self.file_path),
                'video_id': video_id,
            }
            self.write(response)



class AutomaticalVideoEditingHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=1)

    def initialize(self):
        self.openai_client = OpenAI()  # Make sure to authenticate your OpenAI client
        # self.sub2meta = Subtitle2Metadata(self.openai_client)

    def run_autocut(self, autocut_command, lang, gpu_id):
        # Set the CUDA_VISIBLE_DEVICES environment variable
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)

        # Run the autocut command with the specified environment
        subprocess.run(autocut_command, shell=True, check=True, env=env)
        print(f"Finished autocut with lang={lang} on GPU {gpu_id}")

    def transcribe_video(self, input_file, base_name, extension, output_folder):
        # Process the video with autocut
        autocut_processor = AutocutProcessor(input_file, output_folder, base_name, extension)
        futures = [
            self.executor.submit(autocut_processor.run_autocut, 'mixed', 1),
            # self.executor.submit(autocut_processor.run_autocut, 'en', 0),
            # self.executor.submit(autocut_processor.run_autocut, 'zh', 1)
        ]
        for future in as_completed(futures):
            result = future.result()
            print(f"Task completed with result: {result}")


    def caption_video(self, input_file, output_folder, num_frames=3):
        """
        Method to handle video captioning. It directly instantiates and uses VideoCaptioner.
        """
        # Instantiate VideoCaptioner with the required settings
        video_captioner = VideoCaptioner(
            video_path=input_file,
            num_frames=num_frames,
            output_folder=output_folder
        )

        # Submit the captioning task to the thread pool executor
        future = self.executor.submit(video_captioner.run_captioning)
        for future in as_completed([future]):  # Wait for the captioning to complete
            try:
                future.result()  # This will raise an exception if the captioning failed
                print("Captioning completed successfully.")
            except Exception as e:
                print(f"An error occurred during video captioning: {str(e)}")



    @gen.coroutine
    def post(self):
        
        input_file = self.get_argument('file_path', None)
        # input_file = preprocess_if_needed(input_file)
        use_translation_cache = self.get_argument('use_translation_cache', "false").lower() == 'true'
        use_metadata_cache = self.get_argument('use_metadata_cache', "false").lower() == 'true'
        if not input_file or not os.path.exists(input_file):
            self.set_status(400)
            self.write({'status': 'error', 'message': 'File path is invalid or file does not exist'})
            return

        print("Processing File: ", input_file)

        video_length = get_video_length(input_file)
        video_width, video_height = get_video_resolution(input_file)

        print("video_length: ", video_length)
        print("video_width: ", video_width)
        print("video_height: ", video_height)

        base_name, extension = os.path.splitext(os.path.basename(input_file))
        output_folder = os.path.dirname(input_file)

        self.transcribe_video(input_file, base_name, extension, output_folder)
        
        output_json_mixed = f"{output_folder}/{base_name}_mixed.json"
        output_srt_mixed = f"{output_folder}/{base_name}_mixed.srt"

        # Check if files exist before reading
        # for file_path in [output_md_en, output_srt_en, output_md_zh, output_srt_zh]:
        for file_path in [output_json_mixed, output_srt_mixed]:
            if not os.path.exists(file_path):
                self.set_status(500)
                self.write(f"Error: Expected output file not found: {file_path}")
                return

        self.caption_video(input_file, output_folder, num_frames=7)

        output_json_caption = f"{output_folder}/{os.path.splitext(os.path.basename(input_file))[0]}_caption.json"
        output_srt_caption = f"{output_folder}/{os.path.splitext(os.path.basename(input_file))[0]}_caption.srt"

        # Example to handle JSON and SRT files if needed
        if not all(os.path.exists(f) for f in [output_json_caption, output_srt_caption]):
            self.set_status(500)
            self.write({'status': 'error', 'message': 'Expected output files not found'})
            return

        # Merge subtitles
        print("Merging/Translating subtitles...")
        processed_json_path = os.path.join(output_folder, f"{base_name}_processed.json")
        processed_sub_path = os.path.join(output_folder, f"{base_name}_processed.ass")

        subtitles_processor = SubtitlesTranslator(
            self.openai_client, 
            output_json_mixed, output_srt_mixed, 
            processed_json_path, processed_sub_path, 
            video_length=video_length,
            video_width=video_width,
            video_height=video_height,
            use_cache=use_translation_cache
        )
        subtitles_processor.process_subtitles()

        # Burn combined subtitles onto the video
        print("Burning subtitles...")
        subtitles_video_path = os.path.join(output_folder, f"{base_name}_subtitles.mp4")
        burn_subtitles(input_file, processed_sub_path, subtitles_video_path)

        # return


        # After fetching metadata
        print("Generating metadata with OpenAI...")
        # metadata = self.sub2meta.generate_video_metadata(output_srt_en, output_srt_zh)
        sub2meta = Subtitle2Metadata(
            self.openai_client,
            use_cache=use_metadata_cache
        )
        metadata = sub2meta.generate_video_metadata(
            output_srt_mixed, output_srt_caption
        )
        metadata["video_filename"] = f"{base_name}_highlighted.mp4"
        metadata["cover_filename"] = f"{base_name}_cover.jpg"

        pprint(metadata)

        # Save metadata to a JSON file
        metadata_json_path = os.path.join(output_folder, f"{base_name}_metadata.json")
        with open(metadata_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(metadata, json_file, indent=4, ensure_ascii=False)


        


        # # Highlight words to learn on the video
        # highlighted_video_path = os.path.join(output_folder, f"{base_name}_highlighted.mp4")
        # word_card_image_path = highlight_words(subtitles_video_path, metadata['english_words_to_learn'], highlighted_video_path)
       


        # Repeat the first few seconds of the video (e.g., 3 seconds)
        # repeat_sec = 3
        # repeat_sec = calculate_optimal_repeat_sec(output_json_mixed)
        # print("optimized repeat time:", repeat_sec)

        start_sec, end_sec = calculate_optimal_teaser_range(metadata_json_path, output_json_mixed, video_length)
        repeat_sec = end_sec - start_sec  # Calculate the duration to repeat
        print(f"Teaser range: {start_sec}s to {end_sec}s, repeating for {repeat_sec}s")
        
        # Step 1: Repeat the initial section of the video
        # repeated_video_path = os.path.join(output_folder, f"{base_name}_repeated.mp4")
        # repeat_start_of_video(subtitles_video_path, repeat_sec, repeated_video_path)

        teasered_video_path = os.path.join(output_folder, f"{base_name}_teasered.mp4")
        insert_video_segment_at_start(subtitles_video_path, start_sec, end_sec, teasered_video_path)


        # Step 2: Add the word card for the first word and update the words list
        video_with_word_card_path, updated_english_words_to_learn, word_card_image_path = add_first_word_card_to_video(teasered_video_path, metadata['english_words_to_learn'], output_folder, duration=repeat_sec)

        # Ensure word_card_image_path is used or saved as needed here

        # Step 3: Highlight the remaining words in the updated video
        highlighted_video_path = os.path.join(output_folder, f"{base_name}_highlighted.mp4")
        highlight_words_dummy(video_with_word_card_path, updated_english_words_to_learn, highlighted_video_path, delay=repeat_sec)

        # Additional operations involving word_card_image_path can be performed here


        # # Extract the cover image
        # print("Extracting cover...")
        # cover_image_path = os.path.join(output_folder, f"{base_name}_cover.jpg")
        # cover_plain_image_path = os.path.join(output_folder, f"{base_name}_cover_plain.jpg")
        # cover_timestamp, seconds = validate_timestamp(metadata['cover'].replace(',', '.'))  # Correct the timestamp format
        
        # if seconds > get_video_length(input_file) or seconds < 0:
        #     cover_timestamp = "00:00:01,000"

        # extract_cover(input_file, cover_plain_image_path, cover_timestamp.replace(",", "."))

        # Extract the cover image
        print("Extracting cover...")
        cover_image_path = os.path.join(output_folder, f"{base_name}_cover.jpg")
        cover_plain_image_path = os.path.join(output_folder, f"{base_name}_cover_plain.jpg")
        
        # Handle the cover timestamp from metadata (no .replace() needed now)
        cover_timestamp_raw = metadata['cover']
        cover_timestamp, seconds = validate_timestamp(cover_timestamp_raw)
        
        if seconds > get_video_length(input_file) or seconds < 0:
            cover_timestamp = "00:00:01,000"

        extract_cover(input_file, cover_plain_image_path, cover_timestamp.replace(",", "."))


        # overlay_word_card_on_cover(word_card_image_path, cover_plain_image_path, cover_image_path, transparency=0.5)
        if word_card_image_path and os.path.exists(word_card_image_path):
            overlay_word_card_on_cover(word_card_image_path, cover_plain_image_path, cover_image_path, transparency=1)
        else:
            # If we don't have a valid word card image, skip overlay
            # or copy the plain cover
            shutil.copy2(cover_plain_image_path, cover_image_path)
            print("Skipping overlay because `word_card_image_path` was None or didn't exist.")


        # Prepare the files to return by zipping them
        zip_file_path = os.path.join(output_folder, f"{base_name}.zip")
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(highlighted_video_path, os.path.basename(highlighted_video_path))
            zipf.write(output_json_mixed, os.path.basename(output_json_mixed))
            zipf.write(output_srt_mixed, os.path.basename(output_srt_mixed))

            zipf.write(cover_image_path, os.path.basename(cover_image_path))
            zipf.write(metadata_json_path, os.path.basename(metadata_json_path))  # Include the metadata JSON file

        print(f"Files are zipped and saved to {zip_file_path}.")
        
        # Read the zip file content
        with open(zip_file_path, 'rb') as f:
            zip_content = f.read()
        
        # Set the headers for file download
        # self.set_header('Content-Type', 'application/octet-stream')
        self.set_header("Content-Type", "application/octet-stream; charset=UTF-8")
        # self.set_header('Content-Disposition', 'attachment; filename=' + os.path.basename(zip_file_path))
        filename = os.path.basename(zip_file_path)
        ascii_filename = quote(filename)  # This function makes the filename safe for ASCII representation
        self.set_header('Content-Disposition', f'attachment; filename*=UTF-8\'\'{ascii_filename}')
        
        # Return the zip file
        self.write(zip_content)



def make_app(upload_folder):
    return tornado.web.Application([
        (r"/upload", FileUploaderHandler, dict(upload_folder=upload_folder)),
        (r"/upload-stream", FileUploadHandlerStream, dict(upload_folder=upload_folder)),
        (r"/video-processing", AutomaticalVideoEditingHandler),
        # Lightweight JSON APIs for the Expo app
        (r"/api/languages", LanguagesHandler),
        (r"/api/grammar-palettes/([A-Za-z0-9_-]+)", GrammarPaletteHandler),
        (r"/api/ui-settings/([A-Za-z0-9_-]+)", UISettingsHandler),
        (r"/api/video-specs", VideoSpecHandler),
        (r"/api/video-prompts", VideoPromptHandler),
        (r"/api/videos/generate", VideoGenerateHandler),
        (r"/api/videos", VideosHandler),
        (r"/api/videos/(\d+)", VideoDetailHandler),
        (r"/api/videos/(\d+)/proxy", VideoProxyHandler),
        (r"/api/videos/(\d+)/transcribe", VideoTranscribeHandler),
        (r"/api/videos/(\d+)/transcription", VideoTranscriptionHandler),
        (r"/api/videos/(\d+)/caption", VideoCaptionHandler),
        (r"/api/videos/(\d+)/metadata", VideoMetadataHandler),
        (r"/api/videos/(\d+)/cover", VideoCoverHandler),
        (r"/api/videos/(\d+)/keyframes", VideoKeyframesHandler),
        (r"/api/videos/(\d+)/translate", VideoTranslateHandler),
        (r"/api/videos/(\d+)/translation", VideoTranslationHandler),
        (r"/api/videos/(\d+)/translations", VideoTranslationsHandler),
        (r"/api/videos/(\d+)/burn-subtitles", VideoSubtitleBurnHandler),
        (r"/api/videos/(\d+)/process", VideoProcessHandler),
        (r"/api/videos/(\d+)/publish", VideoPublishHandler),
        (r"/api/videos/(\d+)/captions", CaptionsHandler),
        (r"/media/(.*)", MediaHandler, {"path": upload_folder}),
    ])

if __name__ == "__main__":
    # Set the OPENAI_MODEL environment variable
    # os.environ["OPENAI_MODEL"] = "gpt-4-0125-preview"
    os.environ["OPENAI_MODEL"] = "gpt-4o-mini"
    
    upload_folder = UPLOAD_FOLDER
    app = make_app(upload_folder)
    port = PORT
    app.listen(port, max_body_size=10*1024 * 1024 * 1024)
    print(f"LazyEdit backend listening on port {port}")
    tornado.autoreload.start()
    # tornado.autoreload.watch('path/to/config.yaml')
    # tornado.autoreload.watch('path/to/static/file.html')
    tornado.ioloop.IOLoop.current().start()
