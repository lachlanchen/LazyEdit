#!/usr/bin/env python3
"""
Korean (Hangul) enhancement plugin (single-pass, no explanations).

Design
- Single OpenAI request: translate/polish to Korean + break into words with romanization and coarse POS.
- No per-word explanations for speed.
- Render words as <ruby> blocks with <rt>romanization</rt> and POS color classes.

Output
- processed_text: Korean text
- display_html: <ruby>wrapped</ruby> words with <rt>romanization</rt>
- tts_language_code: "all_ko"
"""
from __future__ import annotations

import html
import time
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

from echomind.ai_client_factory import build_with_fallback
from .base import EnhancementResult, EnhancementPlugin


def _try_korean_romanization(text: str) -> Optional[List[str]]:
    """Best-effort romanization using optional local libs; returns token list aligned with characters/segments.

    Libraries attempted (optional):
    - hangul_romanize (romanize)
    - korean_romanizer.Romanizer
    - g2pk for phonemic conversion (not romanization) – skipped for display

    Returns None if no suitable library is available.
    """
    # Try hangul_romanize
    try:
        from hangul_romanize import Romanizer  # type: ignore
        r = Romanizer(text)
        s = str(r.romanize())
        if s and s.strip():
            # Naive split by whitespace to approximate per-word romanization
            # The HTML builder will prefer OpenAI tokenization when available anyway
            return s.split()
    except Exception:
        pass
    # Try korean_romanizer
    try:
        from korean_romanizer.romanizer import Romanizer as KR  # type: ignore
        s = str(KR(text).romanize())
        if s and s.strip():
            return s.split()
    except Exception:
        pass
    # None available
    return None


def _segment_with_openai(client: Any, text: str, model: str) -> Optional[List[Dict[str, Any]]]:
    """Ask OpenAI for words with romanization and POS (legacy fallback)."""
    try:
        schema = {
            "type": "object",
            "properties": {
                "tokens": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "roman": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "noun","verb","adjective","adverb","particle","pronoun",
                                    "numeral","measure","preposition","conjunction","interjection",
                                    "punctuation","other"
                                ]
                            }
                        },
                        "required": ["word","roman","type"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["tokens"],
            "additionalProperties": False
        }
        prompt = (
            "Segment the Korean text into words. For each word, return: word (Hangul), "
            "romanization (Revised Romanization), and a coarse grammar type (noun, verb, adjective, adverb, "
            "particle, pronoun, numeral, measure, preposition, conjunction, interjection, punctuation, other).\n\n"
            f"Text: {text}"
        )
        result = client.send_request_with_json_schema(
            prompt=prompt,
            json_schema=schema,
            system_content=(
                "You are a precise Korean linguistics assistant. Use natural token boundaries and provide "
                "accurate Revised Romanization for each token."
            ),
            filename=f"ko_tokens_{abs(hash(text))}.json",
            schema_name="korean_tokens",
            model=model,
        )
        tokens = (result or {}).get("tokens")
        if isinstance(tokens, list) and tokens:
            return tokens
        return None
    except Exception as e:
        logger.error("[KoreanEnhancer] OpenAI tokenization failed: %s", e)
        return None


def _type_to_class(tp: str) -> str:
    tp = (tp or '').lower()
    mapping = {
        'noun': 'kopos-noun',
        'verb': 'kopos-verb',
        'adjective': 'kopos-adj',
        'adverb': 'kopos-adv',
        'pronoun': 'kopos-pron',
        'preposition': 'kopos-prep',
        'conjunction': 'kopos-conj',
        'particle': 'kopos-part',
        'numeral': 'kopos-num',
        'measure': 'kopos-measure',
        'interjection': 'kopos-interj',
        'punctuation': 'kopos-punc',
        'other': 'kopos-other'
    }
    return mapping.get(tp, 'kopos-other')


