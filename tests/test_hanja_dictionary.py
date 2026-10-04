from copy import deepcopy
from unittest.mock import Mock

import pytest

from lazyedit.hanja_dictionary import parse_dictionary, review_hints, normalize_selected_restorations
from lazyedit.subtitle_annotations import validate_annotations
from lazyedit.subtitle_translate import SubtitlesTranslator


def row(text, word=None, reading="hakgyo", language="ko"):
    return {"start": "00:00:00,000", "end": "00:00:02,000", language: text,
            "tokens": [{"surface": text, "word": word or text,
                        "reading": reading, "type": "noun"}]}


def request(translator, source, language="ko"):
    return translator._request_han_annotations(
        "Translate and annotate.", {}, "Translator", [source], language, 0,
        {"plain": [source]},
    )


@pytest.fixture
def dictionary(monkeypatch):
    entries = parse_dictionary([
        "# comment", "학:學:study", "학교:學校:school", "학교:學敎:teaching",
        "학생:學生:student", "감자:減資:capital reduction", "소고기:소고기:",
        "학교:學校:school", "invalid", "한글말:한글말:",
    ])
    monkeypatch.setattr("lazyedit.subtitle_translate.review_hints",
                        lambda items: review_hints(items, entries))
    monkeypatch.setattr('lazyedit.hanja_dictionary.load_dictionary', lambda: entries)
    return entries


def test_dictionary_is_candidates_only_and_does_not_change_text(dictionary):
    native = row("감자", reading="gamja")
    original = deepcopy(native)
    hints = review_hints([native], dictionary)
    assert hints[0]["candidates"] == [{"word": "減資", "meaning": "capital reduction"}]
    assert native == original
    assert "학" not in dictionary  # No character-by-character guessing.
    assert len(dictionary["학교"]) == 2
    assert review_hints([row("소고기", reading="sogogi")], dictionary) == []


def test_longest_match_finds_attached_particle_and_skips_correct_hanja(dictionary):
    assert review_hints([row("학교에서")], dictionary)[0]["surface"] == "학교"
    assert review_hints([row("학교", "學校", "학교")], dictionary) == []
    hints = review_hints([row("학교 " * 40)], dictionary)
    assert len(hints) == 12


def translator_with(*responses):
    translator = SubtitlesTranslator.__new__(SubtitlesTranslator)
    translator.get_filename = Mock(return_value="test.json")
    translator.send_request_with_json_schema = Mock(side_effect=deepcopy(responses))
    return translator


def test_correct_restoration_needs_only_one_call(dictionary):
    item = row("학교", "學校", "학교")
    translator = translator_with({"items": [item]})
    assert request(translator, item) == [item]
    assert translator.send_request_with_json_schema.call_count == 1


def test_dictionary_can_recover_missed_root_with_one_contextual_review(dictionary):
    missed = row("학교")
    fixed = row("학교", "學校", "학교")
    translator = translator_with({"items": [missed]}, {"items": [fixed]})
    assert request(translator, missed)[0]["tokens"][0]["word"] == "學校"
    calls = translator.send_request_with_json_schema.call_args_list
    assert len(calls) == 2
    assert "Dictionary candidates" in calls[1].kwargs["prompt"]
    assert "學校" in calls[1].kwargs["prompt"]
    assert "Locked clean text" in calls[1].kwargs["prompt"]


def test_native_homophone_can_remain_native_after_review(dictionary):
    item = row("감자", reading="gamja")
    translator = translator_with({"items": [item]}, {"items": [item]})
    assert request(translator, item) == [item]
    assert translator.send_request_with_json_schema.call_count == 2


def test_review_cannot_rewrite_translation(dictionary):
    translator = translator_with({"items": [row("학교")]}, {"items": [row("학생", "學生", "학생")]})
    with pytest.raises(ValueError, match="original native subtitle text"):
        request(translator, row("학교"))


@pytest.mark.parametrize("invalid", [
    {"items": None}, {"items": [None]}, {"items": []},
    {"items": [dict(row("학교"), tokens=[None])]},
    {"items": [dict(row("학교"), tokens=[{"surface": "학교", "word": 123}])]},
    {"items": [row("학교", reading="학교")]},
    {"items": [dict(row("학교"), start="00:00:01,000")]},
])
def test_bad_output_gets_one_repair_then_fails_visibly(dictionary, invalid):
    translator = translator_with(invalid, invalid)
    with pytest.raises(ValueError, match="after one repair"):
        request(translator, row("학교"))
    assert translator.send_request_with_json_schema.call_count == 2


def test_repair_succeeds_and_preserves_clean_translation(dictionary):
    invalid = row("학교", reading="학교")
    fixed = row("학교", "學校", "학교")
    translator = translator_with({"items": [invalid]}, {"items": [fixed]})
    result = translator._request_han_annotations("prompt", {}, "system", [row("학교")], "ko", 0, None)
    assert result == [fixed]
    assert '"ko": "학교"' in translator.send_request_with_json_schema.call_args.kwargs["prompt"]


