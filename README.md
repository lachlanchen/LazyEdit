<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# LazyEdit

LazyEdit is an AI-powered automatic video editing tool that processes videos to add professional-quality subtitles, highlights, word cards, and metadata. It streamlines the video editing workflow using advanced AI techniques to automate labor-intensive tasks.

## Features

- **Auto-Transcription**: Automatically transcribes video audio using AI
- **Auto-Caption**: Generates descriptive captions for video content
- **Auto-Subtitle**: Creates and burns subtitles directly onto videos
- **Auto-Highlight**: Identifies and visually highlights key words during playback
- **Auto-Metadata**: Extracts and generates metadata from video content
- **Word Cards**: Adds educational word cards for language learning
- **Teaser Generation**: Creates intelligent teasers by repeating key segments at the start
- **Multi-language Support**: Handles various languages including English and Chinese
- **Cover Image Generation**: Extracts optimal cover images with word overlays

## Installation

### Prerequisites

- Python 3.10 or higher
- FFmpeg
- CUDA-capable GPU (for transcription acceleration)
- Conda environment manager

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd lazyedit
   ```

2. Run the installation script:
   ```bash
   chmod +x install_lazyedit.sh
   ./install_lazyedit.sh
   ```

The installation script will:
- Install required system packages (ffmpeg, tmux)
- Create and configure a conda environment named "lazyedit"
- Set up the systemd service for automatic startup
- Configure necessary permissions

## Usage

LazyEdit runs as a web application that you can access at http://localhost:8081

### Processing a Video

1. Upload your video through the web interface
2. LazyEdit will automatically:
   - Transcribe and caption the video
   - Generate metadata and educational content
   - Create subtitles in detected languages
   - Add word highlighting for important terms
   - Create a teaser introduction
   - Generate a cover image
   - Package and return the processed content

### Command Line Usage

You can also run LazyEdit directly:

```bash
conda activate lazyedit
cd /path/to/lazyedit
python app.py -m lazyedit
```

## Project Structure

- `app.py` - Main application entry point
- `lazyedit/` - Core module directory
  - `autocut_processor.py` - Handles video segmentation and transcription
  - `subtitle_metadata.py` - Generates metadata from subtitles
  - `subtitle_translate.py` - Handles subtitle translation
  - `video_captioner.py` - Generates video captions
  - `words_card.py` - Creates educational word cards
  - `utils.py` - Utility functions
  - `openai_version_check.py` - OpenAI API compatibility layer

## Configuration

The systemd service configuration is created in `/etc/systemd/system/lazyedit.service`.

LazyEdit uses a tmux session named "lazyedit" to run the application, which allows it to continue running in the background.

## Service Management

- Start the service: `sudo systemctl start lazyedit.service`
- Stop the service: `sudo systemctl stop lazyedit.service`
- Check status: `sudo systemctl status lazyedit.service`
- View logs: `sudo journalctl -u lazyedit.service`

## Advanced Usage

LazyEdit supports customization of:
- Teaser length and placement
- Word highlighting styles
- Subtitle fonts and positioning
- Output folder structure
- GPU selection for processing

## Troubleshooting

- If the application doesn't start, check the systemd service status and logs
- If video processing fails, ensure FFmpeg is correctly installed
- For GPU-related issues, verify CUDA installation and GPU availability
- Ensure the conda environment is correctly activated by the service

## License

[Specify your license here]

## Acknowledgements

LazyEdit uses several open-source libraries and tools including:
- FFmpeg for video processing
- OpenAI models for AI capabilities
- Tornado web framework
- MoviePy for video editing
- CJKWrap for multilingual text processing
