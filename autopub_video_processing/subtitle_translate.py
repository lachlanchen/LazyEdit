import json
import re
import traceback
import openai

import openai
from packaging import version
import json
import os

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__}"
                     " is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")
import os

# -- Now we can get to it
from openai import OpenAI
client = OpenAI()  # should use env variable OPENAI_API_KEY


from autopub_video_processing.utils import JSONParsingError, JSONValidationError



class SubtitlesTranslator:
    def __init__(self, openai_client, input_json_path, input_srt_path, output_srt_path, max_retries=3):
        self.client = openai_client
        self.input_json_path = input_json_path
        self.input_srt_path = input_srt_path
        self.output_srt_path = output_srt_path
        self.max_retries = max_retries

    def load_subtitles_from_json(self):
        """Load subtitles from a JSON file."""
        with open(self.input_json_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def extract_and_parse_json(self, text):
        """Extract and parse JSON from text, handling potential parsing issues."""
        bracket_pattern = r'\[.*\]'
        matches = re.findall(bracket_pattern, text, re.DOTALL)
        # json_string = ""

        if not matches:
            raise JSONParsingError("No JSON string found in text", text, text)
        json_string = matches[0].replace('\n', '')

        print(json_string)

        try:
            return json.loads(json_string)
        except ValueError as e:
            traceback.print_exc()
            raise JSONParsingError(f"JSON Decode Error: {e}", json_string, text)

    def validate_translated_subtitles(self, subtitles):
        """Validate the structure of translated subtitles."""
        required_fields = ["start", "end", "en", "zh"]
        for subtitle in subtitles:
            if not all(field in subtitle for field in required_fields):
                raise JSONValidationError("Subtitle missing one of the required fields: " + ", ".join(required_fields))

    def translate_and_merge_subtitles(self, subtitles):
        """Translate and merge subtitles using the OpenAI API."""

        print("Translating subtitles...")
        
        client = self.client

        retries = 0

        while retries < self.max_retries:
            try:
                # Placeholder for OpenAI API call setup
                # Construct the prompt for translation and merging
                # Constructing the detailed prompt with placeholders for subtitles
                # Prepare the detailed prompt for translation and merging
                prompt_content = (
                    "Below are mixed language subtitles extracted from a video, including timestamps, "
                    "language indicators, and the subtitle text itself. The task is to ensure that each subtitle "
                    "is presented with both English (en) and Chinese (zh) translations, maintaining the original timestamps. "
                    "If a subtitle is already in English, provide the corresponding Chinese translation, and vice versa. "
                    "For subtitles in any other language, keep the original text but also provide translations in both "
                    "English and Chinese.\n\n"
                    
                    "Process the following subtitles, ensuring translations are accurate and coherent, "
                    "and format the output as shown in the example. Note that the original timestamps should be preserved for each entry.\n\n"
                    
                    "Subtitles to process:\n"
                    f"{json.dumps(subtitles, indent=2, ensure_ascii=False)}\n\n"
                    
                    "Expected output format for each entry should be:\n"
                    "[\n"
                    "  {\n"
                    "    \"start\": \"timestamp\",\n"
                    "    \"end\": \"timestamp\",\n"
                    "    \"en\": \"English text\",\n"
                    "    \"zh\": \"Chinese text\",\n"
                    "    \"original lang key if exist\": \"Text in the original language, if not English or Chinese\"\n"
                    "  }\n"
                    "]\n\n"
                    "Please provide a complete and accurate translation and formatting for each subtitle entry."
                )

                # Constructing the messages with the optimized prompt
                messages = [
                    {
                        "role": "system",
                        "content": "Translate and merge mixed language subtitles into English and Chinese, providing coherent and accurate translations."
                    },
                    {
                        "role": "user",
                        "content": prompt_content
                    }
                ]

                # Sending the request to the OpenAI API
                client = openai.OpenAI()  # Initializing the OpenAI client
                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=messages
                )

                # Extracting and printing the AI's response
                ai_response = response.choices[0].message.content.strip()

                translated_subtitles = self.extract_and_parse_json(ai_response)
                self.validate_translated_subtitles(translated_subtitles)
                return translated_subtitles
            except (JSONParsingError, JSONValidationError) as e:
                print(f"Attempt {retries + 1} failed: {e}")

                # Append the response and error message for context
                messages.append({"role": "system", "content": ai_response})
                messages.append({"role": "user", "content": e.message})
                
                retries += 1
                if retries >= self.max_retries:
                    # Check if the combined_srt_path exists and remove it if it does
                    if os.path.exists(self.output_srt_path):
                        os.remove(self.output_srt_path)

                    # Now, safely create a hard link
                    try:
                        os.link(self.input_srt_path, self.output_srt_path)
                    except OSError as e:
                        print(f"Error creating hard link: {e}")

                    # raise



    def save_translated_subtitles_to_srt(self, translated_subtitles):
        """Save the translated subtitles to an SRT file."""
        srt_content = ""
        for index, subtitle in enumerate(translated_subtitles, start=1):
            srt_content += f"{index}\n{subtitle['start']} --> {subtitle['end']}\n{subtitle['zh']}\n{subtitle['en']}\n\n"
        with open(self.output_srt_path, 'w', encoding='utf-8') as file:
            file.write(srt_content)

    def process_subtitles(self):
        """Main process to load, translate, merge, and save subtitles."""
        subtitles = self.load_subtitles_from_json()
        translated_subtitles = self.translate_and_merge_subtitles(subtitles)
        self.save_translated_subtitles_to_srt(translated_subtitles)
        print("Subtitles have been processed and saved successfully.")


if __name__ == '__main__':
    
    # Example usage:
    input_json_path = '/home/lachlan/Projects/autopub-video-processing/autopub_video_processing/data/IMG_6276_mixed.json'
    output_srt_path = '/home/lachlan/Projects/autopub-video-processing/autopub_video_processing/data/translated_subtitles.srt'
    input_srt_path = '/home/lachlan/Projects/autopub-video-processing/autopub_video_processing/data/IMG_6276_mixed.srt'


    openai_client = OpenAI()
    subtitles_processor = SubtitlesTranslator(openai_client, input_json_path, input_srt_path, output_srt_path)
    subtitles_processor.process_subtitles()