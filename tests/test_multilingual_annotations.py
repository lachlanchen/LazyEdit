import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from lazyedit.subtitle_annotations import annotation_contract, validate_annotations
from lazyedit.subtitle_translate import SubtitlesTranslator
from lazyedit.subtitles_burner.burner import _load_burner_module


def test_corrected_chinese_cue_with_stale_english_tag_is_translated(tmp_path):
    translator = SubtitlesTranslator.__new__(SubtitlesTranslator)
    source = {'start': '00:00:19,112', 'end': '00:00:28,884',
              'lang': 'en', 'text': '拌面'}
    item = {'start': source['start'], 'end': source['end'], 'en': 'Mixing noodles',
            'tokens': [{'surface': 'Mixing', 'word': 'Mixing', 'reading': '', 'type': 'verb'},
                       {'surface': ' noodles', 'word': ' noodles', 'reading': '', 'type': 'noun'}]}
    translator.get_filename = Mock(return_value=str(tmp_path / 'response.json'))
    translator.send_request_with_json_schema = Mock(return_value={'items': [item]})
    result = translator.translate_and_merge_subtitles_en_single_pass([source], 0)
    assert result['plain'][0]['en'] == 'Mixing noodles'
    assert result['plain'][0]['start'] == source['start']
    assert source['lang'] == 'en'  # Preserve the original recognition evidence.


@pytest.mark.parametrize('text', ['Thank you', 'This is 莲香西域', '99.99%', '🧡'])
def test_actual_english_mixed_speech_and_nonletters_still_lock(text):
    translator = SubtitlesTranslator.__new__(SubtitlesTranslator)
    source = {'start': '00:00:01,000', 'end': '00:00:02,000', 'lang': 'en', 'text': text}
    locked = translator._same_language_plain_result([source], 'en', 'en')
    assert locked['plain'][0]['en'] == text
    item = dict(start=source['start'], end=source['end'], en='Changed', tokens=[])
    with pytest.raises(ValueError, match='changed original'):
        validate_annotations([item], [source], 'en', locked)


def test_empty_corrected_hallucination_is_not_sent_for_translation(tmp_path):
    path = tmp_path / 'polished.json'
    path.write_text(json.dumps([
        {'text': '谢谢你们', 'lang': 'zh'}, {'text': '', 'lang': 'en'},
        {'text': '   ', 'lang': 'en'}], ensure_ascii=False))
    translator = SubtitlesTranslator.__new__(SubtitlesTranslator)
    translator.input_json_path = path
    assert translator.load_subtitles_from_json() == [{'text': '谢谢你们', 'lang': 'zh'}]


@pytest.fixture(autouse=True)
def local_hanja_candidates(monkeypatch):
    # Unit tests must not download the production dictionary on a fresh checkout.
    monkeypatch.setattr("lazyedit.hanja_dictionary.load_dictionary",
                        lambda: {"학교": [{"word": "學校"}]})


@pytest.mark.parametrize('lang,surface,word,reading', [
    ('ko', '학교', '學校', '학교'), ('vi', 'học', '學', 'học'),
    ('ko', '나', '나', 'na'), ('vi', 'tôi', 'tôi', 'toj˧'),
    ('ar', 'كتاب', 'كتاب', ''), ('ru', 'книга', 'книга', ''),
    ('es', 'libro', 'libro', ''), ('yue', '書', '書', ''),
])
def test_translation_and_burner_keep_annotations(tmp_path, lang, surface, word, reading):
    translator = SubtitlesTranslator.__new__(SubtitlesTranslator)
    source = {'start': '00:00:00,000', 'end': '00:00:02,000', 'text': surface}
    item = {'start': source['start'], 'end': source['end'], lang: surface,
            'tokens': [{'surface': surface, 'word': word, 'reading': reading, 'type': 'noun'}]}
    translator._same_language_plain_result = Mock(return_value={'plain': [item]})
    translator.get_filename = Mock(return_value=str(tmp_path / 'response.json'))
    translator.send_request_with_json_schema = Mock(return_value={'items': [item]})
    result = getattr(translator, f'translate_and_merge_subtitles_{lang}_single_pass')([source], 0)
    assert result['plain'][0][lang] == surface
    assert result['json'][0]['tokens'][0]['word'] == word
    _load_burner_module()
    import subtitles_burner.burner as burner
    path = tmp_path / 'subtitle.json'
    path.write_text(json.dumps(result['json'], ensure_ascii=False))
    palette = json.loads(Path('lazyedit/templates/grammar_palettes/default.json').read_text())
    segments = burner.load_segments_from_json(str(path), text_key=lang, palette=palette)
    assert ''.join(t.text for t in segments[0].tokens) == word
    assert segments[0].tokens[0].ruby == (reading or None)
    assert segments[0].tokens[0].token_type == 'noun'


def test_reject_lost_text_and_missing_reading():
    source = {'start': '00:00:00,000', 'end': '00:00:02,000'}
    item = dict(source, ko='학교', tokens=[{'surface': '학', 'word': '學', 'reading': '학', 'type': 'noun'}])
    with pytest.raises(ValueError, match='complete subtitle'):
        validate_annotations([item], [source], 'ko')
    item['tokens'] = [{'surface': '학교', 'word': '학교', 'reading': '', 'type': 'noun'}]
    with pytest.raises(ValueError, match='Missing'):
        validate_annotations([item], [source], 'ko')


