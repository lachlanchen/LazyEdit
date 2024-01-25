import os


import openai
from packaging import version

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__}"
                     " is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")

# -- Now we can get to it
from openai import OpenAI
client = OpenAI()  # should use env variable OPENAI_API_KEY


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

from autopub_video_processing.video_processing_openai import SocialMediaVideoPublisher

from pprint import pprint
import json5
import json

import subprocess
from urllib.parse import quote


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




def highlight_words(video_path, words_to_learn, output_path):
    # Sort words_to_learn by start time
    words_to_learn.sort(key=lambda x: get_time_range(x['time_stamps'])[0])

    # Initialize variables
    temp_output_path = output_path + ".temp.mp4"
    final_output_path = output_path
    current_input_path = video_path
    successful = False

    # Process each word
    for i, word_info in enumerate(words_to_learn):
        try:
            # Get time range
            start_seconds, end_seconds = get_time_range(word_info['time_stamps'])

            # Construct drawtext filter
            drawtext_filter = (
                f"drawtext=text='{word_info['word']}':"
                f"x=(w-text_w)/2: "
                f"y=(h-text_h)/2: "
                f"fontsize=96: "
                f"fontcolor=white@1.0: "
                f"box=1: "
                f"boxcolor=black@0.5: "
                f"boxborderw=5: "
                f"enable='between(t,{start_seconds},{end_seconds})'"
            )

            # Construct ffmpeg command
            command = (
                f"ffmpeg -y -i \"{current_input_path}\" -vf \"{drawtext_filter}\" "
                f"-c:a copy \"{temp_output_path}\""
            )

            # Execute ffmpeg command
            subprocess.run(command, shell=True, check=True)

            # If successful, prepare for next iteration
            if i < len(words_to_learn) - 1:
                os.rename(temp_output_path, final_output_path)
                current_input_path = final_output_path
            successful = True
        except subprocess.CalledProcessError as e:
            # Log error and skip to the next word
            print(f"Error processing word '{word_info['word']}': {e}")
            continue

    # Finalize output
    if not successful:
        # If no text was successfully drawn, copy the original video to the output
        os.link(video_path, final_output_path)
    else:
        if current_input_path != final_output_path:
            os.rename(current_input_path, final_output_path)



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



def burn_subtitles(video_path, srt_path, output_path):
        command = f"ffmpeg -y -i \"{video_path}\" -vf subtitles=\"{srt_path}\" \"{output_path}\""
        subprocess.run(command, shell=True, check=True)


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


class VideoProcessingHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=2)

    def initialize(self):
        self.openai_client = OpenAI()  # Make sure to authenticate your OpenAI client
        self.video_publisher = SocialMediaVideoPublisher(self.openai_client)

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
            self.executor.submit(autocut_processor.run_autocut, 'en', 0),
            self.executor.submit(autocut_processor.run_autocut, 'zh', 1)
        ]
        for future in as_completed(futures):
            result = future.result()
            print(f"Task completed with result: {result}")


    @gen.coroutine
    def post(self):
        # size = 1024*1024*1024
        # self.request.connection.set_max_body_size(size) 
        


        # # Extract video file from the request
        # video_file = self.request.files['video'][0]
        # original_fname = video_file['filename']

        # print("Filename: ", original_fname)
        
        
        
        # # Determine the basename (without extension) and create a subfolder
        # base_name, extension = os.path.splitext(original_fname)
        # output_folder = os.path.join('/home/lachlan/ProjectsLFS/autopub-video-processing/DATA', base_name)
        # os.makedirs(output_folder, exist_ok=True)
        
        # # Define the full path for the incoming video
        # input_file = os.path.join(output_folder, original_fname)
        
        # # Write the incoming video to the file system
        # with open(input_file, 'wb') as f:
        #     f.write(video_file['body'])
        
        input_file = self.get_argument('file_path', None)
        if not input_file or not os.path.exists(input_file):
            self.set_status(400)
            self.write({'status': 'error', 'message': 'File path is invalid or file does not exist'})
            return

        print("Processing File: ", input_file)
        base_name, extension = os.path.splitext(os.path.basename(input_file))
        output_folder = os.path.dirname(input_file)

        self.process_video(input_file, base_name, extension, output_folder)
        
        # # Extract cover image from the video
        # cover_image_path = os.path.join(output_folder, f"{base_name}.jpg")
        # extract_cover(input_file, cover_image_path, time="00:00:00")
        
        # Define paths for the output files for both languages
        output_md_en = f"{output_folder}/{base_name}_en.md"
        output_srt_en = f"{output_folder}/{base_name}_en.srt"
        output_md_zh = f"{output_folder}/{base_name}_zh.md"
        output_srt_zh = f"{output_folder}/{base_name}_zh.srt"
        

        # Check if files exist before reading
        for file_path in [output_md_en, output_srt_en, output_md_zh, output_srt_zh]:
            if not os.path.exists(file_path):
                self.set_status(500)
                self.write(f"Error: Expected output file not found: {file_path}")
                return



        # After fetching metadata
        print("Generating metadata with OpenAI...")
        metadata = self.video_publisher.generate_video_metadata(output_srt_en, output_srt_zh)
        metadata["video_filename"] = f"{base_name}_highlighted.mp4"
        metadata["cover_filename"] = f"{base_name}_cover.jpg"

        pprint(metadata)

        # Save metadata to a JSON file
        metadata_json_path = os.path.join(output_folder, f"{base_name}_metadata.json")
        with open(metadata_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(metadata, json_file, indent=4, ensure_ascii=False)


        # Parse subtitles
        subtitles_en = parse_subtitles(output_srt_en)
        subtitles_zh = parse_subtitles(output_srt_zh)

        # Merge subtitles
        print("Merging subtitles...")
        combined_srt_path = os.path.join(output_folder, f"{base_name}_combined.srt")
        merge_subtitles(subtitles_en, subtitles_zh, combined_srt_path)

        # Burn combined subtitles onto the video
        print("Burning subtitles...")
        final_video_path = os.path.join(output_folder, f"{base_name}_final.mp4")
        burn_subtitles(input_file, combined_srt_path, final_video_path)


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

        # Extract the cover image
        print("Extracting cover...")
        cover_image_path = os.path.join(output_folder, f"{base_name}_cover.jpg")
        cover_timestamp = validate_timestamp(metadata['cover'].replace(',', '.'))  # Correct the timestamp format
        extract_cover(input_file, cover_image_path, cover_timestamp)

        # Highlight words to learn on the video
        highlighted_video_path = os.path.join(output_folder, f"{base_name}_highlighted.mp4")
        highlight_words(final_video_path, metadata['words_to_learn'], highlighted_video_path)
        
        # Prepare the files to return by zipping them
        zip_file_path = os.path.join(output_folder, f"{base_name}.zip")
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(highlighted_video_path, os.path.basename(highlighted_video_path))
            zipf.write(output_md_en, os.path.basename(output_md_en))
            zipf.write(output_srt_en, os.path.basename(output_srt_en))
            zipf.write(output_md_zh, os.path.basename(output_md_zh))
            zipf.write(output_srt_zh, os.path.basename(output_srt_zh))
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
        (r"/video-processing", VideoProcessingHandler),
    ])

if __name__ == "__main__":
    upload_folder = '/home/lachlan/ProjectsLFS/autopub-video-processing/DATA'  # Folder where files will be uploaded
    app = make_app(upload_folder)
    app.listen(8081, max_body_size=1024 * 1024 * 1024)
    tornado.autoreload.start()
    # tornado.autoreload.watch('path/to/config.yaml')
    # tornado.autoreload.watch('path/to/static/file.html')
    tornado.ioloop.IOLoop.current().start()



