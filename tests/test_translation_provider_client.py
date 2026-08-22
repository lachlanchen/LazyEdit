import unittest
from unittest.mock import patch

import app


class TranslationProviderClientTests(unittest.TestCase):
    def test_turkish_is_a_supported_translation_target(self):
        self.assertEqual(app._normalize_translation_language("tr"), "tr")
        self.assertEqual(app._normalize_translation_language("Turkish"), "tr")
        self.assertEqual(app._sanitize_translation_languages(["en", "tr"]), ["en", "tr"])
        self.assertEqual(app._normalize_translation_language("it"), "it")
        self.assertEqual(app._normalize_translation_language("Italian"), "it")
        self.assertEqual(
            app._sanitize_translation_languages(["it", "zh-Hant", "ja", "en"]),
            ["it", "zh-Hant", "ja", "en"],
        )

    def test_deepseek_translation_does_not_construct_openai_client(self):
        with patch.dict("os.environ", {"LAZYEDIT_TRANSLATION_PROVIDER": "deepseek"}), patch.object(
            app, "OpenAI", side_effect=AssertionError("OpenAI client should not be constructed")
        ):
            self.assertIsNone(app._translation_openai_client())

    def test_openai_translation_constructs_openai_client(self):
        sentinel = object()
        with patch.dict("os.environ", {"LAZYEDIT_TRANSLATION_PROVIDER": "openai"}), patch.object(
            app, "OpenAI", return_value=sentinel
        ) as constructor:
            self.assertIs(app._translation_openai_client(), sentinel)
            constructor.assert_called_once_with()

    def test_deepseek_metadata_does_not_construct_openai_client(self):
        with patch.dict("os.environ", {"LAZYEDIT_AI_PROVIDER": "deepseek"}), patch.object(
            app, "OpenAI", side_effect=AssertionError("OpenAI client should not be constructed")
        ):
            self.assertIsNone(app._metadata_openai_client())

    def test_openai_metadata_constructs_openai_client(self):
        sentinel = object()
        with patch.dict("os.environ", {"LAZYEDIT_AI_PROVIDER": "openai"}), patch.object(
            app, "OpenAI", return_value=sentinel
        ) as constructor:
            self.assertIs(app._metadata_openai_client(), sentinel)
            constructor.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
