"""Exercise the normal edit handler without starting the owner backend."""
import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


@pytest.mark.parametrize('language,key,new_text', [
    ('en', 'en', 'Busy'), ('fr', 'fr', 'Très fréquenté'),
    ('zh-Hant', 'zh', '繁忙'), ('ja', 'ja', '混雑しています'),
])
def test_edit_drops_stale_render_annotations_for_every_language(language, key, new_text):
    tree = ast.parse(Path('app.py').read_text())
    handler = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == 'VideoTranslationHandler')
    row = {'start': '00:00:08,000', 'end': '00:00:10,000', key: 'old',
           'tokens': [{'word': 'old'}], 'ruby': 'old', 'furigana_pairs': [['old', 'old']]}
    other = {'start': '00:00:10,000', 'end': '00:00:12,000', key: 'unchanged'}
    items = [row, copy.deepcopy(other)]
    save = Mock()
    srt = Mock()
    scope = {
        'json': json, 'CorsMixin': type('CorsMixin', (), {}),
        'tornado': SimpleNamespace(web=SimpleNamespace(RequestHandler=object)),
        'ldb': SimpleNamespace(ensure_schema=lambda: None,
            get_latest_subtitle_translation=lambda *a: (1, language, 'completed', 'json', 'srt', None, None, None)),
        '_normalize_translation_language': lambda x: x,
        '_load_subtitle_payload': lambda path: (items, items, None),
        '_resolve_translation_text_key': lambda *a: key,
        '_write_subtitle_payload': save, '_write_srt_from_items': srt,
    }
    exec(compile(ast.Module(body=[handler], type_ignores=[]), 'app.py', 'exec'), scope)
    request = SimpleNamespace(body=json.dumps({'index': 0, 'text': new_text}).encode())
    fake = SimpleNamespace(request=request, get_argument=lambda *a, **kw: language,
                           set_status=Mock(), write=Mock())
    scope['VideoTranslationHandler'].post(fake, '675')
    assert row[key] == new_text
    assert row['start'] == '00:00:08,000'
    assert row['end'] == '00:00:10,000'
    assert not {'tokens', 'ruby', 'furigana_pairs'} & row.keys()
    assert items[1] == other
    save.assert_called_once()
    srt.assert_called_once()
    fake.set_status.assert_not_called()
