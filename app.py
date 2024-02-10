import os



from autopub_video_processing.openai_version_check import OpenAI



import shlex
import subprocess

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import tornado.ioloop
import tornado.web
from tornado import gen
import tornado.autoreload


import zipfile  # for creating zip files

from autopub_video_processing.autocut_processor import AutocutProcessor

from autopub_video_processing.subtitle_to_metadata import Subtitle2Metadata
from autopub_video_processing.words_card import VideoAddWordsCard, overlay_word_card_on_cover
from autopub_video_processing.subtitle_translate import SubtitlesTranslator

from pprint import pprint
import json5
import json

import subprocess
from urllib.parse import quote

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




def get_seconds(timestamp):
    print("timestamp: ", timestamp)
    # Split by ';' and take the last timestamp (if multiple timestamps are present)
    last_timestamp = timestamp.split(';')[0].strip()
    # Convert HH:MM:SS,mmm to HH:MM:SS.mmm and then to seconds
    h, m, s = last_timestamp.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)




def extract_cover(video_path, image_path, time):
    # Replace comma with dot for milliseconds
    time = time.replace(',', '.')
    ffmpeg_command = f"ffmpeg -y -ss {time} -i \"{video_path}\" -frames:v 1 \"{image_path}\""
    subprocess.run(ffmpeg_command, shell=True, check=True)



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

def get_time_range(time_range):
    timestamps = time_range.split(' --> ')
    if len(timestamps) == 2:
        start_timestamp, end_timestamp = timestamps
    elif len(timestamps) == 1:
        # If there's only one timestamp, use it as the start and add 1 second for the end
        start_timestamp = timestamps[0]
        end_timestamp = format_timestamp(get_seconds_from_timestamp(start_timestamp) + 1)
    else:
        # Handle unexpected format by setting both start and end to 0
        start_timestamp, end_timestamp = '00:00:00,000', '00:00:00,000'

    start_seconds = get_seconds_from_timestamp(start_timestamp)
    end_seconds = get_seconds_from_timestamp(end_timestamp)
    
    # Add 1 second to end_timestamp if there's an error in parsing either timestamp
    if start_seconds == 0 or end_seconds == 0:
        end_seconds = start_seconds + 1
        end_timestamp = format_timestamp(end_seconds)

    return start_seconds, end_seconds







def get_video_length(video_path):
    # Get the length of the video using ffprobe
    command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{video_path}\""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

def get_video_resolution(video_path):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height

def find_font_size(text, font_path, max_width, max_height, start_size=120, step=2):
    font_size = start_size
    font = ImageFont.truetype(font_path, font_size)
    while True:
        text_width, text_height = get_text_size(text, font, max_width, max_height)
        if text_width <= max_width and text_height <= max_height:
            break
        font_size -= step
        if font_size <= 0:
            break
        font = ImageFont.truetype(font_path, font_size)
    return font_size

def get_text_size(text, font, max_width, max_height):
    test_canvas_size = (int(max_width), int(max_height))  # Canvas size based on max_width and max_height
    dummy_image = Image.new('RGB', test_canvas_size)
    draw = ImageDraw.Draw(dummy_image)
    return draw.textbbox((0, 0), text, font=font)[2:]



def repeat_start_of_video(video_path, repeat_sec, output_path):
    repeat_command = [
        "ffmpeg", "-y", "-i", video_path, "-filter_complex",
        f"[0:v]trim=0:{repeat_sec},setpts=PTS-STARTPTS[first3v];[0:a]atrim=0:{repeat_sec},asetpts=PTS-STARTPTS[first3a];"
        f"[first3v][0:v]concat=n=2:v=1:a=0[finalv];[first3a][0:a]concat=n=2:v=0:a=1[finala]",
        "-map", "[finalv]", "-map", "[finala]", output_path
    ]
    subprocess.run(repeat_command, check=True)

def get_word_card_image(word, output_folder):
    # URL of the API
    url = 'http://lazyingart:8082/get_words_card'
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


