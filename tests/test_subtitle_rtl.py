import unittest
from types import SimpleNamespace

from PIL import Image, ImageChops, ImageDraw, ImageFont, features

from lazyedit.subtitles_burner.rtl import measure_rtl, render_rtl, rtl_line


def token(text, ruby=None, kind=None):
    return SimpleNamespace(text=text, ruby=ruby, token_type=kind)


@unittest.skipUnless(features.check("raqm"), "Pillow libraqm unavailable")
class RtlSubtitleTests(unittest.TestCase):
    def setUp(self):
        font = ImageFont.truetype("DejaVuSans.ttf", 48)
        self.renderer = SimpleNamespace(
            main_font=font, ruby_font=ImageFont.truetype("DejaVuSans.ttf", 24),
            style=SimpleNamespace(stroke_width=2, text_color=(255, 255, 255),
                                  stroke_color=(0, 0, 0), ruby_font_size=24,
                                  ruby_spacing=0.2, main_font_size=48),
            _load_speaker_icon=lambda size: Image.new("RGBA", (size, size), "white"),
        )

    def test_ltr_rows_do_not_enter_rtl_path(self):
        for text in ["Hello!", "こんにちは", "灯没了，人都在。"]:
            self.assertIsNone(rtl_line([token(text)]))

    def test_arabic_mixed_digits_and_latin_keep_logical_input(self):
        text = "آيا 123 (Aya)، تعالي!"
        self.assertEqual(rtl_line([token(text)]), (text, "rtl"))
        self.assertEqual(rtl_line([token("Aya: "), token("مرحبا")])[1], "ltr")

    def test_split_joining_tokens_render_identically_to_whole_line(self):
        pieces = [token("و"), token("الناس"), token(" كلهم هنا.")]
        whole = [token("والناس كلهم هنا.")]
        a, b = render_rtl(self.renderer, pieces), render_rtl(self.renderer, whole)
        self.assertEqual(a.size, b.size)
        self.assertIsNone(ImageChops.difference(a, b).getbbox())
        width, height = measure_rtl(self.renderer, pieces)
        self.assertEqual(a.size, (width + 32, height + 32))

    def test_output_matches_full_line_raqm_reference(self):
        text = "لا تفتحوا الباب، إنهم خلفكم!"
        actual = render_rtl(self.renderer, [token(part) for part in ["لا ", "تفتحوا ", "الباب، ", "إنهم ", "خلفكم!"]])
        expected = Image.new("RGBA", actual.size)
        draw = ImageDraw.Draw(expected)
        box = draw.textbbox((0, 0), text, font=self.renderer.main_font, direction="rtl", stroke_width=2)
        draw.text((16 - box[0], 16 - box[1]), text, font=self.renderer.main_font,
                  direction="rtl", fill="white", stroke_width=2, stroke_fill="black")
        self.assertIsNone(ImageChops.difference(actual, expected).getbbox())

    def test_speaker_and_transliteration_fit_inside_image(self):
        tokens = [token("speaker", kind="speaker"), token("مرحبا", ruby="marhaban")]
        image = render_rtl(self.renderer, tokens)
        x0, y0, x1, y1 = image.getbbox()
        self.assertGreater(x0, 0)
        self.assertGreater(y0, 0)
        self.assertLess(x1, image.width)
        self.assertLess(y1, image.height)

    def test_lazyedit_renderer_uses_full_line_shaping(self):
        from lazyedit.subtitles_burner.burner import _load_burner_module
        _load_burner_module()
        from subtitles_burner.burner import RubyRenderer, RubyToken, TextStyle

        renderer = RubyRenderer(TextStyle())
        tokens = [RubyToken(text="و"), RubyToken(text="الناس "), RubyToken(text="كلهم هنا.")]
        actual = renderer.render_tokens(tokens)
        expected = render_rtl(renderer, tokens)
        self.assertEqual(actual.size, expected.size)
        self.assertIsNone(ImageChops.difference(actual, expected).getbbox())
        self.assertEqual(renderer.measure_tokens(tokens), measure_rtl(renderer, tokens))


if __name__ == "__main__":
    unittest.main()
