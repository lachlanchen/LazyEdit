#!/usr/bin/env python3
# NOTE: moved from language_enhance_japanese.py to japanese_enhancement.py
"""
Enhanced Language Enhancement for Japanese Furigana Generation - ALWAYS PROCESS VERSION
Features:
- ALWAYS converts any input to Japanese and generates furigana
- No early exits - processes every message regardless of source language
- Better language code mapping for TTS
- Source language preservation
"""

import re
import time
import logging
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from echomind.ai_client_factory import build_with_fallback

logger = logging.getLogger(__name__)

class GrammaticalType(Enum):
    """Grammatical types for Japanese components (unchanged)"""
    # Core sentence elements
    SUBJECT = "subject"
    OBJECT = "object"
    TOPIC = "topic"
    PREDICATE = "predicate"
    
    # Word types
    NOUN = "noun"
    PRONOUN = "pronoun"
    VERB = "verb"
    I_ADJECTIVE = "i_adjective"
    NA_ADJECTIVE = "na_adjective"
    ADVERB = "adverb"
    
    # Particles - Core case markers
    PARTICLE_WA = "particle_wa"
    PARTICLE_GA = "particle_ga"
    PARTICLE_WO = "particle_wo"
    PARTICLE_NI = "particle_ni"
    PARTICLE_DE = "particle_de"
    PARTICLE_TO = "particle_to"
    PARTICLE_NO = "particle_no"
    PARTICLE_HE = "particle_he"
    
    # Other particles
    PARTICLE_KARA = "particle_kara"
    PARTICLE_MADE = "particle_made"
    PARTICLE_YORI = "particle_yori"
    PARTICLE_MO = "particle_mo"
    PARTICLE_KA = "particle_ka"
    PARTICLE_YA = "particle_ya"
    PARTICLE_DEMO = "particle_demo"
    PARTICLE_DAKE = "particle_dake"
    PARTICLE_SHIKA = "particle_shika"
    PARTICLE_NADO = "particle_nado"
    PARTICLE_OTHER = "particle_other"
    
    # Grammar elements
    AUXILIARY = "auxiliary"
    CONJUNCTION = "conjunction"
    COPULA = "copula"
    HONORIFIC = "honorific"
    HUMBLE = "humble"
    
    # Special types
    COUNTER = "counter"
    NUMBER = "number"
    DEMONSTRATIVE = "demonstrative"
    QUESTION_WORD = "question_word"
    INTERJECTION = "interjection"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    
    # Punctuation and others
    PUNCTUATION = "punctuation"
    OTHER = "other"


@dataclass
class FuriganaWord:
    """Represents a word with furigana and grammatical information"""
    word: str
    furigana: Optional[str]
    grammatical_type: GrammaticalType
    color_rgb: Tuple[int, int, int]


@dataclass
class LanguageEnhancementResult:
    """Enhanced result with language information"""
    original_text: str
    source_language: str
    source_language_name: str
    detected_language: str
    language_name: str
    japanese_text: str
    is_japanese_content: bool
    furigana_words: List[FuriganaWord]
    tts_language_code: str
    processing_time: float
    error: Optional[str] = None


