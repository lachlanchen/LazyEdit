#!/usr/bin/env python3
"""
Spanish language enhancement plugin (independent of legacy enhancements).

Behavior:
- One-pass: translate/polish to Spanish, then analyze into coarse grammar tokens.
- No English gloss; render colorized POS tokens consistent with other languages.

Output:
- EnhancementResult.processed_text: Spanish text (normalized/translated/polished)
- EnhancementResult.display_html: inline colored tokens
- EnhancementResult.tts_language_code: 'es'
- EnhancementResult.meta: { tokens, source_language }
"""

from __future__ import annotations

import html
import time
from typing import Any, Dict, List, Optional
import logging
import re

from echomind.enhancements.base import EnhancementResult
from echomind.ai_client_factory import build_with_fallback


def _pos_color(pos: str) -> str:
    mapping = {
        'noun': '#42a5f5', 'proper_noun': '#42a5f5',
        'verb': '#66bb6a',
        'adjective': '#ef5350',
        'adverb': '#ab47bc',
        'pronoun': '#ffa726',
        'preposition': '#9ccc65',
        'conjunction': '#26a69a',
        'numeral': '#26c6da',
        'classifier': '#8d6e63', 'measure': '#8d6e63',
        'particle': '#5c6bc0', 'auxiliary': '#9ccc65', 'determiner': '#ffa726',
        'interjection': '#f06292',
        'punct': '#bdbdbd', 'punc': '#bdbdbd', 'punctuation': '#bdbdbd',
        'other': '#90a4ae',
    }
    return mapping.get(pos, '#90a4ae')


def _norm_pos(p: str) -> str:
    try:
        p = (p or 'other').strip().lower()
        p = re.sub(r"[^a-z]+$", "", p)
        ab = {
            'n': 'noun', 'nn': 'noun', 'noun': 'noun',
            'v': 'verb', 'vb': 'verb', 'verb': 'verb',
            'adj': 'adjective', 'jj': 'adjective', 'adjective': 'adjective',
            'adv': 'adverb', 'rb': 'adverb', 'adverb': 'adverb',
            'pron': 'pronoun', 'pronoun': 'pronoun',
            'prep': 'preposition', 'in': 'preposition', 'preposition': 'preposition',
            'conj': 'conjunction', 'conjunction': 'conjunction',
            'part': 'particle', 'rp': 'particle', 'particle': 'particle',
            'punct': 'punct', 'punc': 'punct', 'punctuation': 'punct',
            'num': 'numeral', 'numeral': 'numeral',
            'meas': 'measure', 'measure': 'measure', 'classifier': 'classifier',
            'aux': 'auxiliary', 'auxiliary': 'auxiliary',
            'det': 'determiner', 'determiner': 'determiner',
        }
        return ab.get(p, p or 'other')
    except Exception:
        return 'other'


class SpanishEnhancer:
    key = 'spanish'

    def __init__(self, max_retries: int = 2):
        self.logger = logging.getLogger(__name__)
        self.client, self.provider_mode = build_with_fallback(
            use_cache=True,
            cache_dir='cachexxx/spanish_enhancement_cache',
            max_retries=max_retries
        )
        self.schema = {
            "type": "object",
            "properties": {
                "spanish_text": {"type": "string"},
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
                            }
                        },
                        "required": ["word","type"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["spanish_text","words"],
            "additionalProperties": False
        }

    def _detect_language(self, text: str) -> str:
        try:
            # rough heuristic for Spanish diacritics/punctuation
            if any(ch in text for ch in "áéíóúñÁÉÍÓÚÑ¡¿"):
                return 'es'
        except Exception:
            pass
        return 'unknown'

    def _build_prompt(self, text: str) -> str:
        return (
            f"If the text: \"{text}\" is not Spanish, translate it into natural Spanish first.\n"
            f"If it's already Spanish, polish it to correct and native Spanish.\n\n"
            "Analyze this Spanish text into words.\n\n"
            "Return JSON with:\n"
            "- spanish_text: native and exact Spanish translation or polished original Spanish\n"
            "- words: array of objects with:\n"
            "  - word: the word/particle/punctuation as it appears in spanish_text\n"
            "  - type: grammatical type from this enum: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, measure, classifier, particle, auxiliary, determiner, interjection, punctuation, other\n\n"
            "Requirements:\n- Keep spanish_text strictly in Spanish (Latin script with proper diacritics).\n- Segment precisely; keep punctuation as separate words.\n- No explanations or gloss. Output strict JSON only with the exact keys above.\n"
        )

    def _fallback(self, text: str) -> Dict[str, Any]:
        words = [w for w in str(text or '').split() if w]
        return { 'spanish_text': text, 'words': [ {'word': w, 'type': 'other'} for w in words ] }

    def _render_html(self, data: Dict[str, Any]) -> str:
        tokens = data.get('tokens') or []
        parts: List[str] = []
        inline: List[str] = []
        for t in tokens:
            w = html.escape(str(t.get('word') or ''))
            if not w:
                continue
            pos = _norm_pos(str(t.get('pos') or 'other'))
            color = _pos_color(pos)
            attrs = [f'class="es-token pos-{pos}"', f'style="--pos-color:{color};"']
            inline.append(f'<span {' '.join(attrs)}>{w}</span>')
        if inline:
            parts.append('<div class="es-inline">' + ' '.join(inline) + '</div>')
        return '<div class="spanish-enhancement">' + ''.join(parts) + '</div>'

    def enhance(self, text: str, source_language: Optional[str] = None) -> EnhancementResult:
        start = time.time()
        try:
            src = (source_language or '').lower().strip() or self._detect_language(text)
            prompt = self._build_prompt(text)
            try:
                resp = self.client.send_request_with_json_schema(
                    prompt=prompt,
                    json_schema=self.schema,
                    system_content="You are a precise Spanish linguistic analyzer. Output strict JSON only.",
                    schema_name="spanish_enhancement_v1",
                )
            except Exception:
                resp = self._fallback(text)

            if not isinstance(resp, dict) or 'words' not in resp:
                resp = self._fallback(text)

            toks: List[Dict[str, Any]] = []
            for wobj in (resp.get('words') or []):
                w = str(wobj.get('word') or '')
                tp = _norm_pos(str(wobj.get('type') or 'other'))
                color = _pos_color(tp)
                toks.append({'word': w, 'pos': tp, 'color': color})

            data = {
                'spanish_text': resp.get('spanish_text') or text,
                'tokens': toks,
            }
            html_out = self._render_html(data)
            return EnhancementResult(
                original_text=text,
                processed_text=data.get('spanish_text') or '',
                display_html=html_out,
                tts_language_code='es',
                processing_time=(time.time() - start),
                meta={'source_language': src, 'tokens': toks},
                error=None
            )
        except Exception as e:
            try:
                logging.getLogger(__name__).error(f"[ES] enhancement error: {e}")
            except Exception:
                pass
            return EnhancementResult(
                original_text=text,
                processed_text='',
                display_html=None,
                tts_language_code='es',
                processing_time=(time.time() - start),
                meta={'source_language': source_language or 'auto'},
                error=str(e)
            )


def get_plugin():
    return SpanishEnhancer()

