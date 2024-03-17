import subprocess
import cv2
import tempfile
import shutil
import os
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

from PIL import Image

def overlay_word_card_on_cover(words_card_path, cover_path, output_path, transparency=0.9):
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
        new_height = cover_img.height
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

class VideoAddWordsCard:
    def __init__(self, video_path, image_path, duration=3):
        self.video_path = video_path
        self.image_path = image_path
        self.output_dir = os.path.dirname(video_path)
        self.duration = duration

    def get_video_info(self):
        video = cv2.VideoCapture(self.video_path)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video.release()
        return width, height

    def correct_video_metadata(self, correct_width, correct_height, tmp_folder):
        filename, file_extension = os.path.splitext(os.path.basename(self.video_path))
        corrected_video_path = os.path.join(tmp_folder, f"corrected_{filename}{file_extension}")
        cmd = f"ffmpeg -y -i \"{self.video_path}\" -vf scale={correct_width}:{correct_height} -c:a copy \"{corrected_video_path}\""
        subprocess.call(cmd, shell=True)
        return corrected_video_path

    def add_image_to_video(self):
        with tempfile.TemporaryDirectory() as tmp_folder:
            video_width, video_height = self.get_video_info()
            corrected_video_path = self.correct_video_metadata(video_width, video_height, tmp_folder)
            video_clip = VideoFileClip(corrected_video_path)

            image_clip = ImageClip(self.image_path).set_duration(min(self.duration, video_clip.duration))
            aspect_ratio_image = image_clip.h / image_clip.w
            new_width = video_width
            new_height = int(new_width * aspect_ratio_image)
            image_clip = image_clip.resize(newsize=(new_width, new_height)).set_position(("center", "center")).set_opacity(0.68).fadeout(1)

            final_video = CompositeVideoClip([video_clip, image_clip.set_start(0)], size=(video_width, video_height))
            filename, file_extension = os.path.splitext(os.path.basename(self.video_path))
            output_video_path = os.path.join(tmp_folder, f"{filename}_with_image{file_extension}")
            final_video.write_videofile(output_video_path, audio=False, verbose=False, logger=None, codec='libx264', ffmpeg_params=["-movflags", "+faststart"])

            temp_audio_path = os.path.join(tmp_folder, 'temp_audio.mp3')
            final_output_path = os.path.join(self.output_dir, f"{filename}_with_words_card{file_extension}")
            self.add_audio_to_video(output_video_path, temp_audio_path, final_output_path)

            first_frame_path = self.extract_first_frame(self.video_path)
            return final_output_path, first_frame_path

    def add_audio_to_video(self, processed_video_path, temp_audio_path, final_output_path):
        extract_audio_cmd = f"ffmpeg -y -i \"{self.video_path}\" -q:a 0 -map a \"{temp_audio_path}\""
        subprocess.call(extract_audio_cmd, shell=True)
        add_audio_cmd = f"ffmpeg -y -i \"{processed_video_path}\" -i \"{temp_audio_path}\" -c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0 \"{final_output_path}\""
        subprocess.call(add_audio_cmd, shell=True)

    def extract_first_frame(self, video_path):
        filename, file_extension = os.path.splitext(os.path.basename(video_path))
        first_frame_path = os.path.join(self.output_dir, f"{filename}_first_frame.jpg")
        video = cv2.VideoCapture(video_path)
        success, image = video.read()
        if success:
            cv2.imwrite(first_frame_path, image)
        video.release()
        return first_frame_path