@pytest.mark.parametrize("tokens", [None, [None], [
    {"surface": "학교", "word": "學校", "reading": "hakgyo", "type": "invalid"},
]])
def test_annotation_repair_still_receives_dictionary_candidates(dictionary, tokens):
    invalid = dict(row("학교"), tokens=tokens)
    fixed = row("학교", "學校", "학교")
    translator = translator_with({"items": [invalid]}, {"items": [fixed]})
    result = translator._request_han_annotations(
        "prompt", {}, "system", [row("학교")], "ko", 0, None,
    )
    assert result == [fixed]
    assert translator.send_request_with_json_schema.call_count == 2
    repair = translator.send_request_with_json_schema.call_args.kwargs["prompt"]
    assert "Validation error to fix" in repair
    assert "Dictionary candidates" in repair
    assert "學校" in repair and "teaching" in repair
    assert "NOT proof" in repair


def test_repair_dictionary_uses_locked_source_not_invalid_retranslation(dictionary):
    invalid = row("학생")
    fixed = row("학교", "學校", "학교")
    translator = translator_with({"items": [invalid]}, {"items": [fixed]})
    assert request(translator, row("학교")) == [fixed]
    repair = translator.send_request_with_json_schema.call_args.kwargs["prompt"]
    candidates = repair.split("Dictionary candidates below", 1)[1]
    assert '"surface": "학교"' in candidates
    assert '"surface": "학생"' not in candidates


def test_vietnamese_uses_same_validation_but_no_korean_dictionary(monkeypatch):
    lookup = Mock(side_effect=AssertionError("Vietnamese must not use Korean data"))
    monkeypatch.setattr("lazyedit.subtitle_translate.review_hints", lookup)
    item = row("học", "學", "học", "vi")
    translator = translator_with({"items": [item]})
    assert request(translator, item, "vi") == [item]
    lookup.assert_not_called()


def test_surface_coverage_rejects_empty_tokens():
    item = row("나", reading="na")
    item["tokens"].append({"surface": "", "word": "漢", "reading": "", "type": "noun"})
    with pytest.raises(ValueError, match="Empty annotation surface"):
        validate_annotations([item], [item], "ko")


def test_selected_hanja_ruby_is_repaired_without_another_model_call(dictionary):
    item = row('학교', '學校', 'hakgyo')
    translator = translator_with({'items': [item]})
    result = request(translator, item)
    assert result[0]['tokens'][0]['reading'] == '학교'
    assert translator.send_request_with_json_schema.call_count == 1


@pytest.mark.parametrize('word', ['祝賀해요', '祝賀'])
def test_selected_mixed_root_splits_losslessly_and_preserves_model_choice(word):
    item = row('축하해요', word, 'chukhahaeyo')
    original = deepcopy(item)
    normalize_selected_restorations([item], {'축하': [{'word': '祝賀'}]})
    assert [(t['surface'], t['word'], t['reading']) for t in item['tokens']] == [
        ('축하', '祝賀', '축하'), ('해요', '해요', 'haeyo')]
    validate_annotations([item], [original], 'ko', {'plain': [original]})
    wrong = deepcopy(original)
    normalize_selected_restorations([wrong], {'축하': [{'word': '祝夏'}]})
    assert [t['word'] for t in wrong['tokens']] == [word]  # Never substitute another Han spelling.
    if word == '祝賀해요':
        with pytest.raises(ValueError, match='Invalid Han restoration'):
            validate_annotations([wrong], [original], 'ko')


def test_missing_dictionary_falls_back_without_repeated_download(monkeypatch, tmp_path):
    import lazyedit.hanja_dictionary as dictionary_module
    monkeypatch.setattr(dictionary_module, "DEFAULT_PATH", tmp_path / "missing.txt")
    monkeypatch.delenv("LAZYEDIT_HANJA_DICTIONARY", raising=False)
    monkeypatch.setattr(dictionary_module, "_download_attempted", False)
    install = Mock(side_effect=OSError("offline"))
    monkeypatch.setattr(dictionary_module, "install_dictionary", install)
    assert dictionary_module.load_dictionary() == {}
    assert dictionary_module.load_dictionary() == {}
    assert install.call_count == 1


def test_failed_download_preserves_existing_dictionary(monkeypatch, tmp_path):
    import lazyedit.hanja_dictionary as dictionary_module
    path = tmp_path / "hanja.txt"
    path.write_text("existing data")
    response = Mock()
    response.read.return_value = b"corrupt download"
    context = Mock(__enter__=Mock(return_value=response), __exit__=Mock(return_value=False))
    monkeypatch.setattr(dictionary_module, "urlopen", Mock(return_value=context))
    with pytest.raises(ValueError, match="checksum"):
        dictionary_module.install_dictionary(path)
    assert path.read_text() == "existing data"
