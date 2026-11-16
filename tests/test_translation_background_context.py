"""Background disambiguates a line without becoming dialogue or requiring AI calls."""
import ast
import asyncio
from contextlib import contextmanager
import copy
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


def prompt_builder():
    source = Path('lazyedit/subtitle_translate.py')
    tree = ast.parse(source.read_text())
    translator = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                      and n.name == 'SubtitlesTranslator')
    selected = ast.ClassDef(name='PromptBuilder', bases=[], keywords=[],
        body=[n for n in translator.body if isinstance(n, ast.FunctionDef)
              and n.name in {'_format_context_value', '_build_prompt_with_context'}],
        decorator_list=[])
    namespace = {'json': json, 'MAX_TRANSLATION_CONTEXT_CHARS': 8000}
    module = ast.fix_missing_locations(ast.Module(body=[selected], type_ignores=[]))
    exec(compile(module, str(source), 'exec'), namespace)
    return namespace['PromptBuilder']()


def test_absent_background_preserves_existing_prompt_and_cache_input():
    builder = prompt_builder()
    template = '{{PREV_LINE}}|{{CURRENT_LINE}}|{{NEXT_LINE}}|{{SUBTITLES_JSON}}'
    expected = 'before|current|after|' + json.dumps([{'text': 'current'}], indent=2)
    assert builder._build_prompt_with_context(template, [{'text': 'current'}],
                                              'before', 'current', 'after') == expected


def test_background_changes_cache_input_but_never_source_dialogue():
    builder = prompt_builder()
    items = [{'start': '00:00:00,000', 'end': '00:00:02,000', 'text': 'ボリューム'}]
    before = copy.deepcopy(items)
    builder.translation_context = 'Hair volume at a salon. Aya is helping the client.'
    hair = builder._build_prompt_with_context('{{SUBTITLES_JSON}}', items, '', '', '')
    builder.translation_context = 'A sound system and its speaker volume.'
    sound = builder._build_prompt_with_context('{{SUBTITLES_JSON}}', items, '', '', '')
    assert hair != sound
    assert 'Hair volume at a salon' in hair
    assert 'not spoken dialogue' in hair
    assert 'preserve native source text' in hair
    assert items == before


def test_background_is_trimmed_bounded_and_json_quoted():
    builder = prompt_builder()
    builder.translation_context = '  ' + 'A' * 9000 + 'DO_NOT_INCLUDE_TAIL'
    prompt = builder._build_prompt_with_context('line', [], '', '', '')
    background = json.loads(prompt.rsplit('\nBackground: ', 1)[1])
    assert len(background) == 8000
    assert 'DO_NOT_INCLUDE_TAIL' not in prompt


@pytest.mark.parametrize('notes,polish,enabled,options,expected', [
    ('current salon', 'older story', False, {}, 'current salon'),
    ('', 'older saved story', False, {}, ''),
    ('', 'current correction', True, {}, 'current correction'),
    ('', 'older saved story', False, {'polish_notes': 'current supplied note'}, 'current supplied note'),
])
def test_pipeline_uses_current_context_not_unrequested_saved_polish_notes(notes, polish, enabled, options, expected):
    tree = ast.parse(Path('app.py').read_text())
    payload = next(node for node in ast.walk(tree) if isinstance(node, ast.Dict)
                   and any(isinstance(k, ast.Constant) and k.value == 'translationContext'
                           for k in node.keys))
    expression = next(value for key, value in zip(payload.keys, payload.values)
                      if isinstance(key, ast.Constant) and key.value == 'translationContext')
    result = eval(compile(ast.Expression(expression), 'app.py', 'eval'), {
        'notes': notes, 'polish_notes': polish,
        'auto_correct_subtitles': enabled, 'data': options,
    })
    assert result == expected


def translate_handler(tmp_path):
    source = Path('app.py')
    handler = next(n for n in ast.parse(source.read_text()).body
                   if isinstance(n, ast.ClassDef) and n.name == 'VideoTranslateHandler')
    video = tmp_path / 'video.mp4'
    original_json = tmp_path / 'source.json'
    original_srt = tmp_path / 'source.srt'
    original_json.write_text('[]')
    original_srt.write_text('')
    cursor = SimpleNamespace(execute=Mock(), fetchone=lambda: (str(video),))

    @contextmanager
    def get_cursor(**kwargs):
        yield cursor

    async def run_blocking(fn):
        return fn()

    translator = Mock()
    translator.process_english_translation_single_pass.return_value = ([], [])
    constructor = Mock(return_value=translator)
    scope = {
        'json': json, 'os': os,
        'CorsMixin': type('CorsMixin', (), {}),
        'tornado': SimpleNamespace(web=SimpleNamespace(RequestHandler=object)),
        'require_subtitle_language': lambda v: v,
        '_parse_bool': lambda v, default=True: default if v is None else bool(v),
        '_parse_int_value': lambda v: None,
        'DEFAULT_PUBLISH_OPTIONS': {'usePolishedSubtitles': True},
        'ldb': SimpleNamespace(ensure_schema=lambda: None, get_cursor=get_cursor,
                               add_subtitle_translation=lambda *a, **kw: 1),
        '_ensure_local_video_path': lambda video_id, path: (path, None),
        'preprocess_if_needed': lambda path: path,
        '_ensure_global_polished_subtitles': lambda *args: None,
        'find_latest_transcription_outputs': lambda *a, **kw: (str(original_json), str(original_srt)),
        '_publication_session_dir': lambda directory, *a, **kw: directory,
        'get_video_length': lambda path: 1,
        'get_video_resolution': lambda path: (1080, 1920),
        '_translation_openai_client': lambda: None,
        'SubtitlesTranslator': constructor,
        'media_url_for_path': lambda path: path,
        'build_srt_preview_with_timestamps': lambda path: '',
        'run_blocking': run_blocking,
    }
    exec(compile(ast.Module(body=[handler], type_ignores=[]), str(source), 'exec'), scope)
    return scope['VideoTranslateHandler'].post, constructor


@pytest.mark.parametrize('options,expected', [
    ({'notes': 'Aya helps at the hair salon'}, 'Aya helps at the hair salon'),
    ({'notes': 'metadata brief', 'translationContext': 'Hair volume, not sound'},
     'Hair volume, not sound'),
    ({}, ''),
])
def test_api_passes_background_to_translator_without_a_provider_request(tmp_path, options, expected):
    post, constructor = translate_handler(tmp_path)
    fake = SimpleNamespace(request=SimpleNamespace(body=json.dumps({'lang': 'en', **options}).encode()),
                           get_argument=lambda name, default=None: default,
                           set_status=Mock(), write=Mock())
    asyncio.run(post(fake, '688'))
    fake.set_status.assert_not_called()
    assert constructor.call_args.kwargs['translation_context'] == expected


@pytest.mark.parametrize('invalid', [[], {'unexpected': 'object'}, 42])
def test_api_rejects_non_text_background_before_processing(tmp_path, invalid):
    post, constructor = translate_handler(tmp_path)
    fake = SimpleNamespace(request=SimpleNamespace(body=json.dumps({'translationContext': invalid}).encode()),
                           get_argument=lambda name, default=None: default,
                           set_status=Mock(), write=Mock())
    asyncio.run(post(fake, '688'))
    fake.set_status.assert_called_once_with(400)
    constructor.assert_not_called()
