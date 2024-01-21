import os
import subprocess

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import tornado.ioloop
import tornado.web
from tornado import gen

import zipfile  # for creating zip files




class VideoProcessingHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=2)

    def run_autocut(self, autocut_command, lang, gpu_id):
        # Set the CUDA_VISIBLE_DEVICES environment variable
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)

        # Run the autocut command with the specified environment
        subprocess.run(autocut_command, shell=True, check=True, env=env)
        print(f"Finished autocut with lang={lang} on GPU {gpu_id}")

    @gen.coroutine
    def post(self):
        # Extract video file from the request
        video_file = self.request.files['video'][0]
        original_fname = video_file['filename']
        
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
        
        # Define filenames with language-specific suffixes before the extension
        input_file_en = f"{output_folder}/{base_name}_en{extension}"
        input_file_zh = f"{output_folder}/{base_name}_zh{extension}"
        
        # Create hard links for language-specific versions
        os.link(input_file, input_file_en)
        os.link(input_file, input_file_zh)
        
        # Define the command to process the video for English and Chinese
        autocut_command_en = f"/home/lachlan/miniconda3/bin/python -m autocut -t {input_file_en} --whisper-model large --lang=en --force"
        autocut_command_zh = f"/home/lachlan/miniconda3/bin/python -m autocut -t {input_file_zh} --whisper-model large --lang=zh --force"

        # Run the autocut commands concurrently, one on each GPU
        futures = [self.executor.submit(self.run_autocut, autocut_command_en, 'en', 0),
                   self.executor.submit(self.run_autocut, autocut_command_zh, 'zh', 1)]

        # Wait for both futures to complete
        for future in as_completed(futures):
            result = future.result()
            print(f"Task completed with result: {result}")


        
        # Extract cover image from the video
        cover_image_path = os.path.join(output_folder, f"{base_name}.jpg")
        extract_cover(input_file, cover_image_path, time="00:00:00")
        
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
        
        # Prepare the files to return by zipping them
        zip_file_path = os.path.join(output_folder, f"{base_name}.zip")
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(cover_image_path, os.path.basename(cover_image_path))
            zipf.write(output_md_en, os.path.basename(output_md_en))
            zipf.write(output_srt_en, os.path.basename(output_srt_en))
            zipf.write(output_md_zh, os.path.basename(output_md_zh))
            zipf.write(output_srt_zh, os.path.basename(output_srt_zh))
        
        # Read the zip file content
        with open(zip_file_path, 'rb') as f:
            zip_content = f.read()
        
        # Set the headers for file download
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + os.path.basename(zip_file_path))
        
        # Return the zip file
        self.write(zip_content)

def extract_cover(video_path, image_path, time="00:00:00"):
    ffmpeg_command = f"ffmpeg -y -ss {time} -i {video_path} -frames:v 1 {image_path}"
    subprocess.run(ffmpeg_command, shell=True, check=True)


def make_app():
    return tornado.web.Application([
        (r"/video-processing", VideoProcessingHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()