def add_first_word_card_to_video(video_path, words_to_learn, output_folder):
    if not words_to_learn:
        print("No words to learn provided.")
        return video_path, words_to_learn, None  # No word card to add

    first_word_info = words_to_learn[0]
    words_to_learn = words_to_learn[1:]  # Exclude the first word for further processing

    word_card_image_path = get_word_card_image(first_word_info["word"], output_folder)
    if word_card_image_path:
        video_add_words_card = VideoAddWordsCard(video_path, word_card_image_path)
        video_with_first_word_card_path, _ = video_add_words_card.add_image_to_video()
        return video_with_first_word_card_path, words_to_learn, word_card_image_path
    else:
        print(f"Failed to obtain word card for '{first_word_info['word']}'. Proceeding without adding word card.")
        return video_path, words_to_learn, None




def highlight_words(video_path, words_to_learn, output_path, delay=3):
    # Get the length of the video
    video_length = get_video_length(video_path)
    video_width, video_height = get_video_resolution(video_path)

    # Sort words_to_learn by start time
    words_to_learn.sort(key=lambda x: get_time_range(x['time_stamps'])[0])

    # Initialize variables
    temp_output_path = output_path + ".temp.mp4"
    final_output_path = output_path
    current_input_path = video_path
    successful = False
    last_end_time = delay  # Initialize last end time with the optional delay parameter

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    # Process each word
    for i, word_info in enumerate(words_to_learn):
        try:
            # Get time range
            start_seconds, end_seconds = get_time_range(word_info['time_stamps'])

            # Ignore words that start beyond the video length or before the last end time
            if start_seconds >= video_length or start_seconds < last_end_time:
                continue

            # Ensure end time is at least 1 second after the start time and does not exceed video length
            end_seconds = min(max(end_seconds, start_seconds + 1), video_length)

            # Update last end time for the next iteration
            last_end_time = end_seconds

            word_text = word_info['word']
            font_size = find_font_size(word_text, font_path, video_width * 0.8, video_height * 0.8)

            drawtext_filter = (
                f"drawtext=text='{word_text}':"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"fontsize={font_size}:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:"
                f"enable='between(t,{start_seconds},{end_seconds})'"
            )

            command = (
                f"ffmpeg -y -i \"{current_input_path}\" -vf \"{drawtext_filter}\" "
                f"-c:a copy \"{temp_output_path}\""
            )

            subprocess.run(command, shell=True, check=True)

            # Prepare for next iteration
            if i < len(words_to_learn) - 1 or current_input_path != final_output_path:
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
            # If os.link fails, consider using shutil.copy as a fallback
            # import shutil
            # shutil.copy(video_path, output_path)

    return None  # Since word_card_image_path logic was removed



# def highlight_words(video_path, words_to_learn, output_path):
#     # Get the length of the video
#     video_length = get_video_length(video_path)
#     video_width, video_height = get_video_resolution(video_path)

#     # Sort words_to_learn by start time
#     first_word_info = words_to_learn[0]
#     words_to_learn = words_to_learn[1:]
#     words_to_learn.sort(key=lambda x: get_time_range(x['time_stamps'])[0])

#     # Initialize variables
#     temp_output_path = output_path + ".temp.mp4"
#     final_output_path = output_path
#     current_input_path = video_path
#     successful = False
#     last_end_time = 3  # Initialize last end time

#     word_card_image_path = None
#     # Fetch the image for the first word and add to video
#     if words_to_learn:
        
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
#     for i, word_info in enumerate(words_to_learn):
#         try:
#             # Get time range
#             start_seconds, end_seconds = get_time_range(word_info['time_stamps'])

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
#             if i < len(words_to_learn) - 1:
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

def process_subtitles(video_file, input_subtitle_file, output_subtitle_file, max_width):
    video_width, video_height = get_video_dimensions(video_file)
    is_landscape = video_width > video_height

    # if portrait
    if not is_landscape:
        max_width = int(max_width * 0.4)

    with open(input_subtitle_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_subtitle_file, 'w', encoding='utf-8') as f:
        for line in lines:
            if '-->' in line:
                f.write(line)
            else:
                is_cjk = any('\u4e00' <= char <= '\u9fff' for char in line)
                wrapped_lines = wrap_text(line, max_width, is_cjk=is_cjk)
                for wrapped_line in wrapped_lines:
                    f.write(wrapped_line + '\n')

