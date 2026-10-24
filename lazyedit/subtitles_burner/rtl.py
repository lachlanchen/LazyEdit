"""Whole-line BiDi shaping for joining scripts; leave LTR ruby layout intact."""
from __future__ import annotations

import unicodedata

from PIL import Image, ImageDraw, features


def rtl_line(tokens):
    text = "".join(t.text for t in tokens if getattr(t, "token_type", None) != "speaker")
    if not any(unicodedata.bidirectional(c) in {"R", "AL"} for c in text):
        return None
    direction = next(("rtl" if unicodedata.bidirectional(c) in {"R", "AL"} else "ltr"
                      for c in text if unicodedata.bidirectional(c) in {"R", "AL", "L"}), "rtl")
    return text, direction


def _metrics(renderer, tokens):
    if not features.check("raqm"):
        raise RuntimeError("Right-to-left subtitles require Pillow with libraqm support")
    text, direction = rtl_line(tokens)
    stroke = max(0, int(renderer.style.stroke_width))
    draw = ImageDraw.Draw(Image.new("L", (1, 1)))
    bbox = draw.textbbox((0, 0), text, font=renderer.main_font,
                         direction=direction, stroke_width=stroke)
    ruby = " ".join(str(t.ruby) for t in tokens if getattr(t, "ruby", None))
    ruby_bbox = draw.textbbox((0, 0), ruby, font=renderer.ruby_font,
                              stroke_width=stroke) if ruby else (0, 0, 0, 0)
    gap = max(0, round(renderer.style.ruby_font_size * renderer.style.ruby_spacing)) if ruby else 0
    bold = 1 if getattr(renderer.style, "lazyedit_font_bold", False) else 0
    width = max(bbox[2] - bbox[0], ruby_bbox[2] - ruby_bbox[0]) + bold
    height = bbox[3] - bbox[1] + ruby_bbox[3] - ruby_bbox[1] + gap + bold
    return text, direction, ruby, bbox, ruby_bbox, gap, bold, width, height


def measure_rtl(renderer, tokens):
    return _metrics(renderer, tokens)[-2:]


def render_rtl(renderer, tokens, padding=16):
    text, direction, ruby, box, ruby_box, gap, bold, width, height = _metrics(renderer, tokens)
    padding = max(int(padding), int(renderer.style.stroke_width * 2))
    speaker = next((t for t in tokens if getattr(t, "token_type", None) == "speaker"), None)
    icon_size = max(1, int(renderer.style.main_font_size * 0.55))
    if speaker:
        padding = max(padding, icon_size + 6)
    image = Image.new("RGBA", (width + padding * 2, height + padding * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    ruby_height = ruby_box[3] - ruby_box[1]

    # Shaping the full logical line keeps clitics/ligatures joined across token
    # boundaries. A single line color is intentional until run-aware color
    # shaping is available; reversing independently drawn words is not BiDi.
    def paint(value, font, bounds, y, text_direction):
        x = padding + (width - (bounds[2] - bounds[0]) - bold) / 2 - bounds[0]
        y -= bounds[1]
        offsets = [(0, 0), (bold, 0), (0, bold), (bold, bold)] if bold else [(0, 0)]
        for dx, dy in offsets:
            draw.text((x + dx, y + dy), value, font=font,
                      direction=text_direction, fill=renderer.style.text_color,
                      stroke_width=int(renderer.style.stroke_width),
                      stroke_fill=renderer.style.stroke_color)

    if ruby:
        paint(ruby, renderer.ruby_font, ruby_box, padding, None)
    paint(text, renderer.main_font, box, padding + ruby_height + gap, direction)
    if speaker:
        icon = renderer._load_speaker_icon(icon_size)
        if icon is not None:
            icon = icon.convert("RGBA")
            tinted = Image.new("RGBA", icon.size, (33, 150, 243, 255))
            tinted.putalpha(icon.getchannel("A"))
            x = padding + width + 3 if direction == "rtl" else padding - icon_size - 3
            y = padding + ruby_height + gap + max(0, (box[3] - box[1] - icon_size) // 2)
            image.alpha_composite(tinted, (int(x), int(y)))
    return image
