#!/usr/bin/env python3
# NOTE: moved from language_enhance_english.py to english_enhancement.py
"""
English Language Enhancement with Grammatical Analysis - ALWAYS PROCESS VERSION
Features:
- ALWAYS converts any input to English and shows grammatical analysis
- English grammatical analysis and color coding
- Translation to/from English for all languages
- English sentence structure analysis
- No early exits - processes every message regardless of source language
"""

import re
import time
import logging
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from echomind.ai_client_factory import build_with_fallback

logger = logging.getLogger(__name__)

class EnglishGrammaticalType(Enum):
    """English grammatical types for word analysis"""
    # Core sentence elements
    SUBJECT = "subject"
    OBJECT = "object"
    PREDICATE = "predicate"
    COMPLEMENT = "complement"
    
    # Parts of speech
    NOUN = "noun"
    PRONOUN = "pronoun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    ARTICLE = "article"
    DETERMINER = "determiner"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    
    # Verb types
    AUXILIARY = "auxiliary"
    MODAL = "modal"
    LINKING_VERB = "linking_verb"
    PHRASAL_VERB = "phrasal_verb"
    
    # Noun types
    PROPER_NOUN = "proper_noun"
    COMMON_NOUN = "common_noun"
    ABSTRACT_NOUN = "abstract_noun"
    COLLECTIVE_NOUN = "collective_noun"
    
    # Pronoun types
    PERSONAL_PRONOUN = "personal_pronoun"
    POSSESSIVE_PRONOUN = "possessive_pronoun"
    DEMONSTRATIVE_PRONOUN = "demonstrative_pronoun"
    RELATIVE_PRONOUN = "relative_pronoun"
    INTERROGATIVE_PRONOUN = "interrogative_pronoun"
    
    # Adjective types
    COMPARATIVE = "comparative"
    SUPERLATIVE = "superlative"
    POSSESSIVE_ADJECTIVE = "possessive_adjective"
    
    # Other elements
    GERUND = "gerund"
    INFINITIVE = "infinitive"
    PARTICIPLE = "participle"
    QUESTION_WORD = "question_word"
    NEGATION = "negation"
    CONTRACTION = "contraction"
    
    # Punctuation and others
    PUNCTUATION = "punctuation"
    NUMBER = "number"
    OTHER = "other"


@dataclass
class EnglishWord:
    """Represents an English word with grammatical information"""
    word: str
    grammatical_type: EnglishGrammaticalType
    color_rgb: Tuple[int, int, int]
    explanation: Optional[str] = None


@dataclass
class EnglishEnhancementResult:
    """English enhancement result"""
    original_text: str
    source_language: str
    source_language_name: str
    detected_language: str
    language_name: str
    english_text: str
    is_english_content: bool
    english_words: List[EnglishWord]
    processing_time: float
    error: Optional[str] = None


