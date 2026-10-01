import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from lazyedit.subtitle_annotations import annotation_contract, validate_annotations
from lazyedit.subtitle_translate import SubtitlesTranslator
from lazyedit.subtitles_burner.burner import _load_burner_module


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
