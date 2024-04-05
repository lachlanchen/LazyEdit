import json
import json5
import re
import traceback
import openai

from packaging import version
import json
import os

from concurrent.futures import ThreadPoolExecutor, as_completed



from lazyedit.openai_version_check import OpenAI


from lazyedit.utils import JSONParsingError, JSONValidationError
from lazyedit.utils import safe_pretty_print, sample_texts, find_font_size
from lazyedit.openai_request import OpenAIRequestBase
from lazyedit.languages import LANGUAGES, TO_LANGUAGE_CODE

from datetime import datetime
from pprint import pprint

import cjkwrap

import glob

import numpy as np

import unicodedata



class SubtitlesTranslator(OpenAIRequestBase):
    def __init__(self, 
        openai_client, 
        input_json_path, 
        input_sub_path, 
        output_json_path,
        output_sub_path,
        video_length=None,
        video_width=1080,
        video_height=1920,
        max_retries=3,
        use_cache=False,
        *args, **kwargs
    ):
        kwargs["use_cache"] = use_cache
        kwargs["max_retries"] = max_retries

        super().__init__(*args, **kwargs)


        self.client = openai_client
        self.input_json_path = input_json_path
        self.input_sub_path = input_sub_path
        self.output_json_path = output_json_path
        self.output_sub_path = output_sub_path

        self.base_filename = os.path.splitext(os.path.basename(self.input_json_path))[0]
        self.datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.video_length = video_length
        self.video_width = video_width
        self.video_height = video_height
        self.base_width = 1920
        self.base_height = 1080

        self.wrapping_limit_half_width_default = 80  # Default wrapping_limit_half_width for landscape
        self.portrait_scale = 0.7   

        
        if not self.is_video_landscape:
            self.wrapping_limit_half_width_default = int(self.wrapping_limit_half_width_default * 0.5)  # Adjust wrapping_limit_half_width for portrait videos


        # self.is_video_landscape = video_width > video_height
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        self.translation_log_folder = 'translation_logs'

        self.subtitles = None

        # self.max_retries = max_retries
        # self.use_cache = use_cache

        self.flags = {
            'zh': '🇨🇳',  # China for Mandarin
            'en': '🇬🇧',  # United Kingdom for English
            'ja': '🇯🇵',  # Japan
            'ar': '🇸🇦',  # Saudi Arabia for Arabic
            'ko': '🇰🇷',  # Korea for Korean
            'es': '🇪🇸',  # Spain for Spanish
            'vi': '🇻🇳',  # Vietnam
            'fr': '🇫🇷',  # France
            'de': '🇩🇪',  # Germany for German
            'it': '🇮🇹',  # Italy for Italian
            'ru': '🇷🇺',  # Russia for Russian
            'pt': '🇵🇹',  # Portugal for Portuguese (Note: Brazil might use 🇧🇷 depending on the context)
            'nl': '🇳🇱',  # Netherlands for Dutch
            'sv': '🇸🇪',  # Sweden for Swedish
            'no': '🇳🇴',  # Norway for Norwegian
            'da': '🇩🇰',  # Denmark for Danish
            'fi': '🇫🇮',  # Finland for Finnish
            'pl': '🇵🇱',  # Poland for Polish
            'tr': '🇹🇷',  # Turkey for Turkish
            'el': '🇬🇷',  # Greece for Greek
            'he': '🇮🇱',  # Israel for Hebrew
            'th': '🇹🇭',  # Thailand for Thai
            'cs': '🇨🇿',  # Czech Republic for Czech
            'ro': '🇷🇴',  # Romania for Romanian
            'hu': '🇭🇺',  # Hungary for Hungarian
            'sk': '🇸🇰',  # Slovakia for Slovak
            'bg': '🇧🇬',  # Bulgaria for Bulgarian
            'sr': '🇷🇸',  # Serbia for Serbian
            'hr': '🇭🇷',  # Croatia for Croatian
            'sl': '🇸🇮',  # Slovenia for Slovenian
            'lt': '🇱🇹',  # Lithuania for Lithuanian
            'lv': '🇱🇻',  # Latvia for Latvian
            'et': '🇪🇪',  # Estonia for Estonian
            'id': '🇮🇩',  # Indonesia for Indonesian
            'ms': '🇲🇾',  # Malaysia for Malay
            'fil': '🇵🇭',  # Philippines for Filipino
            'sw': '🇹🇿',  # Tanzania for Swahili (Note: also widely spoken in Kenya 🇰🇪)
            'uk': '🇺🇦',  # Ukraine for Ukrainian
            'bn': '🇧🇩',  # Bangladesh for Bengali
            'hi': '🇮🇳',  # India for Hindi
            'fa': '🇮🇷',  # Iran for Persian (Farsi)
            'ur': '🇵🇰',  # Pakistan for Urdu
            'mn': '🇲🇳',  # Mongolia for Mongolian
            'ne': '🇳🇵',  # Nepal for Nepali
        }

        print("Using translation cache: ", use_cache)

        # self.ensure_log_folder_exists()



    @property
    def is_video_landscape(self):
        """Determine if the video is landscape or portrait based on class variables."""
        return self.video_width > self.video_height

    def get_filename(self, lang="ja", idx=0, timestamp=None):
        # base_filename = os.path.splitext(os.path.basename(self.input_json_path))[0]
        # datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_filename = self.base_filename
        # datetime_str = self.datetime_str

        if timestamp:
            filename = f"{self.translation_log_folder}/{base_filename}-part{idx}-{lang}-{timestamp}.json"
        else:
            filename = f"{self.translation_log_folder}/{base_filename}-part{idx}-{lang}.json"

        return filename
    


    def load_subtitles_from_json(self):
        """Load subtitles from a JSON file."""
        with open(self.input_json_path, 'r', encoding='utf-8') as file:
            return json5.load(file)

    @staticmethod
    def correct_json_string(s):
        # Remove trailing commas after object properties or array elements
        corrected_s = re.sub(r',\s*}', '}', s)
        corrected_s = re.sub(r',\s*\]', ']', corrected_s)
        return corrected_s

    def extract_and_parse_json(self, text):
        """Extract and parse JSON from text, handling potential parsing issues."""
        bracket_pattern = r'\[.*\]'
        matches = re.findall(bracket_pattern, text, re.DOTALL)
        # json_string = ""

        if not matches:
            raise JSONParsingError("No JSON string found in text", text, text)
        json_string = matches[0].replace('\n', '')

        # pprint(json_string)
        safe_pretty_print(json_string)

        try:
            json_string = self.correct_json_string(json_string)
            return json5.loads(json_string)
        except ValueError as e:
            traceback.print_exc()
            raise JSONParsingError(f"JSON Decode Error: {e}", json_string, text)

    def validate_translated_subtitles(self, subtitles, required_fields=["start", "end", "en", "zh"]):
        """Validate the structure of translated subtitles."""
        # required_fields = ["start", "end", "en", "zh"]
        for subtitle in subtitles:
            if not all(field in subtitle for field in required_fields):
                raise JSONValidationError("Subtitle missing one of the required fields: " + ", ".join(required_fields))



    def translate_and_merge_subtitles(self, subtitles):
        self.subtitles = subtitles

        """Splits subtitles into 1-minute batches and processes each batch in parallel."""
        # subtitles = self.load_subtitles_from_json()

        # Splitting subtitles into 1-minute batches
        batches = self.split_subtitles_into_batches(subtitles)

        # Process each batch and accumulate results in parallel
        translated_subtitles = self.process_batches_in_parallel(batches)

        # Save the final translated subtitles
        # self.save_translated_subtitles_to_ass(translated_subtitles)
        print("All subtitles have been processed and saved successfully.")

        return translated_subtitles

    def process_batches_in_parallel(self, batches):
        """Process subtitle batches in parallel using ThreadPoolExecutor."""
        translated_subtitles = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all batches to be processed in parallel
            future_to_batch = {executor.submit(self.translate_and_merge_subtitles_in_batch, batch, i): batch for i, batch in enumerate(batches)}

            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    translated_batch = future.result()
                    translated_subtitles.extend(translated_batch)
                except Exception as exc:
                    print(f'Batch {batch} generated an exception: {exc}')
        
        # Optional: Sort the merged list by start timestamps if necessary
        translated_subtitles.sort(key=lambda x: datetime.strptime(x['start'], '%H:%M:%S,%f'))

        return translated_subtitles

    def split_subtitles_into_batches(self, subtitles):
        """Splits subtitles into 1-minute batches based on their timestamps."""
        batches = []
        current_batch = []
        current_batch_start_time = None

        for subtitle in subtitles:
            start_time = datetime.strptime(subtitle["start"], '%H:%M:%S,%f')
            if current_batch_start_time is None:
                current_batch_start_time = start_time

            if (start_time - current_batch_start_time).total_seconds() > 60:
                # Start a new batch if the current subtitle start time exceeds 1 minute from the batch's start time
                batches.append(current_batch)
                current_batch = [subtitle]
                current_batch_start_time = start_time
            else:
                current_batch.append(subtitle)

        # Add the last batch if it contains subtitles
        if current_batch:
            batches.append(current_batch)

        return batches

    def translate_and_merge_subtitles_in_batch(self, subtitles, idx):
        """Merge translations from multiple languages' functions in parallel."""
        # Define a dictionary of language codes to their respective translation functions
        translation_tasks = {
            'major': self.translate_and_merge_subtitles_major_languages,
            'ja': self.translate_and_merge_subtitles_ja,
            'ko': self.translate_and_merge_subtitles_ko,
            'vi': self.translate_and_merge_subtitles_vi, 
            'minor': self.translate_and_merge_subtitles_minor_languages
        }

        with ThreadPoolExecutor(max_workers=len(translation_tasks)) as executor:
            futures = {
                executor.submit(translation_func, subtitles, idx): lang_code
                for lang_code, translation_func in translation_tasks.items()
            }

            all_translations = {}

            for future in as_completed(futures):
                lang_code = futures[future]
                try:
                    translations = future.result()
                    all_translations[lang_code] = translations
                except Exception as exc:
                    print(f'{lang_code} translation generated an exception: {exc}')

        # Merge translations
        timestamps_dict = {}

        for translations in all_translations.values():
            for translation in translations:
                key = (translation['start'], translation['end'])

                # Initialize the dictionary entry if it doesn't exist
                if key not in timestamps_dict:
                    timestamps_dict[key] = {'start': translation['start'], 'end': translation['end']}
                
                # Dynamically add all language translations, regardless of the number of languages
                for sub_lang, text in translation.items():
                    if sub_lang not in ['start', 'end']:  # Skip timestamp keys
                        timestamps_dict[key][sub_lang] = text

        merged_translations = list(timestamps_dict.values())
        merged_translations.sort(key=lambda x: x['start'])

        return merged_translations


    def translate_and_merge_subtitles_major_languages(self, subtitles, idx):
        """Translate and merge subtitles using the OpenAI API."""

        print("Translating subtitles into other languages...")
        
        # client = self.client


        # # Define a sample JSON structure for validation purposes
        # sample_json_structure = [
        #     {
        #         "start": "timestamp",
        #         "end": "timestamp",
        #         "en": "English text",
        #         "zh": "Chinese text",
        #         "ar": "Arabic text",
        #         # "...": "Text in the original language, if not in the listed before. "
        #     }
        # ]

        # sample_json_string = json.dumps(sample_json_structure, indent=2, ensure_ascii=False)


        # Define a JSONC string with comments
        sample_json_string = """
        [
            {
                "start": "timestamp",  // Start time of the subtitle
                "end": "timestamp",    // End time of the subtitle
                "en": "English text",  // English translation
                "zh": "Chinese text",  // Chinese translation
                "ar": "Arabic text",    // Arabic translation
                // "...": "Text in the original language, if not in the listed before."
            }
        ]
        """

        # Parse the JSONC string into a Python object
        sample_json_structure = json5.loads(sample_json_string)


        system_content = "Translate and merge mixed language subtitles into Chinese, English and Arabic, providing coherent and accurate translations."
        prompt = (
            "Below are mixed language subtitles extracted from a video, including timestamps, "
            "language indicators, and the subtitle text itself. The task is to ensure that each subtitle "
            "is presented with English (en), Chinese (zh), and Arabic (ar) translations, "
            "maintaining the original timestamps.\n\n"

            # "If a subtitle is already in English, provide the corresponding Chinese and Arabic translation, and vice versa. "
            # "For subtitles in any other language, keep the original text but also provide translations in "
            # "English, Chinese and Arabic. \n\n"

            # "Fullfill the instructions/requests in subtitles per se for other languages with iso_code_639_1 language key. "
            # "If I said in subtitles that I want to know or I don't know how to say something, "
            # "provide the whole subtitles in that language. "
         
            # "Correct some apparent speech recognition error and inconsistencies, "
            # "especially homonym and mumble in both origin and its translation based on the context.\n\n"
    
            "Process the following subtitles, ensuring translations are accurate and coherent, "
            "and format the output as shown in the example.\n\n"

            # "Please provide a complete and accurate translation and formatting for each subtitle entry."

            # "PLEASE DON'T CHANGE ORIGINAL TIMESTAMPS.\n\n"
            
            # "Note that the original timestamps should be PRESERVED for each entry.\n\n"
            
            "Please PRESERVE ALL the original timestamps for EACH ENTRY.\n\n"

            "Subtitles to process:\n"
            f"{json.dumps(subtitles, indent=2, ensure_ascii=False)}\n\n"
            

            "ONLY and ALWAYS return a valid JSON back:\n"
            "```json"
            f"{sample_json_string}\n"
            "```"
        )






        translated_subtitles = self.send_request_with_retry(
            prompt, 
            system_content=system_content, 
            sample_json=sample_json_structure,
            filename=self.get_filename(lang="major", idx=idx)
        )

        print("Translated subtitles (Major): \n")
        pprint(translated_subtitles)



        return translated_subtitles


    def translate_and_merge_subtitles_minor_languages(self, subtitles, idx):
        """Translate and merge subtitles using the OpenAI API into Spanish, French, and Vietnamese by leveraging the 
        translate_and_merge_subtitles_with_specified_languages function."""

        # Define the list of minor languages to translate to
        minor_languages = ["Spanish", "French", "Russian"]
        
        # Call the translate_and_merge_subtitles_with_specified_languages function with the minor languages
        translated_subtitles = self.translate_and_merge_subtitles_with_specified_languages(subtitles, minor_languages, idx)
        
        return translated_subtitles


    def translate_and_merge_subtitles_with_specified_languages(self, subtitles, requested_languages, idx):
        """Translate and merge subtitles into the specified languages using the OpenAI API."""
        print("Translating subtitles into specified languages...")

        # Convert the list of language names into language codes and full names with initial capitalization
        language_codes = []
        language_full_names = []
        for lang_name in requested_languages:
            code = TO_LANGUAGE_CODE.get(lang_name.lower())
            if code and code in LANGUAGES:
                language_codes.append(code)
                language_full_names.append(LANGUAGES[code].capitalize())

        # Generate a sample JSON structure dynamically based on requested language codes
        sample_json_structure = [{"start": "timestamp", "end": "timestamp"}]
        for code in language_codes:
            sample_json_structure[0][code] = f"{LANGUAGES[code]} text"

        sample_json_string = json.dumps(sample_json_structure, indent=2)
        # sample_json_structure = json5.loads(sample_json_string)

        # Generate a human-readable string of the full language names for the prompt
        languages_list_str = ', '.join(language_full_names[:-1]) + ', and ' + language_full_names[-1] if len(language_full_names) > 1 else language_full_names[0]

        print(f"The specified languages are: {languages_list_str}. ")

        system_content = f"Translate mixed language subtitles into {languages_list_str}, providing coherent and accurate translations."
        prompt = (
            "Below are mixed language subtitles extracted from a video, including timestamps, "
            "language indicators, and the subtitle text itself. The task is to ensure that each subtitle "
            f"is presented with translations in {languages_list_str}, "
            "maintaining the original timestamps.\n\n"

            # "Correct some apparent speech recognition error and inconsistencies, "
            # "especially homonym and mumble in both origin and its translation based on the context.\n\n"

            "Process the following subtitles, ensuring translations are accurate and coherent, "
            "and format the output as shown in the example.\n\n"

            # "PLEASE DON'T CHANGE ORIGINAL TIMESTAMPS.\n\n"

            # "Note that the original timestamps should be PRESERVED for each entry.\n\n"

            "Please PRESERVE ALL the original timestamps for EACH ENTRY.\n\n"


            "Subtitles to process:\n"
            f"{json.dumps(subtitles, indent=2, ensure_ascii=False)}\n\n"

            "ONLY and ALWAYS return a valid JSON back:\n"
            "```json"
            f"{sample_json_string}\n"
            "```"
        )

        lang_str = "_".join(language_codes)
        translated_subtitles = self.send_request_with_retry(
            prompt,
            system_content=system_content,
            sample_json=sample_json_structure,
            filename=self.get_filename(lang=lang_str, idx=idx)
        )

        print("Translated subtitles (Specified Languages): \n")
        pprint(translated_subtitles)

        return translated_subtitles

    # Function to annotate Kanji and Katakana independently
    @staticmethod
    def annotate_kanji_katakana(subtitles):
        # Define the regular expression patterns for Kanji and Katakana
        kanji_pattern = r'[\u4e00-\u9faf]+'
        katakana_pattern = r'[\u30a0-\u30ff]+'
        
        # Function to wrap text in <>[]
        def replacer(match):
            return f'<{match.group(0)}>[]'
        
        # Annotate each item in the list
        for item in subtitles:
            # Annotate Kanji
            item['ja'] = re.sub(kanji_pattern, replacer, item['ja'])
            # Annotate Katakana
            item['ja'] = re.sub(katakana_pattern, replacer, item['ja'])
        
        return subtitles

    def translate_and_merge_subtitles_ja(self, subtitles, idx):
        """Request Japanese subtitles separately with specific formatting for furigana."""
        print("Translating subtitles to Japanese...")

        sample_json_structure = [
            {
                "start": "timestamp",
                "end": "timestamp",
                "ja": "Japanese text with optional furigana annotations"
            }
        ]

        sample_json_string = json.dumps(sample_json_structure, indent=2, ensure_ascii=False)

        # system_content = "Translate subtitles into Japanese, correcting any errors based on context."
        system_content = "Translate subtitles into Japanese, providing coherent and accurate translations."
        prompt = (
            "Translate the following subtitles into Japanese. "
            "\n\n"

            # "Correct speech recognition errors and inconsistencies based on context.\n\n"
            
            # "PLEASE DON'T CHANGE ORIGINAL TIMESTAMPS.\n\n"

            # "Note that the original timestamps should be PRESERVED for each entry.\n\n"

            "Please PRESERVE ALL the original timestamps for EACH ENTRY.\n\n"
            
            "Subtitles to process:\n"
            f"{json.dumps(subtitles, indent=2, ensure_ascii=False)}\n\n"

            "ONLY and ALWAYS return a valid JSON back:\n"
            "```json\n"
            f"{sample_json_string}\n"
            "```"
        )

        
        translated_subtitles = self.send_request_with_retry(
            prompt,
            system_content=system_content,
            sample_json=sample_json_structure,
            filename=self.get_filename(lang="ja", idx=idx)
        )


        annotated_subtitles = self.annotate_kanji_katakana(translated_subtitles)

        print("annotated subtitles: \n")
        pprint(annotated_subtitles)

        translated_subtitles = self.add_furigana_for_japanese_subtitles(annotated_subtitles, idx)

        print("furigana subtitles: \n")
        pprint(translated_subtitles)

        return translated_subtitles

            


    def add_furigana_for_japanese_subtitles(self, subtitles, idx):
        """Request Japanese subtitles with specific formatting for furigana using the OpenAI API with retries."""

        sample_json_structure = [
            {
                "start": "timestamp",
                "end": "timestamp",
                "ja": "Japanese text with furigana annotations"
            }
        ]

        sample_json_string = json.dumps(sample_json_structure, indent=2, ensure_ascii=False)

        system_content = "Add furigana annotations to the provided Japanese text."
        prompt = (
            "Given the Japanese subtitles, add furigana annotations correctly based on the context. "
            "Use the format '<Kanji>[Furigana]' for annotations.\n\n"

            # "Correct any speech recognition errors and inconsistencies based on context.\n\n"
            
            "Please PRESERVE ALL the original timestamps for EACH ENTRY.\n\n"

            "Subtitles to process:\n"
            f"{json.dumps(subtitles, indent=2, ensure_ascii=False)}\n\n"

            "ONLY and ALWAYS return a valid JSON back:\n"
            "```json\n"
            f"{sample_json_string}\n"
            "```"
        )

        # Utilize send_request_with_retry to handle API requests, including retries, caching, and JSON validation
        translated_subtitles = self.send_request_with_retry(
            prompt,
            system_content=system_content,
            sample_json=sample_json_structure,
            filename=self.get_filename(lang="furigana", idx=idx)
        )

        print("Translated subtitles (Japanese with furigana): \n")
        pprint(translated_subtitles)

        return translated_subtitles


    def translate_and_merge_subtitles_ko(self, subtitles, idx):
        """Request Korean subtitles with specific considerations."""
        print("Translating subtitles to Korean...")

        # Define a sample JSON structure for Korean subtitles
        sample_json_structure = [
            {
                "start": "timestamp",
                "end": "timestamp",
                "ko": "Korean text"  # Use "ko" for Korean text
            }
        ]

        sample_json_string = json.dumps(sample_json_structure, indent=2, ensure_ascii=False)

        # system_content = "Translate subtitles into Korean, correcting any errors based on context."
        system_content = "Translate subtitles into Korean, providing coherent and accurate translations."
        prompt = (
            "Translate the following subtitles into Korean. "
            "\n\n"
            # "Correct speech recognition errors and inconsistencies based on context.\n\n"

            # "PLEASE DON'T CHANGE ORIGINAL TIMESTAMPS. \n\n"

            # "Note that the original timestamps should be PRESERVED for each entry.\n\n"

            "Please PRESERVE ALL the original timestamps for EACH ENTRY.\n\n"

            "Subtitles to process:\n"
            f"{json.dumps(subtitles, indent=2, ensure_ascii=False)}\n\n"

            "ONLY and ALWAYS return a valid JSON back:\n"
            "```json\n"
            f"{sample_json_string}\n"
            "```"
        )

        # Use the function for sending requests with retries, similarly to the Japanese version
        translated_subtitles = self.send_request_with_retry(
            prompt,
            system_content=system_content,
            sample_json=sample_json_structure,
            filename=self.get_filename(lang="ko", idx=idx)
        )

        # Here, you might add any specific post-processing for Korean subtitles if necessary
        # For example, annotating certain phrases, cultural references, or anything specific to Korean

        translated_subtitles = self.replace_hangul_with_hanja(translated_subtitles, idx)

        print("Translated subtitles (Korean): \n")
        pprint(translated_subtitles)

        return translated_subtitles


    


    def replace_hangul_with_hanja(self, subtitles, idx):
        """Annotate Korean subtitles with Hanja and conservatively replace original text with Hanja annotations."""

        print("Annotating Korean subtitles with Hanja...")

        system_content = "Annotate Korean text with original Chinese Hanja."

        # Sample JSON structure expected in the response
        sample_json_structure = {
            "korean_with_annotation": "",
            "korean_hanja_pairs": [
                # {"korean_part": "한자 ", "hanja": "漢字 ", "roman": "hanja"}
                {"korean_part": "", "hanja": ""}
            ]
        }
        sample_json_string = json.dumps(sample_json_structure, indent=2, ensure_ascii=False)


        # Helper function for conservative replacement in the original text
        def conservative_replace(original_text, hanja_pairs):
            """Perform conservative replacement of Korean text with Hanja annotations."""
            updated_text = original_text
            last_pos = 0  # Initialize the position tracker to the start of the string

            for pair in hanja_pairs:
                korean_part = pair.get("korean_part", "")
                hanja = pair.get("hanja", "")
                pronunciation = pair.get("roman", "")

                # Check if the 'hanja' part is actually Hangul or if there's no Hanja present
                if re.match(r'^[\uAC00-\uD7AF]+$', hanja) or len(hanja) == 0:
                    continue  # Skip replacement if Hanja is actually Hangul or if Hanja is missing

                # replace_with = f"<{hanja}>[{korean_part}]({pronunciation})"
                replace_with = f"<{hanja}>[{korean_part}]"

                # Start search from the last modification position to only look forward
                start_pos = updated_text.find(korean_part, last_pos)
                if start_pos != -1:
                    end_pos = start_pos + len(korean_part)
                    updated_text = updated_text[:start_pos] + replace_with + updated_text[end_pos:]
                    last_pos = start_pos + len(replace_with)  # Update last_pos to the end of the newly inserted segment

            return updated_text

        def process_subtitle(subtitle):
            """Construct and send a request for annotating a single subtitle with Hanja."""
            prompt = (
                "For words that have etymological Hanja alternatives (due to their Sino-Korean origin), "
                "I want to find the corresponding Chinese character origin to replace the Hangul. "
                "However, it's crucial that the Hangul in parenthesis followed by these traditional Hanja "
                "are put in brackets to maintain clarity as in this format: (hangul)[hanja].\n\n"
                # "Please also provide Roman pronunciation of the Hangul. "
                f"Korean to be annotated: {subtitle['ko']}\n\n"
                "I don't need step by step explanation. "
                "ONLY and ALWAYS return a valid JSON back:\n"
                f"```json\n{sample_json_string}\n```"
            )

            response = self.send_request_with_retry(
                prompt,
                system_content=system_content,
                sample_json=sample_json_structure,
                filename=self.get_filename(lang="hanja", idx=idx, timestamp=self.format_subtitle_range(subtitle))
            )
            # Assume response is structured correctly
            annotated_text = response.get("korean_with_annotation", "")
            hanja_pairs = response.get("korean_hanja_pairs", [])
            
            # Update the original text using the conservative replace function
            updated_original_text = conservative_replace(subtitle["ko"], hanja_pairs)

            return {
                "start": subtitle["start"],
                "end": subtitle["end"],
                "ko": updated_original_text,  # Updated original Korean text with Hanja annotations
                # "annotated": annotated_text,  # Full annotated text (if needed separately)
                # "hanja_pairs": hanja_pairs  # Hanja pairs for reference
            }

        # annotated_subtitles = [process_subtitle(sub) for sub in subtitles]

        # Parallel execution with error handling to return original subtitles if an error occurs
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_subtitle, sub): sub for sub in subtitles}
            for future in as_completed(futures):
                sub = futures[future]
                try:
                    result = future.result()
                    sub.update(result)
                except Exception as exc:
                    print(f"Subtitle processing generated an exception: {exc}")
                    # If there's an error, the original subtitle remains unchanged

        print("Korean with Hanja: \n")
        pprint(subtitles)

        return subtitles


    def translate_and_merge_subtitles_vi(self, subtitles, idx):
        """Request Vietnamese subtitles with specific considerations."""
        print("Translating subtitles to Vietnamese...")

        # Define a sample JSON structure for Vietnamese subtitles
        sample_json_structure = [
            {
                "start": "timestamp",
                "end": "timestamp",
                "vi": "Vietnamese text"  # Use "vi" for Vietnamese text
            }
        ]

        sample_json_string = json.dumps(sample_json_structure, indent=2, ensure_ascii=False)

        # system_content = "Translate subtitles into Vietnamese, correcting any errors based on context."
        system_content = "Translate subtitles into Vietnamese, providing coherent and accurate translations."
        prompt = (
            "Translate the following subtitles into Vietnamese. "
            "\n\n"

            # "Correct speech recognition errors and inconsistencies based on context.\n\n"

            # "PLEASE DON'T CHANGE ORIGINAL TIMESTAMPS.\n\n"

            # "Note that the original timestamps should be PRESERVED for each entry.\n\n"

            "Please PRESERVE ALL the original timestamps for EACH ENTRY.\n\n"

            "Subtitles to process:\n"
            f"{json.dumps(subtitles, indent=2, ensure_ascii=False)}\n\n"

            "ONLY and ALWAYS return a valid JSON back:\n"
            "```json\n"
            f"{sample_json_string}\n"
            "```"
        )

        translated_subtitles = self.send_request_with_retry(
            prompt,
            system_content=system_content,
            sample_json=sample_json_structure,
            filename=self.get_filename(lang="vi", idx=idx)
        )

        translated_subtitles = self.replace_viet_with_chuhan(translated_subtitles, idx)

        print("Translated subtitles (Vietnamese): \n")
        pprint(translated_subtitles)

        return translated_subtitles

    def replace_viet_with_chuhan(self, subtitles, idx):
        """Annotate Vietnamese subtitles with Chu-Han and conservatively replace original text with Chu-Han annotations."""
        
        print("Annotating Vietnamese subtitles with Chu-Han...")

        system_content = "Annotate Vietnamese text with original Chinese Chu-Han."
        
        # Sample JSON structure expected in the response
        sample_json_structure = {
            "viet_with_annotation": "",
            "viet_chuhan_pairs": [
                {"viet_part": "", "chuhan": ""}
            ]
        }
        sample_json_string = json.dumps(sample_json_structure, indent=2, ensure_ascii=False)

        def conservative_replace(original_text, chuhan_pairs):
            """Perform conservative replacement of Viet text with Chu-Han annotations, excluding text within <>[]."""
            updated_text = original_text
            last_pos = 0  # Keep track of the last position after the most recent replacement

            for pair in chuhan_pairs:
                viet_part = pair.get("viet_part", "")
                chuhan = pair.get("chuhan", "")

                if len(chuhan) == 0 or len(viet_part) == 0:
                    continue

                replace_with = f"<{chuhan}>[{viet_part}]"

                # Start search from the last modification position
                start_pos = updated_text.find(viet_part, last_pos)

                if start_pos != -1:
                    end_pos = start_pos + len(viet_part)
                    updated_text = updated_text[:start_pos] + replace_with + updated_text[end_pos:]
                    last_pos = start_pos + len(replace_with)  # Update last_pos to the end of the newly inserted segment
            
            return updated_text


        def process_subtitle(subtitle):
            """Construct and send a request for annotating a single subtitle with Chu-Han."""
            prompt = (
                "For words that have etymological Chu-Han alternative (due to their Sino-Vietnamese origin), "
                "I want to find the corresponding Chinese origin to replace the Viet WORDS (provide consecutive words if exist). "
                "However, it's crucial that the Viet in parenthesis followed by these traditional Chu-Han "
                "are put in brackets to maintain clarity. "
                "Like this example: (viet)[chuhan].\n\n"
                f"Vietnamese to be annotated: {subtitle['vi']}\n\n"
                "I don't need step by step explanation. "
                "ONLY and ALWAYS return a valid JSON back:\n"
                f"```json\n{sample_json_string}\n```"
            )

            response = self.send_request_with_retry(
                prompt,
                system_content=system_content,
                sample_json=sample_json_structure,
                filename=self.get_filename(lang="chuhan", idx=idx, timestamp=self.format_subtitle_range(subtitle))
            )
            annotated_text = response.get("viet_with_annotation", "")
            chuhan_pairs = response.get("viet_chuhan_pairs", [])
            
            updated_original_text = conservative_replace(subtitle["vi"], chuhan_pairs)

            return {
                "start": subtitle["start"],
                "end": subtitle["end"],
                "vi": updated_original_text  # Updated original Vietnamese text with Chu-Han annotations
            }

        # Parallel execution with error handling to return original subtitles if an error occurs
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_subtitle, sub): sub for sub in subtitles if 'vi' in sub}
            for future in as_completed(futures):
                sub = futures[future]
                try:
                    result = future.result()
                    sub.update(result)
                except Exception as exc:
                    print(f"Subtitle processing generated an exception: {exc}")
                    # If there's an error, the original subtitle remains unchanged

        print("Vietnamese with Chu-Han: \n")
        pprint(subtitles)

        return subtitles

    @staticmethod
    def format_subtitle_range(subtitle):
        """
        Takes a subtitle dictionary with 'start' and 'end' timestamp strings,
        removes all colons from the timestamps, and returns a concatenated string
        with a dash between the start and end timestamps.

        :param subtitle: A dictionary with 'start' and 'end' keys.
        :return: A string combining the start and end times, with colons removed.
        """
        start_formatted = subtitle["start"].replace(":", "").replace(",", "")
        end_formatted = subtitle["end"].replace(":", "").replace(",", "")
        return f"{start_formatted}-{end_formatted}"

    def save_translated_subtitles_to_srt(self, translated_subtitles):
        """Save the translated subtitles to an SRT file, ensuring language order."""
        srt_content = ""
        for index, subtitle in enumerate(translated_subtitles, start=1):
            # Start the subtitle entry with its sequence number and time range
            srt_content += f"{index}\n{subtitle['start']} --> {subtitle['end']}\n"
            
            # Always add Chinese (zh) translation first if it exists
            if 'zh' in subtitle:
                srt_content += f"{subtitle['zh']}\n"
            
            # Add English (en) translation
            if 'en' in subtitle:
                srt_content += f"{subtitle['en']}\n"
            
            # Add any additional languages present, excluding 'start', 'end', 'zh', and 'en'
            additional_languages = {k: v for k, v in subtitle.items() if k not in ['start', 'end', 'zh', 'en']}
            for lang_code, text in additional_languages.items():
                srt_content += f"{text}\n"
            
            # Separate subtitles with an empty line
            srt_content += "\n"
        
        # Write the constructed SRT content to the output file
        with open(self.output_sub_path, 'w', encoding='utf-8') as file:
            file.write(srt_content)


    def process_subtitles(self):
        """Main process to load, translate, merge, and save subtitles."""
        subtitles = self.load_subtitles_from_json()
        translated_subtitles = self.translate_and_merge_subtitles(subtitles)
        # self.save_translated_subtitles_to_srt(translated_subtitles)
        self.save_translated_subtitles_to_ass(translated_subtitles)
        self.save_translated_subtitles_to_json(translated_subtitles)
        print("Subtitles have been processed and saved successfully.")


    def rearrange_brackets(self, ja_text):
        """
        Detects and rearranges text where [] are found inside <> to follow the <>[] pattern.
        """
        
        # Define a regex pattern to match <...[...]...>
        pattern = re.compile(r'<([^>\[\]]+)\[([^\[\]]+)\]([^>\[\]]*)>')
        
        # Function to rearrange the matched pattern to <...> [...]
        def rearrange(match):
            # Extract the parts of the match
            before_bracket = match.group(1)
            inside_bracket = match.group(2)
            after_bracket = match.group(3)
            
            # Return the rearranged format
            return f'<{before_bracket}{after_bracket}>[{inside_bracket}]'

        # Apply the rearrange function to all matching patterns in the text
        rearranged_text = pattern.sub(rearrange, ja_text)

        return rearranged_text

    def remove_preceding_repetition(self, ja_text):
        """
        Removes a word or phrase that is repeated immediately before <...> when
        the content inside <> is the same as the preceding word.
        """
        
        # Define a regex pattern to match repetition before <>
        pattern = re.compile(r'(\S+)<\1>')
        
        # Function to replace the matched pattern with just the content in angle brackets
        def deduplicate(match):
            # Return only the content within angle brackets
            return f'<{match.group(1)}>'

        # Apply the deduplication function to all matching patterns in the text
        deduplicated_text = pattern.sub(deduplicate, ja_text)

        return deduplicated_text


    def clean_triplicated_sequences(self, ja_text):
        """
        Simplifies text by converting sequences of the form same<same>[same] to just 'same'.
        """
        # Define a regex pattern to match the 'same<same>[same]' structure
        pattern = re.compile(r'(?:(\S+)<\1>\[\1\])')
        
        # Function to perform the substitution
        def replacement(match):
            # Return just the first 'same' part of the match
            return match.group(1)
        
        # Remove same hiragana<same hiragana>[ same hiragana] anywhere
        # Apply the replacement function to all matching patterns in the text
        simplified_text = pattern.sub(replacement, ja_text)

        return simplified_text



    


    def clean_duplicated_kanji_hiragana_sequence(self, ja_text):
        """
        Converts sequences of the form 'same kanji<same kanji>[hiragana]' to '<kanji>[hiragana]'.
        """
        # Define a regex pattern to match the specified structure
        pattern = re.compile(r'([一-龠ァ-ヶ々ー]+)(<\1>)\[([ぁ-ん]+)\]')
        
        # Function to perform the substitution
        def replacement(match):
            # for i in range(4):
            #     print(match.group(i))
            
            # Return the simplified structure '<kanji>[hiragana]'
            kanji = match.group(2)
            hiragana = match.group(3)
            return f'{kanji}[{hiragana}]'
        
        # Convert kanji<kanji>[hiragana] to <kanji>[hiragana], preserving the sequence (two kanji seq is the same)
        # Apply the replacement function to all matching patterns in the text
        simplified_text = pattern.sub(replacement, ja_text)

        return simplified_text

    def clean_redundant_hiragana_sequence(self, ja_text):
        """
        Modifies text by removing redundant angle and square brackets for matching hiragana or kanji sequences.
        - For hiragana immediately before or at the start, followed by <hiragana>[hiragana], it leaves just the hiragana.
        - For kanji followed by <hiragana>[hiragana], it replaces them with [hiragana].
        """

        

        # Remove <same hiragana>[same hiragana] when at the start or directly after punctuation or preceded by different hiragana
        # hiragana_pattern = re.compile(r'(^|(?<=[ぁ-ん]))<([ぁ-ん]+)>\[\2\]')
        hiragana_pattern = re.compile(r'(^|(?<=[、。！？>\]ぁ-ん]))<([ぁ-ん]+)>\[\2\]')
        simplified_text = hiragana_pattern.sub(r'\1\2', ja_text)
        
        # Convert kanji<hiragana>[hiragana] to kanji[hiragana], preserving the sequence
        kanji_hiragana_pattern = re.compile(r'(?<=[一-龠ァ-ヶ々ー])<([ぁ-ん]+)>\[\1\]')
        simplified_text = kanji_hiragana_pattern.sub(r'[\1]', simplified_text)

        
        
        return simplified_text

    def clean_duplicated_hiragana_inside_angle_brackets(self, ja_text):
        """
        Simplifies sequences of the form 'same hiragana<same hiragana>' to just 'hiragana'.
        """
        # Define a regex pattern to match hiragana sequences repeated before and inside angle brackets
        pattern = re.compile(r'<?([ぁ-ん]+)>?<\1>')

        
        # Perform the substitution to replace matched patterns with just the hiragana
        simplified_text = pattern.sub(r'\1', ja_text)

        return simplified_text


    def convert_standalone_angle_to_square_brackets(self, ja_text):
        """
        Converts standalone angle brackets to square brackets in the given text,
        while leaving <kanji>[furigana] pairs unchanged.
        """
        
        # Define a regex pattern to find standalone <> not followed directly by []
        # This pattern assumes 'standalone' means there's no furigana in square brackets immediately following
        pattern = re.compile(r'<([^>]+)>(?!\[)')
        
        # Replace found patterns with square brackets
        converted_text = pattern.sub(r'[\1]', ja_text)
        
        return converted_text






    # # Example usage
    # original_text = "<字幕>[じまく]上[じょう]でこの<日本語>[にほんご]の発音[はつおん]を学[まな]べるようにしています。"
    # preprocessed_text = preprocess_text_for_furigana(original_text)

    # print("Preprocessed Text:", preprocessed_text)

    def katakana_to_hiragana(self, katakana):
        """
        Converts a katakana string to hiragana.
        """
        katakana_hiragana_map = str.maketrans(
            "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ",
            "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ"
        )
        return katakana.translate(katakana_hiragana_map)

    def fill_blank_of_katakana_without_furigana(self, ja_text):
        """
        Converts sequences of the form <katakana>[] to <katakana>[hiragana],
        where hiragana is the equivalent of the katakana text inside the angle brackets.
        """
        # Define a regex pattern to match <katakana>[] structures
        pattern = re.compile(r'<([ァ-ヶー]+)>\[\]')
        
        # Function to perform the substitution
        def replacement(match):
            # Convert the matched katakana to hiragana
            katakana_text = match.group(1)
            hiragana_text = self.katakana_to_hiragana(katakana_text)
            return f'<{katakana_text}>[{hiragana_text}]'
        
        # Apply the replacement function to all matching patterns in the text
        converted_text = pattern.sub(replacement, ja_text)

        return converted_text

    def convert_katakana_in_brackets_to_hiragana(self, ja_text):
        """
        Detects <Katakana>[Katakana] then converts the [Katakana] into [Hiragana].
        """
        # # Define a regex pattern to match <Katakana>[Katakana]
        # pattern = re.compile(r'<([ァ-ヶー]+)>\[\1\]')

        # Define a regex pattern to match both <Katakana>[Katakana] and Katakana[Katakana]
        pattern = re.compile(r'(?:(<([ァ-ヶー]+)>)|([ァ-ヶー]+))\[(\2|\3)\]')

        # # Use the katakana_to_hiragana function to convert matched katakana to hiragana in []
        # corrected_text = re.sub(pattern, lambda m: f'<{m.group(1)}>[{katakana_to_hiragana(m)}]', ja_text)

        def replacement(match):
            # Determine if the match includes angle brackets or not
            katakana = match.group(2) if match.group(2) else match.group(3)
            hiragana = self.katakana_to_hiragana(katakana)
            # Reconstruct the string with the katakana in brackets converted to hiragana
            if match.group(1):  # If katakana was enclosed in angle brackets
                return f'<{katakana}>[{hiragana}]'
            else:  # If katakana was not enclosed in angle brackets
                return f'{katakana}[{hiragana}]'

        # Use the replacement function to convert matched katakana to hiragana in []
        corrected_text = pattern.sub(replacement, ja_text)

        return corrected_text

    
    def preprocess_text_for_furigana(self, ja_text):
        """
        Adjusts Japanese text to ensure that kanji/katakana sequences directly preceding standalone furigana
        are enclosed in <>, without altering or removing any unassociated hiragana or other characters.
        This version stops including characters in the sequence based on the starting character type (kanji or katakana).
        """
        
        # This pattern is updated to differentiate between sequences starting with kanji or katakana.
        # It ensures that if a sequence starts with kanji, it only includes kanji,
        # and if it starts with katakana, it only includes katakana, directly preceding the furigana annotation.
        # pattern = re.compile(
        #     r'(?<!<)'
        #     r'((?:[一-龠々]+|[ァ-ヶー]+))'  # Matches a sequence of kanji or a sequence of katakana
        #     r'(?=\[([^\]]+)\])'  # Lookahead for furigana enclosed in brackets without including them in the match
        # )
        pattern = re.compile(
            r'(?<!<)'
            r'((?:[一-龠々]+|[ァ-ヶー]+))'  # Matches a sequence of kanji or a sequence of katakana
            r'([ぁ-ん]{0,2})'  # Optionally matches zero to two hiragana characters
            r'(?=\[([^\]]+)\])'  # Lookahead for furigana enclosed in brackets without including them in the match
        )

        # Function to enclose matched kanji/katakana sequence in <>
        def enclose_kanji_katakana(match):
            kanji_katakana = match.group(1)  # The kanji/katakana sequence
            return f'<{kanji_katakana}>'

        # Apply the enclosure function to all appropriate sequences in the text
        preprocessed_text = pattern.sub(enclose_kanji_katakana, ja_text)

        # Return the modified text with appropriate enclosures
        return preprocessed_text


    

    # @staticmethod
    def convert_furigana_to_ass(self, ja_text):
        """Convert furigana format from <kanji>[furigana], standalone [furigana], or <kanji> to ASS ruby format,
        applying styles for kanji and furigana where present."""


        

        def replace_with_ruby(match):
            # Adjusted to handle both standalone and combined cases properly.
            kanji = match.group(1)   # Kanji could be in group 1 when present
            furigana = match.group(2 )or match.group(3)  # Furigana is in group 2  or standalone furigana in group 3
            
            # Initialize an empty string for the result
            result = ""
            
            # Format kanji and furigana if present
            if kanji and furigana:
                result = f"{{\\rKanji}}{kanji}{{\\rFurigana}}{furigana}{{\\rDefault}}"
            elif kanji:
                result = f"{{\\rKanji}}{kanji}{{\\rDefault}}"
            elif furigana:
                result = f"{{\\rFurigana}}{furigana}{{\\rDefault}}"
            
            return result

        # Adjusted regex to correctly match <kanji>[furigana], standalone [furigana], or <kanji>
        pattern = r"<([^>]+)>(?:\[(.*?)\])?|\[([^\]]+)\]"

        # Use lambda to pass match object directly to replace_with_ruby
        return re.sub(pattern, replace_with_ruby, ja_text)

    def convert_hanja_to_ass(self, text):
        """Converts text with Hanja annotations to ASS formatted text with styling, based on the given pattern."""
        
        def replace_with_ass(match):
            hanja = match.group(1)
            hangul = match.group(2)
            # roman = match.group(3)

            result = ""


            
            # If Hanja is present, style it with the Kanji style
            if hanja:
                result += f"{{\\rHanja}}{hanja}{{\\rKorean}}"
            
            # Style the Hangul part with the Hangul style
            if hangul:
                result += f"{{\\rHangul}}{hangul}{{\\rKorean}}"
            
            # Add Romanized Korean (RomanKO) if present, styled differently
            # if roman:
            #     # result += f"{{\\rRomanKO}}({roman}){{\\rDefault}}"
            #     # result += f"{{\\rRomanKO}}{roman}{{\\rDefault}}"
            #     pass

            return result

        # Pattern to match the format: <Hanja>[Hangul](RomanKO)
        # pattern = r"<([^>]+)>\[([^]]+)\]\(([^)]*)\)"
        pattern = r"<([^>]+)>\[([^]]+)\]"

        # Replace matches in the text with styled ASS text
        return re.sub(pattern, replace_with_ass, text)

    def convert_chuhan_to_ass(self, text):
        """Converts text with Chu-Han annotations to ASS formatted text with styling, based on the given pattern."""
        
        def replace_with_ass(match):
            chuhan = match.group(1)
            viet = match.group(2)

            result = ""

            # Style the Chu-Han part with the Kanji (or a specific Chu-Han) style
            if chuhan:
                result += f"{{\\rChuhan}}{chuhan}{{\\rVietnamese}}"
            
            # Style the Viet part with a specific Viet style
            if viet:
                result += f"{{\\rViet}}{viet}{{\\rVietnamese}}"

            return result

        # Pattern to match the format: <Chu-Han>[Viet]
        pattern = r"<([^>]+)>\[([^]]*)\]"

        # Replace matches in the text with styled ASS text
        return re.sub(pattern, replace_with_ass, text)

    def estimate_character_width(self, text):
        half_width_count = 0
        full_width_count = 0

        for char in text:
            # Ordinal value of the character
            ord_char = ord(char)
            # Simple checks for half-width vs. full-width character ranges
            if 0x0020 <= ord_char <= 0x007E or 0xFF61 <= ord_char <= 0xFFDC or 0xFFA0 <= ord_char <= 0xFFBE:
                half_width_count += 1
            elif 0x1100 <= ord_char <= 0x11FF or 0x2E80 <= ord_char <= 0x9FFF or 0xAC00 <= ord_char <= 0xD7AF or 0xFF01 <= ord_char <= 0xFF60 or 0xFFE0 <= ord_char <= 0xFFE6:
                full_width_count += 1

        # Determine the predominant character width in the text
        if half_width_count > full_width_count:
            return "half-width"
        else:
            return "full-width"


    # @staticmethod
    def generate_ass_header(self):
        """Generates the header for an ASS file, adjusting `PlayResX` and `PlayResY` based on video orientation."""
        # Determine if the video is landscape or portrait
        # is_video_landscape = self.video_width > self.video_height
        is_video_landscape = self.is_video_landscape

        # Adjust PlayResX and PlayResY based on orientation
        # play_res_x, play_res_y = (self.base_width, self.base_height) if is_video_landscape else (self.base_height, self.base_width)
        play_res_x, play_res_y = (self.video_width, self.video_height) if is_video_landscape else (self.video_height, self.video_width)

        # wrapping_limit_half_width_default = self.wrapping_limit_half_width_default
        # wrapping_limit_full_width_default = self.wrapping_limit_half_width_default // 2

            

        if self.is_video_landscape:
            max_width = self.video_width * 0.8
            max_height = self.video_height * 0.5 / 8
        else:
            max_width = self.video_width * 0.8 * self.portrait_scale
            max_height = self.video_height * 0.5 / 16

        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        # english_portrait_font_size = find_font_size(sample_texts["english"][:wrapping_limit_half_width_default], font_path, max_width, max_height)


        font_sizes = {}
        for language, text in sample_texts.items():
            char_width_type = self.estimate_character_width(text)
            wrapping_limit = self.wrapping_limit_half_width_default # if char_width_type == 'half-width' else self.wrapping_limit_half_width_default // 2
            text_section = text[:wrapping_limit]
            font_sizes[language] = find_font_size(text_section, self.font_path, max_width, max_height)


        print("calculated font size: ")
        pprint(font_sizes)




        base_font_size = font_sizes["English"]
        chinese_font_size = font_sizes["Chinese"]
        english_font_size = font_sizes["English"] 
        japanese_font_size = font_sizes["Japanese"]
        kanji_font_size = font_sizes["Japanese"]
        furigana_font_size = font_sizes["Japanese"]
        arabic_font_size = font_sizes["Arabic"]
        # korean
        korean_font_size = japanese_font_size 
        hanja_font_size = kanji_font_size 
        hangul_font_size = furigana_font_size 
        romanko_font_size = furigana_font_size 
        #
        spanish_font_size = english_font_size
        french_font_size = english_font_size
        # vietnamese
        vietnamese_font_size = kanji_font_size 
        chuhan_font_size = kanji_font_size 
        viet_font_size = furigana_font_size 
        

        return f"""[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: {play_res_x}
PlayResY: {play_res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Vernada,{base_font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Emoji,BabelStone Flags,{base_font_size},&H00FFFFFF,&H00000000,&H00000000,&H00000000,0,0,0,0,50,50,0,0,1,2,2,2,10,10,10,1
Style: Micphone,Noto Color Emoji,{base_font_size},&H00FFFFFF,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: English,Vernada,{english_font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Chinese,Vernada,{chinese_font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Japanese,Vernada,{japanese_font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Kanji,Vernada,{kanji_font_size},&H003C14DC,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Furigana,Vernada,{furigana_font_size},&H007280FA,&H000000FF,&H00000000,&H64000000,-1,0,0,0,50,50,0,0,1,2,2,2,10,10,10,1
Style: Arabic1,Arial,{arabic_font_size},&H00FACE87,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Arabic,Arial,{arabic_font_size},&H0071B33C,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Korean,Vernada,{korean_font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Hanja1,Vernada,{hanja_font_size},&H003C14DC,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Hanja,Vernada,{hanja_font_size},&H00E16941,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Hangul1,Vernada,{hangul_font_size},&H007280FA,&H000000FF,&H00000000,&H64000000,-1,0,0,0,50,50,0,0,1,2,2,2,10,10,10,1
Style: Hangul,Vernada,{hangul_font_size},&H00FACE87,&H000000FF,&H00000000,&H64000000,-1,0,0,0,50,50,0,0,1,2,2,2,10,10,10,1
Style: RomanKO,Vernada,{romanko_font_size},&H00FACADE,&H000000FF,&H00000000,&H64000000,-1,0,0,0,50,50,0,0,1,1,1,2,10,10,10,1
Style: Spanish1,Arial,{spanish_font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Spanish,Arial,{spanish_font_size},&H0000BFF1,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: French,Arial,{french_font_size},&H003929ED,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: French2,Arial,{french_font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Vietnamese,Arial,{vietnamese_font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Chuhan1,Vernada,{chuhan_font_size},&H003C14DC,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Chuhan,Vernada,{chuhan_font_size},&H00ADDEFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Viet1,Vernada,{viet_font_size},&H007280FA,&H000000FF,&H00000000,&H64000000,-1,0,0,0,50,50,0,0,1,2,2,2,10,10,10,1
Style: Viet,Vernada,{viet_font_size},&H00E1E4FF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,50,50,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""             

    def preprocess_japanese_ruby(self, subtitles):
        """Preprocess Japanese text within subtitles."""
        
        def custom_print(enable_print, message, text):
            """Custom print function controlled by an enable flag."""
            if enable_print:
                print(message, text)
        
        enable_print = False  # Control printing for debugging

        for subtitle in subtitles:
            # Check for Japanese text under the 'ja' key
            if 'ja' in subtitle:
                ja_text = subtitle['ja']
                custom_print(enable_print, "Initial text:", ja_text)

                # Apply preprocessing steps
                ja_text = self.rearrange_brackets(ja_text)
                custom_print(enable_print, "After rearranging brackets:", ja_text)

                ja_text = self.fill_blank_of_katakana_without_furigana(ja_text)
                custom_print(enable_print, "After filling in the blank of <katakana>[]:", ja_text)

                ja_text = self.convert_katakana_in_brackets_to_hiragana(ja_text)
                custom_print(enable_print, "After converting katakana in brackets to hiragana:", ja_text)

                ja_text = self.clean_triplicated_sequences(ja_text)
                custom_print(enable_print, "After simplifying triplicated sequences:", ja_text)

                ja_text = self.clean_duplicated_kanji_hiragana_sequence(ja_text)
                custom_print(enable_print, "After converting duplicated kanji-hiragana sequence:", ja_text)

                ja_text = self.clean_redundant_hiragana_sequence(ja_text)
                custom_print(enable_print, "After removing redundant hiragana sequence:", ja_text)

                ja_text = self.clean_duplicated_hiragana_inside_angle_brackets(ja_text)
                custom_print(enable_print, "After simplifying duplicated hiragana inside angle brackets:", ja_text)

                ja_text = self.convert_standalone_angle_to_square_brackets(ja_text)
                custom_print(enable_print, "After converting standalone angle to square brackets:", ja_text)

                ja_text = self.preprocess_text_for_furigana(ja_text)
                custom_print(enable_print, "After preprocessing text for furigana:", ja_text)


                # Update the Japanese text in the subtitle
                subtitle['ja'] = ja_text
                custom_print(enable_print, "Final text:", ja_text)

        return subtitles

    @staticmethod
    def count_furigana(text):
        # Initialize counts for the specified characters
        count_less_than = text.count('<')
        count_greater_than = text.count('>')
        count_open_bracket = text.count('[')
        count_close_bracket = text.count(']')
        hiragana_count = 0

        # Flag to keep track of whether we are inside square brackets
        inside_brackets = False
        
        for char in text:
            # Check if we enter or exit square brackets
            if char == '[':
                inside_brackets = True
            elif char == ']':
                inside_brackets = False
            # If inside brackets, check if the character is a Hiragana
            elif inside_brackets and 'HIRAGANA' in unicodedata.name(char, ''):
                hiragana_count += 1

        # Return the counts as a dictionary
        # return {
        #     'less_than': count_less_than,
        #     'greater_than': count_greater_than,
        #     'open_bracket': count_open_bracket,
        #     'close_bracket': count_close_bracket,
        #     'hiragana_inside_brackets': hiragana_count,
        # }


        # return count_less_than + count_greater_than + \
        #         count_open_bracket + count_close_bracket + \
        #         hiragana_count / 2

        return hiragana_count / 2



    def save_translated_subtitles_to_json(self, translated_subtitles):
        # Write the constructed ASS content to the output file
        with open(self.output_json_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(translated_subtitles, indent=2, ensure_ascii=False))
        print(f"Subtitles have been processed and saved successfully to {self.output_json_path}.")


    def add_flag_emoji(self, lang_code):
        flags = self.flags
        
        # Return the flag emoji or an empty string if the language code is not found
        return flags.get(lang_code, "")



    def add_microphone_symbol_to_translated_subtitles(self, translated_subtitles):
        """Add a 🎙️ symbol to subtitles in translated_subtitles based on the language specified in self.subtitles."""
        
        for original_subtitle in self.subtitles:
            # Extract the start, end, and language from the original subtitle
            start, end, lang = original_subtitle['start'], original_subtitle['end'], original_subtitle['lang']
            
            # Find the corresponding translated subtitle
            for translated_subtitle in translated_subtitles:
                if translated_subtitle['start'] == start and translated_subtitle['end'] == end:
                    # If a matching subtitle is found, append the 🎙️ symbol to the specified language's text
                    if lang in translated_subtitle:
                        translated_subtitle[lang] = "🔊 " + translated_subtitle[lang] 
        
        return translated_subtitles



    def save_translated_subtitles_to_ass(self, translated_subtitles):
        
        """Save the translated subtitles to an ASS file with text wrapping based on video orientation."""

        # translated_subtitles = self.add_country_flags_to_translated_subtitles(translated_subtitles)
        translated_subtitles = self.add_microphone_symbol_to_translated_subtitles(translated_subtitles)


        if self.is_video_landscape:
            wrapping_limit_half_width_default = self.wrapping_limit_half_width_default
        else:
            wrapping_limit_half_width_default = int(self.wrapping_limit_half_width_default / self.portrait_scale)

        wrapping_limit_half_width_ja = wrapping_limit_half_width_default

        translated_subtitles = self.preprocess_japanese_ruby(translated_subtitles)

        ass_content = self.generate_ass_header()
        for index, item in enumerate(translated_subtitles, start=1):
            # Convert HH:MM:SS,mmm format to seconds
            def convert_to_seconds(t):
                parts = re.split('[:|,]', t)
                if len(parts) == 4:
                    h, m, s, ms = parts
                    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
                elif len(parts) == 3:
                    # Fallback in case the format is not as expected
                    h, m, s = parts
                    total_seconds = int(h) * 3600 + int(m) * 60 + float(s.replace(',', '.'))
                else:
                    raise Exception(f"The format of timestamps is not recognized: {t}. ")
                
                return total_seconds
            
            # Format start and end times to ensure two decimal places with comma
            start_seconds = convert_to_seconds(item['start'])
            end_seconds = convert_to_seconds(item['end'])
            start = "{:02d}:{:02d}:{:05.2f}".format(int(start_seconds // 3600), int((start_seconds % 3600) // 60), start_seconds % 60)#.replace('.', ',')
            end = "{:02d}:{:02d}:{:05.2f}".format(int(end_seconds // 3600), int((end_seconds % 3600) // 60), end_seconds % 60)#.replace('.', ',')

            dialogue_lines = []

            # Process languages in a specific order if needed, then all additional languages
            preferred_order = ['zh', 'en', 'ja', "ar", "ko", "es", "vi", "fr", "uk"][::-1]  # Example: Start with Chinese, then English, then Japanese
            handled_keys = set(preferred_order)

            # Add preferred languages first
            for lang in preferred_order:
                if lang in item:
                    text = item[lang]

                    flag_emoji = self.add_flag_emoji(lang)  # Get the flag emoji without adding a space for separation
                    
                    is_cjk = lang in ['zh', 'ja']  # Assuming CJK for Chinese and Japanese
                    
                    if lang == "ja":
                        wrapping_limit_half_width = wrapping_limit_half_width_ja + self.count_furigana(text)
                    else:
                        wrapping_limit_half_width = wrapping_limit_half_width_default

                    if lang == "ar":
                        style = "Arabic"
                    elif lang == "zh":
                        style = "Chinese"
                    elif lang == "en":
                        style = "English"
                    elif lang == "ja":
                        style = "Japanese"
                    elif lang == "es":
                        style = "Spanish"
                    elif lang == "fr":
                        style = "French"
                    elif lang == "vi":
                        style = "Vietnamese"
                    else:
                        style = "Default"

                   

                    wrapped_text_lines = self.wrap_text(text, wrapping_limit_half_width, is_cjk=is_cjk)
                    dialogue_line = '\\N'.join(wrapped_text_lines)

                    # Prepend flag emoji with the Emoji style and revert back to the original style for the text
                    # if "🔊" in dialogue_line:
                    #     dialogue_line = f"{{\\rMicphone}}{dialogue_line[:1]}{{\\rEmoji}}{flag_emoji}{{\\r{style}}}{dialogue_line[1:]}"
                    # else:
                    #     dialogue_line = f"{{\\rEmoji}}{flag_emoji}{{\\r{style}}}{dialogue_line}"


                    if lang == 'ja':
                        dialogue_line = self.convert_furigana_to_ass(dialogue_line)

                    if lang == "ko":
                        dialogue_line = self.convert_hanja_to_ass(dialogue_line)

                    if lang == "vi":
                        dialogue_line = self.convert_chuhan_to_ass(dialogue_line)


                    subtitle_line = f"Dialogue: 0,{start},{end},{style},,0,0,0,,{dialogue_line}"
                    ass_content += subtitle_line + "\n"

            # Add any additional languages present
            additional_languages = {k: v for k, v in item.items() if k not in handled_keys.union(['start', 'end'])}
            for lang_code, text in additional_languages.items():
                # Additional languages will use the default style as this block does not handle style differentiation
                dialogue_line = self.wrap_text(text, wrapping_limit_half_width_default, is_cjk=False)
                formatted_text = '\\N'.join(dialogue_line)
                subtitle_line = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{formatted_text}"
                ass_content += subtitle_line + "\n"

        # Write the constructed ASS content to the output file
        with open(self.output_sub_path, 'w', encoding='utf-8') as file:
            file.write(ass_content)
        print(f"Subtitles have been processed and saved successfully to {self.output_sub_path}.")


    def wrap_text(self, text, wrapping_limit_half_width, is_cjk=False):
        if not is_cjk:
            # For non-CJK text, directly use the wrapping function.
            # return self.cjkwrap_punctuation(text, wrapping_limit_half_width)
            return [text]

        # Step 1: Wrap the text into lines.
        wrapped_lines = self.cjkwrap_punctuation(text, wrapping_limit_half_width)

        # Step 2: Join lines with '###' to mark original line breaks.
        joined_text = '###'.join(wrapped_lines)

        # if "歴史" in joined_text:
        #     print("joined_text: ", joined_text)

        # Step 3: Correct breakpoints only for structured texts that were split.
        def correct_breakpoints(match):
            structured_text = match.group(0)

            # if "歴史" in joined_text:
            #     for i in range(4):
            #         try:
            #             print(match.group(i))
            #         except:
            #             pass

            # If '###' is inside the structured text, it indicates an incorrect break.
            if '###' in structured_text:
                # Remove '###' and keep the structure intact.
                return "###" + structured_text.replace('###', '') + "###"
            else:
                # If no '###' inside, return the structured text as is.
                return structured_text

        pattern = r'(<[^>]*>)(###)?\[[^\]]*\]|<[^>]*>|(\[[^\]]*\])'
        corrected_text = re.sub(pattern, correct_breakpoints, joined_text)

        # Step 4: Split the text back into lines at '###'.
        corrected_lines = corrected_text.split('###')

        joined_lines = self.join_lines_with_length_check(corrected_lines, wrapping_limit_half_width)

        # return corrected_lines
        return joined_lines

    @staticmethod
    def strip_brackets(input_string):
        # Regular expression pattern to match <, >, [, and ]
        pattern = r'[\<\>\[\]]'
        # Replace matched characters with an empty string
        stripped_string = re.sub(pattern, '', input_string)
        return stripped_string

    def join_lines_with_length_check(self, lines, wrapping_limit_half_width):
        final_lines = []
        current_line = ""
        for line in lines:
            if current_line:
                # Attempt to join with the next line and check if it exceeds the wrapping limit.
                test_line = current_line + line
                wrapped_test = self.cjkwrap_punctuation(self.strip_brackets(test_line), wrapping_limit_half_width)
                if len(wrapped_test) > 1:
                    # If joining exceeds the limit, finalize the current line and start a new one.
                    final_lines.append(current_line)
                    current_line = line
                else:
                    # Otherwise, update the current line to include the next line.
                    current_line = test_line
            else:
                current_line = line

        # Ensure the last accumulated line is added to the final output.
        if current_line:
            final_lines.append(current_line)

        return final_lines


    def cjkwrap_punctuation(self, text, width):
        """
        Custom wrapper for CJK text that prioritizes wrapping at punctuation,
        and adjusts lines to avoid starting with punctuation.
        """


        wrapped_lines = cjkwrap.wrap(text, width)



        # Define full-width and half-width punctuation marks for CJK text
        punctuations = ".。、，,！!？?；;：:「」『』（）()【】[]《》<>「」『』“”\"\""
        # punctuations = ".。、，,！!？?；;：:「」『』（）()【】《》「」『』“”\"\""
        # punctuations = "。、，,！!？?；;：:「」『』（）()【】《》「」『』“”\"\""

        

        # Adjust lines to move punctuation from the beginning of a line to the end of the previous line
        for i in range(1, len(wrapped_lines)):
            if wrapped_lines[i][0] in punctuations:
                # Move punctuation to the end of the previous line if it doesn't exceed width
                if len(wrapped_lines[i-1]) + 1 <= width:
                    wrapped_lines[i-1] += wrapped_lines[i][0]  # Move punctuation to the end of the previous line
                    wrapped_lines[i] = wrapped_lines[i][1:]  # Remove punctuation from the current line

        # Handle case where the first line starts with punctuation and there's no previous line to adjust
        # This might involve a specific strategy, such as re-wrapping with cjkwrap if needed
        # For simplicity, this case is not explicitly handled here but should be considered based on your requirements

        return wrapped_lines



if __name__ == '__main__':
    
    # Example usage:
    input_json_path = '/home/lachlan/Projects/lazyedit/lazyedit/data/IMG_6276_mixed.json'
    output_sub_path = '/home/lachlan/Projects/lazyedit/lazyedit/data/translated_subtitles.srt'
    input_sub_path = '/home/lachlan/Projects/lazyedit/lazyedit/data/IMG_6276_mixed.srt'


    openai_client = OpenAI()
    subtitles_processor = SubtitlesTranslator(openai_client, input_json_path, input_sub_path, output_sub_path)
    subtitles_processor.process_subtitles()