class EnglishGrammaticalColorScheme:
    """Color scheme for English grammatical components"""
    
    COLOR_MAP = {
        # Core sentence elements - Blues and Greens
        EnglishGrammaticalType.SUBJECT: (100, 150, 255),      # Light blue
        EnglishGrammaticalType.OBJECT: (150, 100, 255),       # Purple-blue
        EnglishGrammaticalType.PREDICATE: (100, 255, 150),    # Light green
        EnglishGrammaticalType.COMPLEMENT: (150, 255, 100),   # Yellow-green
        
        # Core parts of speech - Primary colors
        EnglishGrammaticalType.NOUN: (255, 200, 100),         # Orange
        EnglishGrammaticalType.PRONOUN: (255, 150, 100),      # Light orange
        EnglishGrammaticalType.VERB: (100, 255, 100),         # Green
        EnglishGrammaticalType.ADJECTIVE: (255, 100, 150),    # Pink
        EnglishGrammaticalType.ADVERB: (150, 100, 255),       # Purple
        
        # Function words - Grays and muted colors
        EnglishGrammaticalType.ARTICLE: (200, 200, 255),      # Light gray-blue
        EnglishGrammaticalType.DETERMINER: (200, 255, 200),   # Light gray-green
        EnglishGrammaticalType.PREPOSITION: (255, 200, 200),  # Light gray-red
        EnglishGrammaticalType.CONJUNCTION: (200, 200, 200),  # Light gray
        EnglishGrammaticalType.INTERJECTION: (255, 255, 100), # Yellow
        
        # Verb types - Green variations
        EnglishGrammaticalType.AUXILIARY: (150, 255, 150),    # Light green
        EnglishGrammaticalType.MODAL: (100, 200, 100),        # Dark green
        EnglishGrammaticalType.LINKING_VERB: (200, 255, 150), # Yellow-green
        EnglishGrammaticalType.PHRASAL_VERB: (100, 255, 200), # Teal-green
        
        # Noun types - Orange variations
        EnglishGrammaticalType.PROPER_NOUN: (255, 150, 50),   # Dark orange
        EnglishGrammaticalType.COMMON_NOUN: (255, 200, 100),  # Light orange
        EnglishGrammaticalType.ABSTRACT_NOUN: (255, 220, 150), # Pale orange
        EnglishGrammaticalType.COLLECTIVE_NOUN: (255, 180, 80), # Medium orange
        
        # Pronoun types - Orange-red variations
        EnglishGrammaticalType.PERSONAL_PRONOUN: (255, 100, 100),     # Red-orange
        EnglishGrammaticalType.POSSESSIVE_PRONOUN: (255, 120, 120),   # Light red-orange
        EnglishGrammaticalType.DEMONSTRATIVE_PRONOUN: (255, 80, 150), # Pink-red
        EnglishGrammaticalType.RELATIVE_PRONOUN: (255, 150, 120),     # Salmon
        EnglishGrammaticalType.INTERROGATIVE_PRONOUN: (255, 100, 200), # Magenta
        
        # Adjective types - Pink variations
        EnglishGrammaticalType.COMPARATIVE: (255, 120, 180),  # Light pink
        EnglishGrammaticalType.SUPERLATIVE: (255, 80, 160),   # Dark pink
        EnglishGrammaticalType.POSSESSIVE_ADJECTIVE: (255, 150, 200), # Pale pink
        
        # Special forms - Purple variations
        EnglishGrammaticalType.GERUND: (180, 100, 255),       # Blue-purple
        EnglishGrammaticalType.INFINITIVE: (160, 120, 255),   # Light purple
        EnglishGrammaticalType.PARTICIPLE: (200, 100, 255),   # Pink-purple
        EnglishGrammaticalType.QUESTION_WORD: (150, 150, 255), # Light blue-purple
        EnglishGrammaticalType.NEGATION: (255, 100, 100),     # Red
        EnglishGrammaticalType.CONTRACTION: (200, 150, 255),  # Pale purple
        
        # Others
        EnglishGrammaticalType.PUNCTUATION: (150, 150, 150),  # Gray
        EnglishGrammaticalType.NUMBER: (100, 255, 255),       # Cyan
        EnglishGrammaticalType.OTHER: (180, 180, 180),        # Light gray
    }
    
    @classmethod
    def get_color(cls, grammatical_type: EnglishGrammaticalType) -> Tuple[int, int, int]:
        return cls.COLOR_MAP.get(grammatical_type, cls.COLOR_MAP[EnglishGrammaticalType.OTHER])


