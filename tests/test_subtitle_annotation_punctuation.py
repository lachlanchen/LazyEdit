import pytest

from lazyedit.subtitle_annotations import validate_annotations


@pytest.mark.parametrize("language", ["en", "fr", "ko", "vi", "ar"])
@pytest.mark.parametrize("surface", [",", "!", "。", "؟", "…", " — "])
def test_empty_display_word_preserves_exact_punctuation(language, surface):
    source = {"start": "00:00:01,000", "end": "00:00:02,000"}
    item = dict(source, **{language: surface}, tokens=[
        dict(surface=surface, word="", reading="", type="punctuation"),
    ])
    validate_annotations([item], [source], language)
    assert item[language] == surface
    assert item["tokens"][0]["word"] == surface
    assert item["tokens"][0]["reading"] == ""
    assert item["start"] == source["start"]
    assert item["end"] == source["end"]


@pytest.mark.parametrize("surface", ["lamp", "42", "灯", "word,", "+"])
def test_empty_lexical_display_still_fails(surface):
    source = {"start": "00:00:01,000", "end": "00:00:02,000"}
    item = dict(source, en=surface, tokens=[
        dict(surface=surface, word="", reading="", type="punctuation"),
    ])
    with pytest.raises(ValueError, match="Invalid Han restoration"):
        validate_annotations([item], [source], "en")


def test_missing_punctuation_surface_still_fails():
    source = {"start": "00:00:01,000", "end": "00:00:02,000"}
    item = dict(source, en="lamp,", tokens=[
        dict(surface="lamp", word="lamp", reading="", type="noun"),
    ])
    with pytest.raises(ValueError, match="complete subtitle"):
        validate_annotations([item], [source], "en")