class GrammaticalColorScheme:
    """Color scheme for grammatical components (unchanged)"""
    
    COLOR_MAP = {
        # Core sentence elements
        GrammaticalType.SUBJECT: (255, 100, 100),
        GrammaticalType.OBJECT: (100, 150, 255),
        GrammaticalType.TOPIC: (255, 180, 180),
        GrammaticalType.PREDICATE: (150, 255, 150),
        
        # Word types
        GrammaticalType.NOUN: (255, 255, 150),
        GrammaticalType.PRONOUN: (255, 220, 120),
        GrammaticalType.VERB: (100, 255, 100),
        GrammaticalType.I_ADJECTIVE: (255, 200, 100),
        GrammaticalType.NA_ADJECTIVE: (255, 170, 120),
        GrammaticalType.ADVERB: (200, 100, 255),
        
        # Core particles
        GrammaticalType.PARTICLE_WA: (255, 150, 150),
        GrammaticalType.PARTICLE_GA: (150, 255, 150),
        GrammaticalType.PARTICLE_WO: (150, 150, 255),
        GrammaticalType.PARTICLE_NI: (255, 255, 100),
        GrammaticalType.PARTICLE_DE: (100, 255, 255),
        GrammaticalType.PARTICLE_TO: (255, 100, 255),
        GrammaticalType.PARTICLE_NO: (255, 200, 255),
        GrammaticalType.PARTICLE_HE: (200, 255, 200),
        
        # Other particles
        GrammaticalType.PARTICLE_KARA: (255, 150, 100),
        GrammaticalType.PARTICLE_MADE: (150, 255, 100),
        GrammaticalType.PARTICLE_YORI: (100, 255, 150),
        GrammaticalType.PARTICLE_MO: (255, 100, 150),
        GrammaticalType.PARTICLE_KA: (150, 100, 255),
        GrammaticalType.PARTICLE_YA: (255, 255, 200),
        GrammaticalType.PARTICLE_DEMO: (200, 150, 255),
        GrammaticalType.PARTICLE_DAKE: (255, 200, 150),
        GrammaticalType.PARTICLE_SHIKA: (200, 255, 150),
        GrammaticalType.PARTICLE_NADO: (150, 200, 255),
        GrammaticalType.PARTICLE_OTHER: (200, 200, 200),
        
        # Grammar elements
        GrammaticalType.AUXILIARY: (150, 200, 150),
        GrammaticalType.CONJUNCTION: (200, 150, 200),
        GrammaticalType.COPULA: (255, 220, 150),
        GrammaticalType.HONORIFIC: (200, 180, 255),
        GrammaticalType.HUMBLE: (180, 200, 255),
        
        # Special types
        GrammaticalType.COUNTER: (255, 180, 120),
        GrammaticalType.NUMBER: (120, 255, 180),
        GrammaticalType.DEMONSTRATIVE: (180, 120, 255),
        GrammaticalType.QUESTION_WORD: (255, 120, 180),
        GrammaticalType.INTERJECTION: (255, 255, 120),
        GrammaticalType.PREFIX: (200, 255, 255),
        GrammaticalType.SUFFIX: (255, 200, 255),
        
        # Punctuation and others
        GrammaticalType.PUNCTUATION: (180, 180, 180),
        GrammaticalType.OTHER: (220, 220, 220),
    }
    
    @classmethod
    def get_color(cls, grammatical_type: GrammaticalType) -> Tuple[int, int, int]:
        return cls.COLOR_MAP.get(grammatical_type, cls.COLOR_MAP[GrammaticalType.OTHER])


