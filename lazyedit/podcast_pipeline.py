#!/usr/bin/env python3

import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path
import time
from datetime import datetime

class PodcastVideoPipeline:
    def __init__(self, 
                 source_lang="Japanese", 
                 model="gpt-4o-mini",
                 threads=16,
                 teacher_model="lazyingart",
                 student_model="lazyingart", 
                 narrator_model="lazyingart",
                 device="cuda",
                 force_regenerate=False,
                 skip_audio=False,
                 skip_images=False,
                 skip_video=False):
        
        self.source_lang = source_lang
        self.model = model
        self.threads = threads
        self.teacher_model = teacher_model
        self.student_model = student_model
        self.narrator_model = narrator_model
        self.device = device
        self.force_regenerate = force_regenerate
        self.skip_audio = skip_audio
        self.skip_images = skip_images
        self.skip_video = skip_video
        
        # Create output podcast directory
        self.podcast_output_dir = Path("Podcast")
        self.podcast_output_dir.mkdir(exist_ok=True)
        
        # Track pipeline statistics
        self.stats = {
            'total_lines': 0,
            'processed_lines': 0,
            'skipped_conversations': 0,
            'skipped_audio': 0,
            'skipped_images': 0,
            'skipped_videos': 0,
            'generated_conversations': 0,
            'generated_audio': 0,
            'generated_images': 0,
            'generated_videos': 0,
            'copied_videos': 0,
            'failed_lines': []
        }

    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def is_txt_file(self, file_path):
        """Check if input is a txt file"""
        return Path(file_path).suffix.lower() == '.txt'

    def detect_input_type(self, input_path):
        """Detect input type and return processing information"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise Exception(f"Input file not found: {input_path}")
        
        if self.is_txt_file(input_path):
            return {
                'type': 'txt',
                'path': input_path,
                'base_dir': input_path.parent / f"{input_path.stem}_line_folders"
            }
        else:
            return {
                'type': 'json', 
                'path': input_path,
                'base_dir': self.find_clips_directory(input_path)
            }

    def find_clips_directory(self, json_path):
        """Find clips directory for JSON input"""
        json_path = Path(json_path)
        filename = json_path.stem
        parts = filename.split('_')
        
        lines_hash = None
        for part in reversed(parts):
            if len(part) == 8 and all(c in '0123456789abcdef' for c in part.lower()):
                lines_hash = part
                break
        
        if lines_hash:
            clips_dir = json_path.parent / f"selected_line_clips_{lines_hash}"
            if clips_dir.exists():
                return clips_dir
        
        return None

    def find_line_folders(self, input_info, indices=None):
        """Find all line folders to process"""
        line_folders = []
        
        if input_info['type'] == 'txt':
            base_dir = input_info['base_dir']
            if not base_dir.exists():
                self.log(f"Line folders directory not found: {base_dir}", "ERROR")
                return []
            
            # Find all folders matching pattern
            for folder in sorted(base_dir.iterdir()):
                if folder.is_dir() and folder.name.startswith(('001_', '002_', '003_')):
                    # Extract line number
                    try:
                        line_num = int(folder.name[:3])
                        if indices is None or line_num in indices:
                            line_folders.append({
                                'folder': folder,
                                'line_number': line_num,
                                'type': 'txt'
                            })
                    except ValueError:
                        continue
        else:
            base_dir = input_info['base_dir']
            if not base_dir or not base_dir.exists():
                self.log(f"Clips directory not found: {base_dir}", "ERROR")
                return []
            
            # Find all line folders in clips directory
            for folder in sorted(base_dir.iterdir()):
                if folder.is_dir() and folder.name.startswith(('001_', '002_', '003_')):
                    try:
                        line_num = int(folder.name[:3])
                        if indices is None or line_num in indices:
                            line_folders.append({
                                'folder': folder,
                                'line_number': line_num,
                                'type': 'json'
                            })
                    except ValueError:
                        continue
        
        return line_folders

    def check_conversation_exists(self, line_folder):
        """Check if podcast conversation already exists"""
        conversation_file = line_folder / "podcast_conversation_aligned.json"
        return conversation_file.exists()

    def check_audio_exists(self, line_folder):
        """Check if podcast audio already exists"""
        audio_files = list(line_folder.glob("podcast_*_sovits_*.mp3"))
        return len(audio_files) > 0

    def check_images_exist(self, line_folder):
        """Check if kawaii images already exist"""
        image_files = list(line_folder.glob("kawaii_*.png"))
        return len(image_files) >= 3  # At least 3 images expected

    def check_video_exists(self, line_folder):
        """Check if video podcast already exists"""
        video_files = list(line_folder.glob("*_sovits_video_podcast.mp4"))
        return len(video_files) > 0

    def run_command(self, cmd, description):
        """Run shell command with error handling"""
        self.log(f"Running: {description}")
        self.log(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.log(f"✅ {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"❌ {description} failed:", "ERROR")
            self.log(f"Exit code: {e.returncode}", "ERROR")
            self.log(f"STDOUT: {e.stdout}", "ERROR")
            self.log(f"STDERR: {e.stderr}", "ERROR")
            return False

    def step1_generate_conversations(self, input_info, indices=None):
        """Step 1: Generate podcast conversations"""
        self.log("=" * 60)
        self.log("STEP 1: Generating Podcast Conversations")
        self.log("=" * 60)
        
        if not self.force_regenerate:
            # Check if any line folders need conversation generation
            line_folders = self.find_line_folders(input_info, indices)
            needs_generation = False
            
            for line_info in line_folders:
                if not self.check_conversation_exists(line_info['folder']):
                    needs_generation = True
                    break
            
            if not needs_generation:
                self.log("All conversation files already exist, skipping generation")
                self.stats['skipped_conversations'] = len(line_folders)
                return True
        
        # Build command
        cmd = [
            "python", "generate_podcast_conversations_idx_lines_aligned_text.py",
            "--learning-lines", str(input_info['path']),
            "--source-lang", self.source_lang,
            "--model", self.model
        ]
        
        if indices:
            cmd.extend(["--indices", ",".join(map(str, indices))])
        
        if self.force_regenerate:
            cmd.append("--no-cache")
        
        success = self.run_command(cmd, "Podcast conversation generation")
        
        if success:
            line_folders = self.find_line_folders(input_info, indices)
            self.stats['generated_conversations'] = len(line_folders)
        
        return success

    def step2_generate_audio(self, input_info, indices=None):
        """Step 2: Generate podcast audio"""
        if self.skip_audio:
            self.log("Skipping audio generation (--skip-audio)")
            return True
        
        self.log("=" * 60)
        self.log("STEP 2: Generating Podcast Audio")
        self.log("=" * 60)
        
        line_folders = self.find_line_folders(input_info, indices)
        success_count = 0
        
        for line_info in line_folders:
            line_folder = line_info['folder']
            
            # Check if audio already exists
            if not self.force_regenerate and self.check_audio_exists(line_folder):
                self.log(f"Audio already exists for {line_folder.name}, skipping")
                self.stats['skipped_audio'] += 1
                success_count += 1
                continue
            
            # Check if conversation exists
            if not self.check_conversation_exists(line_folder):
                self.log(f"No conversation file found for {line_folder.name}, skipping audio", "WARNING")
                continue
            
            conversation_file = line_folder / "podcast_conversation_aligned.json"
            
            # Build command
            cmd = [
                "python", "generate_podcast_audio_sovits_aligned.py",
                "--json", str(conversation_file),
                "--threads", str(self.threads),
                "--teacher-model", self.teacher_model,
                "--student-model", self.student_model,
                "--narrator-model", self.narrator_model,
                "--no-play"
            ]
            
            if self.force_regenerate:
                cmd.append("--force")
            
            success = self.run_command(cmd, f"Audio generation for {line_folder.name}")
            
            if success:
                success_count += 1
                self.stats['generated_audio'] += 1
            else:
                self.stats['failed_lines'].append(f"{line_folder.name} (audio)")
        
        return success_count > 0

    def step3_generate_images(self, input_info, indices=None):
        """Step 3: Generate kawaii images"""
        if self.skip_images:
            self.log("Skipping image generation (--skip-images)")
            return True
        
        self.log("=" * 60)
        self.log("STEP 3: Generating Kawaii Images")
        self.log("=" * 60)
        
        line_folders = self.find_line_folders(input_info, indices)
        success_count = 0
        
        for line_info in line_folders:
            line_folder = line_info['folder']
            
            # Check if images already exist
            if not self.force_regenerate and self.check_images_exist(line_folder):
                self.log(f"Images already exist for {line_folder.name}, skipping")
                self.stats['skipped_images'] += 1
                success_count += 1
                continue
            
            # Check if conversation exists
            if not self.check_conversation_exists(line_folder):
                self.log(f"No conversation file found for {line_folder.name}, skipping images", "WARNING")
                continue
            
            # Build command
            cmd = [
                "python", "generate_anime_images_from_podcast_kawaii_text.py",
                str(line_folder),
                "--device", self.device
            ]
            
            if self.force_regenerate:
                cmd.append("--force")
            
            success = self.run_command(cmd, f"Image generation for {line_folder.name}")
            
            if success:
                success_count += 1
                self.stats['generated_images'] += 1
            else:
                self.stats['failed_lines'].append(f"{line_folder.name} (images)")
        
        return success_count > 0

    def step4_create_videos(self, input_info, indices=None):
        """Step 4: Create video podcasts"""
        if self.skip_video:
            self.log("Skipping video creation (--skip-video)")
            return True
        
        self.log("=" * 60)
        self.log("STEP 4: Creating Video Podcasts")
        self.log("=" * 60)
        
        line_folders = self.find_line_folders(input_info, indices)
        success_count = 0
        
        for line_info in line_folders:
            line_folder = line_info['folder']
            
            # Check if video already exists
            if not self.force_regenerate and self.check_video_exists(line_folder):
                self.log(f"Video already exists for {line_folder.name}, skipping")
                self.stats['skipped_videos'] += 1
                success_count += 1
                continue
            
            # Check prerequisites
            if not self.check_conversation_exists(line_folder):
                self.log(f"No conversation file found for {line_folder.name}, skipping video", "WARNING")
                continue
            
            if not self.skip_audio and not self.check_audio_exists(line_folder):
                self.log(f"No audio file found for {line_folder.name}, skipping video", "WARNING")
                continue
            
            if not self.skip_images and not self.check_images_exist(line_folder):
                self.log(f"No images found for {line_folder.name}, skipping video", "WARNING")
                continue
            
            # Build command
            cmd = [
                "python", "video_podcast_creator_sovits.py",
                "--folder", str(line_folder)
            ]
            
            success = self.run_command(cmd, f"Video creation for {line_folder.name}")
            
            if success:
                success_count += 1
                self.stats['generated_videos'] += 1
            else:
                self.stats['failed_lines'].append(f"{line_folder.name} (video)")
        
        return success_count > 0

    def step5_copy_videos(self, input_info, indices=None):
        """Step 5: Copy videos to Podcast directory"""
        self.log("=" * 60)
        self.log("STEP 5: Copying Videos to Podcast Directory")
        self.log("=" * 60)
        
        line_folders = self.find_line_folders(input_info, indices)
        copied_count = 0
        
        for line_info in line_folders:
            line_folder = line_info['folder']
            
            # Find video files
            video_files = list(line_folder.glob("*_sovits_video_podcast.mp4"))
            
            if not video_files:
                self.log(f"No video file found in {line_folder.name}, skipping copy", "WARNING")
                continue
            
            for video_file in video_files:
                # Create descriptive filename
                safe_name = "".join(c for c in line_folder.name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')[:100]  # Limit length
                
                output_name = f"podcast_{safe_name}.mp4"
                output_path = self.podcast_output_dir / output_name
                
                # Check if already exists
                if output_path.exists() and not self.force_regenerate:
                    self.log(f"Video already exists in Podcast directory: {output_name}, skipping")
                    continue
                
                try:
                    self.log(f"Copying {video_file.name} -> {output_name}")
                    shutil.copy2(video_file, output_path)
                    self.log(f"✅ Copied: {output_name}")
                    copied_count += 1
                    self.stats['copied_videos'] += 1
                except Exception as e:
                    self.log(f"❌ Failed to copy {video_file.name}: {e}", "ERROR")
                    self.stats['failed_lines'].append(f"{line_folder.name} (copy)")
        
        return copied_count > 0

    def print_final_summary(self):
        """Print comprehensive pipeline summary"""
        self.log("=" * 80)
        self.log("PODCAST VIDEO PIPELINE COMPLETE")
        self.log("=" * 80)
        
        print(f"📊 PIPELINE STATISTICS:")
        print(f"   Total lines processed: {self.stats['total_lines']}")
        print(f"   Successful completions: {self.stats['processed_lines']}")
        print(f"")
        print(f"📝 CONVERSATION GENERATION:")
        print(f"   Generated: {self.stats['generated_conversations']}")
        print(f"   Skipped (existing): {self.stats['skipped_conversations']}")
        print(f"")
        print(f"🎵 AUDIO GENERATION:")
        print(f"   Generated: {self.stats['generated_audio']}")
        print(f"   Skipped (existing): {self.stats['skipped_audio']}")
        print(f"")
        print(f"🎨 IMAGE GENERATION:")
        print(f"   Generated: {self.stats['generated_images']}")
        print(f"   Skipped (existing): {self.stats['skipped_images']}")
        print(f"")
        print(f"🎬 VIDEO CREATION:")
        print(f"   Generated: {self.stats['generated_videos']}")
        print(f"   Skipped (existing): {self.stats['skipped_videos']}")
        print(f"")
        print(f"📁 VIDEO COPYING:")
        print(f"   Copied to Podcast/: {self.stats['copied_videos']}")
        print(f"")
        print(f"📁 OUTPUT DIRECTORY: {self.podcast_output_dir}")
        
        if self.stats['failed_lines']:
            print(f"")
            print(f"❌ FAILED STEPS:")
            for failed in self.stats['failed_lines']:
                print(f"   {failed}")
        
        print(f"")
        self.log("Pipeline execution completed!")

    def run_pipeline(self, input_path, indices=None):
        """Run the complete pipeline"""
        start_time = time.time()
        
        self.log("🚀 Starting Podcast Video Pipeline")
        self.log(f"Input: {input_path}")
        self.log(f"Source Language: {self.source_lang}")
        self.log(f"Model: {self.model}")
        self.log(f"Device: {self.device}")
        self.log(f"Force Regenerate: {self.force_regenerate}")
        
        if indices:
            self.log(f"Processing specific indices: {indices}")
        else:
            self.log("Processing all available lines")
        
        try:
            # Detect input type
            input_info = self.detect_input_type(input_path)
            self.log(f"Input type: {input_info['type'].upper()}")
            
            # Count total lines
            line_folders = self.find_line_folders(input_info, indices)
            self.stats['total_lines'] = len(line_folders)
            self.log(f"Found {self.stats['total_lines']} lines to process")
            
            if self.stats['total_lines'] == 0:
                self.log("No lines found to process!", "ERROR")
                return False
            
            # Run pipeline steps
            success = True
            
            # Step 1: Generate conversations
            if not self.step1_generate_conversations(input_info, indices):
                self.log("Failed to generate conversations", "ERROR")
                success = False
            
            # Step 2: Generate audio
            if success and not self.step2_generate_audio(input_info, indices):
                self.log("Failed to generate audio", "ERROR")
                success = False
            
            # Step 3: Generate images
            if success and not self.step3_generate_images(input_info, indices):
                self.log("Failed to generate images", "ERROR")
                success = False
            
            # Step 4: Create videos
            if success and not self.step4_create_videos(input_info, indices):
                self.log("Failed to create videos", "ERROR")
                success = False
            
            # Step 5: Copy videos
            if success:
                self.step5_copy_videos(input_info, indices)
            
            # Update final stats
            if success:
                self.stats['processed_lines'] = self.stats['total_lines']
            
            # Print summary
            elapsed_time = time.time() - start_time
            self.log(f"Total execution time: {elapsed_time:.1f} seconds")
            self.print_final_summary()
            
            return success
            
        except Exception as e:
            self.log(f"Pipeline failed with error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


def parse_indices(indices_str):
    """Parse indices string into a list of integers"""
    if not indices_str:
        return None
    
    indices = []
    parts = indices_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(part))
    
    return sorted(list(set(indices)))


def main():
    parser = argparse.ArgumentParser(
        description="Complete Podcast Video Pipeline - From text/JSON to final videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process txt file (all lines)
  python podcast_pipeline.py DATA/Self-discovery/lines.txt

  # Process specific lines from txt file
  python podcast_pipeline.py DATA/Self-discovery/lines.txt --indices 1,2,3

  # Process JSON file with specific indices
  python podcast_pipeline.py DATA/Doraemon_396/learning_lines_hash.json --indices 1-5

  # Force regenerate everything
  python podcast_pipeline.py input.txt --force

  # Skip certain steps
  python podcast_pipeline.py input.txt --skip-audio --skip-images

Output:
  Final videos will be copied to: Podcast/
        """
    )
    
    parser.add_argument(
        "input_path",
        help="Input file path (TXT file with lines or JSON learning lines file)"
    )
    
    parser.add_argument(
        "--indices",
        type=str,
        help="Specific line indices to process (e.g., '1', '1,3,5', '1-5', '1,3-7,10'). Default: process all lines"
    )
    
    parser.add_argument(
        "--source-lang",
        default="Japanese",
        help="Source language of the learning lines (default: Japanese)"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    
    parser.add_argument(
        "--threads",
        type=int,
        default=16,
        help="Number of threads for audio generation (default: 16)"
    )
    
    parser.add_argument(
        "--teacher-model",
        default="lazyingart",
        help="SoVITS model for teacher voice (default: lazyingart)"
    )
    
    parser.add_argument(
        "--student-model", 
        default="lazyingart",
        help="SoVITS model for student voice (default: lazyingart)"
    )
    
    parser.add_argument(
        "--narrator-model",
        default="lazyingart", 
        help="SoVITS model for narrator voice (default: lazyingart)"
    )
    
    parser.add_argument(
        "--device",
        default="cuda",
        choices=["cuda", "mps", "cpu"],
        help="Device for image generation (default: cuda)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regenerate all steps even if outputs exist"
    )
    
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Skip audio generation step"
    )
    
    parser.add_argument(
        "--skip-images",
        action="store_true", 
        help="Skip image generation step"
    )
    
    parser.add_argument(
        "--skip-video",
        action="store_true",
        help="Skip video creation step"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without running the pipeline"
    )
    
    args = parser.parse_args()
    
    try:
        # Parse indices
        indices = parse_indices(args.indices) if args.indices else None
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - Analyzing input...")
            print("-" * 50)
            
            pipeline = PodcastVideoPipeline()
            input_info = pipeline.detect_input_type(args.input_path)
            line_folders = pipeline.find_line_folders(input_info, indices)
            
            print(f"📁 Input: {args.input_path}")
            print(f"📋 Type: {input_info['type'].upper()}")
            print(f"📊 Lines to process: {len(line_folders)}")
            
            if indices:
                print(f"🎯 Specific indices: {indices}")
            else:
                print(f"🎯 Processing: All available lines")
            
            print(f"🗣️ Source language: {args.source_lang}")
            print(f"🤖 Model: {args.model}")
            print(f"🧵 Threads: {args.threads}")
            print(f"🎭 Voice models: Teacher={args.teacher_model}, Student={args.student_model}, Narrator={args.narrator_model}")
            print(f"💻 Device: {args.device}")
            print(f"🔄 Force regenerate: {args.force}")
            
            if line_folders:
                print(f"\n📂 Folders to process:")
                for i, line_info in enumerate(line_folders, 1):
                    print(f"   {i}. {line_info['folder'].name}")
            
            print(f"\n📁 Final videos will be copied to: Podcast/")
            return 0
        
        # Create and run pipeline
        pipeline = PodcastVideoPipeline(
            source_lang=args.source_lang,
            model=args.model,
            threads=args.threads,
            teacher_model=args.teacher_model,
            student_model=args.student_model,
            narrator_model=args.narrator_model,
            device=args.device,
            force_regenerate=args.force,
            skip_audio=args.skip_audio,
            skip_images=args.skip_images,
            skip_video=args.skip_video
        )
        
        success = pipeline.run_pipeline(args.input_path, indices)
        
        if success:
            print("\n🎉 Pipeline completed successfully!")
            print(f"📁 Check the Podcast/ directory for your videos")
            return 0
        else:
            print("\n❌ Pipeline failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())