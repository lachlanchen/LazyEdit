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