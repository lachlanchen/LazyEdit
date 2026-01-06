#!/usr/bin/env python3
"""
Cantonese enhancement plugin.

Phase 1:
- Translate to native HK Cantonese (Traditional Chinese) using OpenAI.
- Generate Jyutping ruby locally in Python (no AI for Jyutping).

Notes:
- If optional libraries are missing, falls back gracefully (no Jyutping).
"""

from __future__ import annotations

import html
import time
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

from echomind.ai_client_factory import build_with_fallback
from .base import EnhancementResult, EnhancementPlugin


def _try_jyutping(text: str) -> Optional[List[str]]:
    """Return a list of Jyutping per Han character or None if unavailable.

    Tries pycantonese.characters_to_jyutping first; otherwise, returns None.
    """
    try:
        logger.info("[CantoneseEnhancer] Trying pycantonese.characters_to_jyutping on len=%d", len(text))
        from pycantonese import characters_to_jyutping  # type: ignore
        # characters_to_jyutping returns a list aligned by characters
        lst = characters_to_jyutping(text)
        try:
            logger.info("[CantoneseEnhancer] pycantonese returned %s tokens (first 10: %s)",
                        (len(lst) if lst is not None else 'None'), str(lst[:10]) if lst else 'None')
        except Exception:
            pass
        return lst
    except Exception as e:
        logger.error("[CantoneseEnhancer] pycantonese import/call failed: %s", e)
        return None


from typing import Sequence, Tuple

def _build_ruby_html(text: str, jyut_list: Optional[Sequence]) -> str:
    """Build ruby HTML mapping Jyutping to Han characters only.

    - Be lenient about punctuation/whitespace: only consume a Jyutping token when we see a Han char.
    - If no Jyutping available, return empty string (caller can render plain text separately).
    """
    if not jyut_list:
        logger.info("[CantoneseEnhancer] No Jyutping available; returning empty ruby html")
        return ""

    # If pycantonese returned a list of (segment, jyut) pairs, use segment-level ruby
    try:
        if isinstance(jyut_list, (list, tuple)) and jyut_list and isinstance(jyut_list[0], (list, tuple)) and len(jyut_list[0]) >= 1:
            parts: List[str] = []
            used = 0
            for item in jyut_list:  # type: ignore
                try:
                    seg = str(item[0])
                    roman = item[1] if len(item) > 1 else None
                except Exception:
                    seg = str(item)
                    roman = None
                seg_esc = html.escape(seg)
                if roman:
                    parts.append(f"<ruby>{seg_esc}<rt>{html.escape(str(roman))}</rt></ruby>")
                    used += 1
                else:
                    parts.append(seg_esc)
            html_out = "".join(parts)
            try:
                rt_count = html_out.count("<rt>")
                html_out  # keep
                logger.info("[CantoneseEnhancer] Built segment ruby: rts=%d used=%d items=%d", rt_count, used, len(jyut_list))
            except Exception:
                pass
            return html_out
    except Exception:
        pass

    # Otherwise assume list of strings aligned to Han characters and map leniently
    parts = []
    j = 0
    for ch in text:
        ch_esc = html.escape(ch)
        if _is_han(ch) and j < len(jyut_list):
            roman = jyut_list[j]
            parts.append(f"<ruby>{ch_esc}<rt>{html.escape(str(roman or ''))}</rt></ruby>")
            j += 1
        else:
            parts.append(ch_esc)
    html_out = "".join(parts)
    try:
        rt_count = html_out.count("<rt>")
        logger.info("[CantoneseEnhancer] Built ruby html with %d <rt> tags (used %d/%d jyut tokens)", rt_count, j, len(jyut_list))
    except Exception:
        pass
    return html_out


def _is_han(ch: str) -> bool:
    try:
        import regex as re  # type: ignore
        return bool(re.match(r"\p{Script=Han}", ch))
    except Exception:
        # Basic fallback: approximate range for CJK Unified Ideographs
        code = ord(ch)
        return (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF)


class CantoneseEnhancer:
    key = "cantonese"

    def __init__(self, openai_model: str = "gpt-4o-mini", max_retries: int = 3):
        self.client, provider_mode = build_with_fallback(
            use_cache=True,
            cache_dir='cachexxx/cantonese_enhancement_cache',
            max_retries=max_retries
        )
        self.provider_mode = provider_mode
        self.model = openai_model if provider_mode != 'deepseek' else None

    def enhance(self, text: str, source_language: Optional[str] = None) -> EnhancementResult:
        start = time.time()
        # 1) Translate to native HK Cantonese (Traditional Chinese)
        prompt = f"""
Translate the following text into native Hong Kong Cantonese (colloquial style), written in Traditional Chinese characters.
Only output the translated text, no explanations:

"""
        prompt += text

        cantonese_text = self.client.send_simple_request(
            prompt=prompt,
            system_content=(
                "You are a professional translator. Translate to native HK Cantonese, "
                "colloquial style, Traditional Chinese, concise and natural."
            ),
            model=self.model,
        )

        # 2) Generate Jyutping locally
        jyut_list = _try_jyutping(cantonese_text)
        ruby_html = _build_ruby_html(cantonese_text, jyut_list)
        try:
            logger.info("[CantoneseEnhancer] Enhance result: processed_len=%d, jyut_len=%s, has_ruby=%s",
                        len(cantonese_text), (len(jyut_list) if jyut_list else 0), bool(ruby_html and '<rt>' in ruby_html))
        except Exception:
            pass

        return EnhancementResult(
            original_text=text,
            processed_text=cantonese_text,
            display_html=ruby_html,
            tts_language_code="all_yue",
            processing_time=time.time() - start,
            meta={
                "source_language": source_language or "auto",
                "jyutping": jyut_list,
            },
            error=None,
        )


# Convenience: factory function
def get_plugin() -> EnhancementPlugin:
    return CantoneseEnhancer()
