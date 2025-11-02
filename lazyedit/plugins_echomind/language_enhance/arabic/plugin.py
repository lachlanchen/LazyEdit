#!/usr/bin/env python3
"""
Arabic language enhancement plugin (independent of legacy enhancements).

Behavior:
- One-pass: translate/polish to Arabic, then analyze words with core 'type'.
- No English gloss; pronunciation optional (Arabic→Latin) for Arabic words.

Output:
- EnhancementResult.processed_text: Arabic text (possibly normalized from input)
- EnhancementResult.display_html: inline colored tokens with English-only hover gloss
- EnhancementResult.tts_language_code: 'ar' (placeholder; TTS optional)
- EnhancementResult.meta: { tokens, source_language }
"""

from __future__ import annotations

import html
import time
from typing import Any, Dict, List, Optional
import logging

from echomind.enhancements.base import EnhancementResult
from echomind.ai_client_factory import build_with_fallback


def _core_pos_color(pos: str) -> str:
    m = {
        'noun': '#42a5f5', 'proper_noun': '#42a5f5', 'verb': '#66bb6a', 'adjective': '#ef5350',
        'adverb': '#ab47bc', 'pronoun': '#ffa726', 'preposition': '#9ccc65', 'conjunction': '#26a69a',
        'numeral': '#26c6da', 'classifier': '#8d6e63', 'measure': '#8d6e63', 'particle': '#5c6bc0',
        'auxiliary': '#9ccc65', 'determiner': '#ffa726', 'interjection': '#f06292', 'punct': '#bdbdbd', 'other': '#90a4ae'
    }
    return m.get(pos, '#90a4ae')


def _norm_pos(p: str) -> str:
    try:
        p = (p or 'other').strip().lower()
        while p and not p[-1].isalpha():
            p = p[:-1]
        ab = {
            'n': 'noun', 'nn': 'noun', 'noun': 'noun',
            'v': 'verb', 'vb': 'verb', 'verb': 'verb',
            'adj': 'adjective', 'jj': 'adjective', 'adjective': 'adjective',
            'adv': 'adverb', 'rb': 'adverb', 'adverb': 'adverb',
            'pron': 'pronoun', 'pronoun': 'pronoun',
            'prep': 'preposition', 'in': 'preposition', 'preposition': 'preposition',
            'conj': 'conjunction', 'conjunction': 'conjunction',
            'part': 'particle', 'rp': 'particle', 'particle': 'particle',
            'num': 'numeral', 'numeral': 'numeral',
            'meas': 'measure', 'measure': 'measure', 'classifier': 'classifier',
            'aux': 'auxiliary', 'auxiliary': 'auxiliary',
            'det': 'determiner', 'determiner': 'determiner',
            'punct': 'punct', 'punc': 'punct', 'punctuation': 'punct',
        }
        return ab.get(p, p or 'other')
    except Exception:
        return 'other'


