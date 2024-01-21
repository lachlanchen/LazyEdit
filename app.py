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


import subprocess

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import tornado.ioloop
import tornado.web
from tornado import gen

import zipfile  # for creating zip files

from autopub_video_processing.autocut_processor import AutocutProcessor

from autopub_video_processing.video_processing_openai import SocialMediaVideoPublisher

from pprint import pprint



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

def burn_subtitles(video_path, srt_path, output_path):
        command = f"ffmpeg -y -i {video_path} -vf subtitles={srt_path} {output_path}"
        subprocess.run(command, shell=True, check=True)

# def extract_cover(video_path, image_path, time="00:00:00"):
#     ffmpeg_command = f"ffmpeg -y -ss {time} -i {video_path} -frames:v 1 {image_path}"
#     subprocess.run(ffmpeg_command, shell=True, check=True)

# def extract_cover(video_path, image_path, time="00:00:00"):
#     ffmpeg_command = f"ffmpeg -y -ss {time} -i {video_path} -frames:v 1 {image_path}"
#     subprocess.run(ffmpeg_command, shell=True, check=True)

def extract_cover(video_path, image_path, time):
    # Replace comma with dot for milliseconds
    time = time.replace(',', '.')
    ffmpeg_command = f"ffmpeg -y -ss {time} -i {video_path} -frames:v 1 {image_path}"
    subprocess.run(ffmpeg_command, shell=True, check=True)


# def highlight_words(video_path, words_to_learn, output_path):
#     # Construct the FFmpeg drawtext filter command
#     drawtext_filter = '; '.join(
#         f"drawtext=text='{word_info['word']}': start_number=1: x=(w-text_w)/2: y=(h-text_h)/2: fontsize=24: fontcolor=white: box=1: boxcolor=0x00000099: enable='between(t,{get_seconds(word_info['time_stamps'])},{get_seconds(word_info['time_stamps'])+5})'"
#         for word_info in words_to_learn
#     )

#     command = f"ffmpeg -i {video_path} -vf \"{drawtext_filter}\" -codec:a copy {output_path}"
#     subprocess.run(command, shell=True, check=True)

def highlight_words(video_path, words_to_learn, output_path):
    # Initialize the filter_complex string
    filter_complex = ''
    # Initialize the input label for the first drawtext filter
    input_label = '0:v'

    # Iterate over the words to learn and create drawtext filters
    for i, word_info in enumerate(words_to_learn[:2]):  # using only first two words
        # Define the drawtext filter
        drawtext_filter = f"""
        drawtext=text='{word_info['word']}':
        x=(w-text_w)/2: 
        y=(h-text_h)/2: 
        fontsize=48: 
        fontcolor=white@1.0: 
        box=1: 
        boxcolor=black@0.5: 
        boxborderw=5: 
        enable='between(t,{get_seconds(word_info['time_stamps'])},{get_seconds(word_info['time_stamps'])+5})'
        """
        # Add the drawtext filter to the filter_complex string
        filter_complex += f"[{input_label}]{drawtext_filter}[v{i}];"
        # Update the input label for the next filter
        input_label = f"v{i}"

    # Remove the last semicolon from the filter_complex string
    filter_complex = filter_complex.rstrip(';')

    # Construct the final ffmpeg command
    command = f"ffmpeg -i {video_path} -filter_complex \"{filter_complex}\" -map \"[{input_label}]\" -map 0:a -c:a copy {output_path}"
    subprocess.run(command, shell=True, check=True)



