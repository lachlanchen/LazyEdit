import os
import re


import openai
from packaging import version

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__}"
                     " is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")

# -- Now we can get to it
from openai import OpenAI
client = OpenAI()  # should use env variable OPENAI_API_KEY


import json
import json5
import traceback




# class SocialMediaVideoPublisher:
#     def __init__(self, openai_client):
#         self.client = openai_client

#     def generate_video_metadata(self, english_subtitles):
#         # Construct the prompt for the AI
#         prompt = (
#             "Based on the provided English subtitles from a video, please generate a suitable title, "
#             "a brief introduction, tags, and some English words that viewers can learn. "
#             "The title should be in Chinese and up to 20 characters, the introduction should be in Chinese "
#             "and up to 80 characters, there should be 10 tags related to the content of the video, "
#             "and 5 English words or phrases that are important for viewers to learn from the video. "
#             "Each word should be accompanied by timestamps indicating when it appears in the video.\n\n"
#             "English subtitles:\n" + english_subtitles + "\n\n"
#             "Please write the output in the following format:\n"
#             "{\"title\": \"\", \"description\": \"\", \"tags\": [], \"words_to_learn\": [{\"word\": \"\", \"time_stamps\": \"\"}]}"
#         )

#         # Define the request to OpenAI API
#         response = self.client.chat.completions.create(
#             model="gpt-4-1106-preview",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ]
#         )

#         # Extract the AI's response
#         ai_response = response.choices[0].message.content.strip()

#         # Parse the response as JSON
#         try:
#             result = json.loads(ai_response)
#         except json.JSONDecodeError:
#             print("Failed to decode the AI's response as JSON.")
#             return None

#         return result


class JSONParsingError(Exception):
    def __init__(self, message, json_string, user_message):
        super().__init__(message)

        print("JSON String: ")
        print(json_string)


        self.json_string = json_string
        self.user_message = user_message

class MetadataValidationError(Exception):
    def __init__(self, message, metadata):
        super().__init__(message)
        self.metadata = metadata

