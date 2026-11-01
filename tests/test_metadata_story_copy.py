import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from lazyedit.subtitle_metadata import (
    STORY_METADATA_POLICY,
    Subtitle2Metadata,
    metadata_editor_system,
)


TEMPLATES = Path(__file__).resolve().parents[1] / 'lazyedit' / 'templates'


def bare_generator():
    generator = object.__new__(Subtitle2Metadata)
    generator.send_request_with_json_schema = Mock(return_value={})
    generator.validate_metadata = Mock()
    generator.metadata_schema = {}
    generator.subtitles2metadata_folder = 'unused'
    return generator


@pytest.mark.parametrize('language', ['zh', 'en', 'ja'])
def test_live_templates_enforce_story_copy_without_restart(language):
    prompt = json.loads((TEMPLATES / f'metadata_{language}' / 'prompt.json').read_text())
    assert STORY_METADATA_POLICY in prompt['system']
    for field in ('TRANSCRIPTION', 'CAPTIONS', 'CUSTOM_NOTES'):
        assert '{{' + field + '}}' in prompt['user']


@pytest.mark.parametrize('language', ['zh', 'en', 'ja'])
def test_production_notes_stay_below_editor_policy(language, tmp_path):
    generator = bare_generator()
    notes = 'AI-generated 2D animation. Aya welcomes friends home to dinner.'
    generator.generate_metadata_from_template(
        str(TEMPLATES / f'metadata_{language}'), '00:00:01 Dinner is ready!',
        '', notes, str(tmp_path / 'metadata.json'),
    )
    request = generator.send_request_with_json_schema.call_args.kwargs
    assert request['system_content'].count(STORY_METADATA_POLICY) == 1
    assert notes in request['prompt']
    assert request['json_schema']['required']


@pytest.mark.parametrize('language', ['zh', 'en'])
def test_legacy_generation_uses_same_policy(language, tmp_path):
    generator = bare_generator()
    subtitles = tmp_path / 'subtitles.srt'
    captions = tmp_path / 'captions.txt'
    subtitles.write_text('Dinner is ready!')
    captions.write_text('2D AI-generated cottage scene')
    getattr(generator, f'generate_video_metadata_{language}')(str(subtitles), str(captions))
    request = generator.send_request_with_json_schema.call_args.kwargs
    assert STORY_METADATA_POLICY in request['system_content']


def test_policy_is_idempotent_and_preserves_technical_topics_and_native_labels():
    once = metadata_editor_system('Write Japanese.')
    assert metadata_editor_system(once) == once
    assert once.startswith('Write Japanese.')
    assert 'tutorial/making-of' in once
    assert 'AI robot within the story' in once
    assert 'native platform declarations separately' in once
