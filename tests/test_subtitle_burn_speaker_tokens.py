import json
import tempfile
import unittest
from pathlib import Path

from lazyedit.subtitles_burner.burner import _load_burner_module


def _palette(name: str) -> dict:
    root = Path(__file__).resolve().parents[1]
    path = root / "lazyedit" / "templates" / "grammar_palettes" / name
    return json.loads(path.read_text(encoding="utf-8"))


class SubtitleBurnTokenTests(unittest.TestCase):
    def _write_payload(self, name: str, payload: list[dict]) -> str:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / name
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def test_speaker_only_tokens_keep_caption_text(self):
        _load_burner_module()
        import subtitles_burner.burner as burner_mod

        payload = [
            {
                "start": "00:00:00,000",
                "end": "00:00:02,000",
                "ja": "写真大丈夫?",
                "ruby": "写真[しゃしん]大丈夫[だいじょうぶ]?",
                "tokens": [{"text": "🔊", "type": "speaker"}],
            }
        ]

        segments = burner_mod.load_segments_from_json(
            self._write_payload("ja_speaker_only.json", payload),
            text_key="ja",
            ruby_key="ruby",
            auto_ruby=True,
            strip_kana=True,
            kana_romaji=True,
        )

        self.assertEqual(len(segments), 1)
        rendered_text = "".join(token.text for token in segments[0].tokens)
        self.assertIn("🔊", rendered_text)
        self.assertIn("写真", rendered_text)

    def test_plain_japanese_line_gets_grammar_colored_tokens(self):
        _load_burner_module()
        import subtitles_burner.burner as burner_mod

        payload = [
            {
                "start": "00:00:00,000",
                "end": "00:00:02,000",
                "ja": "孔子は魯に帰った。",
            }
        ]

        segments = burner_mod.load_segments_from_json(
            self._write_payload("ja_plain.json", payload),
            text_key="ja",
            palette=_palette("ja.json"),
        )

        tokens = segments[0].tokens
        self.assertEqual("".join(token.text for token in tokens), "孔子は魯に帰った。")
        self.assertEqual(
            [token.text for token in tokens if token.text.strip()],
            ["孔子", "は", "魯", "に", "帰った", "。"],
        )
        self.assertTrue(any(token.text == "は" and token.token_type == "particle_wa" and token.color for token in tokens))
        self.assertTrue(any(token.text == "帰った" and token.token_type == "verb" and token.color for token in tokens))

    def test_word_reading_tokens_are_preserved_and_colored(self):
        _load_burner_module()
        import subtitles_burner.burner as burner_mod

        payload = [
            {
                "start": "00:00:00,000",
                "end": "00:00:02,000",
                "ja": "孔子は魯に帰った。",
                "tokens": [
                    {"word": "孔子", "reading": "こうし", "type": "noun"},
                    {"word": "は", "reading": "は", "type": "particle_wa"},
                    {"word": "魯", "reading": "ろ", "type": "noun"},
                    {"word": "に", "reading": "に", "type": "particle_ni"},
                    {"word": "帰った", "reading": "かえった", "type": "verb"},
                    {"word": "。", "reading": "。", "type": "punctuation"},
                ],
            }
        ]

        segments = burner_mod.load_segments_from_json(
            self._write_payload("ja_word_tokens.json", payload),
            text_key="ja",
            palette=_palette("ja.json"),
        )

        token_map = {token.text: token for token in segments[0].tokens}
        self.assertEqual(token_map["孔子"].ruby, "こうし")
        self.assertEqual(token_map["孔子"].token_type, "noun")
        self.assertTrue(token_map["孔子"].color)
        self.assertEqual(token_map["は"].token_type, "particle_wa")
        self.assertTrue(token_map["は"].color)

    def test_plain_chinese_line_gets_colored_character_tokens(self):
        _load_burner_module()
        import subtitles_burner.burner as burner_mod

        payload = [
            {
                "start": "00:00:00,000",
                "end": "00:00:02,000",
                "zh": "我想去深圳。",
            }
        ]

        segments = burner_mod.load_segments_from_json(
            self._write_payload("zh_plain.json", payload),
            text_key="zh",
            palette=_palette("zh-Hans.json"),
        )

        tokens = segments[0].tokens
        self.assertEqual("".join(token.text for token in tokens), "我想去深圳。")
        self.assertEqual(
            [token.text for token in tokens if token.text.strip()],
            ["我", "想", "去", "深", "圳", "。"],
        )
        self.assertTrue(any(token.text == "我" and token.token_type == "pronoun" and token.color for token in tokens))
        self.assertTrue(any(token.text == "想" and token.token_type == "verb" and token.color for token in tokens))


if __name__ == "__main__":
    unittest.main()
