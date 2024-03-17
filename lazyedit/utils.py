import json
import json5
from pprint import pprint
from PIL import Image, ImageDraw, ImageFont

sample_texts = {
    "English": "This is a sample English text that is designed to test the text wrapping capabilities of the ckjwrap library. The purpose is to see how well it can handle text from different languages, including English, and ensure that wrapping occurs correctly without breaking words inappropriately.",
    # "Japanese": "これはckjwrapライブラリのテキスト折り返し機能をテストするために設計されたサンプルの日本語テキストです。異なる言語のテキストをどの程度適切に扱えるか、そして単語を不適切に分割することなく正しく折り返しが行われるかどうかを確認することが目的です。さらに、このテキストはテキストラッピングのテストを継続しています。",
    "Japanese": "日月金木水火土学生山川愛情友達力美味時空海星雲雨風花雪国会話数家人生年安心出来世界平和夢希望工業科学技術歴史文化祭典会社経済政治法律教育健康医療食品安全環境資源エネルギー問題解決",
    "Chinese": "这是一个样本中文文本，旨在测试ckjwrap库的文本换行能力。目的是看看它如何能够正确处理不同语言的文本，包括中文，确保换行时不会不适当地拆分单词。此外，本文本继续测试文本换行功能。",
    "Arabic": "هذا نص عربي تجريبي مصمم لاختبار قدرات الفقرة في مكتبة ckjwrap. الغرض هو لرؤية كيف يمكنه التعامل مع نصوص من لغات مختلفة، بما في ذلك العربية، وضمان أن يتم الفقرة بشكل صحيح دون تقسيم الكلمات بشكل غير مناسب. بالإضافة إلى ذلك، يستمر هذا النص في اختبار قدرات الفقرة."
}


def get_text_size(text, font, max_width, max_height):
    test_canvas_size = (int(max_width), int(max_height))  # Canvas size based on max_width and max_height
    dummy_image = Image.new('RGB', test_canvas_size)
    draw = ImageDraw.Draw(dummy_image)
    return draw.textbbox((0, 0), text, font=font)[2:]

def find_font_size(text, font_path, max_width, max_height, start_size=360, step=2):
    font_size = start_size
    font = ImageFont.truetype(font_path, font_size)
    while True:
        text_width, text_height = get_text_size(text, font, max_width, max_height)
        if text_width <= max_width and text_height <= max_height:
            break
        font_size -= step
        if font_size <= 0:
            break
        font = ImageFont.truetype(font_path, font_size)
    return font_size



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



