#!/usr/bin/env python3
"""
Simple Video Converter - Fixes Honor phone video issues
Handles invalid color space, rotation, and format problems
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path


def convert_video(input_path, output_path=None):
    """
    Convert problematic video to a compatible format
    
    Args:
        input_path (str): Path to input video
        output_path (str): Path for output video (optional)
    
    Returns:
        str: Path to converted video
    """
    input_path = Path(input_path)
    
    if output_path:
        output_path = Path(output_path)
    else:
        output_path = input_path.parent / f"{input_path.stem}_converted{input_path.suffix}"
    
    print(f"Converting: {input_path}")
    print(f"Output: {output_path}")
    
    # Strategy 1: Force input format and ignore metadata
    commands_to_try = [
        # Most aggressive approach - ignore all input metadata and force basic conversion
        [
            'ffmpeg', '-y',
            '-fflags', '+genpts+igndts',  # Generate PTS and ignore DTS
            '-ignore_unknown', '-i', str(input_path),
            '-map', '0:v:0', '-map', '0:a:0',  # Explicitly map first video and audio
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',  # Force standard pixel format
            '-vf', 'format=yuv420p',  # Force pixel format in filter
            '-avoid_negative_ts', 'make_zero',
            '-movflags', '+faststart',
            '-metadata:s:v:0', 'rotate=0',  # Remove rotation metadata
            str(output_path)
        ],
        
        # Second approach - use scale filter to force format conversion
        [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p',  # Ensure even dimensions and format
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-metadata:s:v:0', 'rotate=0',
            str(output_path)
        ],
        
        # Third approach - very basic conversion
        [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-pix_fmt', 'yuv420p',
            str(output_path)
        ],
        
        # Fourth approach - copy and remux only
        [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-c', 'copy',
            '-movflags', '+faststart',
            str(output_path)
        ]
    ]
    
    for i, cmd in enumerate(commands_to_try, 1):
        print(f"\nTrying method {i}/{len(commands_to_try)}...")
        print(f"Command: {' '.join(cmd)}")
        
        try:
            # Run the command
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False,
                timeout=300  # 5 minute timeout
            )
            
            # Check if output file was created and has reasonable size
            if (output_path.exists() and 
                output_path.stat().st_size > 1000):  # At least 1KB
                
                print(f"✓ Success with method {i}!")
                print(f"Output size: {output_path.stat().st_size / (1024*1024):.1f} MB")
                
                # Verify the output can be read by ffprobe
                try:
                    verify_cmd = [
                        'ffprobe', '-v', 'error',
                        '-select_streams', 'v:0',
                        '-show_entries', 'stream=width,height,duration',
                        '-of', 'csv=p=0',
                        str(output_path)
                    ]
                    verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, check=True)
                    if verify_result.stdout.strip():
                        print(f"✓ Verification successful: {verify_result.stdout.strip()}")
                        return str(output_path)
                    else:
                        print("⚠ Verification failed, trying next method...")
                        output_path.unlink()  # Delete failed output
                        continue
                        
                except subprocess.CalledProcessError:
                    print("⚠ Verification failed, trying next method...")
                    output_path.unlink()  # Delete failed output
                    continue
                    
            else:
                print(f"✗ Method {i} failed - no output or file too small")
                if output_path.exists():
                    output_path.unlink()
                continue
                
        except subprocess.TimeoutExpired:
            print(f"✗ Method {i} timed out")
            if output_path.exists():
                output_path.unlink()
            continue
        except Exception as e:
            print(f"✗ Method {i} failed with exception: {e}")
            if output_path.exists():
                output_path.unlink()
            continue
    
    # If all methods failed, raise an error
    raise RuntimeError("All conversion methods failed. The video file may be severely corrupted.")


def get_video_info(video_path):
    """Get basic video information"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        
        format_info = data.get('format', {})
        video_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'video']
        audio_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'audio']
        
        if video_streams:
            video = video_streams[0]
            print(f"Video: {video.get('codec_name')} {video.get('width')}x{video.get('height')} @ {video.get('avg_frame_rate')} fps")
            print(f"Pixel format: {video.get('pix_fmt')}")
            
            # Check for rotation
            rotation = video.get('tags', {}).get('rotate', '0')
            if rotation != '0':
                print(f"Rotation: {rotation}°")
            
            # Check for display matrix
            side_data = video.get('side_data_list', [])
            for data in side_data:
                if data.get('side_data_type') == 'Display Matrix':
                    print("Has display matrix rotation")
        
        if audio_streams:
            audio = audio_streams[0]
            print(f"Audio: {audio.get('codec_name')} {audio.get('sample_rate')}Hz {audio.get('channels')}ch")
        
        duration = format_info.get('duration', 'unknown')
        size = format_info.get('size', 'unknown')
        print(f"Duration: {duration}s, Size: {size} bytes")
        
    except Exception as e:
        print(f"Could not get video info: {e}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python simple_video_converter.py <input_video> [output_video]")
        print("Example: python simple_video_converter.py honor_video.mp4")
        print("Example: python simple_video_converter.py honor_video.mp4 fixed_video.mp4")
        sys.exit(1)
    
    input_video = sys.argv[1]
    output_video = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_video):
        print(f"❌ Input video not found: {input_video}")
        sys.exit(1)
    
    print("="*60)
    print("SIMPLE VIDEO CONVERTER")
    print("="*60)
    
    print("\n📹 Original video info:")
    get_video_info(input_video)
    
    try:
        print(f"\n🔄 Converting video...")
        output_path = convert_video(input_video, output_video)
        
        print(f"\n📹 Converted video info:")
        get_video_info(output_path)
        
        print("\n" + "="*60)
        print("✅ CONVERSION SUCCESSFUL")
        print("="*60)
        print(f"Input:  {input_video}")
        print(f"Output: {output_path}")
        print("\nThe converted video should now work with your processing pipeline!")
        
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()