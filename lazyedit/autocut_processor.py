# autocut_processor.py
import os
import subprocess
import shlex

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

    @staticmethod
    def _dedupe_models(models):
        ordered = []
        seen = set()
        for model in models:
            name = str(model or "").strip()
            if not name or name in seen:
                continue
            ordered.append(name)
            seen.add(name)
        return ordered

    def _resolve_model_candidates(self, whisper_model, fallback_model):
        configured = os.getenv("LAZYEDIT_WHISPER_MODEL_CANDIDATES")
        if configured:
            return self._dedupe_models(configured.split(","))

        # Progressively step down to smaller multilingual models on CUDA OOM.
        default_chain = [
            whisper_model,
            fallback_model,
            "medium",
            "small",
            "base",
            "tiny",
        ]
        return self._dedupe_models(default_chain)

    @staticmethod
    def _is_cuda_oom(output):
        message = str(output or "").lower()
        return (
            "out of memory" in message
            and (
                "cuda" in message
                or "cudnn" in message
                or "cublas" in message
                or "torch.cuda" in message
            )
        )

    @staticmethod
    def _run_logged_command(command, env):
        process = subprocess.Popen(
            ["bash", "-lc", f"ulimit -c 0; {command}"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        lines = []
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            lines.append(line)
        returncode = process.wait()
        return returncode, "".join(lines)

    def run_autocut(self, lang, gpu_id):
        script_path = os.getenv("LAZYEDIT_WHISPER_SCRIPT")
        if not script_path:
            script_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "whisper_with_lang_detect", "vad_lang_subtitle.py")
            )
        whisper_model = os.getenv("LAZYEDIT_WHISPER_MODEL", "large-v3")
        fallback_model = os.getenv("LAZYEDIT_WHISPER_FALLBACK_MODEL", "large-v2")
        model_candidates = self._resolve_model_candidates(whisper_model, fallback_model)

        # Set the CUDA_VISIBLE_DEVICES environment variable
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
        env["LAZYEDIT_WHISPER_DEVICE"] = "cuda"
        env["LAZYEDIT_WHISPER_GPU_ID"] = str(gpu_id)
        env.setdefault("OMP_NUM_THREADS", "1")
        env.setdefault("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:128")

        # Define filenames with language-specific suffixes before the extension
        input_file_lang = f"{self.output_folder}/{self.base_name}_{lang}{self.extension}"

        # Create hard link for language-specific version
        # os.link(self.input_file, input_file_lang)
        create_or_replace_hard_link(self.input_file, input_file_lang)

        last_failure_output = ""
        saw_cuda_oom = False
        for index, model_name in enumerate(model_candidates, start=1):
            autocut_command = (
                f"/home/lachlan/miniconda3/envs/whisper/bin/python "
                f"{shlex.quote(script_path)} -t {shlex.quote(input_file_lang)} "
                f"--whisper-model {shlex.quote(model_name)} --force"
            )
            print(
                f"Autocut attempt {index}/{len(model_candidates)} for lang={lang} "
                f"on GPU {gpu_id} with Whisper model {model_name}"
            )
            returncode, output = self._run_logged_command(autocut_command, env)
            last_failure_output = output
            if returncode == 0 and not self._is_cuda_oom(output):
                print(f"Finished autocut with lang={lang} on GPU {gpu_id} using model {model_name}")
                return
            if self._is_cuda_oom(output):
                saw_cuda_oom = True
                print(f"CUDA OOM detected with Whisper model {model_name}. Trying a smaller model.")
                continue
            if returncode in (132, 139):
                print("Autocut crashed (illegal instruction/segfault). Retrying with safe CPU flags...")
                break
            raise subprocess.CalledProcessError(returncode, autocut_command, output=output)

        fallback_env = env.copy()
        fallback_env["CUDA_VISIBLE_DEVICES"] = ""
        fallback_env["LAZYEDIT_WHISPER_DEVICE"] = "cpu"
        fallback_env["ATEN_CPU_CAPABILITY"] = "default"
        fallback_env["ONEDNN_MAX_CPU_ISA"] = "AVX2"
        fallback_env["MKL_DEBUG_CPU_TYPE"] = "5"
        cpu_model = model_candidates[-1] if model_candidates else whisper_model
        if saw_cuda_oom:
            print(f"All GPU Whisper model attempts exhausted VRAM. Falling back to CPU with model {cpu_model}.")
        fallback_command = (
            f"/home/lachlan/miniconda3/envs/whisper/bin/python "
            f"{shlex.quote(script_path)} -t {shlex.quote(input_file_lang)} "
            f"--whisper-model {shlex.quote(cpu_model)} --force"
        )
        returncode, output = self._run_logged_command(fallback_command, fallback_env)
        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, fallback_command, output=output)
        print(f"Finished autocut with fallback CPU mode for lang={lang} using model {cpu_model}")