class LanguageEnhancer:
    """FIXED: Enhanced language processor that ALWAYS processes to Japanese"""
    
    # Enhanced language code mappings
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
    
    # TTS Language mapping based on content analysis
    @staticmethod
    def get_tts_language_code(text: str, detected_language: str) -> str:
        """
        Determine the best TTS language code based on text analysis
        
        Rules:
        - Pure languages: en, all_yue, all_zh, all_ko, all_ja
        - Mixed with English: yue, zh, ko, ja
        - Mixed more than 3 languages: auto or auto_yue
        """
        if not text or not text.strip():
            return "auto"
        
        # Count different script types
        has_english = bool(re.search(r'[a-zA-Z]', text))
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        has_japanese_hiragana = bool(re.search(r'[\u3040-\u309f]', text))
        has_japanese_katakana = bool(re.search(r'[\u30a0-\u30ff]', text))
        has_korean = bool(re.search(r'[\uac00-\ud7af]', text))
        has_arabic = bool(re.search(r'[\u0600-\u06ff]', text))
        
        has_japanese = has_japanese_hiragana or has_japanese_katakana
        
        # Count language types
        language_count = sum([
            has_english,
            has_chinese,
            has_japanese,
            has_korean,
            has_arabic
        ])
        
        # Determine if it's Cantonese vs Mandarin (simplified heuristic)
        is_cantonese = detected_language == 'yue' or 'yue' in detected_language.lower()
        
        if language_count >= 3:
            # Mixed more than 3 languages
            return "auto_yue" if is_cantonese else "auto"
        elif language_count == 2:
            # Mixed with English
            if has_japanese and has_english:
                return "ja"
            elif has_chinese and has_english:
                return "yue" if is_cantonese else "zh"
            elif has_korean and has_english:
                return "ko"
            else:
                return "auto"
        elif language_count == 1:
            # Pure language
            if has_english:
                return "en"
            elif has_japanese:
                return "all_ja"
            elif has_chinese:
                return "all_yue" if is_cantonese else "all_zh"
            elif has_korean:
                return "all_ko"
            else:
                return "auto"
        else:
            return "auto"
    
    def __init__(self, openai_model: str = "gpt-4o-mini", max_retries: int = 3):
        """Initialize the enhanced language enhancer"""
        try:
            self.openai_client, provider_mode = build_with_fallback(
                use_cache=True,
                cache_dir='cachexxx/japanese_enhancement_cache',
                max_retries=max_retries
            )
            self.provider_mode = provider_mode
            self.openai_model = openai_model if provider_mode != 'deepseek' else None
            
            # Language detection schema (unchanged)
            self.language_detection_schema = {
                "type": "object",
                "properties": {
                    "language_code": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["language_code", "confidence"],
                "additionalProperties": False
            }
            
            # Japanese cleaning and conversion schema
            self.japanese_conversion_schema = {
                "type": "object",
                "properties": {
                    "japanese_text": {"type": "string"},
                    "is_already_japanese": {"type": "boolean"},
                    "conversion_notes": {"type": "string"}
                },
                "required": ["japanese_text", "is_already_japanese", "conversion_notes"],
                "additionalProperties": False
            }
            
            # Furigana analysis schema (unchanged)
            self.furigana_schema = {
                "type": "object",
                "properties": {
                    "words": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "furigana": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "subject", "object", "topic", "predicate",
                                        "noun", "pronoun", "verb", "i_adjective", "na_adjective", "adverb",
                                        "particle_wa", "particle_ga", "particle_wo", "particle_ni", 
                                        "particle_de", "particle_to", "particle_no", "particle_he",
                                        "particle_kara", "particle_made", "particle_yori", "particle_mo",
                                        "particle_ka", "particle_ya", "particle_demo", "particle_dake",
                                        "particle_shika", "particle_nado", "particle_other",
                                        "auxiliary", "conjunction", "copula", "honorific", "humble",
                                        "counter", "number", "demonstrative", "question_word", 
                                        "interjection", "prefix", "suffix",
                                        "punctuation", "other"
                                    ]
                                }
                            },
                            "required": ["word", "furigana", "type"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["words"],
                "additionalProperties": False
            }

            # Combined schema: translation/polish + furigana tokens
            self.japanese_combined_schema = {
                "type": "object",
                "properties": {
                    "japanese_text": {"type": "string"},
                    "words": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "furigana": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "subject", "object", "topic", "predicate",
                                        "noun", "pronoun", "verb", "i_adjective", "na_adjective", "adverb",
                                        "particle_wa", "particle_ga", "particle_wo", "particle_ni", 
                                        "particle_de", "particle_to", "particle_no", "particle_he",
                                        "particle_kara", "particle_made", "particle_yori", "particle_mo",
                                        "particle_ka", "particle_ya", "particle_demo", "particle_dake",
                                        "particle_shika", "particle_nado", "particle_other",
                                        "auxiliary", "conjunction", "copula", "honorific", "humble",
                                        "counter", "number", "demonstrative", "question_word", 
                                        "interjection", "prefix", "suffix",
                                        "punctuation", "other"
                                    ]
                                }
                            },
                            "required": ["word", "furigana", "type"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["japanese_text", "words"],
                "additionalProperties": False
            }
            
            logger.info("✅ Japanese language enhancer initialized (single-pass ready)")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize enhanced language enhancer: {e}")
            self.openai_client = None
    
    def enhance_message(self, text: str, source_language: Optional[str] = None) -> LanguageEnhancementResult:
        """
        FIXED: Enhanced message processing - ALWAYS converts to Japanese and processes furigana
        
        Args:
            text: Input text to process
            source_language: Known source language (from transcription or AI response)
        """
        start_time = time.time()
        
        if not text or not text.strip():
            return LanguageEnhancementResult(
                original_text=text,
                source_language=source_language or "unknown",
                source_language_name="Unknown",
                detected_language="unknown",
                language_name="Unknown",
                japanese_text="",
                is_japanese_content=False,
                furigana_words=[],
                tts_language_code="auto",
                processing_time=0,
                error="Empty text"
            )
        
        try:
            # Single-pass: translate/polish + analyze. No language detection.
            src_lang = (source_language or "unknown")
            source_language_name = self.LANGUAGE_NAMES.get(src_lang, "Unknown")

            combo = self._translate_and_analyze_japanese(text)
            if not combo:
                return self._create_error_result(text, "Japanese analyze failed", time.time() - start_time, source_language)

            japanese_text = (combo.get('japanese_text') or '').strip()
            words_raw = combo.get('words') or []

            # Determine TTS language code based on content (bias to Japanese)
            tts_language_code = self.get_tts_language_code(japanese_text or text, 'ja')

            # Build furigana list
            furigana_words: List[FuriganaWord] = []
            if japanese_text:
                furigana_words = self._process_furigana_result(words_raw)
                if not furigana_words:
                    logger.warning("⚠️ JA: Analysis empty, using simple fallback")
                    furigana_words = self._create_simple_fallback(japanese_text)
            
            processing_time = time.time() - start_time
            logger.info(f"✅ FIXED: Enhanced language processing completed in {processing_time:.2f}s")
            
            return LanguageEnhancementResult(
                original_text=text,
                source_language=src_lang,
                source_language_name=source_language_name,
                detected_language='ja',
                language_name='Japanese',
                japanese_text=japanese_text,
                is_japanese_content=True,
                furigana_words=furigana_words,
                tts_language_code=tts_language_code,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ FIXED: Enhanced language processing error: {e}")
            return self._create_error_result(text, str(e), time.time() - start_time, source_language)
    
    def _detect_language(self, text: str) -> Optional[Dict]:
        """Detect the language of the input text (unchanged)"""
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
            
            cache_key = f"lang_detect_{abs(hash(text))}.json"
            
            result = self.openai_client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.language_detection_schema,
                filename=cache_key,
                schema_name="language_detection",
                model=self.openai_model
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Language detection error: {e}")
            return None
    
    def _convert_to_japanese(self, text: str, source_language: str) -> Optional[Dict]:
        """FIXED: ALWAYS convert to proper Japanese for furigana processing"""
        try:
            if source_language == 'ja' and self._is_mostly_japanese(text):
                # Already Japanese, just clean it
                prompt = f"""Clean and standardize this Japanese text for furigana analysis: "{text}"

Requirements:
- Remove any foreign words and replace with natural Japanese equivalents
- Ensure proper Japanese grammar and sentence structure
- Keep the same meaning and tone
- Use natural Japanese expressions
- Output should be pure Japanese

If the text is already perfect Japanese, you can return it as-is.
"""
            else:
                # FIXED: ALWAYS convert to Japanese regardless of source language
                language_name = self.LANGUAGE_NAMES.get(source_language, source_language)
                prompt = f"""Convert this {language_name} text to natural, clean Japanese: "{text}"

Requirements:
- Translate to natural, conversational Japanese
- Use appropriate politeness level for the context
- Ensure proper Japanese grammar and sentence structure
- Use pure Japanese without foreign words
- Keep the same meaning and tone as the original

The result should be clean Japanese text that flows naturally.

IMPORTANT: Even if the source is English, Chinese, or any other language, always provide a natural Japanese translation.
"""
            
            cache_key = f"jp_convert_{source_language}_{abs(hash(text))}.json"
            
            result = self.openai_client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.japanese_conversion_schema,
                filename=cache_key,
                schema_name="japanese_conversion",
                model=self.openai_model
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Japanese conversion error: {e}")
            return None
    
    def _analyze_furigana(self, japanese_text: str) -> List[FuriganaWord]:
        """Analyze Japanese text and generate furigana with grammatical coloring (unchanged)"""
        try:
            prompt = f"""Analyze this clean Japanese text for furigana: "{japanese_text}"

Break into words with:
1. word: the word/particle/punctuation  
2. furigana: complete reading for the ENTIRE word (ALWAYS provide, even for hiragana)
3. type: grammatical type

CRITICAL: Provide complete, accurate furigana for the entire word.
This text should be clean Japanese suitable for furigana analysis.
"""
            
            cache_key = f"furigana_{abs(hash(japanese_text))}.json"
            
            result = self.openai_client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.furigana_schema,
                filename=cache_key,
                schema_name="furigana_analysis",
                model=self.openai_model
            )
            
            if result and 'words' in result:
                return self._process_furigana_result(result['words'])
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Furigana analysis error: {e}")
            return []

    def _clean_furigana_for_kanji_only(self, word: str, furigana: str) -> Optional[str]:
        """
        Clean furigana to only show readings for kanji, not hiragana
        
        Examples:
        - 食べる (たべる) -> 食[た]べる  
        - 今日 (きょう) -> 今日[きょう] (both kanji)
        - ありがとう (ありがとう) -> None (all hiragana)
        """
        if not word or not furigana or word == furigana:
            return None
            
        # If word is all hiragana, no furigana needed
        if self._is_all_hiragana(word):
            return None
        
        # If word is all kanji, keep full furigana
        if self._is_all_kanji_and_punctuation(word):
            return furigana
        
        # Mixed kanji/hiragana - need intelligent cleaning
        return self._extract_kanji_furigana(word, furigana)

    def _is_all_kanji_and_punctuation(self, text: str) -> bool:
        """Check if text is all kanji (and punctuation)"""
        for char in text:
            if not (self._is_kanji(char) or char in '、。！？ー'):
                return False
        return True

    def _extract_kanji_furigana(self, word: str, furigana: str) -> Optional[str]:
        """
        Extract furigana that corresponds only to kanji parts
        """
        segments = self._segment_word_by_script(word)
        
        if not segments:
            return furigana
        
        # Try to match furigana to kanji segments
        cleaned_readings = []
        furigana_pos = 0
        
        for i, (segment_type, segment_text) in enumerate(segments):
            if segment_type == 'kanji':
                # This kanji segment needs furigana
                remaining_furigana = furigana[furigana_pos:]
                
                # Find the next hiragana segment in the original word
                next_hiragana = self._find_next_hiragana_segment(word, segments, i)
                
                if next_hiragana:
                    # Look for this hiragana sequence in the remaining furigana
                    hiragana_pos = remaining_furigana.find(next_hiragana)
                    if hiragana_pos > 0:
                        # Take furigana up to this point
                        kanji_reading = remaining_furigana[:hiragana_pos]
                        furigana_pos += len(kanji_reading)
                        cleaned_readings.append(kanji_reading)
                    else:
                        # Fallback: estimate based on kanji count
                        estimated_length = min(len(segment_text) * 2, len(remaining_furigana))
                        kanji_reading = remaining_furigana[:estimated_length]
                        furigana_pos += estimated_length
                        cleaned_readings.append(kanji_reading)
                else:
                    # Last segment - take remaining furigana
                    cleaned_readings.append(remaining_furigana)
                    break
                    
            elif segment_type == 'hiragana':
                # Skip hiragana in furigana (it should match the word)
                hiragana_length = len(segment_text)
                if furigana[furigana_pos:furigana_pos + hiragana_length] == segment_text:
                    furigana_pos += hiragana_length
                # Don't add to cleaned_readings - we skip hiragana parts
        
        # Combine the kanji readings
        if cleaned_readings and any(reading.strip() for reading in cleaned_readings):
            return ''.join(cleaned_readings).strip()
        
        return None

    def _segment_word_by_script(self, word: str) -> List[Tuple[str, str]]:
        """
        Segment word into kanji and hiragana parts
        
        Returns list of (type, text) tuples where type is 'kanji' or 'hiragana'
        """
        if not word:
            return []
        
        segments = []
        current_type = None
        current_text = ""
        
        for char in word:
            if self._is_kanji(char):
                char_type = 'kanji'
            elif self._is_hiragana(char):
                char_type = 'hiragana'
            elif self._is_katakana(char):
                char_type = 'katakana'  # Treat similar to hiragana
            else:
                char_type = 'other'
            
            if char_type == current_type:
                current_text += char
            else:
                if current_text:
                    segments.append((current_type, current_text))
                current_type = char_type
                current_text = char
        
        if current_text:
            segments.append((current_type, current_text))
        
        return segments

    def _find_next_hiragana_segment(self, word: str, segments: List[Tuple[str, str]], current_index: int) -> Optional[str]:
        """Find the next hiragana segment after current position"""
        for i in range(current_index + 1, len(segments)):
            segment_type, segment_text = segments[i]
            if segment_type in ['hiragana', 'katakana']:
                return segment_text
        return None

    def _process_furigana_result(self, words_data: List[Dict]) -> List[FuriganaWord]:
        """
        FIXED: Create separate segments for kanji (with furigana) and hiragana (without)
        """
        processed_words = []
        
        for word_data in words_data:
            word = word_data.get('word', '').strip()
            furigana = word_data.get('furigana', '').strip()
            type_str = word_data.get('type', 'other')
            
            if not word:
                continue
            
            # Convert to enum
            try:
                grammatical_type = GrammaticalType(type_str)
            except ValueError:
                grammatical_type = GrammaticalType.OTHER
            
            # Get color
            color = GrammaticalColorScheme.get_color(grammatical_type)
            
            # ✨ FIXED: Create multiple segments instead of single word
            segments = self._create_furigana_segments(word, furigana, grammatical_type, color)
            processed_words.extend(segments)  # Use extend, not append!
        
        return processed_words

    def _create_furigana_segments(self, word: str, furigana: str, grammatical_type, color) -> List[FuriganaWord]:
        """
        Create proper segments: kanji parts get furigana, hiragana parts don't
        """
        if not word or not furigana or word == furigana:
            return [FuriganaWord(word=word, furigana=None, grammatical_type=grammatical_type, color_rgb=color)]
        
        # All hiragana - no furigana needed
        if self._is_all_hiragana(word):
            return [FuriganaWord(word=word, furigana=None, grammatical_type=grammatical_type, color_rgb=color)]
        
        # All kanji - keep full furigana
        if self._is_all_kanji_and_punctuation(word):
            return [FuriganaWord(word=word, furigana=furigana, grammatical_type=grammatical_type, color_rgb=color)]
        
        # Mixed kanji/hiragana - create segments
        return self._segment_mixed_word_with_furigana(word, furigana, grammatical_type, color)

    def _segment_mixed_word_with_furigana(self, word: str, furigana: str, grammatical_type, color) -> List[FuriganaWord]:
        """
        CORE FIX: Create separate FuriganaWord objects for kanji and hiragana parts
        
        食べる (たべる) → [FuriganaWord("食", "た"), FuriganaWord("べる", None)]
        """
        segments = self._segment_word_by_script(word)
        if not segments:
            return [FuriganaWord(word=word, furigana=None, grammatical_type=grammatical_type, color_rgb=color)]
        
        result_segments = []
        furigana_pos = 0
        
        for i, (segment_type, segment_text) in enumerate(segments):
            if segment_type == 'kanji':
                # Extract furigana for this kanji segment
                remaining_furigana = furigana[furigana_pos:]
                
                # Find next hiragana to know where kanji reading ends
                next_hiragana = self._find_next_hiragana_segment(word, segments, i)
                
                if next_hiragana:
                    # Look for hiragana in remaining furigana
                    hiragana_pos = remaining_furigana.find(next_hiragana)
                    if hiragana_pos > 0:
                        kanji_reading = remaining_furigana[:hiragana_pos]
                        furigana_pos += len(kanji_reading)
                    else:
                        # Fallback: estimate
                        estimated_length = min(len(segment_text) * 3, len(remaining_furigana))
                        kanji_reading = remaining_furigana[:estimated_length]
                        furigana_pos += estimated_length
                else:
                    # Last kanji segment - take remaining
                    kanji_reading = remaining_furigana
                
                # Create kanji segment WITH furigana
                result_segments.append(FuriganaWord(
                    word=segment_text,
                    furigana=kanji_reading.strip() if kanji_reading.strip() else None,
                    grammatical_type=grammatical_type,
                    color_rgb=color
                ))
                
            elif segment_type in ['hiragana', 'katakana']:
                # Skip in furigana tracking
                if furigana_pos < len(furigana) and furigana[furigana_pos:furigana_pos + len(segment_text)] == segment_text:
                    furigana_pos += len(segment_text)
                
                # Create hiragana segment WITHOUT furigana
                result_segments.append(FuriganaWord(
                    word=segment_text,
                    furigana=None,  # ← KEY: No furigana for hiragana!
                    grammatical_type=grammatical_type,
                    color_rgb=color
                ))
                
            else:  # other/punctuation
                result_segments.append(FuriganaWord(
                    word=segment_text,
                    furigana=None,
                    grammatical_type=grammatical_type,
                    color_rgb=color
                ))
        
        return result_segments
    
    def _create_simple_fallback(self, japanese_text: str) -> List[FuriganaWord]:
        """Create simple fallback furigana words when analysis fails (unchanged)"""
        words = []
        current_word = ""
        
        for char in japanese_text:
            if char.isspace():
                if current_word:
                    words.append(FuriganaWord(
                        word=current_word,
                        furigana=None,
                        grammatical_type=GrammaticalType.OTHER,
                        color_rgb=(220, 220, 220)  # Light gray
                    ))
                    current_word = ""
                words.append(FuriganaWord(
                    word=" ",
                    furigana=None,
                    grammatical_type=GrammaticalType.OTHER,
                    color_rgb=(220, 220, 220)
                ))
            else:
                current_word += char
        
        if current_word:
            words.append(FuriganaWord(
                word=current_word,
                furigana=None,
                grammatical_type=GrammaticalType.OTHER,
                color_rgb=(220, 220, 220)
            ))
        
        return words
    
    def _contains_japanese(self, text: str) -> bool:
        """Check if text contains Japanese characters"""
        for char in text:
            if (self._is_hiragana(char) or self._is_katakana(char) or self._is_kanji(char)):
                return True
        return False
    
    def _is_mostly_japanese(self, text: str) -> bool:
        """Check if text is mostly Japanese (>70% Japanese characters)"""
        if not text:
            return False
        
        japanese_chars = sum(1 for char in text if 
                           self._is_hiragana(char) or self._is_katakana(char) or self._is_kanji(char))
        total_chars = len([c for c in text if not c.isspace()])
        
        return total_chars > 0 and (japanese_chars / total_chars) > 0.7
    
    def _is_all_hiragana(self, text: str) -> bool:
        return all(self._is_hiragana(c) or c in '、。！？' for c in text)
    
    def _is_hiragana(self, char: str) -> bool:
        return '\u3040' <= char <= '\u309f'
    
    def _is_katakana(self, char: str) -> bool:
        return '\u30a0' <= char <= '\u30ff'
    
    def _is_kanji(self, char: str) -> bool:
        return '\u4e00' <= char <= '\u9faf'
    
    def _create_error_result(self, original_text: str, error_message: str, processing_time: float, source_language: Optional[str] = None) -> LanguageEnhancementResult:
        """Create error result"""
        return LanguageEnhancementResult(
            original_text=original_text,
            source_language=source_language or "unknown",
            source_language_name=self.LANGUAGE_NAMES.get(source_language or "unknown", "Unknown"),
            detected_language="ja",
            language_name="Japanese",
            japanese_text="",
            is_japanese_content=False,
            furigana_words=[],
            tts_language_code="auto",
            processing_time=processing_time,
            error=error_message
        )

    def _translate_and_analyze_japanese(self, text: str) -> Optional[Dict[str, Any]]:
        """Single request: translate/polish to Japanese and analyze furigana."""
        try:
            prompt = f"""
If the text : "{text}" is not Japanese Translate it into Japanese first . 

If it's already jpanese, polish it to correct and native japanese.

Then Analyze this clean Japanese text for furigana: "{text}"

Break into words with:
1. japanese_text: native and exact japanese translation or polish of original japanese
2. word: the word/particle/punctuation of the japanese 
3. furigana: complete reading for the ENTIRE word (ALWAYS provide, even for hiragana)
4. type: grammatical type

CRITICAL: Provide complete, accurate furigana for the entire word.
This text should be clean Japanese suitable for furigana analysis.
"""

            cache_key = f"furigana_combo_{abs(hash(text))}.json"
            result = self.openai_client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.japanese_combined_schema,
                filename=cache_key,
                schema_name="japanese_translate_analyze",
                model=self.openai_model
            )
            return result
        except Exception as e:
            logger.error(f"❌ Japanese combined analyze error: {e}")
            return None


