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
        script_path = os.getenv("LAZYEDIT_WHISPER_SCRIPT")
        if not script_path:
            script_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "whisper_with_lang_detect", "vad_lang_subtitle.py")
            )
        whisper_model = os.getenv("LAZYEDIT_WHISPER_MODEL", "large-v3")
        fallback_model = os.getenv("LAZYEDIT_WHISPER_FALLBACK_MODEL", "large-v2")

        # Set the CUDA_VISIBLE_DEVICES environment variable
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
        env.setdefault("OMP_NUM_THREADS", "1")

        # Define filenames with language-specific suffixes before the extension
        input_file_lang = f"{self.output_folder}/{self.base_name}_{lang}{self.extension}"

        # Create hard link for language-specific version
        # os.link(self.input_file, input_file_lang)
        create_or_replace_hard_link(self.input_file, input_file_lang)

        # Define the command to process the video for the specified language
        # autocut_command = f"/home/lachlan/miniconda3/bin/python -m autocut -t \"{input_file_lang}\" --whisper-model large --lang={lang} --force"
        # autocut_command = f"/home/lachlan/miniconda3/envs/whisper/bin/python /home/lachlan/Projects/whisper_with_lang_detect/vad_lang_subtitle.py -t \"{input_file_lang}\" --whisper-model large-v2 --force"
        autocut_command = f"/home/lachlan/miniconda3/envs/whisper/bin/python {script_path} -t \"{input_file_lang}\" --whisper-model {whisper_model} --force"
        print("autocut_command: ", autocut_command)


        # Run the autocut command with the specified environment
        try:
            subprocess.run(["bash", "-lc", f"ulimit -c 0; {autocut_command}"], check=True, env=env)
            print(f"Finished autocut with lang={lang} on GPU {gpu_id}")
            return
        except subprocess.CalledProcessError as exc:
            returncode = exc.returncode
            if returncode not in (132, 139) and returncode >= 0:
                raise
            print("Autocut crashed (illegal instruction/segfault). Retrying with safe CPU flags...")

        fallback_env = env.copy()
        fallback_env["CUDA_VISIBLE_DEVICES"] = ""
        fallback_env["ATEN_CPU_CAPABILITY"] = "default"
        fallback_env["ONEDNN_MAX_CPU_ISA"] = "AVX2"
        fallback_env["MKL_DEBUG_CPU_TYPE"] = "5"
        if fallback_model and fallback_model != whisper_model:
            fallback_command = f"/home/lachlan/miniconda3/envs/whisper/bin/python {script_path} -t \"{input_file_lang}\" --whisper-model {fallback_model} --force"
        else:
            fallback_command = autocut_command
        subprocess.run(["bash", "-lc", f"ulimit -c 0; {fallback_command}"], check=True, env=fallback_env)
        print(f"Finished autocut with fallback CPU mode for lang={lang}")
