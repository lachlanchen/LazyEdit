# import os
# import subprocess
# import argparse

import os
import subprocess
import argparse
import signal
import time
import traceback

from config import (
    CAPTION_FALLBACK_CWD,
    CAPTION_FALLBACK_SCRIPT,
    CAPTION_PRIMARY_ROOT,
    CAPTION_PRIMARY_SCRIPT,
    CAPTION_PYTHON,
)


# class VideoCaptioner:
#     def __init__(self, video_path, output_folder, num_frames=3, model_size='L', checkpoint_name='model.pt', temperature=1.0):
#         self.video_path = video_path
#         self.output_folder = output_folder
#         self.num_frames = num_frames
#         self.model_size = model_size
#         self.checkpoint_name = checkpoint_name
#         self.temperature = temperature
#         self.caption_srt_path = os.path.splitext(video_path)[0] + "_caption.srt"
#         self.caption_json_path = os.path.splitext(video_path)[0] + "_caption.json"
#         self.conda_env_path = "/home/lachlan/miniconda3/envs/caption/bin/python"

#     def run_captioning(self):
#         # Build the command for the captioning process
#         # caption_command = f"{self.conda_env_path} /home/lachlan/Projects/image_captioning/clip-gpt-captioning/src/v2c.py -V \"{self.video_path}\" -N {self.num_frames}"
#         caption_command = f"{self.conda_env_path} /home/lachlan/Projects/vit-gpt2-image-captioning/vit_captioner_video.py -V \"{self.video_path}\" -N {self.num_frames}"
        
#         # Run the command in a subprocess
#         result = subprocess.run(caption_command, shell=True, check=True, text=True)
#         if result.returncode == 0:
#             print(f"Captioning completed successfully, output saved to: {self.caption_srt_path}")
#             print(f"Captioning completed successfully, output saved to: {self.caption_json_path}")
#         else:
#             print("Captioning process failed.")


