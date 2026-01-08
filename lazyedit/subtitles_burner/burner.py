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

    # When users increase per-slot fontScale, the subtitle block can become taller
    # than the slot and visually overlap into adjacent rows. To keep scaling
    # readable (including ruby/pinyin) without overlap, expand the bottom subtitle
    # band height if needed (within a reasonable cap) before laying out slots.
    def _estimate_required_height_ratio(current_ratio: float) -> float:
        bottom_height_px = int(height * current_ratio)
        slot_height_px = max(1, (bottom_height_px - gutter * (rows - 1)) // rows)
        slot_width_px = max(1, (width - gutter * (cols - 1) - margin * 2) // cols)

        required_slot_height = 1
        for slot in slots:
            scale = max(0.6, min(1.6, float(slot.font_scale or 1.0)))
            base_main = int(round(min(slot_height_px * 0.38, slot_width_px * 0.07)))
            base_main = max(14, min(base_main, 220))
            base_ruby = int(round(base_main * 0.5))

            main_size = max(12, int(round(base_main * scale)))
            ruby_size = max(8, int(round(base_ruby * scale)))
            default_style = TextStyle()
            stroke = max(1, int(round(default_style.stroke_width * (main_size / default_style.main_font_size))))

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
            if not expects_ruby:
                ruby_size = 0

            style = TextStyle(
                main_font_size=main_size,
                ruby_font_size=ruby_size,
                stroke_width=stroke,
            )
            renderer = RubyRenderer(style)
            sample_tokens = [RubyToken(text="🔊", token_type="speaker")]
            if ruby_size > 0:
                sample_tokens.append(RubyToken(text="漢字", ruby="かんじ"))
            else:
                sample_tokens.append(RubyToken(text="Sample"))
            img = renderer.render_tokens(sample_tokens, padding=16)
            total_h = int(img.size[1])
            # Undo the 0.92 safety factor used later and add slack for rounding/centering.
            required_slot_height = max(required_slot_height, int((total_h / 0.92) + 2))

        required_bottom = required_slot_height * rows + gutter * (rows - 1)
        return required_bottom / float(height) if height else current_ratio

    effective_height_ratio = float(height_ratio)
    for _ in range(3):
        needed = _estimate_required_height_ratio(effective_height_ratio)
        next_ratio = max(effective_height_ratio, float(height_ratio), needed)
        next_ratio = min(next_ratio, 0.85)
        if next_ratio - effective_height_ratio < 0.005:
            break
        effective_height_ratio = next_ratio

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
        scale = max(0.6, min(1.6, float(slot.font_scale or 1.0)))
        slot_width, slot_height = slot_geometry.get(slot.slot_id, (width, max(1, int(height * height_ratio))))

        # Derive font sizes from the pixel geometry of each slot so that
        # subtitle readability stays consistent across high-resolution inputs.
        # The coefficients were tuned so that 720p/1080p outputs remain close to
        # the historical defaults, while 4K+ inputs scale up appropriately.
        base_main = int(round(min(slot_height * 0.38, slot_width * 0.07)))
        base_main = max(14, min(base_main, 220))
        base_ruby = int(round(base_main * 0.5))
        base_ruby = max(10, min(base_ruby, base_main - 2))

        main_font_size = max(12, int(round(base_main * scale)))
        ruby_font_size = max(8, int(round(base_ruby * scale)))
        stroke_width = max(1, int(round(default_style.stroke_width * (main_font_size / default_style.main_font_size))))

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
        # Prevent overlap between stacked slots by ensuring rendered subtitles fit
        # inside each slot's height. We prefer to keep the main font size stable
        # across languages/slots; if the user scales up beyond what the slot can
        # fit, we clamp ruby first, and only then shrink both proportionally.
        safe_height = max(1, int(slot_height * 0.92))
        padding = max(12, stroke_width * 2)
        overhead = padding * 2 + stroke_width * 2 + 6

        def estimate_total_height(main_size: int, ruby_size: int, has_ruby: bool) -> int:
            main_h = int(round(main_size * default_style.line_spacing))
            ruby_h = int(round(ruby_size * (1.0 + default_style.ruby_spacing))) if has_ruby and ruby_size > 0 else 0
            return main_h + ruby_h + overhead

        has_ruby = expects_ruby
        if not has_ruby:
            ruby_font_size = 0

        total_h = estimate_total_height(main_font_size, ruby_font_size, has_ruby)
        if total_h > safe_height and has_ruby:
            main_h_only = estimate_total_height(main_font_size, 0, False)
            remaining = safe_height - main_h_only
            if remaining <= 0:
                ruby_font_size = 0
            else:
                max_ruby = int(remaining / max(1.0, (1.0 + default_style.ruby_spacing)))
                ruby_font_size = max(0, min(ruby_font_size, max_ruby, main_font_size - 2))
                if ruby_font_size < 8:
                    ruby_font_size = 0
            total_h = estimate_total_height(main_font_size, ruby_font_size, ruby_font_size > 0)

        if total_h > safe_height:
            shrink = safe_height / float(total_h)
            main_font_size = max(12, int(round(main_font_size * shrink)))
            if has_ruby and ruby_font_size > 0:
                ruby_font_size = max(8, min(main_font_size - 2, int(round(ruby_font_size * shrink))))
            else:
                ruby_font_size = 0
            stroke_width = max(1, int(round(stroke_width * shrink)))
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