class EnglishLanguageEnhancer:
    """English language processor — single-pass translate/polish + grammar analysis.

    Optimized to avoid language detection and per-token explanations for speed,
    while keeping the public API stable.
    """
    
    # Language code mappings
    LANGUAGE_NAMES = {
        'en': 'English',
        'ja': 'Japanese',
        'zh': 'Chinese',
        'ko': 'Korean',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'yue': 'Cantonese',
        'auto': 'Auto-detected'
    }
    
    def __init__(self, openai_model: str = "gpt-4o-mini", max_retries: int = 3):
        """Initialize the English language enhancer"""
        try:
            self.openai_client, provider_mode = build_with_fallback(
                use_cache=True,
                cache_dir='cachexxx/english_enhancement_cache',
                max_retries=max_retries
            )
            self.provider_mode = provider_mode
            self.openai_model = openai_model if provider_mode != 'deepseek' else None
            
            # Language detection schema
            self.language_detection_schema = {
                "type": "object",
                "properties": {
                    "language_code": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["language_code", "confidence"],
                "additionalProperties": False
            }
            
            # English conversion schema
            self.english_conversion_schema = {
                "type": "object",
                "properties": {
                    "english_text": {"type": "string"},
                    "is_already_english": {"type": "boolean"},
                    "conversion_notes": {"type": "string"}
                },
                "required": ["english_text", "is_already_english", "conversion_notes"],
                "additionalProperties": False
            }
            
            # English grammatical analysis schema
            self.english_analysis_schema = {
                "type": "object",
                "properties": {
                    "words": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "subject", "object", "predicate", "complement",
                                        "noun", "pronoun", "verb", "adjective", "adverb",
                                        "article", "determiner", "preposition", "conjunction", "interjection",
                                        "auxiliary", "modal", "linking_verb", "phrasal_verb",
                                        "proper_noun", "common_noun", "abstract_noun", "collective_noun",
                                        "personal_pronoun", "possessive_pronoun", "demonstrative_pronoun",
                                        "relative_pronoun", "interrogative_pronoun",
                                        "comparative", "superlative", "possessive_adjective",
                                        "gerund", "infinitive", "participle", "question_word",
                                        "negation", "contraction",
                                        "punctuation", "number", "other"
                                    ]
                                },
                                # No explanation field for speed
                            },
                            "required": ["word", "type"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["words"],
                "additionalProperties": False
            }
            
            # Single-pass schema: translation/polish + grammar tokens
            self.english_combined_schema = {
                "type": "object",
                "properties": {
                    "english_text": {"type": "string"},
                    "words": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "subject", "object", "predicate", "complement",
                                        "noun", "pronoun", "verb", "adjective", "adverb",
                                        "article", "determiner", "preposition", "conjunction", "interjection",
                                        "auxiliary", "modal", "linking_verb", "phrasal_verb",
                                        "proper_noun", "common_noun", "abstract_noun", "collective_noun",
                                        "personal_pronoun", "possessive_pronoun", "demonstrative_pronoun",
                                        "relative_pronoun", "interrogative_pronoun",
                                        "comparative", "superlative", "possessive_adjective",
                                        "gerund", "infinitive", "participle", "question_word",
                                        "negation", "contraction",
                                        "punctuation", "number", "other"
                                    ]
                                }
                            },
                            "required": ["word", "type"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["english_text", "words"],
                "additionalProperties": False
            }
            
            logger.info("✅ English language enhancer initialized (single-pass ready)")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize English language enhancer: {e}")
            self.openai_client = None
    
    def enhance_message(self, text: str, source_language: Optional[str] = None) -> EnglishEnhancementResult:
        """
        FIXED: Enhanced English message processing - ALWAYS converts to English and shows grammatical analysis
        
        Args:
            text: Input text to process
            source_language: Known source language (from transcription or AI response)
        """
        start_time = time.time()
        
        if not text or not text.strip():
            return EnglishEnhancementResult(
                original_text=text,
                source_language=source_language or "unknown",
                source_language_name="Unknown",
                detected_language="unknown",
                language_name="Unknown",
                english_text="",
                is_english_content=False,
                english_words=[],
                processing_time=0,
                error="Empty text"
            )
        
        try:
            # Single-pass translate/polish + analyze. No language detection, no per-token explanations.
            src_lang = (source_language or "unknown")
            source_language_name = self.LANGUAGE_NAMES.get(src_lang, "Unknown")
            combo = self._translate_and_analyze_english(text)
            if not combo:
                return self._create_error_result(text, "English analyze failed", time.time() - start_time, source_language)
            english_text = (combo.get('english_text') or '').strip()
            words_raw = combo.get('words') or []
            english_words = self._process_english_result(words_raw) if english_text else []
            if english_text and not english_words:
                logger.warning("⚠️ ENG: Analysis empty, using simple fallback")
                english_words = self._create_simple_english_fallback(english_text)
            
            processing_time = time.time() - start_time
            logger.info(f"✅ FIXED ENG: English language processing completed in {processing_time:.2f}s")
            
            return EnglishEnhancementResult(
                original_text=text,
                source_language=src_lang,
                source_language_name=source_language_name,
                detected_language='en',
                language_name='English',
                english_text=english_text,
                is_english_content=True,  # FIXED: Always True because we converted to English
                english_words=english_words,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ FIXED ENG: English language processing error: {e}")
            return self._create_error_result(text, str(e), time.time() - start_time, source_language)
    
    def _detect_language(self, text: str) -> Optional[Dict]:
        """Detect the language of the input text"""
        try:
            prompt = f"""Detect the primary language of this text: "{text}"

Return the ISO 639-1 language code (like 'en' for English, 'ja' for Japanese, 'zh' for Chinese, 'yue' for Cantonese, etc.) and confidence level.

Common codes:
- en: English
- ja: Japanese  
- zh: Chinese (Mandarin)
- yue: Cantonese
- ko: Korean
- es: Spanish
- fr: French
- de: German
- it: Italian
- pt: Portuguese
- ru: Russian
- ar: Arabic
- hi: Hindi
- th: Thai
- vi: Vietnamese
"""
            
            cache_key = f"eng_lang_detect_{abs(hash(text))}.json"
            
            result = self.openai_client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.language_detection_schema,
                filename=cache_key,
                schema_name="english_language_detection",
                model=self.openai_model
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ English language detection error: {e}")
            return None
    
    def _convert_to_english(self, text: str, source_language: str) -> Optional[Dict]:
        """FIXED: ALWAYS convert and clean text to proper English"""
        try:
            if source_language == 'en' and self._is_mostly_english(text):
                # Already English, just clean it
                prompt = f"""Clean and standardize this English text for grammatical analysis: "{text}"

Requirements:
- Correct any grammatical errors
- Ensure proper English sentence structure
- Keep the same meaning and tone
- Use natural English expressions
- Output should be clean English suitable for grammatical analysis

If the text is already perfect English, you can return it as-is.
"""
            else:
                # FIXED: ALWAYS convert to English regardless of source language
                language_name = self.LANGUAGE_NAMES.get(source_language, source_language)
                prompt = f"""Convert this {language_name} text to natural, clean English: "{text}"

Requirements:
- Translate to natural, conversational English
- Use appropriate tone and style for the context
- Ensure proper English grammar and sentence structure
- Keep the same meaning and tone as the original
- Output should be suitable for grammatical analysis

The result should be clean English text that flows naturally.

IMPORTANT: Even if the source is Japanese, Chinese, or any other language, always provide a natural English translation.
"""
            
            cache_key = f"eng_convert_{source_language}_{abs(hash(text))}.json"
            
            result = self.openai_client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.english_conversion_schema,
                filename=cache_key,
                schema_name="english_conversion",
                model=self.openai_model
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ English conversion error: {e}")
            return None
    
    def _analyze_english_grammar(self, english_text: str) -> List[EnglishWord]:
        """Analyze English text for grammatical components"""
        try:
            prompt = f"""Analyze this English text for grammatical components: "{english_text}"

Break into words with:
1. word: the word/punctuation
2. type: grammatical type from the enum list

Provide detailed grammatical analysis including:
- Parts of speech (noun, verb, adjective, etc.)
- Sentence roles (subject, object, predicate)
- Specific types (proper noun, auxiliary verb, etc.)
- Function words (articles, prepositions, conjunctions)

Be precise with grammatical categorization.
"""
            
            cache_key = f"eng_grammar_{abs(hash(english_text))}.json"
            
            result = self.openai_client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.english_analysis_schema,
                filename=cache_key,
                schema_name="english_grammatical_analysis",
                model=self.openai_model
            )
            
            if result and 'words' in result:
                return self._process_english_result(result['words'])
            
            return []
            
        except Exception as e:
            logger.error(f"❌ English grammatical analysis error: {e}")
            return []
    
    def _process_english_result(self, words_data: List[Dict]) -> List[EnglishWord]:
        """Process English analysis result into EnglishWord objects"""
        processed_words = []
        
        for word_data in words_data:
            word = word_data.get('word', '').strip()
            type_str = word_data.get('type', 'other')
            explanation = word_data.get('explanation', '')
            
            if not word:
                continue
            
            # Convert to enum
            try:
                grammatical_type = EnglishGrammaticalType(type_str)
            except ValueError:
                grammatical_type = EnglishGrammaticalType.OTHER
            
            # Get color
            color = EnglishGrammaticalColorScheme.get_color(grammatical_type)
            
            processed_words.append(EnglishWord(
                word=word,
                grammatical_type=grammatical_type,
                color_rgb=color,
                explanation=explanation if explanation else None
            ))
        
        return processed_words
    
    def _create_simple_english_fallback(self, english_text: str) -> List[EnglishWord]:
        """Create simple fallback English words when analysis fails"""
        words = []
        
        # Simple word splitting
        word_tokens = re.findall(r'\b\w+\b|[^\w\s]', english_text)
        
        for token in word_tokens:
            if token.strip():
                words.append(EnglishWord(
                    word=token,
                    grammatical_type=EnglishGrammaticalType.OTHER,
                    color_rgb=(180, 180, 180)  # Light gray
                ))
        
        return words
    
    def _is_mostly_english(self, text: str) -> bool:
        """Check if text is mostly English (>70% English characters)"""
        if not text:
            return False
        
        # Count ASCII letters (rough English approximation)
        english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
        total_alpha_chars = sum(1 for char in text if char.isalpha())
        
        return total_alpha_chars > 0 and (english_chars / total_alpha_chars) > 0.7

    def _translate_and_analyze_english(self, text: str) -> Optional[Dict[str, Any]]:
        """Single request: translate/polish to English and analyze grammar."""
        try:
            prompt = f"""
If the text : "{text}" is not English Translate it into English first . 

If it's already English , polish the english with more correct and native expression. 

Analyze this English text for grammatical components.

Break into words with:
1. english_text: native and exact english translation or polish of original english 
2. word: the word/punctuation of the english text
3. type: grammatical type from the enum list of the english text

Provide detailed grammatical analysis including:
- Parts of speech (noun, verb, adjective, etc.)
- Sentence roles (subject, object, predicate)
- Specific types (proper noun, auxiliary verb, etc.)
- Function words (articles, prepositions, conjunctions)

Be precise with grammatical categorization.
"""

            cache_key = f"eng_combo_{abs(hash(text))}.json"
            result = self.openai_client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.english_combined_schema,
                filename=cache_key,
                schema_name="english_translate_analyze",
                model=self.openai_model
            )
            return result
        except Exception as e:
            logger.error(f"❌ English combined analyze error: {e}")
            return None
    
    def _create_error_result(self, original_text: str, error_message: str, processing_time: float, source_language: Optional[str] = None) -> EnglishEnhancementResult:
        """Create error result"""
        return EnglishEnhancementResult(
            original_text=original_text,
            source_language=source_language or "unknown",
            source_language_name=self.LANGUAGE_NAMES.get(source_language or "unknown", "Unknown"),
            detected_language="en",
            language_name="English",
            english_text="",
            is_english_content=False,
            english_words=[],
            processing_time=processing_time,
            error=error_message
        )


