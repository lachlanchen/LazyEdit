import json
import json5
from pprint import pprint

def safe_pretty_print(json_str):
    try:
        # Try to directly parse and pretty-print the JSON string
        parsed_json = json5.loads(json_str)
        # print(json.dumps(parsed_json, indent=2, ensure_ascii=False))

        pprint(parsed_json)


    except ValueError as e:
        print("JSONDecodeError: Could not parse the entire JSON string.")
        print("Attempting to print as much as possible...\n")
        
        # Fallback: Attempt to manually parse and print parts of the JSON
        try:
            # Very basic heuristic: split by '}, {' to handle simple cases
            parts = json_str.split('}, {')
            for part in parts:
                # Ensuring each part is properly enclosed in braces
                cleaned_part = part
                if not part.startswith('{'):
                    cleaned_part = '{' + part
                if not part.endswith('}'):
                    cleaned_part += '}'
                try:
                    # Try to parse each part individually
                    parsed_part = json.loads(cleaned_part)
                    print(json.dumps(parsed_part, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    print(f"Could not parse part: {cleaned_part}")
        except Exception as e:
            print(f"Error during fallback parsing: {e}")
            print(json_str)



class JSONParsingError(Exception):
    def __init__(self, message, json_string, user_message):
        super().__init__(message)

        print("JSON String: ")
        print(json_string)

        self.message = message        
        self.json_string = json_string
        self.user_message = user_message

class JSONValidationError(Exception):
    def __init__(self, message, parsed_json):
        super().__init__(message)

        self.message = message
        self.parsed_json = parsed_json