def burn_subtitles(video_path, srt_path, output_path):
    # Determine the name for the processed subtitles
    wrapped_srt_path = srt_path.rsplit('.', 1)[0] + '_wrapped.srt'
    
    # Adjust 'max_width' as needed
    max_width = 50  # You may want to dynamically set this based on the video dimensions
    process_subtitles(video_path, srt_path, wrapped_srt_path, max_width)
    
    # Construct the FFmpeg command to burn the processed subtitles
    command = f"ffmpeg -y -i \"{video_path}\" -vf \"subtitles={wrapped_srt_path}\" \"{output_path}\""
    subprocess.run(command, shell=True, check=True)

def validate_timestamp(timestamp):
    try:
        # Split the timestamp and check if it has the correct format
        h, m, s = timestamp.split(':')
        s, ms = s.split('.')
        # Convert to integers to check if they are within the correct range
        h, m, s, ms = int(h), int(m), int(s), int(ms)
        # Check if hours, minutes, seconds, and milliseconds are in the correct range
        if h >= 0 and m >= 0 and m < 60 and s >= 0 and s < 60 and ms >= 0 and ms < 1000:
            return timestamp  # The timestamp is valid
    except ValueError:
        # Catch ValueError if the timestamp is not in the correct format
        print("Format unrecognized for timestamp of cover: ", timestamp)
        pass
    # Return the default value if the timestamp is not valid
    return '00:00:00,000'

class FileUploaderHandler(tornado.web.RequestHandler):
    def initialize(self, upload_folder):
        self.upload_folder = upload_folder

    @gen.coroutine
    def post(self):
        # Extract video file from the request
        video_file = self.request.files['video'][0]
        original_fname = video_file['filename']
        print("Filename: ", original_fname)

        # Determine the basename (without extension) and create a subfolder
        base_name, _ = os.path.splitext(original_fname)
        output_folder = os.path.join(self.upload_folder, base_name)
        os.makedirs(output_folder, exist_ok=True)

        # Define the full path for the incoming video
        input_file = os.path.join(output_folder, original_fname)

        # Write the incoming video to the file system
        with open(input_file, 'wb') as f:
            f.write(video_file['body'])

        # Respond with the path of the saved file
        self.write({
            'status': 'success',
            'message': f'File {original_fname} uploaded successfully.',
            'file_path': input_file
        })


@tornado.web.stream_request_body
class FileUploadHandlerStream(tornado.web.RequestHandler):
    def initialize(self, upload_folder):
        self.bytes_received = 0
        self.file = None
        self.file_path = None
        self.upload_folder = upload_folder

    def prepare(self):
        filename = self.get_argument('filename', default='uploaded_file')
        base_name, _ = os.path.splitext(filename)
        output_folder = os.path.join(self.upload_folder, base_name)
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
            response = {
                'status': 'success',
                'message': f"Received {self.bytes_received} bytes.",
                'file_path': self.file_path
            }
            self.write(response)



class VideoProcessingHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=2)

    def initialize(self):
        self.openai_client = OpenAI()  # Make sure to authenticate your OpenAI client
        self.sub2meta = Subtitle2Metadata(self.openai_client)

    def run_autocut(self, autocut_command, lang, gpu_id):
        # Set the CUDA_VISIBLE_DEVICES environment variable
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)

        # Run the autocut command with the specified environment
        subprocess.run(autocut_command, shell=True, check=True, env=env)
        print(f"Finished autocut with lang={lang} on GPU {gpu_id}")

    def process_video(self, input_file, base_name, extension, output_folder):
        # Process the video with autocut
        autocut_processor = AutocutProcessor(input_file, output_folder, base_name, extension)
        futures = [
            self.executor.submit(autocut_processor.run_autocut, 'mixed', 0),
            # self.executor.submit(autocut_processor.run_autocut, 'en', 0),
            # self.executor.submit(autocut_processor.run_autocut, 'zh', 1)
        ]
        for future in as_completed(futures):
            result = future.result()
            print(f"Task completed with result: {result}")


    @gen.coroutine
    def post(self):
        
        input_file = self.get_argument('file_path', None)
        if not input_file or not os.path.exists(input_file):
            self.set_status(400)
            self.write({'status': 'error', 'message': 'File path is invalid or file does not exist'})
            return

        print("Processing File: ", input_file)
        base_name, extension = os.path.splitext(os.path.basename(input_file))
        output_folder = os.path.dirname(input_file)

        self.process_video(input_file, base_name, extension, output_folder)
        

        output_json_mixed = f"{output_folder}/{base_name}_mixed.json"
        output_srt_mixed = f"{output_folder}/{base_name}_mixed.srt"
        

        # Check if files exist before reading
        # for file_path in [output_md_en, output_srt_en, output_md_zh, output_srt_zh]:
        for file_path in [output_json_mixed, output_srt_mixed]:
            if not os.path.exists(file_path):
                self.set_status(500)
                self.write(f"Error: Expected output file not found: {file_path}")
                return



        # Merge subtitles
        print("Merging/Translating subtitles...")
        combined_srt_path = os.path.join(output_folder, f"{base_name}_combined.srt")

        subtitles_processor = SubtitlesTranslator(self.openai_client, output_json_mixed, output_srt_mixed, combined_srt_path)
        subtitles_processor.process_subtitles()


        # After fetching metadata
        print("Generating metadata with OpenAI...")
        # metadata = self.sub2meta.generate_video_metadata(output_srt_en, output_srt_zh)
        metadata = self.sub2meta.generate_video_metadata(output_srt_mixed)
        metadata["video_filename"] = f"{base_name}_highlighted.mp4"
        metadata["cover_filename"] = f"{base_name}_cover.jpg"

        pprint(metadata)

        # Save metadata to a JSON file
        metadata_json_path = os.path.join(output_folder, f"{base_name}_metadata.json")
        with open(metadata_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(metadata, json_file, indent=4, ensure_ascii=False)


        # Burn combined subtitles onto the video
        print("Burning subtitles...")
        final_video_path = os.path.join(output_folder, f"{base_name}_final.mp4")
        burn_subtitles(input_file, combined_srt_path, final_video_path)


        # # Highlight words to learn on the video
        # highlighted_video_path = os.path.join(output_folder, f"{base_name}_highlighted.mp4")
        # word_card_image_path = highlight_words(final_video_path, metadata['words_to_learn'], highlighted_video_path)
       

        # Repeat the first few seconds of the video (e.g., 3 seconds)
        repeat_sec = 3
        # Step 1: Repeat the initial section of the video
        repeated_video_path = os.path.join(output_folder, f"{base_name}_repeated.mp4")
        repeat_start_of_video(final_video_path, repeat_sec, repeated_video_path)

        # Step 2: Add the word card for the first word and update the words list
        video_with_word_card_path, updated_words_to_learn, word_card_image_path = add_first_word_card_to_video(repeated_video_path, metadata['words_to_learn'], output_folder)

        # Ensure word_card_image_path is used or saved as needed here

        # Step 3: Highlight the remaining words in the updated video
        highlighted_video_path = os.path.join(output_folder, f"{base_name}_highlighted.mp4")
        highlight_words(video_with_word_card_path, updated_words_to_learn, highlighted_video_path, delay=repeat_sec)

        # Additional operations involving word_card_image_path can be performed here


        # Extract the cover image
        print("Extracting cover...")
        cover_image_path = os.path.join(output_folder, f"{base_name}_cover.jpg")
        cover_plain_image_path = os.path.join(output_folder, f"{base_name}_cover_plain.jpg")
        cover_timestamp = validate_timestamp(metadata['cover'].replace(',', '.'))  # Correct the timestamp format
        extract_cover(input_file, cover_plain_image_path, cover_timestamp)

        overlay_word_card_on_cover(word_card_image_path, cover_plain_image_path, cover_image_path)

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
        (r"/video-processing", VideoProcessingHandler),
    ])

if __name__ == "__main__":
    upload_folder = '/home/lachlan/ProjectsLFS/autopub-video-processing/DATA'  # Folder where files will be uploaded
    app = make_app(upload_folder)
    app.listen(8081, max_body_size=10*1024 * 1024 * 1024)
    tornado.autoreload.start()
    # tornado.autoreload.watch('path/to/config.yaml')
    # tornado.autoreload.watch('path/to/static/file.html')
    tornado.ioloop.IOLoop.current().start()



