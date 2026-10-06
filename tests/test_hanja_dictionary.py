from copy import deepcopy
import json
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from lazyedit.hanja_dictionary import parse_dictionary, review_hints, normalize_selected_restorations
from lazyedit.subtitle_annotations import annotation_contract, validate_annotations
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


def test_partial_restoration_does_not_trigger_completeness_review(dictionary):
    missed = row("학교")
    translator = translator_with({"items": [missed]})
    assert request(translator, missed) == [missed]
    assert translator.send_request_with_json_schema.call_count == 1


def test_native_homophone_remains_native_without_review(dictionary):
    item = row("감자", reading="gamja")
    translator = translator_with({"items": [item]}, {"items": [item]})
    assert request(translator, item) == [item]
    assert translator.send_request_with_json_schema.call_count == 1


def test_review_cannot_rewrite_translation(dictionary):
    translator = translator_with({"items": [dict(row("학교"), tokens=[])]},
                                 {"items": [row("학생", "學生", "학생")]})
    with pytest.raises(ValueError, match="original native subtitle text"):
        request(translator, row("학교"))


@pytest.mark.parametrize("invalid", [
    {"items": None}, {"items": [None]}, {"items": []},
    {"items": [dict(row("학교"), tokens=[None])]},
    {"items": [dict(row("학교"), tokens=[{"surface": "학교", "word": 123}])]},
    {"items": [dict(row("학교"), start="00:00:01,000")]},
])
def test_bad_output_gets_one_repair_then_fails_visibly(dictionary, invalid):
    translator = translator_with(invalid, invalid)
    with pytest.raises(ValueError, match="after one repair"):
        request(translator, row("학교"))
    assert translator.send_request_with_json_schema.call_count == 2


def test_repair_succeeds_and_preserves_clean_translation(dictionary):
    invalid = dict(row("학교"), tokens=[])
    fixed = row("학교", "學校", "학교")
    translator = translator_with({"items": [invalid]}, {"items": [fixed]})
    result = translator._request_han_annotations("prompt", {}, "system", [row("학교")], "ko", 0, None)
    assert result == [fixed]
    assert '"ko": "학교"' in translator.send_request_with_json_schema.call_args.kwargs["prompt"]


@pytest.mark.parametrize("tokens", [None, [None], [
    {"surface": "학교", "word": "學校", "reading": "hakgyo", "type": "invalid"},
]])
def test_annotation_repair_focuses_on_error_not_exhaustive_dictionary(dictionary, tokens):
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
    assert "Dictionary candidates" not in repair
    assert "Locked clean text" in repair


def test_repair_uses_locked_source_not_invalid_retranslation(dictionary):
    invalid = row("학생")
    fixed = row("학교", "學校", "학교")
    translator = translator_with({"items": [invalid]}, {"items": [fixed]})
    assert request(translator, row("학교")) == [fixed]
    repair = translator.send_request_with_json_schema.call_args.kwargs["prompt"]
    locked = repair.split("Locked clean text: ", 1)[1].split("\nPrevious JSON:", 1)[0]
    assert '"ko": "학교"' in locked
    assert '"ko": "학생"' not in locked


def test_vietnamese_uses_same_validation_but_no_korean_dictionary(monkeypatch):
    lookup = Mock(side_effect=AssertionError("Vietnamese must not use Korean data"))
    monkeypatch.setattr("lazyedit.hanja_dictionary.load_dictionary", lookup)
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


def test_selected_hanja_with_native_prefix_and_particle_is_lossless():
    original = row('콧수염이', '콧鬚髥이', 'kotsuyeomi')
    item = deepcopy(original)
    normalize_selected_restorations([item], {'수염': [{'word': '鬚髥'}]})
    assert [(t['surface'], t['word'], t['reading']) for t in item['tokens']] == [
        ('콧', '콧', 'kot'), ('수염', '鬚髥', '수염'), ('이', '이', 'i')]
    validate_annotations([item], [original], 'ko', {'plain': [original]})
    wrong = deepcopy(original)
    normalize_selected_restorations([wrong], {'수염': [{'word': '水鹽'}]})
    assert wrong == original


def test_native_romanization_preserves_name_without_forcing_hanja():
    item = row('그랜빌섬', reading='geuraenbilleom')
    normalize_selected_restorations([item], {})
    assert item['tokens'][0]['reading'] == 'geuraenbilseom'
    assert item['tokens'][0]['word'] == item['ko'] == '그랜빌섬'


@pytest.mark.parametrize('reading', [None, '', '학교', 'wrong'])
def test_pronunciation_is_completed_locally_in_one_call(dictionary, reading):
    item = row('학교', reading=reading)
    if reading is None:
        del item['tokens'][0]['reading']
    translator = translator_with({'items': [item]})
    result = request(translator, item)
    assert result[0]['tokens'][0]['reading'] == 'hakgyo'
    assert translator.send_request_with_json_schema.call_count == 1


