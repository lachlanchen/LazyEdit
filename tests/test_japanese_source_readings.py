import copy
from unittest.mock import Mock

import pytest

from lazyedit.subtitle_translate import SubtitlesTranslator


SOURCE = [{"start": "00:00:01,000", "end": "00:00:02,000", "lang": "ja", "text": "東京へ！"}]
ANNOTATED = {"items": [{
    "start": "00:00:01,000", "end": "00:00:02,000", "ja": "東京へ！",
    "tokens": [
        {"word": "東京", "reading": "とうきょう", "type": "noun"},
        {"word": "へ", "reading": "へ", "type": "particle_he"},
        {"word": "！", "reading": "！", "type": "punctuation"},
    ],
}]}


def translator(response):
    instance = SubtitlesTranslator.__new__(SubtitlesTranslator)
    instance._load_template_json = Mock(return_value={})
    instance._build_prompt_with_context = Mock(return_value="annotate")
    instance.get_filename = Mock(return_value="test.json")
    instance.send_request_with_json_schema = Mock(return_value=response)
    return instance


def test_japanese_source_is_annotated_without_rewriting_or_retiming():
    response = copy.deepcopy(ANNOTATED)
    response["items"][0]["start"] = "00:00:09,000"
    instance = translator(response)
    result = instance.translate_and_merge_subtitles_ja_furigana_single_pass(SOURCE, 0)
    assert result["plain"] == [{"start": "00:00:01,000", "end": "00:00:02,000", "ja": "東京へ！"}]
    assert result["json"][0]["tokens"][0]["reading"] == "とうきょう"
    assert "とうきょう" in result["ruby"][0]["ja"]
    assert "already Japanese" in instance.send_request_with_json_schema.call_args.kwargs["system_content"]


@pytest.mark.parametrize("defect", ["rewritten", "missing_tokens", "missing_reading", "extra_cue"])
def test_invalid_source_annotations_are_rejected(defect):
    response = copy.deepcopy(ANNOTATED)
    item = response["items"][0]
    if defect == "rewritten":
        item["ja"] = "京都へ！"
    elif defect == "missing_tokens":
        item["tokens"] = []
    elif defect == "missing_reading":
        item["tokens"][0]["reading"] = "東京"
    else:
        response["items"].append(copy.deepcopy(item))
    with pytest.raises(ValueError, match="Japanese source annotation"):
        translator(response).translate_and_merge_subtitles_ja_furigana_single_pass(SOURCE, 0)


def test_non_japanese_translation_remains_enabled():
    source = [{**SOURCE[0], "lang": "zh", "text": "去东京！"}]
    instance = translator(copy.deepcopy(ANNOTATED))
    result = instance.translate_and_merge_subtitles_ja_furigana_single_pass(source, 0)
    assert result["plain"][0]["ja"] == "東京へ！"
    assert "already Japanese" not in instance.send_request_with_json_schema.call_args.kwargs["system_content"]


def test_source_timestamps_are_used_when_annotation_omits_them():
    response = copy.deepcopy(ANNOTATED)
    del response["items"][0]["start"]
    del response["items"][0]["end"]
    result = translator(response).translate_and_merge_subtitles_ja_furigana_single_pass(SOURCE, 0)
    assert result["plain"] == [{"start": "00:00:01,000", "end": "00:00:02,000", "ja": "東京へ！"}]