# Utility functions for integration
def enhance_message_with_english(text: str, enhancer: EnglishLanguageEnhancer, source_language: Optional[str] = None) -> EnglishEnhancementResult:
    """English enhancement wrapper — single-pass translate/polish + analyze."""
    return enhancer.enhance_message(text, source_language)


def format_english_for_display(english_words: List[EnglishWord]) -> Dict[str, Any]:
    """Format English words for HTML display"""
    formatted_words = []
    
    for word in english_words:
        formatted_words.append({
            'word': word.word,
            'type': word.grammatical_type.value,
            'color': f"rgb({word.color_rgb[0]}, {word.color_rgb[1]}, {word.color_rgb[2]})",
            'explanation': word.explanation
        })
    
    return {
        'words': formatted_words,
        'html': generate_english_html(english_words)
    }


def generate_english_html(english_words: List[EnglishWord]) -> str:
    """Generate HTML for English display with grammatical coloring"""
    html_parts = []
    
    for word in english_words:
        color = f"rgb({word.color_rgb[0]}, {word.color_rgb[1]}, {word.color_rgb[2]})"
        
        if word.explanation:
            # Word with explanation (tooltip)
            html_parts.append(f'''
                <span style="color: {color};" title="{word.explanation}">{word.word}</span>
            ''')
        else:
            # Word without explanation
            html_parts.append(f'<span style="color: {color};">{word.word}</span>')
    
    return ''.join(html_parts)