class ArabicEnhancer:
    key = 'arabic'

    def __init__(self, max_retries: int = 2):
        self.logger = logging.getLogger(__name__)
        self.client, self.provider_mode = build_with_fallback(
            use_cache=True,
            cache_dir='cachexxx/arabic_enhancement_cache',
            max_retries=max_retries
        )
        self.schema = {
            "type": "object",
            "properties": {
                "arabic_text": {"type": "string"},
                "words": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "noun","proper_noun","verb","adjective","adverb","pronoun",
                                    "preposition","conjunction","numeral","measure","classifier",
                                    "particle","auxiliary","determiner","interjection","punctuation","other"
                                ]
                            },
                            "pronunciation": {"type": "string"}
                        },
                        "required": ["word","type"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["arabic_text","words"],
            "additionalProperties": False
        }

    def _detect_language(self, text: str) -> str:
        # Lightweight meta-only detector (do not block or error)
        try:
            if any('\u0600' <= ch <= '\u06FF' for ch in text):
                return 'ar'
        except Exception:
            pass
        return 'unknown'

    def _build_prompt(self, text: str) -> str:
        return (
            f"If the text: \"{text}\" is not Arabic, translate it into natural Arabic (Arabic script) first.\n"
            f"If it's already Arabic, polish it to correct and native Arabic (Arabic script).\n\n"
            "Analyze this Arabic text into words.\n\n"
            "Return JSON with:\n"
            "- arabic_text: native and exact Arabic translation or polished original Arabic (Arabic script only)\n"
            "- words: array of objects:\n"
            "  - word: the word/particle/punctuation as it appears in arabic_text (Arabic script for Arabic words)\n"
            "  - type: grammatical type from this enum: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, measure, classifier, particle, auxiliary, determiner, interjection, punctuation, other\n"
            "  - pronunciation: Arabic-to-Latin romanization for the ENTIRE word (empty string for non-Arabic words)\n\n"
            "Requirements:\n- Keep arabic_text strictly in Arabic script.\n- Segment precisely; keep punctuation as separate words.\n- Provide pronunciation for Arabic words; leave empty for non-Arabic tokens.\n- Be consistent; no empty items.\n- Output strict JSON only.\n"
        )

    def _fallback(self, text: str) -> Dict[str, Any]:
        words = [w for w in str(text or '').split() if w]
        return { 'arabic_text': text, 'words': [ {'word': w, 'type': 'other', 'pronunciation': ''} for w in words ] }

    def _render_html(self, data: Dict[str, Any]) -> str:
        tokens = data.get('tokens') or []
        parts: List[str] = []
        inline: List[str] = []
        for t in tokens:
            w = html.escape(str(t.get('word') or ''))
            if not w:
                continue
            pos = _norm_pos(str(t.get('pos') or 'other'))
            pron = html.escape(str(t.get('pronunciation') or ''))
            color = _core_pos_color(pos)
            # Wrap ruby inside a generic token span to reuse tooltip (English-only) and color
            attrs = [f'class="lang-token pos-{pos}"', f'style="--pos-color:{color};"']
            if pron:
                ruby = f'<ruby class="arpos-{pos}">{w}<rt>{pron}</rt></ruby>'
            else:
                ruby = w
            inline.append(f'<span {' '.join(attrs)}>{ruby}</span>')
        if inline:
            parts.append('<div class="ar-inline">' + ' '.join(inline) + '</div>')
        return '<div class="arabic-enhancement">' + ''.join(parts) + '</div>'

    def enhance(self, text: str, source_language: Optional[str] = None) -> EnhancementResult:
        start = time.time()
        try:
            src = (source_language or '').lower().strip() or self._detect_language(text)
            prompt = self._build_prompt(text)
            try:
                resp = self.client.send_request_with_json_schema(
                    prompt=prompt,
                    json_schema=self.schema,
                    system_content="You are a precise Arabic linguistic analyzer. Output strict JSON only.",
                    schema_name="arabic_tokens_v3",
                )
            except Exception:
                resp = self._fallback(text)
            if not isinstance(resp, dict) or 'words' not in resp:
                resp = self._fallback(text)

            # Normalize: words -> tokens with compatibility fields
            toks: List[Dict[str, Any]] = []
            for wobj in (resp.get('words') or []):
                w = str(wobj.get('word') or '')
                tp = _norm_pos(str(wobj.get('type') or 'other'))
                pron = str(wobj.get('pronunciation') or '')
                color = _core_pos_color(tp)
                toks.append({'word': w, 'pos': tp, 'pronunciation': pron, 'color': color})
            data = {
                'arabic_text': resp.get('arabic_text') or text,
                'tokens': toks,
            }
            # Ensure processed text is Arabic; if not, rebuild from Arabic token words
            processed = data.get('arabic_text') or text
            try:
                def has_ar(s: str) -> bool:
                    return any('\u0600' <= ch <= '\u06FF' for ch in s)
                if not has_ar(processed):
                    ar_words = [t['word'] for t in toks if has_ar(str(t.get('word','')))]
                    if ar_words:
                        processed = ' '.join(ar_words)
            except Exception:
                pass
            html_out = self._render_html(data)
            return EnhancementResult(
                original_text=text,
                processed_text=processed,
                display_html=html_out,
                tts_language_code='ar',
                processing_time=(time.time() - start),
                meta={'source_language': src, 'tokens': toks},
                error=None
            )
        except Exception as e:
            try:
                logging.getLogger(__name__).error(f"[AR] enhancement error: {e}")
            except Exception:
                pass
            return EnhancementResult(
                original_text=text,
                processed_text=text,
                display_html=None,
                tts_language_code='ar',
                processing_time=(time.time() - start),
                meta={'source_language': source_language or 'auto'},
                error=str(e)
            )


def get_plugin():
    return ArabicEnhancer()
