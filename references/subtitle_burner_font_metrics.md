# Subtitle burner: font metrics fix

## Issue
Some lines (notably French with descenders like "vous") were being cut off at the bottom
when burned into the 4-slot layout. Most other lines looked fine, so the clipping
seemed inconsistent.

## Root cause
The renderer measured text height using the bounding box of the glyphs, which can
ignore font descenders. That meant the computed image height was too small, so the
bottom of letters with descenders was clipped during compositing.

## Fix
In `furigana/subtitles_burner/burner.py`, we now factor in full font metrics when
building layout:

- `main_h` and `ruby_h` are clamped to `ascent + descent` from `ImageFont.getmetrics()`.
- This ensures every rendered line has enough vertical space for descenders and stroke.

Result: subtitle lines render fully without bottom truncation, regardless of language.