if __name__ == "__main__":
    # Test the FIXED English language enhancer
    print("🧪 Testing FIXED English Language Enhancer - ALWAYS PROCESSES...")
    
    enhancer = EnglishLanguageEnhancer()
    
    test_cases = [
        ("Hello, how are you today?", "en"),
        ("今日はいい天気ですね。", "ja"),
        ("Hola, ¿cómo estás?", "es"),
        ("你好，今天天气很好。", "zh"),
        ("Bonjour, comment ça va?", "fr"),
        ("Guten Tag, wie geht es Ihnen?", "de"),
    ]
    
    for text, source_lang in test_cases:
        print(f"\n📝 Testing: {text} (source: {source_lang})")
        result = enhancer.enhance_message(text, source_lang)
        
        if result.error:
            print(f"❌ Error: {result.error}")
        else:
            print(f"🔍 Source: {result.source_language_name}")
            print(f"🔍 Detected: {result.language_name}")
            print(f"🇬🇧 English: {result.english_text}")
            print(f"✨ English Content: {result.is_english_content}")
            print(f"⏱️ Processing time: {result.processing_time:.2f}s")
            
            if result.english_words:
                english_html = generate_english_html(result.english_words)
                print(f"✨ English HTML: {english_html}")
            else:
                print("📝 No English analysis generated")