class VideoCaptioner:
    def __init__(
        self,
        video_path,
        output_folder,
        num_frames=3,
        model_size='L',
        checkpoint_name='model.pt',
        temperature=1.0,
        python_path=None,
        primary_root=None,
        primary_script=None,
        fallback_script=None,
        fallback_cwd=None,
    ):
        self.video_path = video_path
        self.output_folder = output_folder
        self.num_frames = num_frames
        self.model_size = model_size
        self.checkpoint_name = checkpoint_name
        self.temperature = temperature
        self.caption_srt_path = os.path.splitext(video_path)[0] + "_caption.srt"
        self.caption_json_path = os.path.splitext(video_path)[0] + "_caption.json"
        self.conda_env_path = python_path or CAPTION_PYTHON
        self.primary_root = primary_root or CAPTION_PRIMARY_ROOT or self._find_primary_root()
        self.base_command = self._resolve_primary_script(primary_script or CAPTION_PRIMARY_SCRIPT)
        self.alternate_command = self._resolve_path(fallback_script or CAPTION_FALLBACK_SCRIPT)
        self.fallback_cwd = (
            fallback_cwd
            or CAPTION_FALLBACK_CWD
            or self._resolve_fallback_cwd(self.alternate_command)
        )
        self.last_error = None
        self.last_method = None

    def is_configured(self):
        if not self.conda_env_path or not os.path.exists(self.conda_env_path):
            return False
        if self.base_command and os.path.exists(self.base_command):
            return True
        if self.primary_root and os.path.isdir(self.primary_root):
            return True
        return bool(self.alternate_command and os.path.exists(self.alternate_command))

    def _resolve_path(self, path):
        if not path:
            return path
        if os.path.exists(path):
            return path
        if "/Projects/" in path:
            alt = path.replace("/Projects/", "/ProjectsLFS/")
            if os.path.exists(alt):
                return alt
        return path

    def _resolve_primary_script(self, path):
        resolved = self._resolve_path(path)
        if resolved and os.path.exists(resolved):
            return resolved
        return None

    def _find_primary_root(self):
        for root in (
            "/home/lachlan/ProjectsLFS/vit-gpt2-image-captioning",
            "/home/lachlan/Projects/vit-gpt2-image-captioning",
        ):
            if os.path.isdir(root):
                return root
        return None

    def _resolve_fallback_cwd(self, script_path):
        if not script_path:
            return None
        script_dir = os.path.dirname(script_path)
        if os.path.basename(script_dir) == "src":
            return os.path.dirname(script_dir)
        return script_dir

    def vague_kill(self, command):
        # Kill processes based on the script path only
        kill_command = f"pkill -f \"{self.conda_env_path} {command}\""
        print(f"Executing: {kill_command}")
        os.system(kill_command)

    def specific_kill(self, full_command):
        # Kill the specific full command
        kill_command = f"pkill -f \"{full_command}\""
        print(f"Executing: {kill_command}")
        os.system(kill_command)

    def _build_command(self, script_path):
        return f"{self.conda_env_path} {script_path} -V \"{self.video_path}\" -N {self.num_frames}"

    def _build_module_command(self):
        return (
            f"{self.conda_env_path} -m vit_captioner.cli caption-video "
            f"-V \"{self.video_path}\" -N {self.num_frames}"
        )

    def _ensure_fallback_weights_dir(self):
        if not self.fallback_cwd:
            return
        weights_dir = os.path.join(self.fallback_cwd, "weights", "large")
        os.makedirs(weights_dir, exist_ok=True)

    def _run_command(self, command, cwd=None):
        env = os.environ.copy()
        if cwd:
            existing = env.get("PYTHONPATH")
            env["PYTHONPATH"] = f"{cwd}:{existing}" if existing else cwd
        env.setdefault("MPLBACKEND", "Agg")
        env.setdefault("QT_QPA_PLATFORM", "offscreen")
        try:
            return subprocess.run(
                command,
                shell=True,
                check=True,
                timeout=180,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=cwd,
                env=env,
            )
        except subprocess.CalledProcessError as e:
            output = (e.stdout or "").strip()
            tail = output[-2000:] if output else ""
            raise RuntimeError(f"{e}. Output: {tail}") from e

    def run_captioning(self):
        if not self.is_configured():
            raise RuntimeError(
                "Captioner not configured. Set LAZYEDIT_CAPTION_PYTHON and script paths."
            )

        caption_command = None
        alternative_command = None
        if self.base_command and os.path.exists(self.base_command):
            caption_command = self._build_command(self.base_command)
        elif self.primary_root and os.path.isdir(self.primary_root):
            caption_command = self._build_module_command()
        if self.alternate_command and os.path.exists(self.alternate_command):
            alternative_command = self._build_command(self.alternate_command)
        
        try:
            if alternative_command:
                self._ensure_fallback_weights_dir()
                print("Executing fallback command: ", alternative_command)
                self._run_command(alternative_command, cwd=self.fallback_cwd)
                print("Fallback captioning completed successfully.")
                self.last_method = "fallback"
                self.last_error = None
                return
            raise RuntimeError("Fallback caption script not available.")
        except Exception as e:

            traceback.print_exc()
            self.last_error = str(e)

            if alternative_command:
                self.specific_kill(alternative_command)

            print("Fallback command failed. Trying primary command.")

            # Primary command
            try:
                if not caption_command:
                    raise RuntimeError("Primary caption script not available.")
                print("Executing primary command: ", caption_command)
                self._run_command(caption_command, cwd=self.primary_root)
                print(f"Captioning completed successfully, output saved to: {self.caption_srt_path}")
                print(f"Captioning completed successfully, output saved to: {self.caption_json_path}")
                self.last_method = "primary"
                self.last_error = None
            except Exception as e:

                traceback.print_exc()
                self.last_error = str(e)

                if caption_command:
                    self.specific_kill(caption_command)

                print("Primary command failed. Saving empty file.")
                
                with open(self.caption_srt_path, 'w') as file:
                    file.write("")  # Create an empty file

                with open(self.caption_json_path, 'w') as file:
                    file.write("")  # Create an empty file


        if caption_command:
            self.specific_kill(caption_command)
        if alternative_command:
            self.specific_kill(alternative_command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate video captioning process using a specific conda environment")
    parser.add_argument("-V", "--video-path", type=str, required=True, help="Path to the video file")
    parser.add_argument("-O", "--output-folder", type=str, required=True, help="Output folder to store results")
    parser.add_argument("-N", "--num-frames", type=int, default=10, help="Number of frames to caption")
    parser.add_argument("-S", "--size", type=str, default="L", help="Model size [S, L]")
    parser.add_argument("-C", "--checkpoint-name", type=str, default="model.pt", help="Name of the model checkpoint")
    parser.add_argument("-T", "--temperature", type=float, default=1.0, help="Temperature for sampling")

    args = parser.parse_args()

    vc_processor = VideoCaptioner(args.video_path, args.output_folder, args.num_frames, args.size, args.checkpoint_name, args.temperature)
    vc_processor.run_captioning()



# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Automate video captioning process using a specific conda environment")
#     parser.add_argument("-V", "--video-path", type=str, required=True, help="Path to the video file")
#     parser.add_argument("-O", "--output-folder", type=str, required=True, help="Output folder to store results")
#     parser.add_argument("-N", "--num-frames", type=int, default=10, help="Number of frames to caption")
#     parser.add_argument("-S", "--size", type=str, default="L", help="Model size [S, L]")
#     parser.add_argument("-C", "--checkpoint-name", type=str, default="model.pt", help="Name of the model checkpoint")
#     parser.add_argument("-T", "--temperature", type=float, default=1.0, help="Temperature for sampling")

#     args = parser.parse_args()

#     vc_processor = VideoCaptioner(args.video_path, args.output_folder, args.num_frames, args.size, args.checkpoint_name, args.temperature)
#     vc_processor.run_captioning()
