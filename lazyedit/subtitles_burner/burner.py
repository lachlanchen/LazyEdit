from __future__ import annotations

import sys
import re
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

import cv2

from lazyedit.subtitle_tokens import (
    has_content_token,
    is_speaker_only_tokens,
    normalize_tokens_payload,
)


SPEAKER_ICON_COLOR = (33, 150, 243)


@dataclass
class BurnSlotConfig:
    slot_id: int
    language: str
    json_path: str
    text_key: str
    ruby_key: Optional[str] = None
    tokens_key: str = "tokens"
    pairs_key: str = "furigana_pairs"
    palette: Optional[dict[str, Any]] = None
    auto_ruby: bool = False
    strip_kana: bool = False
    font_scale: float = 1.0
    font_bold: bool = True
    font_color: str | tuple[int, int, int] = "#FFFFFF"
    outline_bold: bool = True
    outline_color: str | tuple[int, int, int] = "#000000"
    kana_romaji: bool = False
    pinyin: bool = False
    ipa: bool = False
    jyutping: bool = False
    korean_romaja: bool = False
    arabic_translit: bool = False


def _slot_padding_for_height(slot_height: int, stroke_width: int) -> int:
    base = int(round(max(1, slot_height) * 0.10))
    base = max(2, min(base, 16))
    return max(base, int(stroke_width) * 2)


