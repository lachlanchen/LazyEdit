#!/usr/bin/env python3
"""
Ultimate Video Fixer - Uses multiple tools and approaches to fix corrupted videos
Tries FFmpeg, OpenCV, MoviePy, HandBrake, and other methods
"""

import os
import subprocess
import sys
import tempfile
import shutil
import json
from pathlib import Path
import time


class UltimateVideoFixer:
    def __init__(self, input_path, output_path=None):
        self.input_path = Path(input_path)
        if output_path:
            self.output_path = Path(output_path)
        else:
            self.output_path = self.input_path.parent / f"{self.input_path.stem}_ultimate_fixed{self.input_path.suffix}"
        
        self.temp_dir = None
        
    def check_tools(self):
        """Check which tools are available"""
        tools = {
            'ffmpeg': self._check_command(['ffmpeg', '-version']),
            'handbrake': self._check_command(['HandBrakeCLI', '--version']),
            'vlc': self._check_command(['vlc', '--version']),
            'opencv': self._check_python_module('cv2'),
            'moviepy': self._check_python_module('moviepy.editor'),
            'imageio': self._check_python_module('imageio'),
        }
        
        print("🔧 Available tools:")
        for tool, available in tools.items():
            status = "✅" if available else "❌"
            print(f"  {status} {tool}")
        
        return tools
    
    def _check_command(self, cmd):
        """Check if a command is available"""
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return True
        except:
            return False
    
    def _check_python_module(self, module_name):
        """Check if a Python module is available"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def method_1_aggressive_ffmpeg(self):
        """Most aggressive FFmpeg approach"""
        print("\n🔥 Method 1: Ultra-aggressive FFmpeg")
        
        methods = [
            # Method 1a: Force input format and ignore all metadata
            [
                'ffmpeg', '-y',
                '-f', 'mov',  # Force input format
                '-fflags', '+genpts+igndts+ignore_editlist',
                '-ignore_unknown',
                '-err_detect', 'ignore_err',
                '-i', str(self.input_path),
                '-map', '0:v:0', '-map', '0:a:0',
                '-c:v', 'libx264', '-preset', 'ultrafast',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '192k',
                '-avoid_negative_ts', 'make_zero',
                '-fflags', '+genpts',
                str(self.output_path)
            ],
            
            # Method 1b: Use rawvideo input with forced format
            [
                'ffmpeg', '-y',
                '-f', 'h264',  # Force H264 input
                '-i', str(self.input_path),
                '-c:v', 'libx264', '-preset', 'ultrafast',
                '-pix_fmt', 'yuv420p',
                '-an',  # No audio for this attempt
                str(self.output_path).replace('.mp4', '_video_only.mp4')
            ],
            
            # Method 1c: Force color space on input
            [
                'ffmpeg', '-y',
                '-color_primaries', 'bt709',
                '-color_trc', 'bt709',
                '-colorspace', 'bt709',
                '-i', str(self.input_path),
                '-c:v', 'libx264', '-preset', 'ultrafast',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                str(self.output_path)
            ]
        ]
        
        for i, cmd in enumerate(methods, 1):
            print(f"  Trying FFmpeg method 1.{i}...")
            if self._try_command(cmd):
                return True
        
        return False
    
    def method_2_opencv(self):
        """Use OpenCV to rebuild video"""
        print("\n🐍 Method 2: OpenCV reconstruction")
        
        try:
            import cv2
            import numpy as np
            
            # Open video with OpenCV
            cap = cv2.VideoCapture(str(self.input_path))
            
            if not cap.isOpened():
                print("  ❌ OpenCV couldn't open the video")
                return False
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"  📹 Video: {width}x{height} @ {fps} fps, {total_frames} frames")
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            temp_video = os.path.join(self.temp_dir, 'opencv_video.mp4')
            out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
            
            # Process frames
            frame_count = 0
            print("  🎬 Processing frames...")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Write frame
                out.write(frame)
                frame_count += 1
                
                if frame_count % 100 == 0:
                    print(f"    Processed {frame_count}/{total_frames} frames")
            
            cap.release()
            out.release()
            
            print(f"  ✅ OpenCV processed {frame_count} frames")
            
            # Now add audio back with FFmpeg
            audio_add_cmd = [
                'ffmpeg', '-y',
                '-i', temp_video,
                '-i', str(self.input_path),
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v:0', '-map', '1:a:0',
                str(self.output_path)
            ]
            
            return self._try_command(audio_add_cmd)
            
        except ImportError:
            print("  ❌ OpenCV not available")
            return False
        except Exception as e:
            print(f"  ❌ OpenCV method failed: {e}")
            return False
    
    def method_3_moviepy(self):
        """Use MoviePy to rebuild video"""
        print("\n🎭 Method 3: MoviePy reconstruction")
        
        try:
            from moviepy.editor import VideoFileClip
            
            print("  📖 Loading video with MoviePy...")
            
            # Try to load with MoviePy
            clip = VideoFileClip(str(self.input_path))
            
            print(f"  📹 Video: {clip.w}x{clip.h} @ {clip.fps} fps, {clip.duration}s")
            
            # Write with MoviePy
            temp_output = str(self.output_path).replace('.mp4', '_moviepy.mp4')
            
            clip.write_videofile(
                temp_output,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=clip.fps
            )
            
            clip.close()
            
            # Move to final location
            shutil.move(temp_output, self.output_path)
            return True
            
        except ImportError:
            print("  ❌ MoviePy not available")
            return False
        except Exception as e:
            print(f"  ❌ MoviePy method failed: {e}")
            return False
    
    def method_4_handbrake(self):
        """Use HandBrake CLI"""
        print("\n🔨 Method 4: HandBrake CLI")
        
        cmd = [
            'HandBrakeCLI',
            '-i', str(self.input_path),
            '-o', str(self.output_path),
            '--preset', 'Fast 1080p30',
            '--encoder', 'x264',
            '--quality', '23',
            '--aencoder', 'aac',
            '--ab', '192'
        ]
        
        return self._try_command(cmd)
    
    def method_5_vlc(self):
        """Use VLC command line"""
        print("\n📺 Method 5: VLC command line")
        
        cmd = [
            'vlc',
            str(self.input_path),
            '--intf', 'dummy',
            '--sout', f'#transcode{{vcodec=h264,acodec=mp4a,ab=192,vb=800}}:std{{access=file,mux=mp4,dst={self.output_path}}}',
            '--sout-keep',
            'vlc://quit'
        ]
        
        return self._try_command(cmd)
    
    def method_6_frame_extraction(self):
        """Extract frames as images and rebuild"""
        print("\n🖼️ Method 6: Frame-by-frame extraction")
        
        frames_dir = os.path.join(self.temp_dir, 'frames')
        os.makedirs(frames_dir, exist_ok=True)
        
        # Extract frames as PNG (should work even with color space issues)
        extract_cmd = [
            'ffmpeg', '-y',
            '-i', str(self.input_path),
            '-vsync', '0',  # Don't duplicate frames
            '-q:v', '2',    # High quality
            '-start_number', '0',
            os.path.join(frames_dir, 'frame_%06d.png')
        ]
        
        print("  🎬 Extracting frames...")
        if not self._try_command(extract_cmd):
            return False
        
        # Count extracted frames
        frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
        print(f"  ✅ Extracted {len(frame_files)} frames")
        
        if len(frame_files) == 0:
            return False
        
        # Get video info for framerate
        try:
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', '-select_streams', 'v:0',
                str(self.input_path)
            ]
            result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            fps = 30  # Default
            if info['streams']:
                fps_str = info['streams'][0].get('avg_frame_rate', '30/1')
                if '/' in fps_str:
                    num, den = fps_str.split('/')
                    fps = float(num) / float(den)
        except:
            fps = 30
        
        # Rebuild video from frames
        rebuild_cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', os.path.join(frames_dir, 'frame_%06d.png'),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            os.path.join(self.temp_dir, 'video_from_frames.mp4')
        ]
        
        print("  🔨 Rebuilding video from frames...")
        if not self._try_command(rebuild_cmd):
            return False
        
        # Extract and add audio
        audio_extract_cmd = [
            'ffmpeg', '-y',
            '-i', str(self.input_path),
            '-vn', '-acodec', 'copy',
            os.path.join(self.temp_dir, 'audio.aac')
        ]
        
        if self._try_command(audio_extract_cmd):
            # Combine video and audio
            combine_cmd = [
                'ffmpeg', '-y',
                '-i', os.path.join(self.temp_dir, 'video_from_frames.mp4'),
                '-i', os.path.join(self.temp_dir, 'audio.aac'),
                '-c', 'copy',
                str(self.output_path)
            ]
            return self._try_command(combine_cmd)
        else:
            # Just use video without audio
            shutil.move(os.path.join(self.temp_dir, 'video_from_frames.mp4'), self.output_path)
            return True
    
    def _try_command(self, cmd):
        """Try running a command"""
        try:
            print(f"    Running: {' '.join(cmd[:3])}...")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0 and self.output_path.exists() and self.output_path.stat().st_size > 1000:
                print(f"    ✅ Success!")
                return True
            else:
                if result.stderr:
                    print(f"    ❌ Failed: {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"    ❌ Timeout")
            return False
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return False
    
    def fix_video(self):
        """Try all methods to fix the video"""
        print(f"🚀 Starting ultimate video fixing process")
        print(f"Input: {self.input_path}")
        print(f"Output: {self.output_path}")
        
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp(prefix="ultimate_fix_")
        
        try:
            # Check available tools
            available_tools = self.check_tools()
            
            # Try all methods in order of likelihood to succeed
            methods = [
                ('method_1_aggressive_ffmpeg', 'FFmpeg aggressive'),
                ('method_6_frame_extraction', 'Frame extraction'),
                ('method_2_opencv', 'OpenCV'),
                ('method_3_moviepy', 'MoviePy'),
                ('method_4_handbrake', 'HandBrake'),
                ('method_5_vlc', 'VLC'),
            ]
            
            for method_name, description in methods:
                print(f"\n{'='*50}")
                print(f"Trying: {description}")
                print('='*50)
                
                try:
                    method = getattr(self, method_name)
                    if method():
                        print(f"\n🎉 SUCCESS with {description}!")
                        return str(self.output_path)
                    else:
                        print(f"❌ {description} failed")
                        # Clean up failed output
                        if self.output_path.exists():
                            self.output_path.unlink()
                except Exception as e:
                    print(f"❌ {description} crashed: {e}")
                    if self.output_path.exists():
                        self.output_path.unlink()
            
            raise RuntimeError("All methods failed to fix the video")
            
        finally:
            # Clean up
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)


def install_missing_tools():
    """Suggest installation commands for missing tools"""
    print("\n📦 To install missing tools:")
    print("  OpenCV: pip install opencv-python")
    print("  MoviePy: pip install moviepy")
    print("  HandBrake: sudo apt install handbrake-cli  # Ubuntu/Debian")
    print("  VLC: sudo apt install vlc  # Ubuntu/Debian")


def main():
    if len(sys.argv) < 2:
        print("Usage: python ultimate_video_fixer.py <input_video> [output_video]")
        sys.exit(1)
    
    input_video = sys.argv[1]
    output_video = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_video):
        print(f"❌ Input video not found: {input_video}")
        sys.exit(1)
    
    print("🔧 ULTIMATE VIDEO FIXER")
    print("=" * 50)
    
    try:
        fixer = UltimateVideoFixer(input_video, output_video)
        output_path = fixer.fix_video()
        
        print(f"\n🎉 VIDEO SUCCESSFULLY FIXED!")
        print(f"Output: {output_path}")
        
        # Test the output
        print(f"\n🧪 Testing fixed video...")
        test_cmd = [
            'ffmpeg', '-v', 'error', '-i', output_path,
            '-t', '1', '-f', 'null', '-'
        ]
        
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Fixed video passes FFmpeg test!")
        else:
            print(f"⚠️ Warning: {result.stderr}")
        
    except Exception as e:
        print(f"\n❌ All methods failed: {e}")
        install_missing_tools()
        sys.exit(1)


if __name__ == "__main__":
    main()
