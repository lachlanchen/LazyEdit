#!/usr/bin/env python3
"""
Chinese (Mandarin) enhancement plugin (single-pass, script-parameterized).

Behavior:
- Single OpenAI request: translate/polish to Chinese (Simplified or Traditional) + word breakdown
- No explanations per word; returns { word, pinyin, type } items
- Pinyin via model output; local pypinyin is kept as optional fallback when needed

Output:
- processed_text: Chinese text (Simplified or Traditional per selection)
- display_html: <ruby>wrapped</ruby> Chinese with <rt>Pinyin</rt> (when available)
- tts_language_code: "all_zh"
"""
from __future__ import annotations

import html
import time
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Optional OpenCC conversion (Traditional ⇄ Simplified). Falls back to no-op if unavailable.
try:
    from opencc import OpenCC  # type: ignore
    _OPENCC_T2S = OpenCC('t2s')
    _OPENCC_S2T = OpenCC('s2t')
except Exception:
    _OPENCC_T2S = None
    _OPENCC_S2T = None

def _to_simplified_text(text: str) -> str:
    try:
        if _OPENCC_T2S:
            return _OPENCC_T2S.convert(text)
    except Exception:
        pass
    return text

def _to_traditional_text(text: str) -> str:
    try:
        if _OPENCC_S2T:
            return _OPENCC_S2T.convert(text)
    except Exception:
        pass
    return text

from echomind.ai_client_factory import build_with_fallback
from echomind.ai_config import load_ai_model_config
from .base import EnhancementResult, EnhancementPlugin


def _try_pinyin(text: str) -> Optional[List[str]]:
    """Return a list of Pinyin per Han character or segment list if available.

    Tries pypinyin; when missing, returns None.
    """
    try:
        logger.info("[ChineseEnhancer] Trying pypinyin on len=%d", len(text))
        from pypinyin import pinyin, Style  # type: ignore
        # pinyin returns list of lists (per char); flatten to strings
        arr = pinyin(text, style=Style.TONE3, strict=False, errors='default')
        # Convert [['ni3'], ['hao3']] -> ['ni3','hao3'] but keep punctuation as None
        out: List[str] = []
        for item in arr:
            token = (item[0] if item else '')
            out.append(token)
        try:
            logger.info("[ChineseEnhancer] pypinyin returned %s tokens (first 10: %s)",
                        len(out), str(out[:10]))
        except Exception:
            pass
        return out
    except Exception as e:
        logger.error("[ChineseEnhancer] pypinyin import/call failed: %s", e)
        return None


def _segment_with_openai(client: Any, text: str, model: str) -> Optional[List[Dict[str, Any]]]:
    """Legacy segmentation call (kept as fallback)."""
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
                            "pinyin": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "noun","verb","adjective","adverb","particle","pronoun",
                                    "numeral","measure","preposition","conjunction","interjection",
                                    "punctuation","other"
                                ]
                            },
                            # No explanation for speed
                        },
                        "required": ["word","pinyin","type"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["tokens"],
            "additionalProperties": False
        }
        prompt = (
            "Segment the following Mandarin Chinese text into meaningful tokens.\n"
            "For each word, return: word (Chinese), pinyin with tone numbers (TONE3),\n"
            "and a coarse grammar type (noun, verb, adjective, adverb, particle, pronoun,\n"
            "numeral, measure, preposition, conjunction, interjection, punctuation, other).\n\n"
            f"Text: {text}"
        )
        result = client.send_request_with_json_schema(
            prompt=prompt,
            json_schema=schema,
            system_content=(
                "You are a precise Chinese linguistics assistant. Segment accurately and "
                "provide correct Pinyin with tone numbers for each token."
            ),
            filename=f"zh_tokens_{abs(hash(text))}.json",
            schema_name="chinese_tokens",
            model=model,
        )
        tokens = (result or {}).get("tokens")
        if isinstance(tokens, list) and tokens:
            return tokens
        return None
    except Exception as e:
        logger.error("[ChineseEnhancer] OpenAI tokenization failed: %s", e)
        return None


def _is_han(ch: str) -> bool:
    try:
        import regex as re  # type: ignore
        return bool(re.match(r"\p{Script=Han}", ch))
    except Exception:
        code = ord(ch)
        return (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF)


