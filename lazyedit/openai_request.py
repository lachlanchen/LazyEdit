import os
import json
import traceback
import glob
import re
import csv
from datetime import datetime
from openai import OpenAI

class JSONParsingError(Exception):
    def __init__(self, message, json_string, text):
        super().__init__(message)
        self.message = message
        self.json_string = json_string
        self.text = text

class OpenAIRequestBase:
    def __init__(self, use_cache=True, max_retries=3, cache_dir='cache'):
        self.client = OpenAI()  # Assume correct initialization with API key
        self.max_retries = max_retries
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        self.ensure_dir_exists(self.cache_dir)

    def ensure_dir_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def get_cache_file_path(self, prompt):
        filename = f"{abs(hash(prompt))}.json"
        return os.path.join(self.cache_dir, filename)

    def save_to_cache(self, prompt, response):
        file_path = self.get_cache_file_path(prompt)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({"prompt": prompt, "response": response}, file, ensure_ascii=False, indent=4)

    def load_from_cache(self, prompt):
        file_path = self.get_cache_file_path(prompt)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                cached_data = json.load(file)
                return cached_data["response"]
        return None

    def send_request_with_retry(self, prompt, system_content="You are an AI."):
        retries = 0
        # messages = [{"role": "system", "content": system_content}, {"role": "user", "content": prompt}]
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]

        if self.use_cache:
            cached_response = self.load_from_cache(prompt)
            if cached_response:
                return cached_response

        while retries < self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=os.environ.get("OPENAI_MODEL", "gpt-4-0125-preview"),
                    messages=messages
                )
                ai_response = response.choices[0].message.content.strip()
                parsed_response = self.parse_response(ai_response)
                self.save_to_cache(prompt, parsed_response)
                return parsed_response
            except Exception as e:
                traceback.print_exc()
                retries += 1
                messages.append({"role": "system", "content": ai_response})
                messages.append({"role": "system", "content": str(e)})

        raise Exception("Maximum retries reached without success.")

    def parse_response(self, response):
        first_dict_index = response.find('{')
        first_list_index = response.find('[')
        if first_dict_index == -1 and first_list_index == -1:
            raise JSONParsingError("No JSON structure found.", response, response)
        
        if (first_dict_index < first_list_index) or (first_list_index == -1):
            parse_pattern = r'\{.*\}'
        else:
            parse_pattern = r'\[.*\]'

        matches = re.findall(parse_pattern, response, re.DOTALL)
        if not matches:
            raise JSONParsingError("No matching JSON structure found.", response, response)

        json_string = matches[0]
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise JSONParsingError("Failed to decode JSON.", json_string, response)