# Utility functions for integration
def enhance_message_with_language(text: str, enhancer: LanguageEnhancer, source_language: Optional[str] = None) -> LanguageEnhancementResult:
    """FIXED: Enhanced async wrapper with language information - ALWAYS PROCESSES"""
    return enhancer.enhance_message(text, source_language)


def format_furigana_for_display(furigana_words: List[FuriganaWord]) -> Dict[str, Any]:
    """Format furigana words for HTML display (unchanged)"""
    formatted_words = []
    
    for word in furigana_words:
        formatted_words.append({
            'word': word.word,
            'furigana': word.furigana,
            'type': word.grammatical_type.value,
            'color': f"rgb({word.color_rgb[0]}, {word.color_rgb[1]}, {word.color_rgb[2]})"
        })
    
    return {
        'words': formatted_words,
        'html': generate_furigana_html(furigana_words)
    }


def generate_furigana_html(furigana_words: List[FuriganaWord]) -> str:
    """Generate HTML for furigana display (unchanged)"""
    html_parts = []
    
    for word in furigana_words:
        color = f"rgb({word.color_rgb[0]}, {word.color_rgb[1]}, {word.color_rgb[2]})"
        
        if word.furigana and word.furigana != word.word:
            # Word with furigana
            html_parts.append(f'''
                <ruby style="color: {color};">
                    {word.word}
                    <rt style="font-size: 0.7em; color: {color};">{word.furigana}</rt>
                </ruby>
            ''')
        else:
            # Word without furigana
            html_parts.append(f'<span style="color: {color};">{word.word}</span>')
    
    return ''.join(html_parts)


if __name__ == "__main__":
    # Test the FIXED enhanced language enhancer
    print("🧪 Testing FIXED Enhanced Language Enhancer - ALWAYS PROCESSES...")
    
    enhancer = LanguageEnhancer()
    
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
            print(f"🇯🇵 Japanese: {result.japanese_text}")
            print(f"🎵 TTS Code: {result.tts_language_code}")
            print(f"✨ Japanese Content: {result.is_japanese_content}")
            print(f"⏱️ Processing time: {result.processing_time:.2f}s")
            
            if result.furigana_words:
                furigana_html = generate_furigana_html(result.furigana_words)
                print(f"✨ Furigana HTML: {furigana_html}")
            else:
                print("📝 No furigana generated")
