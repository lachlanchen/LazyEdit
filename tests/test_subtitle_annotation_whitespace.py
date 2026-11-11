from copy import deepcopy

import pytest

from lazyedit.subtitle_annotations import validate_annotations


def annotated(text, surfaces):
    source = {"start": "00:00:00,640", "end": "00:00:01,640"}
    item = dict(source, en=text, tokens=[
        dict(surface=s, word=s, reading="", type="other") for s in surfaces
    ])
    return source, item


@pytest.mark.parametrize("text,surfaces", [
    ("We've arrived!", ["We", " ", "'ve", " ", "arrived", "!"]),
    ("Give it back!", ["Give", "  ", " ", "it", "back", "!"]),
    ("Hello!", [" ", "Hello", "!", "\n"]),
])
def test_only_whitespace_reconciled_to_exact_clean_text(text, surfaces):
    source, item = annotated(text, surfaces)
    before = deepcopy(item)
    validate_annotations([item], [source], "en")
    assert "".join(t["surface"] for t in item["tokens"]) == text
    assert "".join(t["word"] for t in item["tokens"]) == text
    assert item["start"] == before["start"]
    assert item["end"] == before["end"]
    assert [t for t in item["tokens"] if not t["surface"].isspace()] == [
        t for t in before["tokens"] if not t["surface"].isspace()
    ]


@pytest.mark.parametrize("text,surfaces", [
    ("We've arrived!", ["We", " ", "ve", " ", "arrived", "!"]),
    ("Give it back!", ["Give", " ", "back", "!"]),
    ("Give it back!", ["Give", " ", "it", " ", "back"]),
    ("Give it back!", ["Give", " ", "it", " ", "back", "!", "extra"]),
    ("Give it back!", ["Give", " ", "back", " ", "it", "!"]),
])
def test_whitespace_repair_never_changes_non_whitespace_coverage(text, surfaces):
    source, item = annotated(text, surfaces)
    with pytest.raises(ValueError, match="complete subtitle"):
        validate_annotations([item], [source], "en")


def test_whitespace_repair_keeps_timing_validation():
    source, item = annotated("We've arrived!", ["We", " ", "'ve", " ", "arrived", "!"])
    item["start"] = "00:00:00,000"
    with pytest.raises(ValueError, match="timing"):
        validate_annotations([item], [source], "en")