def test_compact_schema_only_omits_korean_readings():
    base = {'properties': {'items': {'items': {'properties': {}, 'required': []}}}}
    for lang in ['ko', 'vi', 'en']:
        schema, prompt = annotation_contract(base, lang)
        fields = schema['properties']['items']['items']['properties']['tokens']['items']
        assert ('reading' in fields['required']) == (lang != 'ko')
        assert ('reading' in fields['properties']) == (lang != 'ko')
        if lang == 'ko':
            assert 'partial restoration is enough' in prompt
            assert len(prompt.split()) < 140
    assert base['properties']['items']['items']['properties'] == {}


def test_missing_readings_mixed_names_spaces_and_numbers_are_local():
    item = row('AI와 그랜빌섬 2개!')
    item['tokens'] = [dict(surface=s, word=s, type='other')
                      for s in ['AI와', ' ', '그랜빌섬', ' ', '2개', '!']]
    normalize_selected_restorations([item], {})
    assert [t['reading'] for t in item['tokens']] == ['AIwa', '', 'geuraenbilseom', '', '2gae', '']
    validate_annotations([item], [item], 'ko')


def test_native_only_cue_does_not_load_dictionary(monkeypatch):
    lookup = Mock(side_effect=AssertionError('No dictionary needed'))
    monkeypatch.setattr('lazyedit.hanja_dictionary.load_dictionary', lookup)
    item = row('먹어요')
    normalize_selected_restorations([item])
    assert item['tokens'][0]['reading'] == 'meogeoyo'
    lookup.assert_not_called()


@pytest.mark.parametrize('surface,lemma,reading', [
    ('합니다', '하다', 'hamnida'), ('먹어요', '먹다', 'meogeoyo'),
])
def test_native_lemma_is_replaced_with_exact_surface_locally(surface, lemma, reading):
    item = row(surface, lemma)
    normalize_selected_restorations([item], {})
    assert item['tokens'][0]['word'] == surface
    assert item['tokens'][0]['reading'] == reading
    validate_annotations([item], [item], 'ko')


def test_omitted_affixes_around_selected_root_are_preserved():
    item = row('콧수염이', '鬚髥')
    normalize_selected_restorations([item], {'수염': [{'word': '鬚髥'}]})
    assert [t['word'] for t in item['tokens']] == ['콧', '鬚髥', '이']
    assert ''.join(t['surface'] for t in item['tokens']) == item['ko']
    validate_annotations([item], [item], 'ko')


def test_cues_run_independently_in_parallel_with_context_and_stable_order(dictionary):
    sources = [dict(start=f'00:00:0{i * 2},000', end=f'00:00:0{i * 2 + 2},000',
                    text=text, lang='ko')
               for i, text in enumerate(['학교', '감자', '그랜빌섬', '건배'])]
    translator = translator_with()
    translator.translation_workers = 4
    translator.load_subtitles_from_json = Mock(return_value=sources)
    gate = Barrier(4, timeout=5)

    def respond(**kwargs):
        gate.wait()  # All four cue requests must reach the existing worker pool.
        cue = json.loads(kwargs['prompt'].split('Subtitles:\n', 1)[1].split('\nInclude', 1)[0]
                         .split('\nTranslate this cue', 1)[0])[0]
        item = row(cue['text'])
        item.update(start=cue['start'], end=cue['end'])
        del item['tokens'][0]['reading']
        if cue['text'] == '건배':
            item['tokens'][0]['word'] = '乾杯'
        return {'items': [item]}

    translator.send_request_with_json_schema.side_effect = respond
    plain, annotated = translator.process_korean_translation_single_pass()
    assert [item['ko'] for item in plain] == [item['text'] for item in sources]
    assert [(i['start'], i['end']) for i in annotated] == [(i['start'], i['end']) for i in sources]
    assert translator.send_request_with_json_schema.call_count == 4
    prompts = [call.kwargs['prompt'] for call in translator.send_request_with_json_schema.call_args_list]
    assert any('Previous line: 학교' in p and 'Current line: 감자' in p
               and 'Next line: 그랜빌섬' in p for p in prompts)
    assert annotated[-1]['tokens'][0]['reading'] == '건배'


def test_cached_compact_response_gets_local_readings_without_network(tmp_path, dictionary):
    from lazyedit.openai_request_json import OpenAIRequestJSONBase
    translator = translator_with()
    translator.send_request_with_json_schema = OpenAIRequestJSONBase.send_request_with_json_schema.__get__(translator)
    translator.api_provider, translator.model = 'deepseek', 'test-model'
    translator.use_cache, translator.max_retries = True, 1
    translator.cache_dir = str(tmp_path)
    translator.client = Mock()
    raw = row('학교', '學校')
    del raw['tokens'][0]['reading']
    translator.client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({'items': [raw]})))])
    first = request(translator, raw)
    translator.client.chat.completions.create.side_effect = AssertionError('Expected cached request')
    assert request(translator, raw) == first
    assert first[0]['tokens'][0]['reading'] == '학교'
    assert translator.client.chat.completions.create.call_count == 1


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
