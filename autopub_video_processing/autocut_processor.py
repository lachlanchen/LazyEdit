# autocut_processor.py
import os
import subprocess

def create_or_replace_hard_link(source, link_name):
    if os.path.exists(link_name):
        os.remove(link_name)  # Remove the existing file to replace
    os.link(source, link_name)



class AutocutProcessor:
    def __init__(self, input_file, output_folder, base_name, extension):
        self.input_file = input_file
        self.output_folder = output_folder
        self.base_name = base_name
        self.extension = extension

    def run_autocut(self, lang, gpu_id):
        # Set the CUDA_VISIBLE_DEVICES environment variable
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)

        # Define filenames with language-specific suffixes before the extension
        input_file_lang = f"{self.output_folder}/{self.base_name}_{lang}{self.extension}"

        # Create hard link for language-specific version
        # os.link(self.input_file, input_file_lang)
        create_or_replace_hard_link(self.input_file, input_file_lang)

        # Define the command to process the video for the specified language
        autocut_command = f"/home/lachlan/miniconda3/bin/python -m autocut -t {input_file_lang} --whisper-model large --lang={lang} --force"

        # Run the autocut command with the specified environment
        subprocess.run(autocut_command, shell=True, check=True, env=env)
        print(f"Finished autocut with lang={lang} on GPU {gpu_id}")