def test_german_generic_path_keeps_grammar(tmp_path):
    translator = SubtitlesTranslator.__new__(SubtitlesTranslator)
    source = {'start': '00:00:00,000', 'end': '00:00:02,000', 'text': 'Buch', 'language': 'de'}
    item = dict(start=source['start'], end=source['end'], de='Buch',
                tokens=[{'surface': 'Buch', 'word': 'Buch', 'reading': '', 'type': 'noun'}])
    translator.load_subtitles_from_json = Mock(return_value=[source])
    translator.get_filename = Mock(return_value=str(tmp_path / 'response.json'))
    translator.send_request_with_json_schema = Mock(return_value={'items': [item]})
    plain, annotated = translator.process_specified_language_translation('de')
    assert plain == [{'start': source['start'], 'end': source['end'], 'de': 'Buch'}]
    assert annotated[0]['tokens'][0]['type'] == 'noun'
    assert 'tokens' in translator.send_request_with_json_schema.call_args.kwargs['json_schema']['properties']['items']['items']['required']


def test_korean_wrapping_keeps_restored_root_with_native_particle(tmp_path):
    _load_burner_module()
    import subtitles_burner.burner as burner
    item = {'start': '00:00:00,000', 'end': '00:00:05,000', 'ko': '학교에서 먹어요', 'tokens': [
        {'word': '學校', 'reading': '학교', 'type': 'noun'},
        {'word': '에서', 'reading': 'eseo', 'type': 'particle'},
        {'word': ' ', 'reading': '', 'type': 'other'},
        {'word': '먹어요', 'reading': 'meogeoyo', 'type': 'verb'},
    ]}
    path = tmp_path / 'ko.json'
    path.write_text(json.dumps([item], ensure_ascii=False))
    tokens = burner.load_segments_from_json(str(path), text_key='ko')[0].tokens
    assert tokens[0]._lazyedit_group == tokens[1]._lazyedit_group
    assert tokens[3]._lazyedit_group != tokens[0]._lazyedit_group
    assert tokens[0].ruby == '학교'
    assert tokens[1].ruby == 'eseo'
    # A long cue uses multiple timed chunks without detaching the particle.
    repeated = tokens + [burner.RubyToken(text=' ')] + tokens
    segment = burner.SubtitleSegment(0.0, 5.0, repeated, '學校에서 먹어요 學校에서 먹어요')
    chunks = burner._auto_split_segments_for_slot(
        [segment], burner.Slot(1, 0, 0, 230, 120), burner.TextStyle(main_font_size=40, ruby_font_size=20),
    )
    assert len(chunks) > 1
    assert chunks[0].start_time == 0.0 and chunks[-1].end_time == 5.0
    for chunk in chunks:
        for i, token in enumerate(chunk.tokens):
            if token.text == '學校':
                assert chunk.tokens[i + 1].text == '에서'
                assert token.ruby == '학교'


def test_empty_display_for_space_is_repaired_without_losing_spacing():
    source = {'start': '00:00:00,000', 'end': '00:00:02,000'}
    item = dict(source, en='Beef potatoes', tokens=[
        {'surface': 'Beef', 'word': 'Beef', 'reading': '', 'type': 'noun'},
        {'surface': ' ', 'word': '', 'reading': '', 'type': 'other'},
        {'surface': 'potatoes', 'word': 'potatoes', 'reading': '', 'type': 'noun'},
    ])
    validate_annotations([item], [source], 'en')
    assert ''.join(t['word'] for t in item['tokens']) == item['en']


def test_omitted_spaces_are_restored_but_missing_words_are_rejected():
    source = {'start': '00:00:00,000', 'end': '00:00:02,000'}
    item = dict(source, ko='학교에서 먹어요', tokens=[
        {'surface': '학교', 'word': '學校', 'reading': '학교', 'type': 'noun'},
        {'surface': '에서', 'word': '에서', 'reading': 'eseo', 'type': 'particle'},
        {'surface': '먹어요', 'word': '먹어요', 'reading': 'meogeoyo', 'type': 'verb'},
    ])
    validate_annotations([item], [source], 'ko')
    assert ''.join(t['surface'] for t in item['tokens']) == item['ko']
    assert item['tokens'][2] == dict(surface=' ', word=' ', reading='', type='other')
    item['ko'] = '학교에서 같이 먹어요'
    with pytest.raises(ValueError, match='complete subtitle'):
        validate_annotations([item], [source], 'ko')


def test_han_repair_error_identifies_invalid_token():
    source = {'start': '00:00:00,000', 'end': '00:00:02,000'}
    item = dict(source, ko='도착했어', tokens=[
        {'surface': '도착했어', 'word': '到着했어', 'reading': 'dochakhaesseo', 'type': 'verb'},
    ])
    with pytest.raises(ValueError, match='ONLY Han characters') as error:
        validate_annotations([item], [source], 'ko')
    assert '到着했어' in str(error.value)


@pytest.mark.parametrize('lang', ['ko', 'vi'])
def test_generated_ruby_has_readable_size_without_auto_pronunciation_toggle(monkeypatch, lang):
    from lazyedit.subtitles_burner import burner as adapter
    components = adapter._load_burner_module()
    encode = Mock()
    monkeypatch.setattr(adapter, '_load_burner_module', lambda: (*components[:-1], encode))
    monkeypatch.setattr(adapter, '_get_video_resolution', lambda path: (1080, 1920))
    adapter.burn_video_with_slots('input.mp4', 'output.mp4', [
        adapter.BurnSlotConfig(4, lang, 'unused.json', lang),
    ], rows=4, cols=1, lift_ratio=0)
    style = encode.call_args.args[3][0].style
    assert style.ruby_font_size >= style.main_font_size * 0.5
