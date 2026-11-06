"""Exercise the burn endpoint without starting databases, models or encoders."""
import ast
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock

import tornado.web
import tornado.testing as testing


class EmptyCorrectedBurnTests(testing.AsyncHTTPTestCase):
    def runTest(self):
        pass

    def get_app(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.transcript = self.root / "polished.json"
        self.db = MagicMock()
        self.db.get_cursor.return_value.__enter__.return_value.fetchone.return_value = (
            str(self.root / "source.mp4"),
        )
        self.db.add_subtitle_burn.return_value = 1
        self.db.get_latest_transcription.return_value = None
        self.db.get_latest_subtitle_translation.return_value = None
        self.executor = Mock()
        namespace = {
            "os": os, "json": json, "tornado": tornado,
            "ldb": self.db, "BURN_EXECUTOR": self.executor,
            "DEFAULT_PUBLISH_OPTIONS": {"usePolishedSubtitles": True},
            "DEFAULT_BURN_LAYOUT": {}, "DEFAULT_LOGO_SETTINGS": {},
            "SubtitleLanguageError": type("SubtitleLanguageError", (ValueError,), {}),
            "_sanitize_burn_layout": lambda value: value,
            "_sanitize_logo_settings": lambda value: value,
            "sanitize_portrait_blurfill": lambda value: value or {},
            "is_portrait_blurfill_enabled": lambda value: bool(value.get("enabled")),
            "_ensure_local_video_path": lambda video_id, path: (path, None),
            "_publication_session_dir": lambda *args, **kwargs: str(self.root),
            "_get_latest_subtitle_burn_with_recovery": lambda *args: None,
            "_ensure_global_polished_subtitles": Mock(),
            "find_latest_transcription_outputs": lambda *args, **kwargs: (str(self.transcript), None),
            "_get_latest_global_transcription": lambda *args: None,
            "_normalize_translation_language": lambda value: value,
            "_track_active_burn_future": Mock(),
        }
        source = Path(os.environ.get("LAZYEDIT_BURN_CONTRACT_SOURCE", Path(__file__).resolve().parents[1] / "app.py"))
        names = {"_parse_bool", "_parse_int_value", "_load_subtitle_payload",
                 "_logo_overlay_enabled", "CorsMixin", "VideoSubtitleBurnHandler"}
        nodes = [n for n in ast.parse(source.read_text()).body
                 if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)
        return tornado.web.Application([(r"/burn/(\d+)", namespace["VideoSubtitleBurnHandler"])])

    def burn(self, texts, logo=True):
        cues = [{"start": "00:00:00,000", "end": "00:00:03,920", "lang": "zh", "text": text}
                for text in texts]
        self.transcript.write_text(json.dumps(cues))
        request = {"burnSubtitles": True, "usePolishedSubtitles": True,
                   "layout": {"slots": [{"slot": 1, "language": "en"}]},
                   "logo": {"enabled": logo, "logoPath": "existing-logo.png"}}
        response = self.fetch("/burn/1", method="POST", body=json.dumps(request))
        assert json.loads(self.transcript.read_text()) == cues  # Audit timing/text remains intact.
        return response.code, json.loads(response.body)

    def test_removed_speech_keeps_logo_and_skips_translation_lookup(self):
        for texts in ([], [""], [" \n\t", None]):
            with self.subTest(texts=texts):
                status, body = self.burn(texts)
                self.assertEqual(status, 200)
                self.assertEqual(body["status"], "processing")
                self.assertEqual(body["detail"], "processed output; no subtitles to burn")
        self.db.get_latest_subtitle_translation.assert_not_called()
        self.assertEqual(self.executor.submit.call_count, 3)
        config = self.db.add_subtitle_burn.call_args.args[3]
        self.assertFalse(config["burnSubtitles"])
        self.assertTrue(config["logoOnly"])

    def test_empty_cues_without_logo_are_skipped(self):
        status, body = self.burn([""], logo=False)
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "skipped")
        self.executor.submit.assert_not_called()

    def test_real_speech_still_requires_translation(self):
        status, body = self.burn(["", "你好"])
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "translation missing for en")
        self.executor.submit.assert_not_called()
