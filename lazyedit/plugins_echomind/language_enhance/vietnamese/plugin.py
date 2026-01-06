#!/usr/bin/env python3
"""
Vietnamese language enhancement plugin (independent of legacy enhancements).

Behavior:
- Detect source language.
- If source is Vietnamese (vi): return English translation and analyze the original Vietnamese text.
- If source is not Vietnamese: translate to Vietnamese first, then analyze the Vietnamese version.

Output:
- EnhancementResult.processed_text: the translation (EN if source vi; VI if source != vi)
- EnhancementResult.display_html: HTML block including translation line and token chips
- EnhancementResult.tts_language_code: 'vi'
- EnhancementResult.meta: { tokens, source_language, mode }
"""

from __future__ import annotations

import html
import time
import unicodedata
from typing import Any, Dict, List, Optional
import re

import logging
from echomind.enhancements.base import EnhancementResult, EnhancementPlugin
from echomind.ai_client_factory import build_with_fallback


def _strip_diacritics(s: str) -> str:
    try:
        nfkd = unicodedata.normalize('NFKD', s)
        return ''.join([c for c in nfkd if not unicodedata.combining(c)])
    except Exception:
        return s


def _default_pos_color(pos: str) -> str:
    """Map coarse POS to the app's core palette (aligned with Chinese/Korean).

    Core colors (from static/css/voice_chatbot.css):
      noun #42a5f5, verb #66bb6a, adj #ef5350, adv #ab47bc, num #26c6da,
      measure/classifier #8d6e63, pron #ffa726, prep #9ccc65, conj #26a69a,
      part #5c6bc0, interj #f06292, punct #bdbdbd, other #90a4ae
    """
    mapping = {
        'noun': '#42a5f5',
        'proper_noun': '#42a5f5',
        'verb': '#66bb6a',
        'adjective': '#ef5350',
        'adverb': '#ab47bc',
        'pronoun': '#ffa726',
        'preposition': '#9ccc65',
        'conjunction': '#26a69a',
        'numeral': '#26c6da',
        'classifier': '#8d6e63',
        'measure': '#8d6e63',
        'particle': '#5c6bc0',
        'auxiliary': '#9ccc65',
        'determiner': '#ffa726',
        'interjection': '#f06292',
        'punct': '#bdbdbd',
        'punc': '#bdbdbd',
        'punctuation': '#bdbdbd',
        'other': '#90a4ae',
    }
    return mapping.get(pos, '#90a4ae')


