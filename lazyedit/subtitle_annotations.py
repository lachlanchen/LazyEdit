"""Lossless grammar/ruby contracts for single-pass subtitle translation."""
from copy import deepcopy
import re

GRAMMAR_TYPES = ["noun", "pronoun", "verb", "adjective", "adverb", "particle",
                 "preposition", "conjunction", "determiner", "auxiliary",
                 "interjection", "number", "punctuation", "other"]
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+")


def annotation_contract(schema, language):
    schema = deepcopy(schema)
    row = schema["properties"]["items"]["items"]
    row["properties"]["tokens"] = {
        "type": "array", "items": {
            "type": "object", "properties": {
                "surface": {"type": "string"},
                "word": {"type": "string"},
                "reading": {"type": "string"},
                "type": {"type": "string", "enum": GRAMMAR_TYPES},
            }, "required": ["surface", "word", "reading", "type"],
            "additionalProperties": False,
        },
    }
    row["required"] = list(row["required"]) + ["tokens"]
    prompt = (
        "\nInclude grammar-colored tokens for every line. Concatenating token.surface "
        "must reproduce the clean translated text EXACTLY, including spaces and punctuation. "
        "Classify grammatical function in this sentence, not English word heuristics. "
        "Keep word=surface except the explicitly allowed Han restoration below. "
        "Use separate whitespace tokens with empty reading. No omitted words. "
        "Punctuation has empty reading. Keep the clean language field in native orthography. "
        "For languages without a rule below use empty reading; pronunciation is handled by the renderer."
    )
    if language in {"ko", "vi"}:
        native = "Hangul" if language == "ko" else "Vietnamese with all tone marks"
        roman = "Revised Romanization" if language == "ko" else "IPA pronunciation (standard Hanoi Vietnamese)"
        prompt += (
            f"\nRestore only confidently identified {'Sino-Korean Hanja' if language == 'ko' else 'Sino-Vietnamese Chữ Hán'} "
            f"roots using traditional Han characters in word, with their ORIGINAL {native} surface in reading. "
            "Do not invent Han etymologies, translate native words into Chinese, or replace names speculatively. "
            "Split inflection/particles from restored roots without losing characters. "
            f"For all non-restored lexical tokens keep word=surface and give {roman} in reading. "
            "Vietnamese is already Latin-script, so IPA supplies meaningful pronunciation rather than repeating it."
        )
    return schema, prompt


def validate_annotations(items, sources, language, same_language_result=None):
    """Fail visibly rather than silently burn truncated or unannotated subtitles."""
    if len(items) != len(sources):
        raise ValueError("Annotated translation changed subtitle count")
    for index, (item, source) in enumerate(zip(items, sources)):
        if any(item.get(key) != source.get(key) for key in ("start", "end")):
            raise ValueError("Annotated translation changed subtitle timing")
        text = item.get(language, "")
        if same_language_result and text != same_language_result["plain"][index][language]:
            raise ValueError("Annotation changed original native subtitle text")
        tokens = item.get("tokens") or []
        if not tokens or "".join(t.get("surface", "") for t in tokens) != text:
            raise ValueError("Annotation tokens do not cover the complete subtitle")
        for token in tokens:
            surface, word = token["surface"], token["word"]
            reading = token.get("reading", "")
            if token.get("type") not in GRAMMAR_TYPES:
                raise ValueError("Invalid grammar type")
            if word != surface:
                if language not in {"ko", "vi"} or not HAN.fullmatch(word) or reading != surface:
                    raise ValueError("Invalid Han restoration or native ruby")
            if language in {"ko", "vi"} and any(c.isalpha() for c in surface) and not reading.strip():
                raise ValueError("Missing native reading or pronunciation transliteration")
