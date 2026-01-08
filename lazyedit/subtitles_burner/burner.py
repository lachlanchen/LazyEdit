from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

import cv2


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
    kana_romaji: bool = False
    pinyin: bool = False
    ipa: bool = False
    jyutping: bool = False
    korean_romaja: bool = False
    arabic_translit: bool = False


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
            original_render_segment = OriginalSubtitleTrack.render_segment

            def _dynamic_padding_for_slot(slot_height: int, stroke_width: int) -> int:
                base = int(round(max(1, slot_height) * 0.10))
                base = max(6, min(base, 16))
                return max(base, int(stroke_width) * 2)

            def render_segment(self, seg):  # type: ignore[no-redef]
                key = id(seg)
                cached = self._render_cache.get(key)
                if cached is not None:
                    return cached

                pad = _dynamic_padding_for_slot(int(self.slot.height), int(getattr(self.style, "stroke_width", 0)))
                img = self.renderer.render_tokens(seg.tokens, padding=pad)
                if img.width > self.slot.width:
                    scale = min(1.0, self.slot.width / img.width)
                    if scale > 0:
                        new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
                        resample = burner_mod.Image.Resampling.LANCZOS if hasattr(burner_mod.Image, "Resampling") else burner_mod.Image.LANCZOS
                        img = img.resize(new_size, resample)
                img = burner_mod._append_padding(img, self.slot.height, self.slot.height)
                self._render_cache[key] = img
                return img

            OriginalSubtitleTrack.render_segment = render_segment
            burner_mod._lazyedit_dynamic_padding_patch = True
    except Exception:
        # If patching fails, fall back to upstream behavior.
        pass

    # LazyEdit patch: upstream RubyRenderer reserves a "ruby row" height even
    # when a token has no ruby text (because it always max()'s ruby_h with the
    # ruby font metrics). That creates large empty vertical space (most obvious
    # in landscape/square layouts) and prevents slots from being used fully.
    # Keep the dependency read-only by monkeypatching at import time.
    try:
        if getattr(burner_mod, "_lazyedit_no_phantom_ruby_row_patch", False) is not True and hasattr(burner_mod, "RubyRenderer"):
            OriginalRubyRenderer = burner_mod.RubyRenderer
            original_build_layout = OriginalRubyRenderer._build_layout

            def _build_layout_no_phantom_ruby_row(self, tokens):  # type: ignore[no-redef]
                layout, total_width, max_ruby_h, max_main_h = original_build_layout(self, tokens)
                any_ruby = False
                for token, metrics in zip(tokens, layout):
                    if getattr(token, "ruby", None):
                        any_ruby = True
                        continue
                    metrics["ruby_w"] = 0
                    metrics["ruby_h"] = 0
                if not any_ruby:
                    max_ruby_h = 0
                else:
                    max_ruby_h = max((m.get("ruby_h", 0) for m in layout), default=0)
                return layout, total_width, max_ruby_h, max_main_h

            OriginalRubyRenderer._build_layout = _build_layout_no_phantom_ruby_row
            burner_mod._lazyedit_no_phantom_ruby_row_patch = True
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
    # Respect the user-specified subtitle band height. We scale text to fit within
    # the resulting slot height (and clamp ruby if needed) rather than silently
    # expanding the band, so layout height + vertical shift behave predictably.
    effective_height_ratio = float(height_ratio)

    if lift_ratio is not None:
        lift_ratio = max(0.0, float(lift_ratio))
        lift_pixels = int(height * lift_ratio)
        bottom_height = int(height * effective_height_ratio)
        slot_height = max(1, (bottom_height - gutter * (rows - 1)) // rows)
        slot_width = max(1, (width - gutter * (cols - 1) - margin * 2) // cols)
        top_y = max(0, height - bottom_height - lift_pixels)
        slots_layout: list[Slot] = []
        slot_id = 1
        for row in range(rows):
            for col in range(cols):
                x = margin + col * (slot_width + gutter)
                y = top_y + row * (slot_height + gutter)
                slots_layout.append(Slot(slot_id=slot_id, x=x, y=y, width=slot_width, height=slot_height))
                slot_id += 1
        layout = BurnLayout(slots=slots_layout)
    else:
        layout = build_bottom_slot_layout(
            width,
            height,
            rows=rows,
            cols=cols,
            height_ratio=effective_height_ratio,
            margin=margin,
            gutter=gutter,
            lift_slots=lift_slots,
        )

    slot_geometry: dict[int, tuple[int, int]] = {
        slot_entry.slot_id: (int(slot_entry.width), int(slot_entry.height)) for slot_entry in layout.slots
    }
    default_style = TextStyle()

    assignments: list[SlotAssignment] = []
    for slot in slots:
        scale = max(0.6, min(2.5, float(slot.font_scale or 1.0)))
        slot_width, slot_height = slot_geometry.get(slot.slot_id, (width, max(1, int(height * height_ratio))))

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
        base_main_ref_h = base_slot_height_px if expects_ruby else slot_height
        base_main_ref_w = base_slot_width_px if expects_ruby else slot_width
        base_main = int(round(min(base_main_ref_h * 0.38, base_main_ref_w * 0.07)))
        base_main = int(round(base_main * _language_visual_scale(slot.language)))
        base_main = max(14, min(base_main, 220))
        base_ruby = int(round(base_main * 0.6))
        base_ruby = max(10, min(base_ruby, base_main - 2))

        main_font_size = max(12, int(round(base_main * scale)))
        ruby_font_size = max(8, int(round(base_ruby * scale)))
        stroke_width = max(1, int(round(default_style.stroke_width * (main_font_size / default_style.main_font_size))))

        # Prevent overlap between stacked slots by ensuring rendered subtitles fit
        # inside each slot's height. We prefer to keep the main font size stable
        # across languages/slots; if the user scales up beyond what the slot can
        # fit, we clamp ruby first, and only then shrink both proportionally.
        safe_height = max(1, int(slot_height * 0.98))
        padding = max(max(6, min(int(round(slot_height * 0.10)), 16)), stroke_width * 2)
        is_cjk = (slot.language or "").lower() in {"ja", "zh", "zh-hant", "zh-hans", "yue", "ko"}
        sample_text = "漢字" if is_cjk else "Sample"
        sample_ruby = "かんじ" if is_cjk else "sam-pəl"

        def render_height(main_size: int, ruby_size: int, stroke: int, pad: int, include_ruby: bool) -> int:
            style = TextStyle(main_font_size=main_size, ruby_font_size=ruby_size, stroke_width=stroke)
            renderer = RubyRenderer(style)
            tokens = [RubyToken(text=sample_text)]
            if include_ruby and ruby_size > 0:
                tokens = [RubyToken(text=sample_text, ruby=sample_ruby)]
            img = renderer.render_tokens(tokens, padding=pad)
            return int(img.size[1])

        has_ruby = expects_ruby
        if not has_ruby:
            ruby_font_size = 0

        # Use the slot height more fully (especially landscape/square), while keeping
        # main size independent of ruby toggles. We compute the fill ratio from a
        # *main-only* render and then scale ruby proportionally.
        ruby_ratio = (ruby_font_size / float(main_font_size)) if (has_ruby and ruby_font_size > 0) else 0.0

        try:
            main_only_h = render_height(main_font_size, 0, stroke_width, padding, include_ruby=False)
        except Exception:
            main_only_h = 0
        if main_only_h > 0 and main_only_h < safe_height:
            target = safe_height * 0.98
            grow = target / float(main_only_h)
            if grow > 1.02:
                main_font_size = max(12, int(round(main_font_size * grow)))
                stroke_width = max(1, int(round(stroke_width * grow)))
                if ruby_ratio > 0:
                    ruby_font_size = max(8, min(main_font_size - 2, int(round(main_font_size * ruby_ratio))))
                else:
                    ruby_font_size = 0

        try:
            full_h = render_height(main_font_size, ruby_font_size, stroke_width, padding, include_ruby=has_ruby)
        except Exception:
            full_h = 0
        if full_h > safe_height and full_h > 0:
            shrink = safe_height / float(full_h)
            main_font_size = max(12, int(round(main_font_size * shrink)))
            stroke_width = max(1, int(round(stroke_width * shrink)))
            if has_ruby and ruby_font_size > 0:
                ruby_font_size = max(8, min(main_font_size - 2, int(round(main_font_size * ruby_ratio))))
            else:
                ruby_font_size = 0
        style = TextStyle(
            main_font_size=main_font_size,
            ruby_font_size=ruby_font_size,
            stroke_width=stroke_width,
        )
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
