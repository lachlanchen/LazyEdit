import os
import json
import traceback
from datetime import datetime
from openai import OpenAI


class JSONValidationError(Exception):
    def __init__(self, message, json_string=None):
        super().__init__(message)
        self.message = message
        self.json_string = json_string


class JSONParsingError(Exception):
    def __init__(self, message, json_string, text):
        super().__init__(message)
        print("The failed JSON string: \n\n")
        print(json_string)
        self.message = message
        self.json_string = json_string
        self.text = text


class OpenAIRequestJSONBase:
    def __init__(self, use_cache=True, max_retries=3, cache_dir='cache'):
        self.client = OpenAI()  # Assume correct initialization with API key
        self.max_retries = max_retries
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        self.ensure_dir_exists(self.cache_dir)

    def ensure_dir_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def get_cache_file_path(self, prompt, filename=None):
        if filename is None:
            filename = f"{abs(hash(prompt))}.json"
    
        cache_path = os.path.join(self.cache_dir, filename)
        print("cache_path: ", cache_path)
        cache_dir = os.path.dirname(cache_path)
        print("cache_dir: ", cache_dir)
        os.makedirs(cache_dir, exist_ok=True)
        return cache_path

    def save_to_cache(self, prompt, response, filename=None):
        file_path = self.get_cache_file_path(prompt, filename=filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({"prompt": prompt, "response": response}, file, ensure_ascii=False, indent=4)

    def load_from_cache(self, prompt, filename=None):
        file_path = self.get_cache_file_path(prompt, filename=filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                cached_data = json.load(file)
                return cached_data["response"]
        return None

    def send_request_with_json_schema(self, prompt, json_schema, system_content="You are an AI.", filename=None, schema_name="response"):
        """
        Send a request to OpenAI with structured JSON schema validation.
        
        Args:
            prompt: The user prompt
            json_schema: The JSON schema to validate against
            system_content: System message content
            filename: Optional cache filename
            schema_name: Name for the JSON schema
        
        Returns:
            Parsed JSON response that conforms to the schema
        """
        retries = 0
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]

        print("self.use_cache: ", self.use_cache)

        if self.use_cache:
            cached_response = self.load_from_cache(prompt, filename=filename)
            if cached_response:
                print("OpenAI cache found. ")
                return cached_response

        while retries < self.max_retries:
            try:
                print(f"Querying OpenAI with structured outputs (attempt {retries + 1})...")
                
                # Use the new Structured Outputs API
                response = self.client.chat.completions.create(
                    model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=messages,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema_name,
                            "strict": True,
                            "schema": json_schema
                        }
                    }
                )

                # Check for refusal
                message = response.choices[0].message
                if message.refusal:
                    raise Exception(f"Request was refused: {message.refusal}")

                # Parse the structured response
                parsed_response = json.loads(message.content)
                
                # Save to cache
                if self.use_cache:
                    self.save_to_cache(prompt, parsed_response, filename=filename)
                
                return parsed_response

            except json.JSONDecodeError as e:
                error_msg = f"Failed to decode JSON response: {e}"
                print(error_msg)
                traceback.print_exc()
                retries += 1
                
                if retries < self.max_retries:
                    messages.append({"role": "system", "content": f"Previous response had JSON parsing error: {error_msg}. Please provide a valid JSON response."})
                
            except Exception as e:
                error_msg = f"OpenAI API error: {e}"
                print(error_msg)
                traceback.print_exc()
                retries += 1
                
                if retries < self.max_retries:
                    messages.append({"role": "system", "content": f"Previous request failed: {error_msg}. Please try again."})

        raise Exception("Maximum retries reached without success.")

    def send_request_with_retry(self, prompt, system_content="You are an AI.", sample_json=None, filename=None):
        """
        Legacy method for backward compatibility. 
        Converts sample_json to a JSON schema and uses structured outputs.
        """
        if sample_json is None:
            # Fallback to basic JSON object format if no schema provided
            json_schema = {
                "type": "object",
                "additionalProperties": True
            }
        else:
            # Convert sample JSON to a JSON schema
            json_schema = self._convert_sample_to_schema(sample_json)
        
        return self.send_request_with_json_schema(
            prompt=prompt,
            json_schema=json_schema,
            system_content=system_content,
            filename=filename
        )

    def _convert_sample_to_schema(self, sample_json):
        """
        Convert a sample JSON object to a JSON schema.
        This is a simplified conversion - for complex schemas, 
        you should define them explicitly.
        """
        def get_type_schema(value):
            if isinstance(value, str):
                return {"type": "string"}
            elif isinstance(value, int):
                return {"type": "integer"}
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, list):
                if len(value) > 0:
                    return {
                        "type": "array",
                        "items": get_type_schema(value[0])
                    }
                else:
                    return {
                        "type": "array",
                        "items": {"type": "object", "additionalProperties": True}
                    }
            elif isinstance(value, dict):
                properties = {}
                required = []
                for key, val in value.items():
                    properties[key] = get_type_schema(val)
                    required.append(key)
                return {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False
                }
            else:
                return {"type": "string"}

        return get_type_schema(sample_json)

    # Legacy methods for backward compatibility
    def validate_json(self, json_data, sample_json):
        """Legacy method - not needed with structured outputs but kept for compatibility"""
        pass

    def parse_response(self, response):
        """Legacy method - not needed with structured outputs but kept for compatibility"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise JSONParsingError("Failed to parse JSON response", response, response)