class SocialMediaVideoPublisher:
    def __init__(self, openai_client, max_retries=3):
        self.client = openai_client
        self.max_retries = max_retries
        self.subtitles2metadata_file = 'subtitles2metadata.json'
        self.subtitles2metadata = self.load_subtitles2metadata()

    def load_subtitles2metadata(self):
        if os.path.exists(self.subtitles2metadata_file):
            with open(self.subtitles2metadata_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            return []

    def save_subtitles2metadata(self):
        with open(self.subtitles2metadata_file, 'w', encoding='utf-8') as file:
            json.dump(self.subtitles2metadata, file, indent=4, ensure_ascii=False)

    def extract_and_parse_json(self, text):

        bracket_pattern = r'\{.*\}'
        matches = re.findall(bracket_pattern, text, re.DOTALL)

        if not matches:
            raise JSONParsingError("No JSON string found in text", text, text)

        json_string = matches[0]

        try:
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
            "tags", "words_to_learn", "cover"
        ]
        missing_fields = [field for field in required_fields if field not in metadata]
        if missing_fields:
            raise MetadataValidationError(f"Missing required fields: {', '.join(missing_fields)}", metadata)


    def generate_video_metadata(self, file_path_en, file_path_zh):

        with open(file_path_en, 'r', encoding='utf-8') as file:
            english_subtitles = file.read()

        with open(file_path_zh, 'r', encoding='utf-8') as file:
            chinese_subtitles = file.read()

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
                # # Construct the prompt for the AI
                # prompt = (
                #     "Based on the provided English subtitles from a video, please generate a suitable title, "
                #     "a brief introduction, tags, and some English words that viewers can learn. "
                #     "Also, suggest a timestamp for the best scene to use as a cover image for the video. "
                #     "The title should be in Chinese and up to 20 characters, the introduction should be in Chinese "
                #     "and up to 80 characters, there should be 10 tags related to the content of the video, "
                #     "5 English words or phrases that are important for viewers to learn from the video sorted by interestingness, "
                #     "and a cover timestamp indicating the best scene to use as the cover image. "
                #     "Each word should be accompanied by a single timestamp indicating when it appears in the video.\n\n"
                #     "English subtitles:\n" + english_subtitles + "\n\n"
                #     "Please write the output in the following format:\n"
                #     "{\"title\": \"\", \"description\": \"\", \"tags\": [], "
                #     "\"words_to_learn\": [{\"word\": \"\", \"time_stamps\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"}], \"cover\": \"HH:MM:SS,mmm\"}"
                # )

                # Construct the prompt for the AI
                prompt = (
                    "I want to publish this video on XiaoHongShu, Bilibili, Douyin and Youtube. "
                    "Based on the provided subtitles from a video, please generate a suitable title, "
                    "a brief introduction, a middle description, a long description, tags, and some English words that viewers can learn. "
                    "Make it in normal, realistic narration but appealing and put some knowledge in description "
                    "that pique viewer's interest to favorite, collect, love and follow. "
                    "(This is our secret. Don't let it be seen in the title or description per se. "
                    "Make it achieve this subconsiously. ) "
                    "Try to find instructions also in subtitles if exist. "
                    "Also, suggest a timestamp for the best scene to use as a cover image for the video. "
                    "The title should be in Chinese and up to 20 characters, the brief introduction should be in Chinese "
                    "and up to 80 characters, the middle description should be in Chinese and up to 250 characters, "
                    "the long description should be in Chinese and up to 1000 characters, there should be 10 tags related to the content of the video, "
                    "5 English words or phrases that are important for viewers to learn from the video sorted by interestingness, "
                    "and a cover timestamp indicating the best scene to use as the cover image. "
                    "Each word should be accompanied by a time stamps range indicating when it appears in the video.\n\n"
                    "English subtitles:\n" + english_subtitles + "\n\n"
                    "Chinese subtitles:\n" + chinese_subtitles + "\n\n"
                    "Please write the output in the following format:\n"
                    "{\"title\": \"\", \"brief_description\": \"\", \"middle_description\": \"\", \"long_description\": \"\", \"tags\": [], "
                    "\"words_to_learn\": [{\"word\": \"\", \"time_stamps\": \"HH:MM:SS,mmm --> HH:MM:SS,mmm\"}], \"cover\": \"HH:MM:SS,mmm\"}"
                )

                messages[-1]["content"] = prompt  # Update the actual prompt content


                print("Querying OpenAI...")

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
                
                # Save the prompt and response pair
                self.subtitles2metadata.append({
                    "english_subtitle_path": file_path_en,
                    "chinese_subtitle_path": file_path_zh,
                    "prompt": prompt,
                    "answer": ai_response
                })
                self.save_subtitles2metadata()

                return result  # Successfully parsed JSON, return the result

            # except JSONParsingError as e:
            #     error_message = f"JSON parsing failed on attempt {retries + 1}: {e}"
            #     print(error_message)
            #     traceback.print_exc()
            #     retries += 1  # Increment the retry count
                
            #     # Append the response and error message for context
            #     messages.append({"role": "system", "content": ai_response})
            #     messages.append({"role": "user", "content": error_message})
                
            #     if retries >= self.max_retries:
            #         raise JSONParsingError("Failed to parse JSON after maximum retries.", ai_response, error_message)
            except (JSONParsingError, MetadataValidationError) as e:
                error_message = f"Failed on attempt {retries + 1}: {e}"
                print(error_message)
                traceback.print_exc()
                retries += 1  # Increment the retry count
                
                # Append the response and error message for context
                messages.append({"role": "system", "content": ai_response})
                messages.append({"role": "user", "content": error_message})
                
                if retries >= self.max_retries:
                    raise e  # Re-raise the last exception (either JSONParsingError or MetadataValidationError)


        raise JSONParsingError("Reached maximum retries without success.", ai_response, messages[-1]["content"])


if __name__ == "__main__":

    from io import StringIO

    # Usage example
    openai_client = OpenAI()  # Make sure to authenticate your OpenAI client
    video_publisher = SocialMediaVideoPublisher(openai_client)
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


    result = video_publisher.generate_video_metadata(english_subtitles_file, chinese_subtitles_file)
    print(result)
