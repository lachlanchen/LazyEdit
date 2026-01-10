"""
Video utilities for lazyedit - wrapper functions for video preprocessing
"""

import os
from pathlib import Path
from lazyedit.handbrake import preprocess_video


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
    
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = input_path.parent
    
    # Create output path in the specified directory
    output_path = output_dir / f"{input_path.stem}_compatible{input_path.suffix}"
    # output_path = output_dir / f"{input_path.stem}{input_path.suffix}"
    
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