def get_seconds(timestamp):
    print("timestamp: ", timestamp)
    # Split by ';' and take the last timestamp (if multiple timestamps are present)
    last_timestamp = timestamp.split(';')[0].strip()
    # Convert HH:MM:SS,mmm to HH:MM:SS.mmm and then to seconds
    h, m, s = last_timestamp.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def merge_subtitles(subtitles_en, subtitles_zh, output_path):
    # Merging based on the English timestamps
    with open(output_path, 'w', encoding='utf-8') as file:
        index = 1
        for sub_en in subtitles_en:
            # Find any overlapping Chinese subtitles
            overlaps = [sub_zh for sub_zh in subtitles_zh if not (sub_zh['end'] < sub_en['start'] or sub_zh['start'] > sub_en['end'])]
            if overlaps:
                # Write the combined subtitle
                file.write(f"{index}\n{sub_en['start']} --> {sub_en['end']}\n")
                file.write(f"{overlaps[0]['text']}\n{sub_en['text']}\n\n")
            else:
                # Write the English subtitle only
                file.write(f"{index}\n{sub_en['start']} --> {sub_en['end']}\n{sub_en['text']}\n\n")
            index += 1

            # Remove processed Chinese subtitles
            for overlap in overlaps:
                subtitles_zh.remove(overlap)

        # Write remaining Chinese subtitles that didn't overlap
        for sub_zh in subtitles_zh:
            file.write(f"{index}\n{sub_zh['start']} --> {sub_zh['end']}\n{sub_zh['text']}\n\n")
            index += 1
    print("Subtitles merged successfully.")



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
        # Extract video file from the request
        video_file = self.request.files['video'][0]
        original_fname = video_file['filename']

        print("Filename: ", original_fname)
        
        # Determine the basename (without extension) and create a subfolder
        base_name = os.path.splitext(original_fname)[0]
        output_folder = os.path.join('/home/lachlan/ProjectsLFS/autopub-video-processing/DATA', base_name)
        os.makedirs(output_folder, exist_ok=True)
        
        # Determine the basename (without extension) and create a subfolder
        base_name, extension = os.path.splitext(original_fname)
        output_folder = os.path.join('/home/lachlan/ProjectsLFS/autopub-video-processing/DATA', base_name)
        os.makedirs(output_folder, exist_ok=True)
        
        # Define the full path for the incoming video
        input_file = os.path.join(output_folder, original_fname)
        
        # Write the incoming video to the file system
        with open(input_file, 'wb') as f:
            f.write(video_file['body'])
        
        # # Define filenames with language-specific suffixes before the extension
        # input_file_en = f"{output_folder}/{base_name}_en{extension}"
        # input_file_zh = f"{output_folder}/{base_name}_zh{extension}"
        
        # # Create hard links for language-specific versions
        # os.link(input_file, input_file_en)
        # os.link(input_file, input_file_zh)
        
        # # Define the command to process the video for English and Chinese
        # autocut_command_en = f"/home/lachlan/miniconda3/bin/python -m autocut -t {input_file_en} --whisper-model large --lang=en --force"
        # autocut_command_zh = f"/home/lachlan/miniconda3/bin/python -m autocut -t {input_file_zh} --whisper-model large --lang=zh --force"

        # # Run the autocut commands concurrently, one on each GPU
        # futures = [self.executor.submit(self.run_autocut, autocut_command_en, 'en', 0),
        #            self.executor.submit(self.run_autocut, autocut_command_zh, 'zh', 1)]

        # autocut_processor = AutocutProcessor(input_file, output_folder, base_name, extension)
        # # Run the autocut commands concurrently, one on each GPU
        # futures = [self.executor.submit(autocut_processor.run_autocut, 'en', 0),
        #            self.executor.submit(autocut_processor.run_autocut, 'zh', 1)]


        # # Wait for both futures to complete
        # for future in as_completed(futures):
        #     result = future.result()
        #     print(f"Task completed with result: {result}")


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
        metadata = self.video_publisher.generate_video_metadata(output_srt_en)

        pprint(metadata)

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


        # Extract the cover image
        print("Extracting cover...")
        cover_image_path = os.path.join(output_folder, f"{base_name}_cover.jpg")
        cover_timestamp = metadata['cover'].replace(',', '.')  # Correct the timestamp format
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
      
        
        # Read the zip file content
        with open(zip_file_path, 'rb') as f:
            zip_content = f.read()
        
        # Set the headers for file download
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + os.path.basename(zip_file_path))
        
        # Return the zip file
        self.write(zip_content)



def make_app():
    return tornado.web.Application([
        (r"/video-processing", VideoProcessingHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()

