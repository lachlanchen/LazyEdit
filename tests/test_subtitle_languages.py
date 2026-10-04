"""Exercise real target resolution/settings handlers without booting GPU services."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import tornado.web
import tornado.testing as testing

from lazyedit import subtitle_languages as targets
from lazyedit.languages import LANGUAGES
from lazyedit.plugins.languages import list_languages
from lazyedit.portrait_blurfill import DEFAULT_PORTRAIT_BLURFILL, sanitize_portrait_blurfill
from lazyedit.subtitle_translate import SubtitlesTranslator


def app_contract():
    source = Path(__file__).resolve().parents[1] / "app.py"
    names = {"_normalize_translation_language", "_sanitize_translation_languages",
             "_sanitize_burn_layout", "_burn_layout_for_languages", "_speaker_lang_key",
             "_parse_bool", "_parse_int_value", "_sanitize_hex_color",
             "_sanitize_publish_options", "_persistable_publish_options",
             "_burn_layout_payload_from_request", "_load_burn_layout_setting",
             "CorsMixin", "LanguagesHandler", "UISettingsHandler", "VideoTranslateHandler"}
    constants = {"DEFAULT_TRANSLATION_LANGUAGES", "DEFAULT_PUBLISH_OPTIONS", "DEFAULT_BURN_LAYOUT"}
    namespace = {**vars(targets), "tornado": tornado, "json": json,
                 "list_languages": list_languages,
                 "DEFAULT_PORTRAIT_BLURFILL": DEFAULT_PORTRAIT_BLURFILL,
                 "sanitize_portrait_blurfill": sanitize_portrait_blurfill}
    nodes = [n for n in ast.parse(source.read_text()).body if
             (isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names) or
             (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constants for t in n.targets))]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)
    return namespace


@pytest.mark.parametrize("value,canonical", [
    ("pt-br", "pt-BR"), ("SR-latn", "sr-Latn"), ("fil", "fil"), ("eo", "eo"),
    ("de", "de"), ("it", "it"), ("th", "th"), ("hi", "hi"), ("es-419", "es-419"),
    ("zh", "zh-Hant"), ("zh_cn", "zh-Hans"), ("zh-yue-hk", "yue"),
    ("Korean", "ko"), ("türkçe", "tr"), ("chinese_simplified", "zh-Hans"),
])
def test_shared_resolver(value, canonical):
    functions = app_contract()
    assert targets.require_subtitle_language(value) == canonical
    assert functions["_normalize_translation_language"](value) == canonical
    assert targets.subtitle_language(value)["code"] == canonical


@pytest.mark.parametrize("value", ["zz", "xx-XX", "../en", "en/ja", "en\\ja", "en\x00", "en-US-x-private", 1, {}, ""])
def test_unsafe_or_unknown_choices_never_become_defaults(value):
    with pytest.raises(targets.SubtitleLanguageError):
        app_contract()["_sanitize_translation_languages"](["ja", value])


def test_catalogue_is_not_an_asr_whitelist_and_capabilities_do_not_overclaim():
    original = dict(LANGUAGES)
    languages = {row["code"]: row for row in list_languages()}
    assert len(languages) >= 101
    assert {"de", "it", "th", "fil", "eo", "ko", "vi"} <= languages.keys()
    assert targets.subtitle_language("pt-BR")["name"] == "Portuguese (Brazil)"
    assert targets.subtitle_language("sr-Latn")["reading"] is None
    assert languages["ko"]["reading"] == "hanja"
    assert languages["vi"]["reading"] == "chu-han"
    assert languages["ar"]["rtl"] and all(row["requiresPreview"] for row in languages.values())
    assert "word order" in languages["ar"]["renderingWarning"]
    assert "renderingWarning" not in languages["en"]
    assert LANGUAGES == original and "eo" not in LANGUAGES


def test_order_slot_count_no_lift_and_empty_choice():
    f = app_contract()
    codes = f["_sanitize_translation_languages"](["ko", "zh", "ja", "en", "Korean"])
    assert codes == ["ko", "zh-Hant", "ja", "en"]
    layout = f["_burn_layout_for_languages"]({"rows": 4, "liftRatio": 0}, codes)
    assert [row["language"] for row in layout["slots"]] == ["en", "ja", "zh-Hant", "ko"]
    assert layout["rows"] == 4 and layout["liftRatio"] == 0
    assert f["_speaker_lang_key"]("pt-BR") == f["_speaker_lang_key"]("pt")
    assert f["_sanitize_translation_languages"](None) == ["ja", "en", "zh-Hant"]
    assert f["_sanitize_translation_languages"]([]) == []
    with pytest.raises(targets.SubtitleLanguageError):
        f["_sanitize_burn_layout"]({"slots": [{"slot": 1, "language": "../en"}]})


class TestLanguageHTTP(testing.AsyncHTTPTestCase):
    def runTest(self):
        # Tornado's wrapper expects this during pytest's unittest discovery.
        pass

    def get_app(self):
        self.settings = {"translation_languages": ["ko", "zh-Hant", "ja", "en"]}
        self.writes = []
        self.contract = app_contract()
        def save(key, value):
            self.writes.append(key)
            self.settings[key] = value
        self.contract["ldb"] = SimpleNamespace(ensure_schema=lambda: None,
            get_ui_preference=self.settings.get, set_ui_preference=save)
        return tornado.web.Application([
            (r"/api/languages", self.contract["LanguagesHandler"]),
            (r"/api/ui-settings/([a-z_]+)", self.contract["UISettingsHandler"]),
            (r"/api/videos/(\d+)/translate", self.contract["VideoTranslateHandler"]),
        ])

    def post(self, path, data):
        response = self.fetch(path, method="POST", body=json.dumps(data),
                              headers={"Content-Type": "application/json"})
        return response.code, json.loads(response.body)

    def test_round_trip_and_rejected_settings_are_atomic(self):
        codes = ["pt-BR", "sr-Latn", "fil", "eo"]
        status, payload = self.post("/api/languages", {"languages": codes})
        assert status == 200 and payload["codes"] == codes
        assert self.writes == []  # Validation does not persist a registration.
        assert self.post("/api/ui-settings/translation_languages", codes)[0] == 200
        assert json.loads(self.fetch("/api/ui-settings/translation_languages").body)["value"] == codes
        previous_writes = list(self.writes)
        status, error = self.post("/api/ui-settings/translation_languages", ["ja", "zz"])
        assert status == 400 and error["code"] == "unsupported_subtitle_language"
        status, error = self.post("/api/ui-settings/publish_options", {"translationLanguages": ["en", "zz"]})
        assert status == 400 and self.settings["translation_languages"] == codes
        assert self.writes == previous_writes
        assert self.post("/api/languages", {"languages": None})[0] == 400
        assert self.post("/api/ui-settings/translation_languages", None)[0] == 400
        assert self.post("/api/ui-settings/publish_options", {"translationLanguages": None})[0] == 400
        assert self.post("/api/ui-settings/publish_options", {"translationLanguages": ["en"], "translation_languages": ["eo"]})[0] == 400
        assert self.post("/api/ui-settings/translation_languages", [])[0] == 200
        assert json.loads(self.fetch("/api/ui-settings/translation_languages").body)["value"] == []

    def test_explicit_single_language_errors_cannot_start_japanese_translation(self):
        for options in ({"language": ""}, {"language": None}, {"language": 0},
                        {"lang": "zz"}, {"language": "en", "lang": "eo"}):
            status, reply = self.post("/api/videos/1/translate", options)
            assert status == 400 and reply["code"] == "unsupported_subtitle_language"
        assert self.post("/api/videos/1/translate", ["en"])[0] == 400
        assert self.writes == []


@pytest.mark.parametrize("target,text", [
    ("pt-BR", "Um livro"), ("sr-Latn", "Knjiga"), ("fil", "Aklat"),
    ("eo", "Libro"), ("th", "หนังสือ"), ("hi", "किताब"),
])
def test_generic_translation_routes_exact_language_key_and_grammar(tmp_path, target, text):
    translator = SubtitlesTranslator.__new__(SubtitlesTranslator)
    source = {"start": "00:00:00,000", "end": "00:00:02,000", "text": "a book", "language": "en"}
    translated = {"start": source["start"], "end": source["end"], target: text,
                  "tokens": [{"surface": text, "word": text, "reading": "", "type": "noun"}]}
    translator.load_subtitles_from_json = Mock(return_value=[source])
    translator.get_filename = Mock(return_value=str(tmp_path / "reply.json"))
    translator.send_request_with_json_schema = Mock(return_value={"items": [translated]})
    plain, annotated = translator.process_specified_language_translation(target)
    assert plain == [{"start": source["start"], "end": source["end"], target: text}]
    assert annotated[0]["tokens"][0]["type"] == "noun"
    request = translator.send_request_with_json_schema.call_args.kwargs
    assert target in request["json_schema"]["properties"]["items"]["items"]["required"]
    assert targets.subtitle_language(target)["name"] in request["prompt"]
    with pytest.raises(targets.SubtitleLanguageError):
        translator.process_specified_language_translation("../en")
    assert translator.send_request_with_json_schema.call_count == 1
