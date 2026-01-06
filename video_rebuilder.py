#!/usr/bin/env python3
"""
Video Rebuilder - Completely reconstructs video by separating and rebuilding streams
Fixes Honor phone video issues by rebuilding from scratch
"""

import os
import subprocess
import sys
import tempfile
import shutil
import json
from pathlib import Path


class VideoRebuilder:
    def __init__(self, input_path, output_path=None):
        """
        Initialize the video rebuilder
        
        Args:
            input_path (str): Path to input video
            output_path (str): Path for output video (optional)
        """
        self.input_path = Path(input_path)
        if output_path:
            self.output_path = Path(output_path)
        else:
            self.output_path = self.input_path.parent / f"{self.input_path.stem}_rebuilt{self.input_path.suffix}"
        
        self.temp_dir = None
        self.video_info = None
        
    def analyze_streams(self):
        """Analyze input video streams"""
        print("🔍 Analyzing input video streams...")
        
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(self.input_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.video_info = json.loads(result.stdout)
            
            print("📊 Stream Analysis:")
            for i, stream in enumerate(self.video_info.get('streams', [])):
                codec_type = stream.get('codec_type')
                codec_name = stream.get('codec_name')
                
                if codec_type == 'video':
                    width = stream.get('width')
                    height = stream.get('height')
                    pix_fmt = stream.get('pix_fmt')
                    print(f"  Video Stream {i}: {codec_name} {width}x{height} {pix_fmt}")
                    
                    # Check for problematic color space
                    color_space = stream.get('color_space')
                    color_primaries = stream.get('color_primaries') 
                    color_trc = stream.get('color_trc')
                    print(f"    Color info: space={color_space}, primaries={color_primaries}, trc={color_trc}")
                    
                elif codec_type == 'audio':
                    sample_rate = stream.get('sample_rate')
                    channels = stream.get('channels')
                    print(f"  Audio Stream {i}: {codec_name} {sample_rate}Hz {channels}ch")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to analyze streams: {e}")
            return False
    
    def extract_raw_video(self, output_file):
        """Extract video stream and decode to raw format"""
        print("🎬 Extracting and decoding video stream...")
        
        # Use rawvideo to completely bypass any color space issues
        cmd = [
            'ffmpeg', '-y',
            '-i', str(self.input_path),
            '-map', '0:v:0',  # First video stream
            '-c:v', 'rawvideo',  # Decode to raw video
            '-pix_fmt', 'yuv420p',  # Force standard pixel format
            '-f', 'yuv4mpegpipe',  # Use Y4M format which includes frame info
            output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Raw video extracted to: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Raw video extraction failed: {e.stderr}")
            return False
    
    def extract_audio(self, output_file):
        """Extract audio stream"""
        print("🎵 Extracting audio stream...")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(self.input_path),
            '-map', '0:a:0',  # First audio stream
            '-c:a', 'copy',  # Copy audio as-is
            output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Audio extracted to: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Audio extraction failed: {e.stderr}")
            return False
    
    def encode_clean_video(self, raw_video_file, output_file):
        """Encode raw video with clean color space metadata"""
        print("🎨 Encoding video with clean color space...")
        
        # Get video dimensions from original
        video_streams = [s for s in self.video_info.get('streams', []) if s.get('codec_type') == 'video']
        if not video_streams:
            raise RuntimeError("No video streams found")
        
        video_stream = video_streams[0]
        width = video_stream.get('width')
        height = video_stream.get('height')
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'yuv4mpegpipe',
            '-i', raw_video_file,
            
            # Video encoding with explicit clean color space
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            
            # Force standard color space metadata
            '-colorspace', 'bt709',
            '-color_primaries', 'bt709',
            '-color_trc', 'bt709',
            '-color_range', 'tv',
            
            # Standard pixel format
            '-pix_fmt', 'yuv420p',
            
            # No rotation metadata
            '-metadata:s:v:0', 'rotate=0',
            
            # Output format
            '-f', 'mp4',
            output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Clean video encoded to: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Video encoding failed: {e.stderr}")
            return False
    
    def combine_streams(self, video_file, audio_file, output_file):
        """Combine video and audio streams"""
        print("🔗 Combining video and audio streams...")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_file,  # Clean video
            '-i', audio_file,  # Original audio
            
            # Copy both streams
            '-c:v', 'copy',
            '-c:a', 'copy',
            
            # Clean metadata
            '-map_metadata', '-1',  # Remove all metadata
            '-metadata', 'encoder=VideoRebuilder',
            
            # Fast start for web compatibility
            '-movflags', '+faststart',
            
            output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Streams combined to: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Stream combination failed: {e.stderr}")
            return False
    
    def rebuild_video(self):
        """Complete video rebuilding process"""
        print(f"🔧 Rebuilding video: {self.input_path}")
        print(f"📁 Output will be: {self.output_path}")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="video_rebuild_")
        
        try:
            # Step 1: Analyze streams
            if not self.analyze_streams():
                raise RuntimeError("Failed to analyze input streams")
            
            # Step 2: Extract raw video
            raw_video_file = os.path.join(self.temp_dir, "raw_video.y4m")
            if not self.extract_raw_video(raw_video_file):
                raise RuntimeError("Failed to extract raw video")
            
            # Step 3: Extract audio
            audio_file = os.path.join(self.temp_dir, "audio.aac")
            if not self.extract_audio(audio_file):
                raise RuntimeError("Failed to extract audio")
            
            # Step 4: Encode clean video
            clean_video_file = os.path.join(self.temp_dir, "clean_video.mp4")
            if not self.encode_clean_video(raw_video_file, clean_video_file):
                raise RuntimeError("Failed to encode clean video")
            
            # Step 5: Combine streams
            if not self.combine_streams(clean_video_file, audio_file, str(self.output_path)):
                raise RuntimeError("Failed to combine streams")
            
            print("🎉 Video rebuilding completed successfully!")
            return str(self.output_path)
            
        except Exception as e:
            print(f"❌ Rebuilding failed: {e}")
            raise
        finally:
            # Clean up temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print("🧹 Temporary files cleaned up")
    
    def verify_output(self):
        """Verify the rebuilt video"""
        print("✅ Verifying rebuilt video...")
        
        try:
            # Test with ffprobe
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,duration,pix_fmt,color_space,color_primaries,color_trc',
                '-of', 'json',
                str(self.output_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            if info.get('streams'):
                stream = info['streams'][0]
                print(f"📹 Rebuilt video info:")
                print(f"   Resolution: {stream.get('width')}x{stream.get('height')}")
                print(f"   Pixel format: {stream.get('pix_fmt')}")
                print(f"   Color space: {stream.get('color_space')}")
                print(f"   Color primaries: {stream.get('color_primaries')}")
                print(f"   Color TRC: {stream.get('color_trc')}")
                print(f"   Duration: {stream.get('duration')}s")
                
                # Test if it can be processed
                test_cmd = [
                    'ffmpeg', '-v', 'error',
                    '-i', str(self.output_path),
                    '-t', '1', '-f', 'null', '-'
                ]
                test_result = subprocess.run(test_cmd, capture_output=True, text=True, check=False)
                
                if test_result.returncode == 0:
                    print("✅ Video can be processed by FFmpeg without errors")
                    return True
                else:
                    print(f"⚠️ Video may still have issues: {test_result.stderr}")
                    return False
            else:
                print("❌ No video streams found in output")
                return False
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python video_rebuilder.py <input_video> [output_video]")
        print("Example: python video_rebuilder.py honor_video.mp4")
        print("Example: python video_rebuilder.py honor_video.mp4 rebuilt_video.mp4")
        sys.exit(1)
    
    input_video = sys.argv[1]
    output_video = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_video):
        print(f"❌ Input video not found: {input_video}")
        sys.exit(1)
    
    print("="*70)
    print("🔧 VIDEO REBUILDER - COMPLETE STREAM RECONSTRUCTION")
    print("="*70)
    
    try:
        rebuilder = VideoRebuilder(input_video, output_video)
        output_path = rebuilder.rebuild_video()
        
        if rebuilder.verify_output():
            print("\n" + "="*70)
            print("🎉 REBUILDING SUCCESSFUL")
            print("="*70)
            print(f"Input:  {input_video}")
            print(f"Output: {output_path}")
            print("\nThe rebuilt video should now work perfectly with your processing pipeline!")
        else:
            print("\n⚠️ Rebuilding completed but verification shows potential issues")
        
    except Exception as e:
        print(f"\n❌ Rebuilding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
