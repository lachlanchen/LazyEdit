import json
from pathlib import Path
from unittest.mock import patch

import app
from scripts.lazyedit_publish import default_steps, step_summary


def test_japanese_aliases_and_template_contract():
    for alias in ('ja', 'jp', 'ja-JP', 'Japanese'):
        assert app._normalize_metadata_language(alias) == 'ja'
    root = Path(app.METADATA_TEMPLATE_DIR)
    prompt, schema = app._load_metadata_templates('ja')
    assert '{{CUSTOM_NOTES}}' in prompt['user']
    assert '{{TRANSCRIPTION}}' in prompt['user']
    existing = json.loads((root / 'metadata_en' / 'schema.json').read_text())
    assert set(schema['required']) == set(existing['required'])


def test_new_default_processing_reports_japanese_metadata():
    assert 'metadata_ja' in default_steps(True)
    assert 'metadata_ja' in default_steps(False)
    assert 'metadata_ja:done' in step_summary({'steps': {'metadata_ja': {'status': 'done'}}})


def test_bundle_keeps_japanese_payload_without_chinese_conversion():
    ja = {'title': '約束の旅', 'middle_description': '彼女は帰ってきた。'}
    assembled = {'title': '中文'}
    # Stop after metadata assembly, before any filesystem/video processing.
    with patch.object(app, '_get_video_row', return_value=(999, '/tmp/test.mp4', '', '')), \
         patch.object(app, '_ensure_local_video_path', return_value=('/tmp/test.mp4', None)), \
         patch.object(app, '_get_latest_metadata_payload', side_effect=lambda _id, lang, **kw: ({'title': '中文'} if lang == 'zh' else {'title': 'English'} if lang == 'en' else ja, None)), \
         patch.object(app, '_simplify_metadata_payload', return_value=assembled), \
         patch.object(app, '_publication_session_publish_dir', side_effect=RuntimeError('assembled')) as stop, \
         patch.object(app, 'apply_publish_category', side_effect=lambda metadata, **kw: metadata):
        import pytest
        with pytest.raises(RuntimeError, match='assembled'):
            app._prepare_publish_bundle(999, {'instagram': True})
        assert stop.called
    assert ja['title'] == '約束の旅'
    assert assembled['japanese_version'] == ja
    assert assembled['english_version']['title'] == 'English'
