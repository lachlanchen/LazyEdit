import os
import re
from datetime import datetime

from lazyedit.openai_version_check import OpenAI



import json
import json5
import traceback

from lazyedit.utils import JSONParsingError, JSONValidationError


import glob
from concurrent.futures import ThreadPoolExecutor


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
    def __init__(self, openai_client, use_cache=False, max_retries=3):
        self.client = openai_client
        self.max_retries = max_retries
        self.subtitles2metadata_file = 'subtitles2metadata.json'
        # self.subtitles2metadata = self.load_subtitles2metadata()

        self.subtitles2metadata_folder = 'subtitles2metadata'
        self.ensure_folder_exists(self.subtitles2metadata_folder)

        self.use_cache = use_cache

    def ensure_folder_exists(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def get_filename(self, subtitle_path, lang):
        base_name = os.path.basename(subtitle_path)
        # Strip extension from base_name if necessary
        base_name = os.path.splitext(base_name)[0]
        datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{self.subtitles2metadata_folder}/{base_name}-{datetime_str}_{lang}.json"

    def save_subtitles2metadata(self, subtitle_path, prompt, ai_response, metatype="XiaoHongShu", lang="en"):
        filename = self.get_filename(subtitle_path, lang=lang)
        data_to_save = {
            "mixed_subtitle_path": subtitle_path,
            "prompt": prompt,
            "answer": ai_response,
            "type": metatype
        }
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data_to_save, file, indent=4, ensure_ascii=False)


    def load_latest_subtitles2metadata(self, subtitle_path, metatype="XiaoHongShu", lang="en"):
        base_name = os.path.basename(subtitle_path)
        base_name = os.path.splitext(base_name)[0]
        pattern = f"{self.subtitles2metadata_folder}/{base_name}-*_{lang}.json"
        files = glob.glob(pattern)
        if not files:
            return None  # No cache available

        # Find the latest file based on the naming convention
        latest_file = max(files, key=os.path.getctime)
        with open(latest_file, 'r', encoding='utf-8') as file:
            cached_data = json.load(file)


        # print(cached_data)
        # return json.dumps(cached_data["answer"], indent=4, ensure_ascii=False)
        return cached_data["answer"]#["answer"]


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

    # def validate_metadata(self, metadata):
    #     required_fields = [
    #         "title", "brief_description", "middle_description", "long_description",
    #         "tags", "english_words_to_learn", "teaser", "cover"
    #     ]
    #     missing_fields = [field for field in required_fields if field not in metadata]
    #     if missing_fields:
    #         raise JSONValidationError(f"Missing required fields: {', '.join(missing_fields)}", metadata)

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
        required_fields = [
            "title", "brief_description", "middle_description", "long_description",
            "tags", "english_words_to_learn", "teaser", "cover"
        ]
        missing_fields = [field for field in required_fields if field not in metadata]
        if missing_fields:
            raise JSONValidationError(f"Missing required fields: {', '.join(missing_fields)}", metadata)

        # Validate teaser timestamps
        if 'teaser' in metadata:
            start, end = metadata['teaser'].split(" --> ")
            metadata['teaser'] = " --> ".join(self.switch_timestamps_if_necessary(start, end))

        # Validate english_words_to_learn timestamp_range
        if 'english_words_to_learn' in metadata:
            for word_info in metadata['english_words_to_learn']:
                if 'timestamp_range' in word_info:
                    start, end = word_info['timestamp_range'].split(" --> ")
                    word_info['timestamp_range'] = " --> ".join(self.switch_timestamps_if_necessary(start, end))


    # def generate_video_metadata(self, subtitle_path):
    #     result_zh = self.generate_video_metadata_zh(subtitle_path)
    #     result_en = self.generate_video_metadata_en(subtitle_path)
        
    #     try:
    #         result_zh["english_version"] = result_en
    #     except:
    #         result_zh["english_version"] = result_zh.copy()

    #     try:
    #         result_zh["english_words_to_learn_zh"] = result_zh["english_words_to_learn"].copy()
    #         result_zh["english_words_to_learn"] = result_en["english_words_to_learn"]
    #     except:
    #         pass

    #     return result_zh

    def generate_video_metadata(self, subtitle_path):
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Initiate both tasks in parallel
            future_zh = executor.submit(self.generate_video_metadata_zh, subtitle_path)
            future_en = executor.submit(self.generate_video_metadata_en, subtitle_path)

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
                    "I want to publish this video on XiaoHongShu, Bilibili, Douyin. \n\n"

                    # "My channel name is LazyingArt懒人艺术. I am 陈苗. I strive to"
                    # "help people eliminate anxiety, learn language (zh, en, ja, ar) and embrace simple mindset, thinking, attitude "
                    # "by sharing real life (cooking, working-out, scientific esearch) without filters, coding skills and meditation. "
                    # "Most of my videos are casual and free of purpose "
                    # "as an attempt to mitigate effect of Goodhart's Law: "
                    # "(Using clickbait, sowing anxiety, diseminating seduction, catering audiences's pleasure) "
                    # "When a measure becomes a target, it ceases to be a good measure. "
                    # "(Don't explicitly put this in description. Focus on the subtitles. "
                    # "Blend it with the title and description subconsiously.)\n\n"

                    # "Welcome to 陈苗LazyingArt懒人艺术, the sanctuary where authenticity meets simplicity. "
                    # "I'm 陈苗, your guide on this journey to a more serene and enriched life. "
                    # "Through the lens of my everyday experiences, from the simplicity of cooking to the dedication of working out, "
                    # "from the rigor of scientific research to the tranquility of meditation, I invite you to explore the real essence of life with me. "
                    # "My channel is a haven for those seeking to alleviate anxiety, dive into the depths of languages (Chinese, English, Japanese, Arabic), "
                    # "and cultivate a mindset focused on simplicity and clarity."
                    # "Here, every video is a step away from the noise—crafted deliberately casual and with a purpose that transcends mere content consumption."
                    # " We sidestep the traps of Goodhart's Law by eschewing clickbait, avoiding the creation of anxiety, steering clear of seduction, "
                    # "and never merely pandering to the pleasure of the audience. Instead, we embrace the art of 'Lazying'—living fully, learning deeply, "
                    # "and loving the simplicity of our real, unfiltered lives."
                    # "Join me, and let's embark on this journey together, fostering a space where learning, growth, and peace flourish naturally."
                    # "(Don't explicitly put this in description. Foucus on the subtitles. Blend it with the title and description subconsiously.)\n\n"


                    "Based on the provided subtitles from a video, please generate a suitable title, "
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
                    # "and a cover timestamp indicating the best scene to use as the cover image. "

                    "Try to find instructions also in subtitles if exist. \n\n"
                    
                    "Return correct format result with imagination even subtitles is little or even empty. \n\n"

                    "Multilingual subtitles:\n" + mixed_subtitles + "\n\n"
                    
                    "Based on the subtitles, please output in the following JSON format:\n"
                    # "{\"title\": \"\", \"brief_description\": \"\", \"middle_description\": \"\", \"long_description\": \"\", \"tags\": [], "
                    # "\"english_words_to_learn\": [{\"word\": \"\", \"timestamp_range\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"}], \"cover\": \"HH:MM:SS,mmm\"}"
                    "```json"
                    "{\n"
                    "  \"title\": \"\",\n"
                    "  \"brief_description\": \"\",\n"
                    "  \"middle_description\": \"\",\n"
                    "  \"long_description\": \"\",\n"
                    "  \"tags\": [],\n"
                    "  \"english_words_to_learn\": [\n"
                    "    {\n"
                    "      \"word\": \"\",\n"
                    "      \"timestamp_range\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"\n"
                    "    }\n"
                    "  ],\n"
                    "  \"teaser\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\",\n"
                    "  \"cover\": \"HH:MM:SS,mmm\"\n"
                    "}"
                    "```"
                )

                ai_response = None
                if self.use_cache:
                    ai_response = self.load_latest_subtitles2metadata(subtitle_path, lang="zh")
                
                if not self.use_cache or not ai_response:

                    messages[1]["content"] = prompt  # Update the actual prompt content


                    print("Querying OpenAI (Chinese) ...")

                    # Define the request to OpenAI API
                    response = self.client.chat.completions.create(
                        model=os.environ.get("OPENAI_MODEL", "gpt-4-0125-preview"),
                        messages=messages
                    )

                    # Extract the AI's response
                    ai_response = response.choices[0].message.content.strip()


                print(ai_response)

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
                self.save_subtitles2metadata(subtitle_path, prompt, ai_response, metatype="XiaoHongShu", lang="zh")

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
                    "I want to publish this video on Youtube. \n\n"

                    # "I am Lachlan Chen. My channel name is The Art of Lazying. I strive to"
                    # "help people eliminate anxiety, learn language (zh, en, ja, ar) and embrace simple mindset, thinking, attitude "
                    # "by sharing real life (cooking, working-out, scientific esearch) without filters, coding skills and meditation. "
                    # "Most of my videos are casual and free of purpose. "
                    # " as an attempt to mitigate effect of Goodhart's Law: "
                    # "(Using clickbait, sowing anxiety, diseminating seduction, catering audiences's pleasure) "
                    # "When a measure becomes a target, it ceases to be a good measure. "
                    # "(Don't explicitly put this in description. Focus on the subtitles. "
                    # "Blend it with the title and description subconsiously.)\n\n"

                    # "Welcome to The Art of Lazying, the sanctuary where authenticity meets simplicity. "
                    # "I'm Lachlan Chen, your guide on this journey to a more serene and enriched life. "
                    # "Through the lens of my everyday experiences, from the simplicity of cooking to the dedication of working out, "
                    # "from the rigor of scientific research to the tranquility of meditation, I invite you to explore the real essence of life with me. "
                    # "My channel is a haven for those seeking to alleviate anxiety, dive into the depths of languages (Chinese, English, Japanese, Arabic), "
                    # "and cultivate a mindset focused on simplicity and clarity."
                    # "Here, every video is a step away from the noise—crafted deliberately casual and with a purpose that transcends mere content consumption."
                    # " We sidestep the traps of Goodhart's Law by eschewing clickbait, avoiding the creation of anxiety, steering clear of seduction, "
                    # "and never merely pandering to the pleasure of the audience. Instead, we embrace the art of 'Lazying'—living fully, learning deeply, "
                    # "and loving the simplicity of our real, unfiltered lives."
                    # "Join me, and let's embark on this journey together, fostering a space where learning, growth, and peace flourish naturally."
                    # "(Don't explicitly put this in description. Foucus on the subtitles. Blend it with the title and description subconsiously.)\n\n"

                    "Based on the provided subtitles from a video, please generate a suitable title, "
                    "a brief introduction, a middle description, a long description, tags, "
                    "some English words that viewers can learn, teaser range, and a cover timestamp. "
                    "\n\n"

                    "Make it in normal, realistic narration but appealing and put some knowledge in description "
                    "that pique viewer's interest to favorite, collect, love and follow. "
                    "(This is our secret. Don't let it be seen in the title or description per se. "
                    "Make it achieve this subconsiously. ) "
                    "\n\n"

                    "The title should be in English and up to 20 words, the brief description should be in English "
                    "and up to 80 words, the middle description should be in English and up to 250 words, "
                    "the long description should be in English and up to 500 words, there should be 10 tags related to the content of the video, "
                    "Five pure ENGLISH words that are important for viewers to learn from the video sorted by interestingness, "
                    "Each word should be accompanied by a timestamp range indicating when it appears in the video."
                    "Give 2~4 seconds timestamp range which can reflect the essense of the video as teaser. "
                    "Also, suggest a timestamp for the best scene to use as a cover image for the video. "
                    # "and a cover timestamp indicating the best scene to use as the cover image. "
                    "\n\n"

                    "Try to find instructions also in subtitles if exist. \n\n"

                    "Return correct format result with imagination even subtitles is little or even empty. \n\n"

                    "Multilingual subtitles:\n" + mixed_subtitles + "\n\n"
                    "Based on the subtitels, please output in the following JSON format:\n"
                    # "{\"title\": \"\", \"brief_description\": \"\", \"middle_description\": \"\", \"long_description\": \"\", \"tags\": [], "
                    # "\"english_words_to_learn\": [{\"word\": \"\", \"timestamp_range\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"}], \"cover\": \"HH:MM:SS,mmm\"}"
                    "```json"
                    "{\n"
                    "  \"title\": \"\",\n"
                    "  \"brief_description\": \"\",\n"
                    "  \"middle_description\": \"\",\n"
                    "  \"long_description\": \"\",\n"
                    "  \"tags\": [],\n"
                    "  \"english_words_to_learn\": [\n"
                    "    {\n"
                    "      \"word\": \"\",\n"
                    "      \"timestamp_range\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"\n"
                    "    }\n"
                    "  ],\n"
                    "  \"teaser\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\",\n"
                    "  \"cover\": \"HH:MM:SS,mmm\"\n"
                    "}"
                    "```"
                )

                ai_response = None
                if self.use_cache:
                    ai_response = self.load_latest_subtitles2metadata(subtitle_path, lang="en")
                
                if not self.use_cache or not ai_response:

                    messages[1]["content"] = prompt  # Update the actual prompt content


                    print("Querying OpenAI (English) ...")

                    # Define the request to OpenAI API
                    response = self.client.chat.completions.create(
                        model=os.environ.get("OPENAI_MODEL", "gpt-4-0125-preview"),
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