def _build_ruby_html_from_tokens(tokens: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for tok in tokens:
        w = str(tok.get('word') or '')
        rr = str(tok.get('roman') or '')
        tp = str(tok.get('type') or 'other')
        expl = ''  # no per-word explanations in single-pass mode
        if not w:
            continue
        cls = _type_to_class(tp)
        title_attr = f" title=\"{html.escape(expl)}\"" if expl else ""
        if rr.strip():
            parts.append(f"<ruby class=\"{cls}\"{title_attr}>{html.escape(w)}<rt>{html.escape(rr)}</rt></ruby>")
        else:
            parts.append(html.escape(w))
    return "".join(parts)


class KoreanEnhancer:
    key = "korean"

    def __init__(self, openai_model: str = "gpt-4o-mini", max_retries: int = 3):
        self.client, provider_mode = build_with_fallback(
            use_cache=True,
            cache_dir='cachexxx/korean_enhancement_cache',
            max_retries=max_retries
        )
        self.provider_mode = provider_mode
        self.model = openai_model if provider_mode != 'deepseek' else None
        # Combined schema: korean_text + words[{word,roman,type}]
        self.combined_schema = {
            "type": "object",
            "properties": {
                "korean_text": {"type": "string"},
                "words": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "roman": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "noun","verb","adjective","adverb","particle","pronoun",
                                    "numeral","measure","preposition","conjunction","interjection",
                                    "punctuation","other"
                                ]
                            }
                        },
                        "required": ["word","roman","type"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["korean_text","words"],
            "additionalProperties": False
        }

    def enhance(self, text: str, source_language: Optional[str] = None) -> EnhancementResult:
        start = time.time()
        # Single-pass: translate/polish + analyze
        try:
            prompt = (
                f"If the text: \"{text}\" is not Korean, translate it into natural Korean (Hangul) first.\n"
                f"If it's already Korean, polish it to correct and native Korean.\n\n"
                "Analyze this Korean text into words.\n\n"
                "Break into words with:\n"
                "1. korean_text: native and exact Korean translation or polished original Korean\n"
                "2. word: the character/word/particle/punctuation as it appears in korean_text\n"
                "3. roman: Revised Romanization for the ENTIRE Korean word\n"
                "4. type: grammatical type from this enum list:\n"
                "   noun, verb, adjective, adverb, particle, pronoun, numeral, measure, preposition, conjunction, interjection, punctuation, other\n\n"
                "Requirements:\n- Keep korean_text strictly in Hangul.\n- Segment precisely; keep punctuation as separate words.\n- Provide romanization for Hangul words; leave empty for non-Hangul.\n- Be consistent and concise.\n"
            )
            result = self.client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.combined_schema,
                filename=f"ko_combo_{abs(hash(text))}.json",
                schema_name="korean_translate_analyze",
                model=self.model,
            )
            ko_text = (result or {}).get('korean_text') or ''
            tokens = (result or {}).get('words') or []
            ruby_html = ''
            if tokens:
                try:
                    ruby_html = _build_ruby_html_from_tokens(tokens)
                except Exception as e:
                    logger.error("[KoreanEnhancer] token-based ruby build failed: %s", e)
        except Exception as e:
            # Fallback to legacy translate + segmentation
            logger.error("[KoreanEnhancer] Combined request failed, fallback: %s", e)
            src = (source_language or 'auto').lower()
            def _is_src_korean(s: str) -> bool:
                return s.startswith('ko') or ('all_ko' in s) or (s == 'korean')
            if _is_src_korean(src):
                ko_text = text
            else:
                tprompt = (
                    "Translate the following text into natural Korean (Hangul). "
                    "Only output the translated Korean text, no explanations.\n\n"
                    f"{text}"
                )
                ko_text = self.client.send_simple_request(
                    prompt=tprompt,
                    system_content=(
                        "You are a professional translator. Translate to native Korean, concise and natural."
                    ),
                    model=self.model,
                )
            _ = _try_korean_romanization(ko_text)
            tokens = _segment_with_openai(self.client, ko_text, self.model)
            ruby_html = ''
            if tokens:
                try:
                    ruby_html = _build_ruby_html_from_tokens(tokens)
                except Exception as e2:
                    logger.error("[KoreanEnhancer] token-based ruby build failed (fallback): %s", e2)

        return EnhancementResult(
            original_text=text,
            processed_text=ko_text,
            display_html=ruby_html or None,
            tts_language_code="all_ko",
            processing_time=time.time() - start,
            meta={ "source_language": source_language or "auto", "tokens": tokens or None },
            error=None,
        )


def get_plugin() -> EnhancementPlugin:
    return KoreanEnhancer()
