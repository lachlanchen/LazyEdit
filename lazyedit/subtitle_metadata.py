import os
import re
from datetime import datetime
from openai import OpenAI
import json
import json5
import traceback
from lazyedit.openai_request_json import OpenAIRequestJSONBase, JSONParsingError, JSONValidationError
import glob
from concurrent.futures import ThreadPoolExecutor


def robust_json5_parse(json_str):
    # Attempt to handle unexpected newlines and unescaped double quotes
    json_str = ''.join(line.strip() if not line.strip().startswith('"') else line for line in json_str.split('\n'))

    # Try to parse the JSON string using json5 for more flexibility
    try:
        parsed_json = json.loads(json_str)
        return parsed_json
    except ValueError as e:
        print(f'JSON Decode Error: {e}')
        return None


class Subtitle2Metadata(OpenAIRequestJSONBase):
    def __init__(self, openai_client, use_cache=False, max_retries=3, *args, **kwargs):
        kwargs["use_cache"] = use_cache
        kwargs["max_retries"] = max_retries
        super().__init__(*args, **kwargs)

        self.client = openai_client
        self.max_retries = max_retries
        self.subtitles2metadata_folder = 'subtitles2metadata'
        self.datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Define JSON schema for metadata structure
        self.metadata_schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The video title"
                },
                "brief_description": {
                    "type": "string",
                    "description": "Brief description of the video"
                },
                "middle_description": {
                    "type": "string",
                    "description": "Medium length description of the video"
                },
                "long_description": {
                    "type": "string",
                    "description": "Detailed description of the video"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of tags related to the video content"
                },
                "english_words_to_learn": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {
                                "type": "string",
                                "description": "English word to learn"
                            },
                            "timestamp_range": {
                                "type": "object",
                                "properties": {
                                    "start": {
                                        "type": "string",
                                        "pattern": "^\\d{2}:\\d{2}:\\d{2},\\d{3}$",
                                        "description": "Start timestamp in HH:MM:SS,mmm format"
                                    },
                                    "end": {
                                        "type": "string",
                                        "pattern": "^\\d{2}:\\d{2}:\\d{2},\\d{3}$",
                                        "description": "End timestamp in HH:MM:SS,mmm format"
                                    }
                                },
                                "required": ["start", "end"],
                                "additionalProperties": False
                            }
                        },
                        "required": ["word", "timestamp_range"],
                        "additionalProperties": False
                    },
                    "description": "Array of English words with their timestamps"
                },
                "teaser": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "string",
                            "pattern": "^\\d{2}:\\d{2}:\\d{2},\\d{3}$",
                            "description": "Teaser start timestamp in HH:MM:SS,mmm format"
                        },
                        "end": {
                            "type": "string",
                            "pattern": "^\\d{2}:\\d{2}:\\d{2},\\d{3}$",
                            "description": "Teaser end timestamp in HH:MM:SS,mmm format"
                        }
                    },
                    "required": ["start", "end"],
                    "additionalProperties": False,
                    "description": "Timestamp range for video teaser"
                },
                "cover": {
                    "type": "string",
                    "pattern": "^\\d{2}:\\d{2}:\\d{2},\\d{3}$",
                    "description": "Cover image timestamp in HH:MM:SS,mmm format"
                }
            },
            "required": [
                "title", "brief_description", "middle_description", "long_description",
                "tags", "english_words_to_learn", "teaser", "cover"
            ],
            "additionalProperties": False
        }

    def get_filename(self, subtitle_path, lang):
        base_filename = os.path.splitext(os.path.basename(subtitle_path))[0]
        return f"{self.subtitles2metadata_folder}/{base_filename}_{lang}.json"

    def parse_timestamp(self, timestamp):
        try:
            return datetime.strptime(timestamp, "%H:%M:%S,%f")
        except ValueError:
            # Handle incorrect format, you might want to adjust based on your needs
            return None

    def switch_timestamps_if_necessary(self, start, end):
        start_dt = self.parse_timestamp(start)
        end_dt = self.parse_timestamp(end)
        if start_dt and end_dt and start_dt > end_dt:
            return end, start
        return start, end

    def validate_metadata(self, metadata):
        """
        Validate and fix metadata timestamps.
        With structured outputs, the schema validation is automatic,
        but we still need to fix timestamp ordering.
        """
        # Validate teaser timestamps
        if 'teaser' in metadata:
            start, end = metadata['teaser']["start"], metadata['teaser']["end"]
            corrected_start, corrected_end = self.switch_timestamps_if_necessary(start, end)
            metadata['teaser']['start'] = corrected_start
            metadata['teaser']['end'] = corrected_end

        # Validate english_words_to_learn timestamp_range
        if 'english_words_to_learn' in metadata:
            for word_info in metadata['english_words_to_learn']:
                if 'timestamp_range' in word_info:
                    start, end = word_info["timestamp_range"]["start"], word_info["timestamp_range"]["end"]
                    corrected_start, corrected_end = self.switch_timestamps_if_necessary(start, end)
                    word_info['timestamp_range']['start'] = corrected_start
                    word_info['timestamp_range']['end'] = corrected_end
                    word_info['word'] = word_info['word'].lower()

    def generate_video_metadata(self, subtitle_path, caption_path):
        with ThreadPoolExecutor(max_workers=1) as executor:
            # Initiate both tasks in parallel
            future_zh = executor.submit(self.generate_video_metadata_zh, subtitle_path, caption_path)
            future_en = executor.submit(self.generate_video_metadata_en, subtitle_path, caption_path)

            # Wait for both tasks to complete
            result_zh = future_zh.result()
            result_en = future_en.result()

        # Try to merge 'english_version' from result_en into result_zh
        try:
            result_zh["english_version"] = result_en
        except Exception:
            # In case there's an error, fallback to a copy of result_zh
            result_zh["english_version"] = result_zh.copy()

        # Try to merge 'english_words_to_learn' from result_en into result_zh,
        # while keeping a backup of the original 'english_words_to_learn' from result_zh
        try:
            # Backup 'english_words_to_learn' from the Chinese version before replacing
            if "english_words_to_learn" in result_zh:
                result_zh["english_words_to_learn_zh"] = result_zh["english_words_to_learn"].copy()

            # Replace 'english_words_to_learn' with the version from the English metadata
            if "english_words_to_learn" in result_en:
                result_zh["english_words_to_learn"] = result_en["english_words_to_learn"]
                
        except Exception as e:
            # Handle any exceptions that might occur during the process
            print(f"An error occurred while merging 'english_words_to_learn': {e}")

        return result_zh

    def generate_video_metadata_zh(self, subtitle_path, caption_path):
        # Load the subtitles from the given file path
        with open(subtitle_path, 'r', encoding='utf-8') as file:
            mixed_subtitles = file.read()

        with open(caption_path, 'r', encoding='utf-8') as file:
            captions = file.read()

        # System prompt and user prompt for API call
        system_content = (
            "My name is OpenAI. I am an expert of social media who can help vlogers add influences, grow fans, "
            "reach out audiences and create values. "
            "I can help vlogers influence people subconsiously."
        )
        prompt = (
            "I want to publish this video on XiaoHongShu, Bilibili, Douyin. \n\n"
            "Based on the provided CLIPxGPT caption (Never use it unless subtitles unavailable. ) of frames and subtitles (Use more) from the voice track, "
            "please generate a suitable title, "
            "a brief introduction, a middle description, a long description, tags, "
            "some English words that viewers can learn, teaser range, and a cover timestamp. \n\n"
            "Make it in normal, realistic narration but appealing and put some knowledge in description "
            "that pique viewer's interest to favorite, collect, love and follow. "
            "(This is our secret. Don't let it be seen in the title or description per se. "
            "Achieve this subconsiously. ) \n\n"
            "The title should be in Chinese and up to 20 characters, the brief description should be in Chinese "
            "and up to 80 characters, the middle description should be in Chinese and up to 250 characters, "
            "the long description should be in Chinese and up to 1000 characters, there should be 10 tags related to the content of the video, "
            "Five pure ENGLISH words or phrases that are important for viewers to learn from the video sorted by interestingness, "
            "Each word should be accompanied by a timestamp range indicating when it appears in the video.\n\n"
            "Give a 2~4 seconds timestamp range which can reflect the essense of the video as teaser. "
            "Also, suggest a timestamp for the best scene to use as a cover image for the video. \n\n"
            "Try to find instructions also in subtitles if exist. \n\n"
            "Return correct format result with imagination even subtitles is little or even empty. \n\n"
            f"Captions:\n{captions}\n\n"
            f"Subtitles:\n{mixed_subtitles}\n\n"
            "Please provide the metadata in the specified JSON format."
        )

        # Use the new structured outputs method
        result = self.send_request_with_json_schema(
            prompt=prompt,
            json_schema=self.metadata_schema,
            system_content=system_content,
            filename=self.get_filename(subtitle_path, lang="zh"),
            schema_name="video_metadata"
        )

        self.validate_metadata(result)
        return result

    def generate_video_metadata_en(self, subtitle_path, caption_path):
        # Load the subtitles from the given file path
        with open(subtitle_path, 'r', encoding='utf-8') as file:
            mixed_subtitles = file.read()

        with open(caption_path, 'r', encoding='utf-8') as file:
            captions = file.read()

        # System prompt and user prompt for API call
        system_content = (
            "My name is OpenAI. I am an expert of social media who can help Youtube vlogers add influences, grow fans, "
            "reach out audiences and create values. "
            "I can help vlogers influence people subconsiously."
        )
        prompt = (
            "I want to publish this video on Youtube. \n\n"
            "Based on the provided CLIPxGPT caption (Never use it unless subtitles unavailable. ) of frames and subtitles (Use more) from the voice track, "
            "please generate a suitable title, "
            "a brief introduction, a middle description, a long description, tags, "
            "some English words that viewers can learn, teaser range, and a cover timestamp. \n\n"
            "Make it in normal, realistic narration but appealing and put some knowledge in description "
            "that pique viewer's interest to favorite, collect, love and follow. "
            "(This is our secret. Don't let it be seen in the title or description per se. "
            "Achieve this subconsiously. ) \n\n"
            "The title should be in English and up to 20 words, the brief description should be in English "
            "and up to 80 words, the middle description should be in English and up to 250 words, "
            "the long description should be in English and up to 500 words, there should be 10 tags related to the content of the video, "
            "Five pure ENGLISH words that are important for viewers to learn from the video sorted by interestingness, "
            "Each word should be accompanied by a timestamp range indicating when it appears in the video.\n\n"
            "Give a 2~4 seconds timestamp range which can reflect the essence of the video as teaser. "
            "Also, suggest a timestamp for the best scene to use as a cover image for the video. \n\n"
            "Try to find instructions also in subtitles if exist. \n\n"
            "Return correct format result with imagination even subtitles is little or even empty. \n\n"
            f"Captions:\n{captions}\n\n"
            f"Subtitles:\n{mixed_subtitles}\n\n"
            "Please provide the metadata in the specified JSON format."
        )

        # Use the new structured outputs method
        result = self.send_request_with_json_schema(
            prompt=prompt,
            json_schema=self.metadata_schema,
            system_content=system_content,
            filename=self.get_filename(subtitle_path, lang="en"),
            schema_name="video_metadata"
        )

        self.validate_metadata(result)
        return result

    def generate_metadata_from_template(
        self,
        template_dir: str,
        transcription_text: str,
        caption_text: str,
        custom_notes: str | None,
        output_path: str,
        schema_name: str = "video_metadata",
    ):
        prompt_path = os.path.join(template_dir, "prompt.json")
        schema_path = os.path.join(template_dir, "schema.json")
        prompt_payload = self._load_json_file(prompt_path)
        json_schema = self._load_json_file(schema_path)

        system_content = prompt_payload.get("system") or "You are an AI assistant."
        user_template = prompt_payload.get("user") or ""
        notes_value = (custom_notes or "").strip() or "None"
        prompt = self._render_prompt_template(
            user_template,
            {
                "TRANSCRIPTION": transcription_text or "No transcription available.",
                "CAPTIONS": caption_text or "No keyframe captions available.",
                "CUSTOM_NOTES": notes_value,
            },
        )

        result = self.send_request_with_json_schema(
            prompt=prompt,
            json_schema=json_schema,
            system_content=system_content,
            filename=output_path,
            schema_name=schema_name,
        )
        self.validate_metadata(result)
        return result

    @staticmethod
    def _render_prompt_template(template: str, values: dict[str, str]) -> str:
        rendered = template
        for key, value in values.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        return rendered

    @staticmethod
    def _load_json_file(path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError:
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    return json5.load(handle)
            except Exception as exc:
                raise RuntimeError(f"Failed to parse JSON template: {path}") from exc


if __name__ == "__main__":
    from io import StringIO

    # Usage example
    openai_client = OpenAI()  # Make sure to authenticate your OpenAI client
    sub2meta = Subtitle2Metadata(openai_client)
    english_subtitles = """
1
00:00:00,000 --> 00:00:03,500
The only good thing about this is the chicken. It's really good.

2
00:00:03,500 --> 00:00:04,500
Very tender.

3
00:00:05,500 --> 00:00:06,500
Really good.

"""  # Replace with actual subtitles

    chinese_subtitles = """
1
00:00:00,000 --> 00:00:02,880
这个唯一好吃的是这个鸡肉挺好吃的

2
00:00:02,880 --> 00:00:03,400
特别好吃

3
00:00:03,400 --> 00:00:04,180
很嫩

4
00:00:04,180 --> 00:00:05,980
太好吃了

"""
    # Creating file-like objects from strings.
    english_subtitles_file = StringIO(english_subtitles)
    chinese_subtitles_file = StringIO(chinese_subtitles)

    result = sub2meta.generate_video_metadata(english_subtitles_file, chinese_subtitles_file)
    print(result)
