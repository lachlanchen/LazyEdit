import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import app
from lazyedit.openai_request_json import OpenAIRequestJSONBase


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

    def test_structured_request_falls_back_from_deepseek_to_openai(self):
        deepseek_client = Mock()
        deepseek_client.chat.completions.create.side_effect = RuntimeError(
            "402 Insufficient Balance"
        )
        openai_client = Mock()
        openai_client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"answer": "ok"}'))]
        )
        schema = {
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": ["answer"],
            "additionalProperties": False,
        }

        with tempfile.TemporaryDirectory() as cache_dir, patch.dict(
            "os.environ",
            {
                "DEEPSEEK_API_KEY": "test-deepseek",
                "OPENAI_API_KEY": "test-openai",
                "LAZYEDIT_OPENAI_FALLBACK_MODEL": "gpt-4o-mini",
            },
            clear=False,
        ), patch(
            "lazyedit.openai_request_json.OpenAI",
            side_effect=[deepseek_client, openai_client],
        ):
            client = OpenAIRequestJSONBase(
                api_provider="deepseek",
                model="deepseek-chat",
                max_retries=1,
                use_cache=False,
                cache_dir=cache_dir,
            )
            result = client.send_request_with_json_schema(
                "test prompt",
                schema,
                schema_name="test_response",
            )

        self.assertEqual(result, {"answer": "ok"})
        self.assertEqual(client.api_provider, "openai")
        self.assertEqual(client.model, "gpt-4o-mini")
        deepseek_client.chat.completions.create.assert_called_once()
        openai_client.chat.completions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
