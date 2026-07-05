"""
Video utilities for lazyedit - wrapper functions for video preprocessing
"""

import os
import json
import subprocess
from pathlib import Path
from lazyedit.handbrake import preprocess_video


def _is_readable_video(path: Path) -> bool:
    """Fast sanity check for a reusable preprocessed video."""
    if not path.exists() or path.stat().st_size < 1000:
        return False
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration:stream=codec_type,codec_name",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=20,
        )
        payload = json.loads(result.stdout or "{}")
    except Exception:
        return False
    streams = payload.get("streams") if isinstance(payload, dict) else None
    if not isinstance(streams, list):
        return False
    if not any(stream.get("codec_type") == "video" for stream in streams):
        return False
    try:
        duration = float((payload.get("format") or {}).get("duration") or 0)
    except Exception:
        duration = 0
    return duration > 0


def ensure_video_compatibility(input_path: str, output_dir: str = None) -> str:
    """
    Ensure video is compatible with FFmpeg processing pipeline
    
    Args:
        input_path (str): Path to input video
        output_dir (str, optional): Directory for output. Defaults to same as input.
    
    Returns:
        str: Path to compatible video (original if no fixes needed, or fixed version)
    """
    input_path = Path(input_path)
    if input_path.stem.endswith("_compatible") and _is_readable_video(input_path):
        return str(input_path)
    
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = input_path.parent
    
    # Create output path in the specified directory
    output_path = output_dir / f"{input_path.stem}_compatible{input_path.suffix}"
    try:
        if (
            output_path.exists()
            and output_path.stat().st_mtime >= input_path.stat().st_mtime
            and _is_readable_video(output_path)
        ):
            print(f"✅ Reusing compatible video: {output_path}")
            return str(output_path)
    except Exception:
        pass
    
    try:
        # Use the handbrake preprocessor
        compatible_path, was_fixed = preprocess_video(str(input_path), str(output_path))
        
        return compatible_path
        
    except Exception as e:
        print(f"⚠️  Video preprocessing failed: {e}")
        print("   Continuing with original video...")
        return str(input_path)


def preprocess_if_needed(video_path: str) -> str:
    """
    Simple wrapper that preprocesses video only if needed
    
    Args:
        video_path (str): Path to video file
        
    Returns:
        str: Path to processed video (may be original if no processing needed)
    """
    return ensure_video_compatibility(video_path)
