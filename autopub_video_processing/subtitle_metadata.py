import os
import re
from datetime import datetime

from autopub_video_processing.openai_version_check import OpenAI



import json
import json5
import traceback

from autopub_video_processing.utils import JSONParsingError, JSONValidationError

def robust_json5_parse(json_str):
    # Attempt to handle unexpected newlines and unescaped double quotes
    json_str = ''.join(line.strip() if not line.strip().startswith('"') else line for line in json_str.split('\n'))

    # Try to parse the JSON string using json5 for more flexibility
    try:
        parsed_json = json5.loads(json_str)
        return parsed_json
    except ValueError as e:
        print(f'JSON Decode Error: {e}')
        return None




class Subtitle2Metadata:
    def __init__(self, openai_client, max_retries=3):
        self.client = openai_client
        self.max_retries = max_retries
        self.subtitles2metadata_file = 'subtitles2metadata.json'
        # self.subtitles2metadata = self.load_subtitles2metadata()

        self.subtitles2metadata_folder = 'subtitles2metadata'
        self.ensure_folder_exists(self.subtitles2metadata_folder)

    def ensure_folder_exists(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def get_filename(self, subtitle_path, lang):
        base_name = os.path.basename(subtitle_path)
        # Strip extension from base_name if necessary
        base_name = os.path.splitext(base_name)[0]
        datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{self.subtitles2metadata_folder}/{base_name}-{datetime_str}_{lang}.json"

    def save_subtitles2metadata(self, subtitle_path, prompt, ai_response, metatype="XiaoHongShu, Douyin, Bilibili", lang="en"):
        filename = self.get_filename(subtitle_path, lang=lang)
        data_to_save = {
            "mixed_subtitle_path": subtitle_path,
            "prompt": prompt,
            "answer": ai_response,
            "type": metatype
        }
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data_to_save, file, indent=4, ensure_ascii=False)


    # def load_subtitles2metadata(self):
    #     if os.path.exists(self.subtitles2metadata_file):
    #         with open(self.subtitles2metadata_file, 'r', encoding='utf-8') as file:
    #             return json.load(file)
    #     else:
    #         return []

    # def save_subtitles2metadata(self):
    #     with open(self.subtitles2metadata_file, 'w', encoding='utf-8') as file:
    #         json.dump(self.subtitles2metadata, file, indent=4, ensure_ascii=False)

    def extract_and_parse_json(self, text):

        bracket_pattern = r'\{.*\}'
        matches = re.findall(bracket_pattern, text, re.DOTALL)

        if not matches:
            raise JSONParsingError("No JSON string found in text", text, text)

        json_string = matches[0]

        try:
            # json_string = ''.join(line.strip() if not line.strip().startswith('"') else line for line in json_string.split('\n'))
            json_string = json_string.replace('\n', '')
            parsed_json = json5.loads(json_string)
            if len(parsed_json) == 0:
                raise JSONParsingError("Parsed JSON string is empty", json_string, text)

            return parsed_json
        except ValueError as e:
            traceback.print_exc()
            raise JSONParsingError(f"JSON Decode Error: {e}", json_string, text)

    def validate_metadata(self, metadata):
        required_fields = [
            "title", "brief_description", "middle_description", "long_description",
            "tags", "english_words_to_learn", "cover"
        ]
        missing_fields = [field for field in required_fields if field not in metadata]
        if missing_fields:
            raise JSONValidationError(f"Missing required fields: {', '.join(missing_fields)}", metadata)


    def generate_video_metadata(self, subtitle_path):
        result_zh = self.generate_video_metadata_zh(subtitle_path)
        try:
            result_en = self.generate_video_metadata_en(subtitle_path)
            result_zh["english_version"] = result_en
        except:
            result_zh["english_version"] = result_zh.copy()

        try:
            result_zh["english_words_to_learn_zh"] = result_zh["english_words_to_learn"].copy()
            result_zh["english_words_to_learn"] = result_en["english_words_to_learn"]
        except:
            pass

        return result_zh


    def generate_video_metadata_zh(self, subtitle_path):

        with open(subtitle_path, 'r', encoding='utf-8') as file:
            mixed_subtitles = file.read()

        retries = 0
        messages = [
            {"role": "system", "content": (
                "My name is OpenAI. I am an expert of social media who can help vlogers add influences, grow fans, "
                "reach out audiences and create values. "
                "I can help vlogers influence people subconsiously. "
            )},
            {"role": "user", "content": ""}  # Placeholder for the actual prompt
        ]

        while retries < self.max_retries:
            try:

                # Construct the prompt for the AI
                prompt = (
                    "I want to publish this video on XiaoHongShu, Bilibili, Douyin. "
                    "Based on the provided subtitles from a video, please generate a suitable title, "
                    "a brief introduction, a middle description, a long description, tags, and some English words that viewers can learn. "
                    "Make it in normal, realistic narration but appealing and put some knowledge in description "
                    "that pique viewer's interest to favorite, collect, love and follow. "
                    "(This is our secret. Don't let it be seen in the title or description per se. "
                    "Make it achieve this subconsiously. ) "
                    "Try to find instructions also in subtitles if exist. "
                    "Also, suggest a timestamp for the best scene to use as a cover image for the video. "
                    "The title should be in Chinese and up to 20 characters, the brief description should be in Chinese "
                    "and up to 80 characters, the middle description should be in Chinese and up to 250 characters, "
                    "the long description should be in Chinese and up to 1000 characters, there should be 10 tags related to the content of the video, "
                    "Five pure ENGLISH words or phrases that are important for viewers to learn from the video sorted by interestingness, "
                    "and a cover timestamp indicating the best scene to use as the cover image. "
                    "Each word should be accompanied by a time stamps range indicating when it appears in the video.\n\n"
                    "Return correct format result with imagination even subtitles is little or even empty. "
                    "Multilingual subtitles:\n" + mixed_subtitles + "\n\n"
                    "Please write the output in the following format:\n"
                    # "{\"title\": \"\", \"brief_description\": \"\", \"middle_description\": \"\", \"long_description\": \"\", \"tags\": [], "
                    # "\"english_words_to_learn\": [{\"word\": \"\", \"time_stamps\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"}], \"cover\": \"HH:MM:SS,mmm\"}"
                    "{\n"
                    "  \"title\": \"\",\n"
                    "  \"brief_description\": \"\",\n"
                    "  \"middle_description\": \"\",\n"
                    "  \"long_description\": \"\",\n"
                    "  \"tags\": [],\n"
                    "  \"english_words_to_learn\": [\n"
                    "    {\n"
                    "      \"word\": \"\",\n"
                    "      \"time_stamps\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"\n"
                    "    }\n"
                    "  ],\n"
                    "  \"cover\": \"HH:MM:SS,mmm\"\n"
                    "}"
                )

                messages[-1]["content"] = prompt  # Update the actual prompt content


                print("Querying OpenAI (Chinese) ...")

                # Define the request to OpenAI API
                response = self.client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=messages
                )

                # Extract the AI's response
                ai_response = response.choices[0].message.content.strip()

                # Extract and parse the JSON part of the AI's response
                result = self.extract_and_parse_json(ai_response)

                # Validate the parsed JSON data
                self.validate_metadata(result)
                
                # # Save the prompt and response pair
                # self.subtitles2metadata.append({
                #     "mixed_subtitle_path": subtitle_path,
                #     "prompt": prompt,
                #     "answer": ai_response,
                #     "type": "XiaoHongShu, Douyin, Bilibili"
                # })
                # self.save_subtitles2metadata()
                self.save_subtitles2metadata(subtitle_path, prompt, ai_response, metatype="XiaoHongShu, Douyin, Bilibili", lang="zh")

                return result  # Successfully parsed JSON, return the result

            
            except (JSONParsingError, JSONValidationError) as e:
                error_message = f"Failed on attempt {retries + 1}: {e}"
                print(error_message)
                traceback.print_exc()
                retries += 1  # Increment the retry count
                
                # Append the response and error message for context
                messages.append({"role": "system", "content": ai_response})
                messages.append({"role": "user", "content": e.message})
                
                if retries >= self.max_retries:
                    raise e  # Re-raise the last exception (either JSONParsingError or JSONValidationError)


        raise JSONParsingError("Reached maximum retries without success.", ai_response, messages[-1]["content"])

    def generate_video_metadata_en(self, subtitle_path):

        with open(subtitle_path, 'r', encoding='utf-8') as file:
            mixed_subtitles = file.read()


        retries = 0
        messages = [
            {"role": "system", "content": (
                "My name is OpenAI. I am an expert of social media who can help Youtube vlogers add influences, grow fans, "
                "reach out audiences and create values. "
                "I can help vlogers influence people subconsiously. "
            )},
            {"role": "user", "content": ""}  # Placeholder for the actual prompt
        ]

        while retries < self.max_retries:
            try:

                # Construct the prompt for the AI
                prompt = (
                    "I want to publish this video on Youtube. "
                    "Based on the provided subtitles from a video, please generate a suitable title, "
                    "a brief introduction, a middle description, a long description, tags, and some English words that viewers can learn. "
                    "Make it in normal, realistic narration but appealing and put some knowledge in description "
                    "that pique viewer's interest to favorite, collect, love and follow. "
                    "(This is our secret. Don't let it be seen in the title or description per se. "
                    "Make it achieve this subconsiously. ) "
                    "Try to find instructions also in subtitles if exist. "
                    "Also, suggest a timestamp for the best scene to use as a cover image for the video. "
                    "The title should be in English and up to 20 words, the brief description should be in English "
                    "and up to 80 words, the middle description should be in English and up to 250 words, "
                    "the long description should be in English and up to 1000 words, there should be 10 tags related to the content of the video, "
                    "Five pure ENGLISH words that are important for viewers to learn from the video sorted by interestingness, "
                    "and a cover timestamp indicating the best scene to use as the cover image. "
                    "Each word should be accompanied by a time stamps range indicating when it appears in the video.\n\n"
                    "Return correct format result with imagination even subtitles is little or even empty. "
                    "Multilingual subtitles:\n" + mixed_subtitles + "\n\n"
                    "Please write the output in the following format:\n"
                    # "{\"title\": \"\", \"brief_description\": \"\", \"middle_description\": \"\", \"long_description\": \"\", \"tags\": [], "
                    # "\"english_words_to_learn\": [{\"word\": \"\", \"time_stamps\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"}], \"cover\": \"HH:MM:SS,mmm\"}"
                    "{\n"
                    "  \"title\": \"\",\n"
                    "  \"brief_description\": \"\",\n"
                    "  \"middle_description\": \"\",\n"
                    "  \"long_description\": \"\",\n"
                    "  \"tags\": [],\n"
                    "  \"english_words_to_learn\": [\n"
                    "    {\n"
                    "      \"word\": \"\",\n"
                    "      \"time_stamps\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"\n"
                    "    }\n"
                    "  ],\n"
                    "  \"cover\": \"HH:MM:SS,mmm\"\n"
                    "}"
                )

                messages[-1]["content"] = prompt  # Update the actual prompt content


                print("Querying OpenAI (English) ...")

                # Define the request to OpenAI API
                response = self.client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=messages
                )

                # Extract the AI's response
                ai_response = response.choices[0].message.content.strip()

                # Extract and parse the JSON part of the AI's response
                result = self.extract_and_parse_json(ai_response)

                # Validate the parsed JSON data
                self.validate_metadata(result)
                
                # # Save the prompt and response pair
                # self.subtitles2metadata.append({
                #     "mixed_subtitle_path": subtitle_path,
                #     "prompt": prompt,
                #     "answer": ai_response,
                #     "type": "Youtube"
                # })
                # self.save_subtitles2metadata()

                self.save_subtitles2metadata(subtitle_path, prompt, ai_response, metatype="Youtube", lang="en")

                return result  # Successfully parsed JSON, return the result

            
            except (JSONParsingError, JSONValidationError) as e:
                error_message = f"Failed on attempt {retries + 1}: {e}"
                print(error_message)
                traceback.print_exc()
                retries += 1  # Increment the retry count
                
                # Append the response and error message for context
                messages.append({"role": "system", "content": ai_response})
                messages.append({"role": "user", "content": error_message})
                
                if retries >= self.max_retries:
                    raise e  # Re-raise the last exception (either JSONParsingError or JSONValidationError)


        raise JSONParsingError("Reached maximum retries without success.", ai_response, messages[-1]["content"])


    

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
