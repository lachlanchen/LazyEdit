import subprocess
import cv2
import tempfile
import shutil
import os
import traceback
from PIL import Image, ImageDraw

class VideoAddWordsCard:
    def __init__(self, video_path, image_path, duration=3):
        self.video_path = video_path
        self.image_path = image_path
        self.output_dir = os.path.dirname(video_path)
        self.duration = duration
        self.width, self.height = self.get_video_info()

    def get_video_info(self):
        """Get video dimensions using OpenCV."""
        video = cv2.VideoCapture(self.video_path)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video.release()
        return width, height

    @property
    def is_video_landscape(self):
        """Check if the video is in landscape orientation."""
        return self.width > self.height

    def add_image_to_video(self):
        """
        Add an image overlay to the beginning of a video using direct FFmpeg command.
        This avoids using MoviePy's problematic write_videofile method.
        """
        # Create output file paths
        filename, file_extension = os.path.splitext(os.path.basename(self.video_path))
        final_output_path = os.path.join(self.output_dir, f"{filename}_with_words_card{file_extension}")
        first_frame_path = self.extract_first_frame(self.video_path)
        
        print(f"Adding word card overlay to: {self.video_path}")
        print(f"Output will be saved to: {final_output_path}")

        # Calculate image size and position
        if self.is_video_landscape:
            overlay_width = int(self.width * 0.7)
        else:
            overlay_width = self.width
            
        # Load and process the overlay image
        try:
            overlay_img = Image.open(self.image_path)
            img_width, img_height = overlay_img.size
            aspect_ratio = img_height / img_width
            overlay_height = int(overlay_width * aspect_ratio)
            
            # Create filter complex string for FFmpeg
            # This overlays the image for the specified duration with fade out
            overlay_filter = (
                f"[0:v]trim=duration={self.duration},"
                f"overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2:"
                f"overlay_w={overlay_width}:overlay_h={overlay_height}:"
                f"enable='between(t,0,{self.duration})',"
                f"fade=out:st={self.duration - 1}:d=1:alpha=1[v]"
            )
            
            # Create a temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a scaled version of the overlay image
                scaled_overlay_path = os.path.join(temp_dir, "scaled_overlay.png")
                scaled_overlay = overlay_img.resize((overlay_width, overlay_height), Image.LANCZOS)
                # Add alpha channel for transparency
                if scaled_overlay.mode != 'RGBA':
                    scaled_overlay = scaled_overlay.convert('RGBA')
                # Make the image semi-transparent (38% opacity)
                pixels = scaled_overlay.getdata()
                new_pixels = [(r, g, b, int(a * 0.38)) for r, g, b, a in pixels]
                scaled_overlay.putdata(new_pixels)
                scaled_overlay.save(scaled_overlay_path, format="PNG")
                
                # Simple FFmpeg command: overlay the image for the specified duration
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", self.video_path,  # Input video
                    "-i", scaled_overlay_path,  # Overlay image
                    "-filter_complex",
                    f"[0:v][1:v]overlay=x=(W-w)/2:y=(H-h)/2:enable='between(t,0,{self.duration})':alpha=0.38,fade=out:st={self.duration-1}:d=1:alpha=1",
                    "-c:a", "copy",  # Copy audio stream
                    "-c:v", "libx264",  # Use H.264 codec
                    "-preset", "medium",  # Balance speed and quality
                    "-crf", "23",  # Constant Rate Factor (quality)
                    final_output_path
                ]
                
                try:
                    # Execute FFmpeg command
                    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print(f"Successfully added word card overlay to video")
                except subprocess.CalledProcessError as e:
                    print(f"Error during FFmpeg processing: {e}")
                    print(f"FFmpeg stderr: {e.stderr.decode() if e.stderr else 'No error output'}")
                    traceback.print_exc()
                    
                    # If FFmpeg fails, try a simpler command without filters
                    try:
                        print("Trying simpler FFmpeg command...")
                        simpler_cmd = [
                            "ffmpeg", "-y",
                            "-i", self.video_path,
                            "-c:v", "libx264", "-c:a", "copy",
                            final_output_path
                        ]
                        subprocess.run(simpler_cmd, check=True)
                        print("Successfully processed video without overlay")
                    except subprocess.CalledProcessError:
                        # Last resort: just copy the original file
                        print("All FFmpeg approaches failed, copying original file")
                        shutil.copy2(self.video_path, final_output_path)
        
        except Exception as e:
            print(f"Error processing image overlay: {e}")
            traceback.print_exc()
            # Fallback: copy the original video
            shutil.copy2(self.video_path, final_output_path)
        
        return final_output_path, first_frame_path

    def extract_first_frame(self, video_path):
        """Extract the first frame of the video and save it as an image."""
        filename, file_extension = os.path.splitext(os.path.basename(video_path))
        first_frame_path = os.path.join(self.output_dir, f"{filename}_first_frame.jpg")
        
        try:
            video = cv2.VideoCapture(video_path)
            success, image = video.read()
            if success:
                cv2.imwrite(first_frame_path, image)
            video.release()
        except Exception as e:
            print(f"Error extracting first frame: {e}")
            traceback.print_exc()
        
        return first_frame_path


def overlay_word_card_on_cover(words_card_path, cover_path, output_path, transparency=0.5):
    """Overlay a word card image on a cover image with the specified transparency."""
    try:
        # Open the word card and the cover images
        words_card_img = Image.open(words_card_path).convert("RGBA")
        cover_img = Image.open(cover_path).convert("RGBA")

        # Calculate the scaling factor to maintain aspect ratio
        aspect_ratio_word_card = words_card_img.width / words_card_img.height
        aspect_ratio_cover = cover_img.width / cover_img.height

        if aspect_ratio_word_card > aspect_ratio_cover:
            # Fit to width
            new_width = cover_img.width
            new_height = int(new_width / aspect_ratio_word_card)
        else:
            # Fit to height
            new_height = int(0.7 * cover_img.height)
            new_width = int(new_height * aspect_ratio_word_card)

        # Resize word card image
        words_card_img_resized = words_card_img.resize((new_width, new_height), Image.LANCZOS)

        # Set transparency
        words_card_img_resized.putalpha(int(255 * transparency))

        # Calculate position to center the word card on the cover
        x_position = (cover_img.width - new_width) // 2
        y_position = (cover_img.height - new_height) // 2

        # Create a transparent image for compositing
        transparent_img = Image.new("RGBA", cover_img.size, (0, 0, 0, 0))
        
        # Paste the word card image onto the transparent image
        transparent_img.paste(words_card_img_resized, (x_position, y_position), words_card_img_resized)

        # Create a composite image
        combined_img = Image.alpha_composite(cover_img, transparent_img)

        # Save the result
        combined_img = combined_img.convert("RGB")  # Convert back to RGB to save as JPG or other formats
        combined_img.save(output_path, quality=100)
        
    except Exception as e:
        print(f"Error overlaying word card on cover: {e}")
        traceback.print_exc()
        # Fallback: copy the original cover
        shutil.copy2(cover_path, output_path)