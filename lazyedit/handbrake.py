#!/usr/bin/env python3
"""
HandBrake Video Preprocessor - Detects and fixes problematic videos
Can be used standalone or imported as lazyedit.handbrake module
"""

import os
import subprocess
import sys
import shutil
import tempfile
import json
from pathlib import Path
from typing import Tuple, Optional


class HandBrakePreprocessor:
    """
    Video preprocessor using HandBrake to fix problematic videos
    """
    
    # Common error patterns that indicate video needs fixing
    ERROR_PATTERNS = [
        'Invalid color space',
        'moov atom not found',
        'Invalid data found when processing input',
        'Error reinitializing filters',
        'Could not open encoder before EOF',
        'reserved/reserved/smpte170m',
        'yuvj420p(pc, reserved/reserved',
        'Format .* detected only with low score'
    ]
    
    def __init__(self, input_path: str, output_path: Optional[str] = None):
        """
        Initialize the preprocessor
        
        Args:
            input_path (str): Path to input video
            output_path (str, optional): Path for output video. If None, creates one with _fixed suffix
        """
        self.input_path = Path(input_path)
        
        if output_path:
            self.output_path = Path(output_path)
        else:
            # Create output path with _fixed suffix
            self.output_path = self.input_path.parent / f"{self.input_path.stem}_fixed{self.input_path.suffix}"
        
        self.needs_fixing = False
        self.detected_issues = []
    
    def check_handbrake_available(self) -> bool:
        """Check if HandBrake CLI is available"""
        try:
            result = subprocess.run(
                ['HandBrakeCLI', '--version'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def detect_video_issues(self) -> bool:
        """
        Detect if the video has issues that need fixing
        
        Returns:
            bool: True if issues detected, False if video is fine
        """
        print(f"🔍 Checking video for issues: {self.input_path.name}")
        
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input video not found: {self.input_path}")
        
        # Test 1: Try to get basic video info with ffprobe
        try:
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(self.input_path)
            ]
            result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
            video_info = json.loads(result.stdout)
            
            # Check for problematic color space in metadata
            video_streams = [s for s in video_info.get('streams', []) if s.get('codec_type') == 'video']
            for stream in video_streams:
                pix_fmt = stream.get('pix_fmt', '')
                color_space = stream.get('color_space', '')
                color_primaries = stream.get('color_primaries', '')
                
                # Check for problematic pixel formats
                if 'yuvj420p' in pix_fmt:
                    self.detected_issues.append("Problematic pixel format: yuvj420p")
                
                # Check for reserved/invalid color space
                if 'reserved' in str(color_space) or 'reserved' in str(color_primaries):
                    self.detected_issues.append("Invalid color space metadata")
                
                # Check for rotation metadata
                side_data = stream.get('side_data_list', [])
                for data in side_data:
                    if data.get('side_data_type') == 'Display Matrix':
                        self.detected_issues.append("Has display matrix rotation")
        
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self.detected_issues.append(f"ffprobe failed: {str(e)}")
        
        # Test 2: Try to process a small sample of the video
        test_issues = self._test_video_processing()
        self.detected_issues.extend(test_issues)
        
        # Test 3: Check if FFmpeg can read the file properly
        compatibility_issues = self._test_ffmpeg_compatibility()
        self.detected_issues.extend(compatibility_issues)
        
        self.needs_fixing = len(self.detected_issues) > 0
        
        if self.needs_fixing:
            print(f"⚠️  Issues detected:")
            for issue in self.detected_issues:
                print(f"   - {issue}")
        else:
            print("✅ Video appears to be compatible")
        
        return self.needs_fixing
    
    def _test_video_processing(self) -> list:
        """Test if video can be processed by trying basic operations"""
        issues = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_output = os.path.join(temp_dir, "test.jpg")
            
            # Test 1: Try to extract a frame
            extract_cmd = [
                'ffmpeg', '-v', 'error', '-y',
                '-i', str(self.input_path),
                '-ss', '1', '-frames:v', '1',
                test_output
            ]
            
            try:
                result = subprocess.run(extract_cmd, capture_output=True, text=True, check=False)
                
                # Check for specific error patterns
                for pattern in self.ERROR_PATTERNS:
                    if pattern in result.stderr:
                        issues.append(f"Frame extraction error: {pattern}")
                        break
                
                # Check if output was actually created
                if not os.path.exists(test_output) or os.path.getsize(test_output) < 1000:
                    issues.append("Failed to extract frame")
                    
            except Exception as e:
                issues.append(f"Frame extraction failed: {str(e)}")
        
        return issues
    
    def _test_ffmpeg_compatibility(self) -> list:
        """Test basic FFmpeg compatibility"""
        issues = []
        
        # Test: Try to read video with ffmpeg
        test_cmd = [
            'ffmpeg', '-v', 'error',
            '-i', str(self.input_path),
            '-t', '1', '-f', 'null', '-'
        ]
        
        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True, check=False)
            
            # Check for specific error patterns
            for pattern in self.ERROR_PATTERNS:
                if pattern in result.stderr:
                    issues.append(f"FFmpeg compatibility issue: {pattern}")
                    break
            
            if result.returncode != 0 and not issues:
                issues.append("FFmpeg cannot process video properly")
                
        except Exception as e:
            issues.append(f"FFmpeg test failed: {str(e)}")
        
        return issues
    
    def fix_video_with_handbrake(self) -> str:
        """
        Fix the video using HandBrake
        
        Returns:
            str: Path to fixed video
        """
        if not self.check_handbrake_available():
            raise RuntimeError("HandBrake CLI not available. Install with: sudo apt install handbrake-cli")
        
        print(f"🔧 Fixing video with HandBrake...")
        print(f"   Input: {self.input_path}")
        print(f"   Output: {self.output_path}")
        
        # HandBrake command optimized for compatibility
        handbrake_cmd = [
            'HandBrakeCLI',
            '-i', str(self.input_path),
            '-o', str(self.output_path),
            
            # Use a reliable preset
            '--preset', 'Fast 1080p30',
            
            # Video settings
            '--encoder', 'x264',
            '--quality', '23',  # Good quality
            '--vfr',  # Variable frame rate
            
            # Audio settings  
            '--aencoder', 'aac',
            '--ab', '192',  # 192kbps audio
            
            # Format settings
            '--format', 'av_mp4',
            '--optimize',  # Optimize for streaming
            
            # Compatibility settings
            '--loose-anamorphic',  # Handle aspect ratio issues
            '--color-matrix', 'bt709',  # Standard color matrix
        ]
        
        try:
            print("   Running HandBrake...")
            result = subprocess.run(
                handbrake_cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode != 0:
                # Try with simpler settings if first attempt fails
                print("   First attempt failed, trying simplified settings...")
                
                simple_cmd = [
                    'HandBrakeCLI',
                    '-i', str(self.input_path),
                    '-o', str(self.output_path),
                    '--preset', 'Very Fast 1080p30',
                    '--encoder', 'x264',
                    '--quality', '25'
                ]
                
                result = subprocess.run(simple_cmd, capture_output=True, text=True, check=True)
            
            # Verify output
            if not self.output_path.exists() or self.output_path.stat().st_size < 1000:
                raise RuntimeError("HandBrake produced no output or file too small")
            
            print(f"✅ Video fixed successfully")
            print(f"   Original size: {self.input_path.stat().st_size / 1024 / 1024:.1f} MB")
            print(f"   Fixed size: {self.output_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            return str(self.output_path)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("HandBrake processing timed out")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"HandBrake failed: {e.stderr}")
    
    def verify_fixed_video(self) -> bool:
        """
        Verify that the fixed video works properly
        
        Returns:
            bool: True if video is working, False otherwise
        """
        print("🧪 Verifying fixed video...")
        
        # Test 1: Check if ffprobe can read it
        try:
            probe_cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,duration',
                '-of', 'csv=p=0',
                str(self.output_path)
            ]
            result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
            if not result.stdout.strip():
                return False
        except subprocess.CalledProcessError:
            return False
        
        # Test 2: Check if ffmpeg can process it
        try:
            test_cmd = [
                'ffmpeg', '-v', 'error',
                '-i', str(self.output_path),
                '-t', '1', '-f', 'null', '-'
            ]
            result = subprocess.run(test_cmd, capture_output=True, text=True, check=False)
            
            # Check for error patterns
            for pattern in self.ERROR_PATTERNS:
                if pattern in result.stderr:
                    return False
            
            if result.returncode != 0:
                return False
                
        except Exception:
            return False
        
        print("✅ Fixed video verified successfully")
        return True
    
    def process_video(self) -> Tuple[str, bool]:
        """
        Main processing function - detects issues and fixes if needed
        
        Returns:
            Tuple[str, bool]: (output_path, was_fixed)
        """
        # Check if video needs fixing
        needs_fixing = self.detect_video_issues()
        
        if not needs_fixing:
            print("✅ Video is compatible, no processing needed")
            # Return original path if no issues
            return str(self.input_path), False
        
        # Fix the video
        fixed_path = self.fix_video_with_handbrake()
        
        # Verify the fix worked
        if not self.verify_fixed_video():
            print("⚠️  Warning: Fixed video may still have issues")
        
        return fixed_path, True


def preprocess_video(input_path: str, output_path: Optional[str] = None) -> Tuple[str, bool]:
    """
    Convenience function to preprocess a video
    
    Args:
        input_path (str): Path to input video
        output_path (str, optional): Path for output video
    
    Returns:
        Tuple[str, bool]: (output_path, was_fixed)
    """
    preprocessor = HandBrakePreprocessor(input_path, output_path)
    return preprocessor.process_video()


def main():
    """Main function for standalone usage"""
    if len(sys.argv) < 2:
        print("HandBrake Video Preprocessor")
        print("Usage: python handbrake_preprocessor.py <input_video> [output_video]")
        print()
        print("Examples:")
        print("  python handbrake_preprocessor.py video.mp4")
        print("  python handbrake_preprocessor.py video.mp4 fixed_video.mp4")
        print()
        print("This tool:")
        print("  - Detects problematic videos (color space, moov atom, rotation issues)")
        print("  - Only processes videos that need fixing")
        print("  - Uses HandBrake to create compatible videos")
        print("  - Returns original video if no issues detected")
        sys.exit(1)
    
    input_video = sys.argv[1]
    output_video = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_video):
        print(f"❌ Input video not found: {input_video}")
        sys.exit(1)
    
    print("🎬 HANDBRAKE VIDEO PREPROCESSOR")
    print("=" * 50)
    
    try:
        output_path, was_fixed = preprocess_video(input_video, output_video)
        
        print("\n" + "=" * 50)
        print("✅ PROCESSING COMPLETE")
        print("=" * 50)
        print(f"Input:  {input_video}")
        print(f"Output: {output_path}")
        
        if was_fixed:
            print("Status: Video was fixed and is now compatible")
        else:
            print("Status: Video was already compatible (no changes made)")
        
        print("\nThe output video is ready for your processing pipeline!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
