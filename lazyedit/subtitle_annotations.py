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
            "Choose the natural translation first, then examine EVERY lexical root for restoration. "
            "Resolve homophones using this sentence and adjacent context. Restore clear common roots; "
            "do not skip them just because modern writing normally uses the native script. "
            "Do not invent Han etymologies, translate native words into Chinese, or replace names speculatively. "
            "Historical etymology alone is not a conventional modern Han spelling. "
            "Do not rewrite the translation to use more Sino-derived vocabulary. Zero restored roots is valid. "
            "Split inflection/particles from restored roots without losing characters. "
            f"For all non-restored lexical tokens keep word=surface and give {roman} in reading. "
            "Before returning JSON, check for missed clear roots, wrong homophones, lost spaces, "
            "and missing pronunciation. Return only the final JSON, without explanations. "
        )
        if language == "ko":
            prompt += (
                "Example: 학교에서 -> 學校 with reading 학교, then 에서 with reading eseo. "
                "먹어요 stays 먹어요 with reading meogeoyo; do not substitute Chinese for native words."
            )
        else:
            prompt += (
                "Example: học sinh -> 學 with reading học, space, 生 with reading sinh. "
                "Keep native words in Quốc ngữ. Chữ Nôm conversion is not requested. "
                "Vietnamese already uses Latin script; native-word pronunciation is Hanoi IPA, not repeated spelling."
            )
    return schema, prompt


def validate_annotations(items, sources, language, same_language_result=None):
    """Fail visibly rather than silently burn truncated or unannotated subtitles."""
    if not isinstance(items, list) or len(items) != len(sources):
        raise ValueError("Annotated translation changed subtitle count")
    for index, (item, source) in enumerate(zip(items, sources)):
        if not isinstance(item, dict):
            raise ValueError("Annotated subtitle must be an object")
        if any(item.get(key) != source.get(key) for key in ("start", "end")):
            raise ValueError("Annotated translation changed subtitle timing")
        text = item.get(language, "")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Missing clean subtitle text")
        if same_language_result and text != same_language_result["plain"][index][language]:
            raise ValueError("Annotation changed original native subtitle text")
        tokens = item.get("tokens") or []
        if not isinstance(tokens, list) or not tokens:
            raise ValueError("Missing annotation tokens")
        if any(not isinstance(t, dict) or any(not isinstance(t.get(k), str)
               for k in ("surface", "word", "reading", "type")) for t in tokens):
            raise ValueError("Annotation token fields must be strings")
        if any(not t["surface"] for t in tokens):
            raise ValueError("Empty annotation surface")
        if "".join(t["surface"] for t in tokens) != text:
            # Restore only exact whitespace gaps from the authoritative clean text.
            # Missing letters, punctuation, reordered tokens and extra text still fail.
            restored = []
            offset = 0
            for token in tokens:
                surface = token["surface"]
                if not text.startswith(surface, offset):
                    end = offset
                    while end < len(text) and text[end].isspace():
                        end += 1
                    if end == offset or not text.startswith(surface, end):
                        raise ValueError("Annotation tokens do not cover the complete subtitle")
                    gap = text[offset:end]
                    restored.append(dict(surface=gap, word=gap, reading="", type="other"))
                    offset = end
                restored.append(token)
                offset += len(surface)
            if offset < len(text) and text[offset:].isspace():
                gap = text[offset:]
                restored.append(dict(surface=gap, word=gap, reading="", type="other"))
                offset = len(text)
            if offset != len(text):
                raise ValueError("Annotation tokens do not cover the complete subtitle")
            tokens = item["tokens"] = restored
        for token in tokens:
            surface, word = token["surface"], token["word"]
            # Models sometimes leave a whitespace token's display word empty.
            # Surface coverage was already verified; restore that exact spacing.
            if surface.isspace() and not word.strip():
                word = token["word"] = surface
                token["reading"] = ""
            reading = token.get("reading", "")
            if token.get("type") not in GRAMMAR_TYPES:
                raise ValueError("Invalid grammar type")
            if word != surface:
                if language not in {"ko", "vi"} or not HAN.fullmatch(word) or reading != surface:
                    raise ValueError(
                        f"Invalid Han restoration or native ruby: surface={surface!r}, "
                        f"word={word!r}, reading={reading!r}. A restored word must contain "
                        "ONLY Han characters and reading must be the exact native surface, "
                        "not romanization. Split native suffixes/particles into separate "
                        "tokens with word=surface and their own pronunciation."
                    )
            if language in {"ko", "vi"} and any(c.isalpha() for c in surface) and not reading.strip():
                raise ValueError("Missing native reading or pronunciation transliteration")
            if language == "ko" and word == surface and re.search(r"[가-힣]", surface):
                if re.search(r"[가-힣]", reading) or not re.search(r"[A-Za-z]", reading):
                    raise ValueError("Native Korean tokens need romanization, not repeated Hangul")