class VietnameseEnhancer:
    key = 'vietnamese'

    def __init__(self, max_retries: int = 2):
        self.logger = logging.getLogger(__name__)
        self.client, self.provider_mode = build_with_fallback(
            use_cache=True,
            cache_dir='cachexxx/vietnamese_enhancement_cache',
            max_retries=max_retries
        )
        # One-pass schema: Vietnamese text + words with core 'type'
        self.schema = {
            "type": "object",
            "properties": {
                "vietnamese_text": {"type": "string"},
                "words": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "noun","verb","adjective","adverb","particle","pronoun",
                                    "numeral","measure","preposition","conjunction","interjection",
                                    "punctuation","other"
                                ]
                            }
                        },
                        "required": ["word","type"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["vietnamese_text","words"],
            "additionalProperties": False
        }

    def _detect_language(self, text: str) -> str:
        # No external detection required for one-pass prompt; keep a light heuristic for meta only
        try:
            if any(ch in text for ch in 'ăâêôơưđĂÂÊÔƠƯĐ'):
                return 'vi'
        except Exception:
            pass
        return 'unknown'

    def _build_prompt(self, text: str) -> str:
        # One-pass: translate/polish to Vietnamese, then analyze into words with core 'type'.
        return (
            f"If the text: \"{text}\" is not Vietnamese, translate it into natural Vietnamese (with correct diacritics) first.\n"
            f"If it's already Vietnamese, polish it to correct and native Vietnamese.\n\n"
            "Analyze this Vietnamese text into words.\n\n"
            "Return JSON with:\n"
            "- vietnamese_text: native and exact Vietnamese translation or polished original Vietnamese\n"
            "- words: array of objects with:\n"
            "  - word: the word/particle/punctuation as it appears in vietnamese_text\n"
            "  - type: grammatical type from this enum: noun, verb, adjective, adverb, particle, pronoun, numeral, measure, preposition, conjunction, interjection, punctuation, other\n\n"
            "Requirements:\n- Segment precisely; keep punctuation as separate words.\n- Use Vietnamese diacritics.\n- Be consistent; no empty items.\n"
        )

    def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        words = [w for w in text.strip().split() if w]
        return {
            'vietnamese_text': text,
            'words': [ {'word': w, 'type': ('punctuation' if w in {'.',',','!','?',';',':'} else 'other')} for w in words ]
        }

    def _render_html(self, data: Dict[str, Any]) -> str:
        """Render minimal, inline, grammar-colored tokens with hover gloss.

        Structure:
        <div class="vietnamese-enhancement">
          <div class="vi-translation">...</div>              # optional
          <div class="vi-inline">                             # inline sentence
            <span class="vi-token pos-verb" data-gloss="..." data-p="..." style="--pos-color:#16a34a">nghĩ</span>
            ...
          </div>
        </div>
        """
        tokens = data.get('tokens') or []

        parts: List[str] = []
        # Omit translation line as requested; only show colorized tokens
        if tokens:
            inline_bits: List[str] = []
            for t in tokens:
                w = html.escape(str(t.get('word') or ''))
                if not w:
                    continue
                pos = sanitize_pos(str(t.get('pos') or 'other'))
                pos = html.escape(pos)
                gloss = ''
                color = str(_default_pos_color(pos))
                attrs = [f'class="vi-token pos-{pos}"', f'style="--pos-color:{color};"']
                # do not attach gloss in minimal variant
                # Do not expose pronunciation on hover; keep only English gloss
                inline_bits.append(f'<span {' '.join(attrs)}>{w}</span>')
            if inline_bits:
                parts.append('<div class="vi-inline">' + ' '.join(inline_bits) + '</div>')

        return '<div class="vietnamese-enhancement">' + ''.join(parts) + '</div>'

    def enhance(self, text: str, source_language: Optional[str] = None) -> EnhancementResult:  # type: ignore[override]
        start = time.time()
        try:
            src = (source_language or '').lower().strip() or self._detect_language(text)
            try:
                self.logger.info(f"[VI] Starting enhancement: src={src} text='{text[:40]}...' ")
            except Exception:
                pass
            prompt = self._build_prompt(text)
            try:
                resp = self.client.send_request_with_json_schema(
                    prompt=prompt,
                    json_schema=self.schema,
                    system_content=("You are a precise Vietnamese linguistic analyzer. Output strict JSON only."),
                    schema_name="vietnamese_enhancement_v2",
                )
            except Exception:
                resp = self._fallback_analysis(text)

            if not isinstance(resp, dict) or 'words' not in resp:
                resp = self._fallback_analysis(text)

            # Normalize words -> tokens compatible with existing UI (pos/color)
            toks = []
            words = resp.get('words') or []
            for t in words:
                w = str(t.get('word') or '')
                tp = sanitize_pos(str(t.get('type') or 'other'))
                color = _default_pos_color(tp)
                toks.append({'word': w, 'pos': tp, 'pronunciation': _strip_diacritics(w), 'color': color, 'gloss': ''})
            data = {
                'vietnamese_text': resp.get('vietnamese_text') or text,
                'tokens': toks
            }
            try:
                self.logger.info(f"[VI] mode={data.get('mode')} tokens={len(toks)} src={src}")
            except Exception:
                pass
            html_out = self._render_html(data)
            return EnhancementResult(
                original_text=text,
                processed_text=data.get('vietnamese_text') or '',
                display_html=html_out,
                tts_language_code='vi',
                processing_time=(time.time() - start),
                meta={'source_language': src, 'tokens': toks},
                error=None
            )
        except Exception as e:
            try:
                self.logger.error(f"[VI] enhancement error: {e}")
            except Exception:
                pass
            return EnhancementResult(
                original_text=text,
                processed_text='',
                display_html=None,
                tts_language_code='vi',
                processing_time=(time.time() - start),
                meta={'source_language': source_language or 'auto'},
                error=str(e)
            )

def sanitize_pos(pos_val: str) -> str:
    try:
        p = (pos_val or 'other').strip().lower()
        # strip trailing punctuation like '.' or ':'
        p = re.sub(r"[^a-z]+$", "", p)
        # normalize common abbreviations
        abbr = {
            'n': 'noun', 'nn': 'noun', 'noun': 'noun',
            'v': 'verb', 'vb': 'verb', 'verb': 'verb',
            'adj': 'adjective', 'jj': 'adjective', 'adjective': 'adjective',
            'adv': 'adverb', 'rb': 'adverb', 'adverb': 'adverb',
            'pron': 'pronoun', 'pronoun': 'pronoun',
            'prep': 'preposition', 'in': 'preposition', 'preposition': 'preposition',
            'part': 'particle', 'rp': 'particle', 'particle': 'particle',
            'punct': 'punct', 'punc': 'punct', 'punctuation': 'punct',
            'num': 'numeral', 'numeral': 'numeral',
            'meas': 'measure', 'measure': 'measure', 'classifier': 'classifier',
            'aux': 'auxiliary', 'auxiliary': 'auxiliary',
            'det': 'determiner', 'determiner': 'determiner',
            'conj': 'conjunction', 'conjunction': 'conjunction',
        }
        return abbr.get(p, p or 'other')
    except Exception:
        return 'other'


def get_plugin():
    return VietnameseEnhancer()