def _color_to_rgb(value: str | tuple[int, int, int] | None, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    if isinstance(value, tuple) and len(value) == 3:
        try:
            return tuple(max(0, min(255, int(channel))) for channel in value)  # type: ignore[return-value]
        except Exception:
            return fallback
    color = str(value or "").strip()
    if not color.startswith("#") or len(color) not in {4, 7}:
        return fallback
    if len(color) == 4:
        color = "#" + "".join(char * 2 for char in color[1:])
    try:
        return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
    except Exception:
        return fallback


def _load_burner_module():
    furigana_root = Path(__file__).resolve().parents[2] / "furigana"
    if not furigana_root.exists():
        raise RuntimeError("furigana submodule not found")
    furigana_path = str(furigana_root)
    if furigana_path not in sys.path:
        sys.path.insert(0, furigana_path)

    try:
        import subtitles_burner.burner as burner_mod
        from subtitles_burner.burner import (
            BurnLayout,
            RubyRenderer,
            RubyToken,
            Slot,
            SlotAssignment,
            TextStyle,
            build_bottom_slot_layout,
            burn_subtitles_with_layout,
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to import subtitles_burner: {exc}") from exc

    # LazyEdit patch: normalize subtitle token payloads before delegating to
    # upstream. This keeps recovered/polished plain text, schema-drifted tokens,
    # ruby markup, and speaker-icon rows on the same grammar-colored path.
    try:
        if getattr(burner_mod, "_lazyedit_token_normalization_patch", False) is not True and hasattr(burner_mod, "load_segments_from_json"):
            original_load_segments_from_json = burner_mod.load_segments_from_json

            def _base_text_from_item(item: dict[str, Any], text_key: str | None) -> str:
                value = item.get(text_key) if text_key else None
                if value is None:
                    value = item.get("text")
                return "" if value is None else str(value)

            def _ruby_tokens_to_dicts(tokens: list[Any]) -> list[dict[str, Any]]:
                out: list[dict[str, Any]] = []
                for token in tokens:
                    text = getattr(token, "text", "") or ""
                    ruby = getattr(token, "ruby", None)
                    token_type = getattr(token, "token_type", None)
                    if not text and token_type != "speaker":
                        continue
                    row: dict[str, Any] = {"text": text}
                    if ruby:
                        row["ruby"] = ruby
                    if token_type:
                        row["type"] = token_type
                    out.append(row)
                return out

            def _fallback_content_tokens(
                item: dict[str, Any],
                text_key: str | None,
                ruby_key: str | None,
                pairs_key: str,
                auto_ruby: bool,
                palette: Optional[dict[str, Any]],
            ) -> list[dict[str, Any]]:
                base_text = _base_text_from_item(item, text_key)
                if pairs_key and item.get(pairs_key):
                    tokens = _ruby_tokens_to_dicts(burner_mod._tokens_from_pairs(item.get(pairs_key)))
                    return normalize_tokens_payload(tokens, text=base_text, text_key=text_key, palette=palette)
                if ruby_key and item.get(ruby_key):
                    tokens = _ruby_tokens_to_dicts(burner_mod._tokens_from_ruby_markup(str(item.get(ruby_key))))
                    return normalize_tokens_payload(tokens, text=base_text, text_key=text_key, palette=palette)
                if auto_ruby and base_text:
                    try:
                        tokens = _ruby_tokens_to_dicts(burner_mod.FuriganaGenerator().generate(base_text))
                        return normalize_tokens_payload(tokens, text=base_text, text_key=text_key, palette=palette)
                    except Exception:
                        pass
                return normalize_tokens_payload([{"text": base_text}], text=base_text, text_key=text_key, palette=palette) if base_text else []

            def load_segments_from_json_lazyedit(
                json_path: str,
                text_key: Optional[str] = None,
                ruby_key: Optional[str] = None,
                tokens_key: str = "tokens",
                pairs_key: str = "furigana_pairs",
                palette: Optional[dict[str, Any]] = None,
                auto_ruby: bool = False,
                strip_kana: bool = False,
                kana_romaji: bool = False,
                pinyin: bool = False,
                ipa_lang: Optional[str] = None,
                jyutping: bool = False,
                korean_romaja: bool = False,
                arabic_translit: bool = False,
            ):
                def _delegate(path: str):
                    return original_load_segments_from_json(
                        path,
                        text_key=text_key,
                        ruby_key=ruby_key,
                        tokens_key=tokens_key,
                        pairs_key=pairs_key,
                        palette=palette,
                        auto_ruby=auto_ruby,
                        strip_kana=strip_kana,
                        kana_romaji=kana_romaji,
                        pinyin=pinyin,
                        ipa_lang=ipa_lang,
                        jyutping=jyutping,
                        korean_romaja=korean_romaja,
                        arabic_translit=arabic_translit,
                    )

                if not tokens_key:
                    return _delegate(json_path)

                try:
                    with open(json_path, "r", encoding="utf-8") as handle:
                        payload = json.load(handle)
                except Exception:
                    return _delegate(json_path)

                if isinstance(payload, dict):
                    items = payload.get("items") or payload.get("subtitles") or payload.get("segments") or []
                elif isinstance(payload, list):
                    items = payload
                else:
                    items = []

                modified = False
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    base_text = _base_text_from_item(item, text_key)
                    tokens_payload = item.get(tokens_key)
                    if is_speaker_only_tokens(tokens_payload):
                        fallback_tokens = _fallback_content_tokens(item, text_key, ruby_key, pairs_key, auto_ruby, palette)
                        if not fallback_tokens:
                            continue
                        normalized_tokens = normalize_tokens_payload(
                            list(tokens_payload) + fallback_tokens,
                            text=base_text,
                            text_key=text_key,
                            palette=palette,
                        )
                    elif has_content_token(tokens_payload):
                        normalized_tokens = normalize_tokens_payload(
                            tokens_payload,
                            text=base_text,
                            text_key=text_key,
                            palette=palette,
                        )
                    else:
                        normalized_tokens = _fallback_content_tokens(
                            item,
                            text_key,
                            ruby_key,
                            pairs_key,
                            auto_ruby,
                            palette,
                        )
                    if normalized_tokens and normalized_tokens != tokens_payload:
                        item[tokens_key] = normalized_tokens
                        modified = True

                if not modified:
                    return _delegate(json_path)

                temp_path = None
                try:
                    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
                        json.dump(payload, handle, ensure_ascii=False)
                        temp_path = handle.name
                    return _delegate(temp_path)
                finally:
                    if temp_path:
                        try:
                            os.unlink(temp_path)
                        except OSError:
                            pass

            burner_mod.load_segments_from_json = load_segments_from_json_lazyedit
            burner_mod._lazyedit_token_normalization_patch = True
    except Exception:
        pass

    # LazyEdit patch: keep the upstream dependency read-only and patch behavior
    # at import time instead.
    try:
        if getattr(burner_mod, "_lazyedit_padding_patch", False) is not True and hasattr(burner_mod, "_append_padding"):
            def _append_padding_passthrough(img, _padding_top: int, _padding_bottom: int):
                return img

            burner_mod._append_padding = _append_padding_passthrough  # type: ignore[attr-defined]
            burner_mod._lazyedit_padding_patch = True
    except Exception:
        pass

    # LazyEdit patch: upstream render defaults to a fixed 16px padding around
    # subtitles. That wastes a large fraction of short landscape slots and makes
    # text look tiny. Use padding proportional to slot height instead.
    try:
        if getattr(burner_mod, "_lazyedit_dynamic_padding_patch", False) is not True and hasattr(burner_mod, "SubtitleTrack"):
            OriginalSubtitleTrack = burner_mod.SubtitleTrack

            def render_segment(self, seg):  # type: ignore[no-redef]
                key = id(seg)
                cached = self._render_cache.get(key)
                if cached is not None:
                    return cached

                pad = _slot_padding_for_height(int(self.slot.height), int(getattr(self.style, "stroke_width", 0)))
                img = self.renderer.render_tokens(seg.tokens, padding=pad)
                img = burner_mod._append_padding(img, self.slot.height, self.slot.height)
                self._render_cache[key] = img
                return img

            OriginalSubtitleTrack.render_segment = render_segment
            burner_mod._lazyedit_dynamic_padding_patch = True
    except Exception:
        # If patching fails, fall back to upstream behavior.
        pass

    # LazyEdit patch: upstream pinyin tokenization zips raw characters with
    # pypinyin() output. Mixed CJK/Latin text such as "一个bucket" then becomes
    # 一/个/b because pypinyin groups "bucket" as one item while zip consumes
    # only the first Latin character. Keep Latin words and decimal+unit runs
    # atomic, and annotate only CJK characters with pinyin.
    try:
        if getattr(burner_mod, "_lazyedit_mixed_pinyin_patch", False) is not True:
            RubyToken = burner_mod.RubyToken
            cjk_pred = getattr(burner_mod, "_is_cjk", None)
            pinyin_available = bool(getattr(burner_mod, "PINYIN_AVAILABLE", False))
            pypinyin_fn = getattr(burner_mod, "pypinyin", None)
            pinyin_style = getattr(getattr(burner_mod, "Style", None), "TONE", None)

            token_pattern = re.compile(
                r"\d+(?:[.,]\d+)*(?:\s*(?:[%°℃℉]|[A-Za-zµμ/%]+))?"
                r"|[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[’'\-][A-Za-zÀ-ÖØ-öø-ÿ]+)*"
                r"|[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]+"
                r"|\s+"
                r"|.",
                re.UNICODE,
            )

            def _is_cjk_char(char: str) -> bool:
                if callable(cjk_pred):
                    try:
                        return bool(cjk_pred(char))
                    except Exception:
                        pass
                return "\u3400" <= char <= "\u9fff" or "\uf900" <= char <= "\ufaff"

            def _pinyin_for_char(char: str) -> str | None:
                if not pinyin_available or not callable(pypinyin_fn):
                    return None
                try:
                    result = pypinyin_fn(char, style=pinyin_style, errors=lambda value: [value])
                except Exception:
                    return None
                if not result:
                    return None
                first = result[0]
                reading = first[0] if first else ""
                if not reading or reading == char:
                    return None
                return str(reading)

            def _pinyin_for_cjk_run(text: str) -> list[str | None]:
                if not pinyin_available or not callable(pypinyin_fn):
                    return [None] * len(text)
                try:
                    result = pypinyin_fn(text, style=pinyin_style, errors=lambda value: [value])
                except Exception:
                    return [_pinyin_for_char(char) for char in text]
                readings: list[str | None] = []
                for char, item in zip(text, result):
                    reading = item[0] if item else ""
                    readings.append(str(reading) if reading and reading != char else None)
                if len(readings) < len(text):
                    readings.extend(_pinyin_for_char(char) for char in text[len(readings) :])
                return readings

            def _smart_text_tokens(text: str, color=None, token_type=None) -> list:
                if not text:
                    return []
                out = []
                for match in token_pattern.finditer(str(text)):
                    part = match.group(0)
                    if not part:
                        continue
                    if all(_is_cjk_char(char) for char in part):
                        for char, ruby in zip(part, _pinyin_for_cjk_run(part)):
                            out.append(
                                RubyToken(
                                    text=char,
                                    ruby=ruby,
                                    color=color,
                                    token_type=token_type,
                                )
                            )
                    elif any(_is_cjk_char(ch) for ch in part):
                        for ch in part:
                            if _is_cjk_char(ch):
                                out.append(
                                    RubyToken(
                                        text=ch,
                                        ruby=_pinyin_for_char(ch),
                                        color=color,
                                        token_type=token_type,
                                    )
                                )
                            else:
                                out.append(RubyToken(text=ch, color=color, token_type=token_type))
                    else:
                        out.append(RubyToken(text=part, color=color, token_type=token_type))
                return out

            def _tokens_with_pinyin_lazyedit(text: str):
                return _smart_text_tokens(text)

            def _apply_pinyin_lazyedit(tokens):  # type: ignore[no-redef]
                if not pinyin_available:
                    return tokens
                expanded = []
                for token in tokens:
                    if getattr(token, "token_type", None) == "speaker":
                        expanded.append(token)
                        continue
                    text = getattr(token, "text", "") or ""
                    if getattr(token, "ruby", None) or not text:
                        expanded.append(token)
                        continue
                    if any(_is_cjk_char(char) for char in text):
                        expanded.extend(
                            _smart_text_tokens(
                                text,
                                color=getattr(token, "color", None),
                                token_type=getattr(token, "token_type", None),
                            )
                        )
                    else:
                        expanded.append(token)
                return expanded

            def _split_text_tokens_for_fit_lazyedit(text: str):  # type: ignore[no-redef]
                if not text:
                    return []
                parts = _smart_text_tokens(text)
                if parts:
                    return parts
                return [RubyToken(text=text)]

            burner_mod._tokens_with_pinyin = _tokens_with_pinyin_lazyedit
            burner_mod._apply_pinyin = _apply_pinyin_lazyedit
            burner_mod._split_text_tokens_for_fit = _split_text_tokens_for_fit_lazyedit
            burner_mod._lazyedit_mixed_pinyin_patch = True
    except Exception:
        pass

    # LazyEdit patch: prefer time-splitting segments for long lines (instead of
    # shrinking text to fit width). This keeps font size consistent and makes
    # `fontScale` behave like a simple multiplier: larger scale => fewer words
    # per timestamped chunk.
    try:
        if getattr(burner_mod, "_lazyedit_split_patch", False) is not True and hasattr(burner_mod, "_auto_split_segments_for_slot"):
            SubtitleSegment = burner_mod.SubtitleSegment
            RubyRenderer = burner_mod.RubyRenderer
            _split_text_tokens_for_fit = burner_mod._split_text_tokens_for_fit
            _split_segment_timing = burner_mod._split_segment_timing
            _segment_text_from_tokens = burner_mod._segment_text_from_tokens
            _trim_chunk = getattr(burner_mod, "_trim_chunk", None)

            def _auto_split_segments_for_slot_lazyedit(segments, slot, style):  # type: ignore[no-redef]
                import re

                renderer = RubyRenderer(style)
                split_segments = []
                max_w = max(1, int(slot.width))
                stroke = int(getattr(style, "stroke_width", 0) or 0)

                def _is_japanese_text(text: str) -> bool:
                    if not text:
                        return False
                    return bool(re.search(r"[\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF]", text))

                def _keep_token_atomic(token) -> bool:
                    if getattr(token, "token_type", None) == "speaker":
                        return True
                    if hasattr(token, "_lazyedit_group"):
                        return True
                    text = getattr(token, "text", "") or ""
                    if not _is_japanese_text(text):
                        return False
                    # If tokens come from the JSON (word-level), keep each word intact.
                    token_type = getattr(token, "token_type", None)
                    ruby = getattr(token, "ruby", None)
                    return token_type is not None or ruby is not None

                def _padding_for_tokens(tokens):
                    pad = _slot_padding_for_height(int(slot.height), stroke)
                    if tokens and getattr(tokens[0], "token_type", None) == "speaker":
                        gap = max(1, int(round(getattr(style, "main_font_size", 0) * 0.06)))
                        icon_w = max(1, int(getattr(style, "main_font_size", 0) * 0.55))
                        pad = max(pad, stroke * 2, icon_w + gap + 2)
                    return pad

                def _split_ruby_token(token):
                    """Split a single RubyToken into smaller RubyTokens while keeping ruby roughly aligned."""
                    text = getattr(token, "text", "") or ""
                    ruby = getattr(token, "ruby", None)
                    color = getattr(token, "color", None)
                    token_type = getattr(token, "token_type", None)
                    if _keep_token_atomic(token):
                        return [token]
                    split_text_tokens = _split_text_tokens_for_fit(text)
                    if not ruby:
                        return [
                            burner_mod.RubyToken(text=t.text, ruby=None, color=color, token_type=token_type)  # type: ignore[attr-defined]
                            for t in split_text_tokens
                        ]

                    ruby_parts = re.findall(r"\S+|\s+", str(ruby))
                    ruby_words = [p for p in ruby_parts if not p.isspace()]
                    text_words = [t for t in split_text_tokens if (t.text or "") and not (t.text or "").isspace()]

                    # Best-effort mapping: when counts match, assign 1:1.
                    mapping: list[str | None] = []
                    if ruby_words and len(ruby_words) == len(text_words):
                        mapping = list(ruby_words)
                    elif ruby_words and len(text_words) > 1 and len(ruby_words) > 1:
                        # Proportional allocation by visible text length.
                        lengths = [len((t.text or "").strip()) for t in text_words]
                        total = max(1, sum(lengths))
                        remaining = len(ruby_words)
                        allocations: list[int] = []
                        for idx, ln in enumerate(lengths):
                            if idx == len(lengths) - 1:
                                take = remaining
                            else:
                                take = max(1, int(round(remaining * (ln / total))))
                                take = min(take, remaining - (len(lengths) - idx - 1))
                            allocations.append(take)
                            remaining -= take
                        cursor = 0
                        for take in allocations:
                            chunk = ruby_words[cursor : cursor + take]
                            cursor += take
                            mapping.append(" ".join(chunk).strip() or None)
                    else:
                        mapping = [str(ruby)]

                    out = []
                    word_idx = 0
                    for t in split_text_tokens:
                        token_text = t.text
                        if not token_text:
                            continue
                        if token_text.isspace():
                            out.append(burner_mod.RubyToken(text=token_text, ruby=None, color=color, token_type=token_type))  # type: ignore[attr-defined]
                            continue
                        ruby_piece = mapping[word_idx] if word_idx < len(mapping) else None
                        out.append(burner_mod.RubyToken(text=token_text, ruby=ruby_piece, color=color, token_type=token_type))  # type: ignore[attr-defined]
                        word_idx += 1
                    return out or [token]

                def _expand_tokens_for_width(tokens, max_w, pad):
                    expanded = []
                    for tok in tokens:
                        if getattr(tok, "token_type", None) == "speaker":
                            expanded.append(tok)
                            continue
                        if _keep_token_atomic(tok):
                            expanded.append(tok)
                            continue
                        try:
                            w, _ = renderer.measure_tokens([tok])
                        except Exception:
                            expanded.append(tok)
                            continue
                        if (w + pad * 2) <= max_w:
                            expanded.append(tok)
                            continue
                        parts = _split_ruby_token(tok)
                        if len(parts) <= 1:
                            expanded.append(tok)
                        else:
                            expanded.extend(parts)
                    return expanded

                for segment in segments:
                    if not getattr(segment, "tokens", None):
                        continue
                    tokens = segment.tokens
                    pad = _padding_for_tokens(tokens)
                    width, _ = renderer.measure_tokens(tokens)
                    if (width + pad * 2) <= max_w:
                        split_segments.append(segment)
                        continue

                    split_tokens = tokens
                    if len(tokens) == 1:
                        tok = tokens[0]
                        if getattr(tok, "token_type", None) != "speaker" and not _keep_token_atomic(tok):
                            split_tokens = _split_ruby_token(tok)
                        else:
                            split_tokens = tokens

                    # Greedy chunking by measured width with the same padding
                    # that render_segment uses. This yields stable chunk sizes
                    # as the user adjusts fontScale.
                    split_tokens = _expand_tokens_for_width(split_tokens, max_w, pad)
                    # Build units that keep grouped Japanese tokens together.
                    units = []
                    idx = 0
                    while idx < len(split_tokens):
                        tok = split_tokens[idx]
                        group = getattr(tok, "_lazyedit_group", None)
                        if group is None:
                            units.append([tok])
                            idx += 1
                            continue
                        grouped = [tok]
                        idx += 1
                        while idx < len(split_tokens) and getattr(split_tokens[idx], "_lazyedit_group", None) == group:
                            grouped.append(split_tokens[idx])
                            idx += 1
                        units.append(grouped)

                    chunks = []
                    current_tokens = []
                    for unit in units:
                        trial = current_tokens + unit
                        w, _ = renderer.measure_tokens(trial)
                        if current_tokens and (w + pad * 2) > max_w:
                            chunk = current_tokens
                            if callable(_trim_chunk):
                                chunk = _trim_chunk(chunk)
                            if chunk:
                                chunks.append(chunk)
                            current_tokens = list(unit)
                            continue
                        current_tokens = trial
                    if current_tokens:
                        chunk = current_tokens
                        if callable(_trim_chunk):
                            chunk = _trim_chunk(chunk)
                        if chunk:
                            chunks.append(chunk)

                    if len(chunks) > 1:
                        split_segments.extend(_split_segment_timing(segment, chunks))
                        continue

                    if split_tokens is not tokens:
                        split_segments.append(
                            SubtitleSegment(
                                start_time=segment.start_time,
                                end_time=segment.end_time,
                                tokens=split_tokens,
                                text=_segment_text_from_tokens(split_tokens),
                            )
                        )
                    else:
                        split_segments.append(segment)
                return split_segments

            burner_mod._auto_split_segments_for_slot = _auto_split_segments_for_slot_lazyedit
            burner_mod._lazyedit_split_patch = True
    except Exception:
        pass

    # LazyEdit patch: keep word-level Japanese tokens intact when applying
    # kana/romaji expansion. The upstream behavior splits kana-only tokens into
    # per-character pieces, which breaks word-level tokens like ドン・キホーテ.
    try:
        if getattr(burner_mod, "_lazyedit_kana_expand_patch", False) is not True and hasattr(burner_mod, "_expand_kana_affixes"):
            original_expand_kana = burner_mod._expand_kana_affixes

            def _expand_kana_affixes_lazyedit(tokens, add_romaji):  # type: ignore[no-redef]
                expanded = []
                group_counter = 0
                for token in tokens:
                    if not getattr(token, "text", None):
                        continue
                    token_type = getattr(token, "token_type", None)
                    ruby = getattr(token, "ruby", None)
                    if add_romaji and token_type is not None and token_type != "speaker":
                        # Preserve word-level tokens but still annotate kana affixes.
                        if burner_mod._has_kanji(token.text):
                            parts = original_expand_kana([token], add_romaji)
                            if len(parts) > 1:
                                group_counter += 1
                                group_id = f"jpword-{group_counter}"
                                for part in parts:
                                    setattr(part, "_lazyedit_group", group_id)
                                expanded.extend(parts)
                            else:
                                expanded.extend(parts)
                            continue
                        if not ruby and burner_mod._is_kana_text(token.text):
                            romaji = burner_mod._kana_to_romaji(token.text)
                            if romaji and romaji != token.text:
                                token.ruby = romaji
                        expanded.append(token)
                        continue
                    if ruby and burner_mod._has_kanji(token.text):
                        expanded.append(token)
                        continue
                    expanded.extend(original_expand_kana([token], add_romaji))
                return expanded

            burner_mod._expand_kana_affixes = _expand_kana_affixes_lazyedit
            burner_mod._lazyedit_kana_expand_patch = True
    except Exception:
        pass

    # LazyEdit patch: upstream RubyRenderer inflates ruby row height using full
    # font metrics (ascent+descent) even for small romanization like "ge ru",
    # creating an overly large invisible gap between ruby and main text. It also
    # previously reserved a ruby row even when ruby is absent. Keep dependency
    # read-only by monkeypatching at import time.
    try:
        if getattr(burner_mod, "_lazyedit_ruby_layout_patch", False) is not True and hasattr(burner_mod, "RubyRenderer"):
            OriginalRubyRenderer = burner_mod.RubyRenderer

            def _build_layout_compact_ruby(self, tokens):  # type: ignore[no-redef]
                temp_img = burner_mod.Image.new("RGB", (1, 1))
                draw = burner_mod.ImageDraw.Draw(temp_img)
                main_ascent, main_descent = self.main_font.getmetrics()

                layout = []
                total_width = 0
                max_ruby_h = 0
                max_main_h = 0

                for token in tokens:
                    if getattr(token, "token_type", None) == "speaker":
                        # Speaker icon should not affect centering; treat it as a
                        # zero-width overlay rendered into padding.
                        icon_size = max(1, int(self.style.main_font_size * 0.55))
                        main_w = main_h = icon_size
                        ruby_w = ruby_h = 0
                        prefix_w = core_w = suffix_w = 0
                        column_w = 0
                        max_main_h = max(max_main_h, main_h)
                        layout.append(
                            {
                                "main_w": main_w,
                                "main_h": main_h,
                                "ruby_w": ruby_w,
                                "ruby_h": ruby_h,
                                "prefix_w": prefix_w,
                                "core_w": core_w,
                                "suffix_w": suffix_w,
                                "column_w": column_w,
                            }
                        )
                        continue

                    main_w, main_h = OriginalRubyRenderer._measure_text(draw, getattr(token, "text", "") or "", self.main_font)
                    ruby_text = getattr(token, "ruby", None) or ""
                    if ruby_text:
                        ruby_w, ruby_h = OriginalRubyRenderer._measure_text(draw, ruby_text, self.ruby_font)
                    else:
                        ruby_w = ruby_h = 0

                    # Keep main row stable, but keep ruby row compact by using bbox height.
                    main_h = max(main_h, main_ascent + main_descent)

                    prefix_w = core_w = suffix_w = 0
                    if ruby_text and getattr(token, "text", None) and burner_mod._has_kanji(token.text):  # type: ignore[attr-defined]
                        prefix, core, suffix = OriginalRubyRenderer._split_kana_affixes(token.text)
                        prefix_w, _ = OriginalRubyRenderer._measure_text(draw, prefix, self.main_font)
                        core_w, _ = OriginalRubyRenderer._measure_text(draw, core, self.main_font)
                        suffix_w, _ = OriginalRubyRenderer._measure_text(draw, suffix, self.main_font)

                    column_w = main_w
                    if ruby_text:
                        if core_w > 0:
                            ruby_span = prefix_w + max(ruby_w, core_w) + suffix_w
                        else:
                            ruby_span = ruby_w
                        column_w = max(main_w, ruby_span)

                    total_width += column_w
                    max_ruby_h = max(max_ruby_h, ruby_h)
                    max_main_h = max(max_main_h, main_h)

                    layout.append(
                        {
                            "main_w": main_w,
                            "main_h": main_h,
                            "ruby_w": ruby_w,
                            "ruby_h": ruby_h,
                            "prefix_w": prefix_w,
                            "core_w": core_w,
                            "suffix_w": suffix_w,
                            "column_w": column_w,
                        }
                    )

                return layout, total_width, max_ruby_h, max_main_h

            OriginalRubyRenderer._build_layout = _build_layout_compact_ruby

            # Render speaker icon in the left padding so it doesn't consume
            # horizontal centering space for the main text. Also support
            # LazyEdit-specific bold/outline style flags without editing the
            # upstream furigana dependency.
            def render_tokens_lazyedit(self, tokens, padding=16):  # type: ignore[no-redef]
                if not tokens:
                    return burner_mod.Image.new("RGBA", (1, 1), (0, 0, 0, 0))

                padding = max(int(padding), int(self.style.stroke_width * 2))
                speaker = tokens[0] if getattr(tokens[0], "token_type", None) == "speaker" else None
                render_tokens = tokens[1:] if speaker and len(tokens) > 1 else tokens
                if speaker and len(tokens) > 1:
                    gap = max(1, int(round(self.style.main_font_size * 0.06)))
                    icon_w = max(1, int(getattr(self.style, "main_font_size", 0) * 0.55))
                    padding = max(padding, icon_w + gap + 2)
                else:
                    gap = 0
                    icon_w = 0

                layout, text_width, max_ruby_h, max_main_h = self._build_layout(render_tokens)
                ruby_row = max_ruby_h + int(self.style.ruby_font_size * self.style.ruby_spacing) if max_ruby_h else 0
                text_height = max_main_h + ruby_row
                width = max(text_width + padding * 2, 1)
                height = max(text_height + padding * 2, 1)
                img = burner_mod.Image.new("RGBA", (width, height), (0, 0, 0, 0))
                draw = burner_mod.ImageDraw.Draw(img)

                start_x = padding
                start_y = padding
                ascent, descent = self.main_font.getmetrics()
                main_row_center = start_y + ruby_row + (ascent + descent) / 2
                current_x = start_x
                bold_width = 1 if bool(getattr(self.style, "lazyedit_font_bold", False)) else 0

                def _draw_foreground(position, text, font, fill):
                    x, y = position
                    if bold_width <= 0:
                        draw.text((x, y), text, font=font, fill=fill)
                        return
                    for dx, dy in ((0, 0), (bold_width, 0), (0, bold_width), (bold_width, bold_width)):
                        draw.text((x + dx, y + dy), text, font=font, fill=fill)

                def _draw_stroke(position, text, font):
                    stroke_width = int(getattr(self.style, "stroke_width", 0) or 0)
                    if stroke_width <= 0:
                        return
                    x, y = position
                    for dx in range(-stroke_width, stroke_width + 1):
                        for dy in range(-stroke_width, stroke_width + 1):
                            if dx * dx + dy * dy <= stroke_width * stroke_width:
                                draw.text((x + dx, y + dy), text, font=font, fill=self.style.stroke_color)

                if speaker and len(tokens) > 1:
                    try:
                        icon_y = main_row_center - icon_w / 2
                        icon_x = max(0, padding - icon_w - gap)
                        icon = self._load_speaker_icon(icon_w)
                        if icon:
                            if icon.mode != "RGBA":
                                icon = icon.convert("RGBA")
                            alpha = icon.split()[-1]
                            tinted = burner_mod.Image.new("RGBA", icon.size, (*SPEAKER_ICON_COLOR, 255))
                            tinted.putalpha(alpha)
                            img.alpha_composite(tinted, (int(icon_x), int(round(icon_y))))
                        else:
                            _draw_foreground((icon_x, icon_y), getattr(speaker, "text", None) or "🔊", self.main_font, SPEAKER_ICON_COLOR)
                    except Exception:
                        pass

                for token, metrics in zip(render_tokens, layout):
                    main_w = metrics["main_w"]
                    ruby_w = metrics["ruby_w"]
                    ruby_h = metrics["ruby_h"]
                    prefix_w = metrics["prefix_w"]
                    core_w = metrics["core_w"]
                    column_w = metrics["column_w"]

                    main_x = current_x + (column_w - main_w) // 2
                    main_y = start_y + ruby_row

                    if getattr(token, "token_type", None) == "speaker":
                        icon = self._load_speaker_icon(main_w)
                        icon_y = main_row_center - metrics["main_h"] / 2
                        if icon:
                            img.alpha_composite(icon, (int(main_x), int(round(icon_y))))
                        else:
                            _draw_foreground((main_x, icon_y), getattr(token, "text", None) or "🔊", self.main_font, self.style.text_color)
                        current_x += column_w
                        continue

                    color = getattr(token, "color", None) or self.style.text_color
                    _draw_stroke((main_x, main_y), token.text, self.main_font)
                    _draw_foreground((main_x, main_y), token.text, self.main_font, color)

                    if getattr(token, "ruby", None):
                        if core_w > 0:
                            ruby_x = int(main_x + prefix_w + (core_w - ruby_w) / 2)
                        else:
                            ruby_x = current_x + (column_w - ruby_w) // 2
                        ruby_y = start_y + (max_ruby_h - ruby_h)
                        _draw_stroke((ruby_x, ruby_y), token.ruby, self.ruby_font)
                        _draw_foreground((ruby_x, ruby_y), token.ruby, self.ruby_font, color)

                    current_x += column_w

                return img

            OriginalRubyRenderer.render_tokens = render_tokens_lazyedit
            burner_mod._lazyedit_ruby_layout_patch = True
    except Exception:
        pass

    # LazyEdit patch: allow subtitles to use the empty gutter between slots as
    # extra vertical room, without changing the user-selected band height.
    # We tag each Slot instance with per-row extra space, then shift the overlay
    # accordingly.
    try:
        if getattr(burner_mod, "_lazyedit_gutter_overlay_patch", False) is not True and hasattr(burner_mod, "_overlay_image"):
            original_overlay_image = burner_mod._overlay_image

            def _overlay_image_with_gutter(frame, img, slot):  # type: ignore[no-redef]
                extra_top = int(getattr(slot, "_lazyedit_extra_top", 0) or 0)
                extra_bottom = int(getattr(slot, "_lazyedit_extra_bottom", 0) or 0)
                try:
                    overlay_img = img
                    h, w = overlay_img.size[1], overlay_img.size[0]
                    overlay = burner_mod.cv2.cvtColor(burner_mod.np.array(overlay_img), burner_mod.cv2.COLOR_RGBA2BGRA)

                    if slot.align == "left":
                        x = slot.x
                    elif slot.align == "right":
                        x = slot.x + max(slot.width - w, 0)
                    else:
                        x = slot.x + max((slot.width - w) // 2, 0)

                    virtual_y = slot.y - extra_top
                    virtual_h = int(slot.height) + extra_top + extra_bottom
                    y = virtual_y + (virtual_h - h) // 2

                    x = max(0, min(int(x), frame.shape[1] - w))
                    y = max(0, min(int(y), frame.shape[0] - h))

                    alpha = overlay[:, :, 3] / 255.0
                    alpha = burner_mod.np.stack([alpha] * 3, axis=2)
                    region = frame[y : y + h, x : x + w]
                    blended = region * (1 - alpha) + overlay[:, :, :3] * alpha
                    frame[y : y + h, x : x + w] = blended.astype(burner_mod.np.uint8)
                    return frame
                except Exception:
                    return original_overlay_image(frame, img, slot)

            burner_mod._overlay_image = _overlay_image_with_gutter
            burner_mod._lazyedit_gutter_overlay_patch = True
    except Exception:
        pass

    return (
        BurnLayout,
        RubyRenderer,
        RubyToken,
        Slot,
        SlotAssignment,
        TextStyle,
        build_bottom_slot_layout,
        burn_subtitles_with_layout,
    )


def _get_video_resolution(video_path: str) -> tuple[int, int]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height


def burn_video_with_slots(
    video_path: str,
    output_path: str,
    slots: list[BurnSlotConfig],
    height_ratio: float = 0.28,
    rows: int = 2,
    cols: int = 2,
    margin: int = 24,
    gutter: int = 12,
    lift_slots: int = 1,
    lift_ratio: float | None = None,
    ruby_spacing: float = 0.1,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> None:
    (
        BurnLayout,
        RubyRenderer,
        RubyToken,
        Slot,
        SlotAssignment,
        TextStyle,
        build_bottom_slot_layout,
        burn_subtitles_with_layout,
    ) = _load_burner_module()

    width, height = _get_video_resolution(video_path)
    base_bottom_height_px = int(height * float(height_ratio))
    base_slot_height_px = max(1, (base_bottom_height_px - gutter * (rows - 1)) // max(rows, 1))
    base_slot_width_px = max(1, (width - gutter * (cols - 1) - margin * 2) // max(cols, 1))

    def _language_visual_scale(lang: str) -> float:
        """Compensate for fonts where CJK glyphs appear visually smaller than Latin."""
        normalized = (lang or "").strip().lower()
        if normalized in {"ja", "zh", "zh-hant", "zh-hans", "yue", "ko"}:
            return 1.15
        return 1.0
    # Respect the user-specified subtitle band height and vertical shift.
    effective_height_ratio = float(height_ratio)
    bottom_height = int(height * effective_height_ratio)
    available_h = max(1, bottom_height - gutter * (rows - 1))
    slot_width = max(1, (width - gutter * (cols - 1) - margin * 2) // max(cols, 1))
    base_slot_height = max(1, available_h // max(rows, 1))
    row_heights = [base_slot_height for _ in range(max(rows, 1))]
    # Distribute leftover pixels to top rows for deterministic packing.
    remainder = available_h - base_slot_height * max(rows, 1)
    for i in range(max(0, remainder)):
        row_heights[i % len(row_heights)] += 1

    if lift_ratio is not None:
        lift_ratio = max(0.0, float(lift_ratio))
        lift_pixels = int(height * lift_ratio)
    else:
        lift_slots = max(0, int(lift_slots))
        lift_pixels = sum(row_heights[:lift_slots]) + gutter * lift_slots if lift_slots else 0

    top_y = max(0, height - bottom_height - lift_pixels)

    slots_layout: list[Slot] = []
    slot_id = 1
    y_cursor = top_y
    for row in range(rows):
        row_h = row_heights[row] if row < len(row_heights) else max(1, available_h // max(rows, 1))
        for col in range(cols):
            x = margin + col * (slot_width + gutter)
            slot_obj = Slot(slot_id=slot_id, x=x, y=y_cursor, width=slot_width, height=row_h)
            # Tag each slot with per-row extra room taken from the gutter so the
            # renderer can place ruby without shrinking the main font.
            extra_top = gutter // 2 if row > 0 else 0
            extra_bottom = gutter - (gutter // 2) if row < rows - 1 else 0
            setattr(slot_obj, "_lazyedit_extra_top", extra_top)
            setattr(slot_obj, "_lazyedit_extra_bottom", extra_bottom)
            slots_layout.append(slot_obj)
            slot_id += 1
        y_cursor += row_h + gutter
    layout = BurnLayout(slots=slots_layout)

    slot_geometry: dict[int, tuple[int, int, int, int]] = {
        slot_entry.slot_id: (
            int(slot_entry.width),
            int(slot_entry.height),
            int(getattr(slot_entry, "_lazyedit_extra_top", 0) or 0),
            int(getattr(slot_entry, "_lazyedit_extra_bottom", 0) or 0),
        )
        for slot_entry in layout.slots
    }
    default_style = TextStyle()

    assignments: list[SlotAssignment] = []
    prepared_slots: list[dict[str, Any]] = []
    ruby_spacing = min(max(float(ruby_spacing), 0.0), 0.2)
    for slot in slots:
        scale = max(0.6, min(2.5, float(slot.font_scale or 1.0)))
        slot_width, slot_height, extra_top, extra_bottom = slot_geometry.get(
            slot.slot_id, (width, max(1, int(height * height_ratio)), 0, 0)
        )

        expects_ruby = bool(
            slot.ruby_key
            or slot.auto_ruby
            or slot.kana_romaji
            or slot.pinyin
            or slot.ipa
            or slot.jyutping
            or slot.korean_romaja
            or slot.arabic_translit
        )

        # Derive font sizes from the pixel geometry of each slot so that
        # subtitle readability stays consistent across high-resolution inputs.
        # The coefficients were tuned so that 720p/1080p outputs remain close to
        # the historical defaults, while 4K+ inputs scale up appropriately.
        # Main font sizing should not change when ruby is toggled on/off.
        base_main_ref_h = slot_height
        base_main_ref_w = slot_width
        base_main = int(round(min(base_main_ref_h * 0.38, base_main_ref_w * 0.07)))
        base_main = int(round(base_main * _language_visual_scale(slot.language)))
        base_main = max(14, min(base_main, 220))
        base_ruby = int(round(base_main * 0.6))
        base_ruby = max(10, min(base_ruby, base_main - 2))

        # Choose a stable "base" font size that fits within the slot height at
        # scale=1 (no aspect-ratio hardcoding), then apply `font_scale` as a
        # simple multiplier. We intentionally do not shrink to fit at higher
        # scales: overflow/overlap is acceptable, and long lines are split into
        # timestamped chunks instead of shrinking.
        safe_height = max(1, int(slot_height + max(0, extra_top) + max(0, extra_bottom)))

        is_cjk = (slot.language or "").lower() in {"ja", "zh", "zh-hant", "zh-hans", "yue", "ko"}
        sample_text = "漢字" if is_cjk else "Sample"
        if (slot.language or "").lower() in {"zh", "zh-hant", "zh-hans", "yue"}:
            sample_ruby = "hàn zì"
        elif is_cjk:
            sample_ruby = "かんじ"
        else:
            sample_ruby = "sam-pəl"

        def _render_sample_height(main_size: int, include_ruby: bool) -> int:
            stroke = max(1, int(round(default_style.stroke_width * (main_size / default_style.main_font_size))))
            pad_base = int(round(max(1, slot_height) * 0.10))
            pad_base = max(2, min(pad_base, 16))
            pad = max(pad_base, stroke * 2)
            ruby_size = max(0, int(round(main_size * 0.6))) if include_ruby else 0
            if ruby_size:
                ruby_size = min(ruby_size, max(0, main_size - 2))
            style = TextStyle(
                main_font_size=main_size,
                ruby_font_size=ruby_size,
                stroke_width=stroke,
                ruby_spacing=ruby_spacing,
            )
            renderer = RubyRenderer(style)
            token = RubyToken(text=sample_text, ruby=sample_ruby if include_ruby else None)
            img = renderer.render_tokens([token], padding=pad)
            return int(img.size[1])

        # Start from the heuristic size, then clamp to what fits at scale=1.
        base_main_fit = max(12, int(round(base_main)))
        lo, hi = 10, 260
        while lo < hi:
            mid = (lo + hi + 1) // 2
            try:
                h = _render_sample_height(mid, include_ruby=False)
            except Exception:
                h = safe_height + 1
            if h <= safe_height:
                lo = mid
            else:
                hi = mid - 1
        base_main_fit = max(12, min(lo, 260))

        max_main_font_size = max(12, int(round(base_main_fit * scale)))
        has_ruby = expects_ruby
        if has_ruby:
            # Ruby/pinyin rows must not intrude into adjacent subtitle rows. We
            # compute a per-slot cap here, then apply the smallest cap as the
            # shared base font below so ruby rows do not look smaller than
            # non-ruby rows.
            ruby_safe_height = max(1, safe_height - max(2, gutter // 3))
            lo, hi = 10, max(10, max_main_font_size)
            while lo < hi:
                mid = (lo + hi + 1) // 2
                try:
                    h = _render_sample_height(mid, include_ruby=True)
                except Exception:
                    h = ruby_safe_height + 1
                if h <= ruby_safe_height:
                    lo = mid
                else:
                    hi = mid - 1
            max_main_font_size = max(12, min(max_main_font_size, lo))

        prepared_slots.append(
            {
                "slot": slot,
                "scale": scale,
                "has_ruby": has_ruby,
                "max_main_font_size": max_main_font_size,
            }
        )

    shared_base_font_size = 12.0
    if prepared_slots:
        shared_base_font_size = min(
            float(entry["max_main_font_size"]) / max(0.1, float(entry["scale"]))
            for entry in prepared_slots
        )

    for entry in prepared_slots:
        slot = entry["slot"]
        scale = float(entry["scale"])
        has_ruby = bool(entry["has_ruby"])
        max_main_font_size = int(entry["max_main_font_size"])
        main_font_size = max(12, int(round(shared_base_font_size * scale)))
        main_font_size = min(main_font_size, max_main_font_size)
        stroke_width = max(1, int(round(default_style.stroke_width * (main_font_size / default_style.main_font_size))))
        if not bool(slot.outline_bold):
            stroke_width = max(1, int(round(stroke_width * 0.45)))
        ruby_font_size = max(0, int(round(main_font_size * 0.6)))
        ruby_font_size = min(ruby_font_size, max(0, main_font_size - 2))
        if not has_ruby:
            ruby_font_size = 0
        text_color = _color_to_rgb(slot.font_color, default_style.text_color)
        stroke_color = _color_to_rgb(slot.outline_color, default_style.stroke_color)
        style = TextStyle(
            main_font_size=main_font_size,
            ruby_font_size=ruby_font_size,
            text_color=text_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            ruby_spacing=ruby_spacing,
        )
        setattr(style, "lazyedit_font_bold", bool(slot.font_bold))
        ipa_lang = None
        if slot.ipa:
            if slot.language == "en":
                ipa_lang = "en-us"
            elif slot.language == "fr":
                ipa_lang = "fr-fr"
        jyutping = slot.jyutping and slot.language == "yue"
        korean_romaja = slot.korean_romaja and slot.language == "ko"
        arabic_translit = slot.arabic_translit and slot.language == "ar"
        assignments.append(
            SlotAssignment(
                slot_id=slot.slot_id,
                language=slot.language,
                json_path=slot.json_path,
                text_key=slot.text_key,
                ruby_key=slot.ruby_key,
                tokens_key=slot.tokens_key,
                pairs_key=slot.pairs_key,
                palette=slot.palette,
                style=style,
                auto_ruby=slot.auto_ruby,
                strip_kana=slot.strip_kana,
                kana_romaji=slot.kana_romaji,
                pinyin=slot.pinyin,
                ipa_lang=ipa_lang,
                jyutping=jyutping,
                korean_romaja=korean_romaja,
                arabic_translit=arabic_translit,
            )
        )

    burn_subtitles_with_layout(
        video_path,
        output_path,
        layout,
        assignments,
        progress_callback=progress_callback,
    )