def _type_to_class(tp: str) -> str:
    tp = (tp or '').lower()
    mapping = {
        'noun': 'zhpos-noun',
        'verb': 'zhpos-verb',
        'adjective': 'zhpos-adj',
        'adverb': 'zhpos-adv',
        'pronoun': 'zhpos-pron',
        'preposition': 'zhpos-prep',
        'conjunction': 'zhpos-conj',
        'particle': 'zhpos-part',
        'numeral': 'zhpos-num',
        'measure': 'zhpos-measure',
        'interjection': 'zhpos-interj',
        'punctuation': 'zhpos-punc',
        'other': 'zhpos-other'
    }
    return mapping.get(tp, 'zhpos-other')


def _build_ruby_html_from_tokens(tokens: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for tok in tokens:
        w = str(tok.get('word') or '')
        py = str(tok.get('pinyin') or '')
        tp = str(tok.get('type') or 'other')
        expl = str(tok.get('explanation') or '')
        if not w:
            continue
        if not any(_is_han(ch) for ch in w):
            parts.append(html.escape(w))
            continue
        cls = _type_to_class(tp)
        if py.strip():
            title_attr = f" title=\"{html.escape(expl)}\"" if expl else ""
            parts.append(f"<ruby class=\"{cls}\"{title_attr}>{html.escape(w)}<rt>{html.escape(py)}</rt></ruby>")
        else:
            parts.append(html.escape(w))
    return "".join(parts)


def _build_ruby_html(text: str, py_list: Optional[List[str]], client: Any, model: str) -> str:
    # Prefer OpenAI tokens for POS-based color
    tokens = _segment_with_openai(client, text, model)
    if tokens:
        try:
            html_out = _build_ruby_html_from_tokens(tokens)
            if html_out:
                logger.info("[ChineseEnhancer] Built OpenAI token-based ruby html")
                return html_out
        except Exception as e:
            logger.error("[ChineseEnhancer] OpenAI token ruby build failed: %s", e)
    # Fallback to per-character build
    if not py_list:
        return ""
    parts: List[str] = []
    color_idx = 0
    for idx, ch in enumerate(text):
        ch_esc = html.escape(ch)
        roman = py_list[idx] if idx < len(py_list) else None
        if _is_han(ch) and roman and str(roman).strip():
            cls = f"zhc{color_idx % 6}"
            parts.append(f"<ruby class=\"{cls}\">{ch_esc}<rt>{html.escape(str(roman))}</rt></ruby>")
            color_idx += 1
        else:
            parts.append(ch_esc)
    return "".join(parts)


class ChineseEnhancer:
    key = "chinese"

    def __init__(self, openai_model: str = "gpt-4o-mini", max_retries: int = 3):
        self.client, provider_mode = build_with_fallback(
            use_cache=True,
            cache_dir='cachexxx/chinese_enhancement_cache',
            max_retries=max_retries
        )
        self.provider_mode = provider_mode
        self.model = openai_model if provider_mode != 'deepseek' else None
        # Combined schema: chinese_text + words[{word,pinyin,type}]
        self.combined_schema = {
            "type": "object",
            "properties": {
                "chinese_text": {"type": "string"},
                "words": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "pinyin": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "noun","verb","adjective","adverb","particle","pronoun",
                                    "numeral","measure","preposition","conjunction","interjection",
                                    "punctuation","other"
                                ]
                            }
                        },
                        "required": ["word","pinyin","type"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["chinese_text", "words"],
            "additionalProperties": False
        }

    def enhance(self, text: str, source_language: Optional[str] = None) -> EnhancementResult:
        start = time.time()
        # Requested script from source_language hint: 'zh-Hans' (simplified) / 'zh-Hant' (traditional)
        src = (source_language or 'auto').lower()
        requested_script = 'simplified'
        if 'hant' in src or 'traditional' in src:
            requested_script = 'traditional'

        # Strategy from admin AI config (plugin-only behavior)
        try:
            cfg = load_ai_model_config() or {}
        except Exception:
            cfg = {}
        strategy = str(cfg.get('chinese_enhance_strategy') or 'simplified_main')
        if strategy not in ('simplified_main','traditional_main','independent'):
            strategy = 'simplified_main'

        canonical_script = None
        if strategy == 'simplified_main':
            canonical_script = 'simplified'
        elif strategy == 'traditional_main':
            canonical_script = 'traditional'
        # independent: canonical_script stays None → compute requested as-is

        compute_script = requested_script if not canonical_script else canonical_script
        need_convert = (canonical_script is not None) and (requested_script != canonical_script)

        # 1-step: translate/polish + analyze
        try:
            var = 'Simplified' if compute_script == 'simplified' else 'Traditional'
            prompt = (
                f"If the text: \"{text}\" is not Mandarin Chinese ({var}), translate it into Mandarin Chinese first.\n"
                f"If it's already Chinese, polish it to correct and natural Mandarin ({var}).\n\n"
                "Analyze this Chinese text into words.\n\n"
                "Break into words with:\n"
                "1. chinese_text: native and exact Mandarin Chinese translation or polished original Chinese\n"
                "2. word: the character/word/particle/punctuation as it appears in chinese_text\n"
                "3. pinyin: Hanyu Pinyin with tone numbers (TONE3) for the ENTIRE word (use empty string for non-Han words)\n"
                "4. type: grammatical type from this enum list: \n"
                "   noun, verb, adjective, adverb, particle, pronoun, numeral, measure, preposition, conjunction, interjection, punctuation, other\n\n"
                f"Requirements:\n- Keep chinese_text strictly in {var} Chinese.\n- Segment precisely; keep punctuation as separate words.\n- Provide Pinyin for Han words; leave empty for non-Han words (numbers, Latin text, punctuation).\n- Be consistent and concise.\n"
            )
            result = self.client.send_request_with_json_schema(
                prompt=prompt,
                json_schema=self.combined_schema,
                filename=f"zh_combo_{compute_script}_{abs(hash(text))}.json",
                schema_name="chinese_translate_analyze",
                model=self.model,
            )
            zh_text = (result or {}).get('chinese_text') or ''
            tokens = (result or {}).get('words') or []
            # Build initial HTML from tokens (for the computed script)
            html_out = _build_ruby_html_from_tokens(tokens) if tokens else ''
            if not html_out and not need_convert:
                # Fallback to legacy segmentation/pinyin pipeline for computed script
                py_list = _try_pinyin(zh_text) if zh_text else _try_pinyin(text)
                html_out = _build_ruby_html(zh_text or text, py_list, self.client, self.model)
        except Exception as e:
            # Legacy fallback path: translate-only then segment
            logger.error("[ChineseEnhancer] Combined request failed, fallback: %s", e)
            if compute_script == 'traditional':
                tprompt = (
                    "Translate the following text into natural Mandarin Chinese (Traditional).\n"
                    "Only output the translated Chinese text, no explanations. Do not add Pinyin.\n\n"
                    f"{text}"
                )
                zh_text = self.client.send_simple_request(
                    prompt=tprompt,
                    system_content=(
                        "You are a professional translator. Translate to native Mandarin Chinese, "
                        "concise and natural, in Traditional Chinese characters."
                    ),
                    model=self.model,
                )
            else:
                sprompt = (
                    "Translate the following text into natural Mandarin Chinese (Simplified).\n"
                    "Only output the translated Chinese text, no explanations. Do not add Pinyin.\n\n"
                    f"{text}"
                )
                zh_text = self.client.send_simple_request(
                    prompt=sprompt,
                    system_content=(
                        "You are a professional translator. Translate to native Mandarin Chinese, "
                        "concise and natural, in Simplified Chinese characters."
                    ),
                    model=self.model,
                )
            py_list = _try_pinyin(zh_text)
            html_out = _build_ruby_html(zh_text, py_list, self.client, self.model)

        # If strategy requires conversion, convert processed text and rebuild HTML
        final_text = zh_text
        if need_convert:
            try:
                if requested_script == 'simplified':
                    final_text = _to_simplified_text(zh_text)
                else:
                    final_text = _to_traditional_text(zh_text)
            except Exception:
                final_text = zh_text
            # Rebuild HTML for the converted script using local pinyin/segmentation fallback
            try:
                py_list2 = _try_pinyin(final_text)
            except Exception:
                py_list2 = None
            rebuilt = _build_ruby_html(final_text, py_list2, self.client, self.model)
            if rebuilt:
                html_out = rebuilt

        try:
            logger.info("[ChineseEnhancer] Enhance result: strategy=%s requested=%s computed=%s len=%d has_html=%s",
                        strategy, requested_script, compute_script, len(final_text or ''), bool(html_out and '<rt>' in html_out))
        except Exception:
            pass

        return EnhancementResult(
            original_text=text,
            processed_text=final_text,
            display_html=html_out,
            tts_language_code="all_zh",
            processing_time=time.time() - start,
            meta={
                "source_language": source_language or "auto",
                "strategy": strategy,
                "requested_script": requested_script,
                "computed_script": compute_script,
            },
            error=None,
        )


def get_plugin() -> EnhancementPlugin:
    return ChineseEnhancer()
