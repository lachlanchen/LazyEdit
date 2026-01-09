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
                base = max(2, min(base, 16))
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

    # LazyEdit patch: upstream auto-splitting uses a 1.05 slack factor based on
    # measured text width. With our dynamic padding/styling this can bypass
    # splitting for near-limit lines, which then get scaled down at render time.
    # Prefer time-splitting segments so font size stays consistent as fontScale
    # changes.
    try:
        if getattr(burner_mod, "_lazyedit_strict_split_patch", False) is not True and hasattr(burner_mod, "_auto_split_segments_for_slot"):
            SubtitleSegment = burner_mod.SubtitleSegment
            RubyRenderer = burner_mod.RubyRenderer
            _split_text_tokens_for_fit = burner_mod._split_text_tokens_for_fit
            _tokens_fit_width = burner_mod._tokens_fit_width
            _chunk_tokens_to_fit_width = burner_mod._chunk_tokens_to_fit_width
            _split_segment_timing = burner_mod._split_segment_timing
            _segment_text_from_tokens = burner_mod._segment_text_from_tokens
            RENDER_PADDING = int(getattr(burner_mod, "RENDER_PADDING", 16))

            def _auto_split_segments_for_slot_strict(segments, slot, style):  # type: ignore[no-redef]
                renderer = RubyRenderer(style)
                split_segments = []
                for segment in segments:
                    if not getattr(segment, "tokens", None):
                        continue
                    tokens = segment.tokens
                    width, height = renderer.measure_tokens(tokens)
                    # Never split vertically-overflowing segments here; let the upstream
                    # chunking logic handle them conservatively.
                    if height > slot.height:
                        split_segments.append(segment)
                        continue
                    # If the rendered width plus padding does not fit, split.
                    if (width + RENDER_PADDING * 2) <= slot.width:
                        split_segments.append(segment)
                        continue

                    split_tokens = tokens
                    if len(tokens) == 1 and not getattr(tokens[0], "ruby", None):
                        text = getattr(tokens[0], "text", "") or getattr(segment, "text", "") or ""
                        split_tokens = _split_text_tokens_for_fit(text)

                    if not _tokens_fit_width(split_tokens, slot, renderer):
                        chunks = _chunk_tokens_to_fit_width(split_tokens, slot, renderer)
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

            burner_mod._auto_split_segments_for_slot = _auto_split_segments_for_slot_strict
            burner_mod._lazyedit_strict_split_patch = True
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
                        icon_size = max(1, int(self.style.main_font_size * 0.9))
                        main_w = main_h = icon_size
                        ruby_w = ruby_h = 0
                        prefix_w = core_w = suffix_w = 0
                        column_w = main_w
                        total_width += column_w
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
                    max_w = max(1, slot.width - 16)
                    scale = min(1.0, max_w / w if w else 1.0)
                    if scale < 1.0:
                        new_w = max(1, int(w * scale))
                        new_h = max(1, int(h * scale))
                        overlay_img = overlay_img.resize((new_w, new_h), burner_mod.Image.LANCZOS)
                        h, w = new_h, new_w
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

        main_font_size = max(12, int(round(base_main * scale)))
        ruby_font_size = max(8, int(round(base_ruby * scale)))
        stroke_width = max(1, int(round(default_style.stroke_width * (main_font_size / default_style.main_font_size))))

        # Prevent overlap between stacked slots by ensuring rendered subtitles fit
        # inside each slot's height. Main font size should be independent of ruby
        # toggles; we size main from a main-only render, then size ruby
        # proportionally and shrink ruby first if needed.
        virtual_slot_height = max(1, int(slot_height + max(0, extra_top) + max(0, extra_bottom)))
        safe_height = virtual_slot_height
        padding = max(max(2, min(int(round(slot_height * 0.10)), 16)), stroke_width * 2)
        is_cjk = (slot.language or "").lower() in {"ja", "zh", "zh-hant", "zh-hans", "yue", "ko"}
        sample_text = "漢字" if is_cjk else "Sample"
        sample_ruby = "かんじ" if is_cjk else "sam-pəl"

        def render_height(main_size: int, ruby_size: int, stroke: int, pad: int, include_ruby: bool) -> int:
            style = TextStyle(
                main_font_size=main_size,
                ruby_font_size=ruby_size,
                stroke_width=stroke,
                ruby_spacing=ruby_spacing,
            )
            renderer = RubyRenderer(style)
            tokens = [RubyToken(text=sample_text)]
            if include_ruby and ruby_size > 0:
                tokens = [RubyToken(text=sample_text, ruby=sample_ruby)]
            img = renderer.render_tokens(tokens, padding=pad)
            return int(img.size[1])

        has_ruby = expects_ruby
        ruby_ratio = 0.6 if has_ruby else 0.0

        # 1) Fit main-only height to slot (grow or shrink as needed).
        def _main_only_height() -> int:
            return render_height(main_font_size, 0, stroke_width, padding, include_ruby=False)

        try:
            main_only_h = _main_only_height()
        except Exception:
            main_only_h = 0

        if main_only_h > 0:
            # Make `font_scale` meaningful: at scale=1 we don't fully "max out"
            # the slot; increasing scale fills more of the slot height.
            # This keeps main readability consistent and allows long lines to be
            # split into additional timestamped segments instead of shrinking.
            scale_norm = (scale - 0.6) / (2.5 - 0.6)
            scale_norm = min(max(scale_norm, 0.0), 1.0)
            target_frac = 0.78 + 0.22 * scale_norm
            target = max(1, int(round(safe_height * target_frac)))
            if main_only_h < target:
                grow = target / float(main_only_h)
                main_font_size = max(12, int(round(main_font_size * grow)))
                stroke_width = max(1, int(round(stroke_width * grow)))
                padding = max(max(2, min(int(round(slot_height * 0.10)), 16)), stroke_width * 2)
            else:
                # If the main-only render is too tall, shrink to fit within target.
                if main_only_h > target:
                    shrink = target / float(main_only_h)
                    main_font_size = max(12, int(round(main_font_size * shrink)))
                    stroke_width = max(1, int(round(stroke_width * shrink)))
                    padding = max(max(2, min(int(round(slot_height * 0.10)), 16)), stroke_width * 2)

        # 2) Set ruby proportionally to main, but don't let ruby change main size.
        if has_ruby:
            ruby_font_size = max(8, min(main_font_size - 2, int(round(main_font_size * ruby_ratio))))
        else:
            ruby_font_size = 0
        style = TextStyle(
            main_font_size=main_font_size,
            ruby_font_size=ruby_font_size,
            stroke_width=stroke_width,
            ruby_spacing=ruby_spacing,
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
