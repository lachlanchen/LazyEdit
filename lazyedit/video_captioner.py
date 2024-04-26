import os
import subprocess
import argparse

class VideoCaptioner:
    def __init__(self, video_path, output_folder, num_frames=3, model_size='L', checkpoint_name='model.pt', temperature=1.0):
        self.video_path = video_path
        self.output_folder = output_folder
        self.num_frames = num_frames
        self.model_size = model_size
        self.checkpoint_name = checkpoint_name
        self.temperature = temperature
        self.caption_srt_path = os.path.splitext(video_path)[0] + "_caption.srt"
        self.caption_json_path = os.path.splitext(video_path)[0] + "_caption.json"
        self.conda_env_path = "/home/lachlan/miniconda3/envs/caption/bin/python"

    def run_captioning(self):
        # Build the command for the captioning process
        # caption_command = f"{self.conda_env_path} /home/lachlan/Projects/image_captioning/clip-gpt-captioning/src/v2c.py -V \"{self.video_path}\" -N {self.num_frames}"
        caption_command = f"{self.conda_env_path} /home/lachlan/Projects/vit-gpt2-image-captioning/vit_captioner_video.py -V \"{self.video_path}\" -N {self.num_frames}"
        
        # Run the command in a subprocess
        result = subprocess.run(caption_command, shell=True, check=True, text=True)
        if result.returncode == 0:
            print(f"Captioning completed successfully, output saved to: {self.caption_srt_path}")
            print(f"Captioning completed successfully, output saved to: {self.caption_json_path}")
        else:
            print("Captioning process failed.")

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
