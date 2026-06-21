from __future__ import annotations

import re
from typing import Any, Optional


_TOKEN_RE = re.compile(
    r"\d+(?:[.,]\d+)*(?:\s*(?:[%°℃℉]|[A-Za-zµμ/%]+))?"
    r"|[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[’'\-][A-Za-zÀ-ÖØ-öø-ÿ]+)*"
    r"|[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]+"
    r"|[\u3040-\u309F]+"
    r"|[\u30A0-\u30FFー]+"
    r"|[\uAC00-\uD7AF]+"
    r"|\s+"
    r"|.",
    re.UNICODE,
)

_JA_PARTICLES = {
    "は": "particle_wa",
    "が": "particle_ga",
    "を": "particle_wo",
    "に": "particle_ni",
    "で": "particle_de",
    "と": "particle_to",
    "の": "particle_no",
    "へ": "particle_he",
    "から": "particle_kara",
    "まで": "particle_made",
    "より": "particle_yori",
    "も": "particle_mo",
    "か": "particle_ka",
    "や": "particle_ya",
    "でも": "particle_demo",
    "だけ": "particle_dake",
    "しか": "particle_shika",
    "など": "particle_nado",
}

_EN_PRONOUNS = {
    "i",
    "me",
    "you",
    "he",
    "him",
    "she",
    "her",
    "it",
    "we",
    "us",
    "they",
    "them",
    "this",
    "that",
    "these",
    "those",
}
_EN_DETERMINERS = {"a", "an", "the", "my", "your", "his", "its", "our", "their"}
_EN_PREPOSITIONS = {
    "in",
    "on",
    "at",
    "by",
    "for",
    "from",
    "with",
    "without",
    "to",
    "of",
    "into",
    "through",
    "over",
    "under",
    "between",
}
_EN_CONJUNCTIONS = {"and", "or", "but", "because", "so", "while", "although", "if"}
_EN_AUXILIARIES = {
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "do",
    "does",
    "did",
    "have",
    "has",
    "had",
    "can",
    "could",
    "will",
    "would",
    "shall",
    "should",
    "may",
    "might",
    "must",
}


def _normalize_language(language: Any) -> str:
    text = str(language or "").strip().lower().replace("_", "-")
    aliases = {
        "japanese": "ja",
        "zh": "zh",
        "zh-cn": "zh",
        "zh-hans": "zh",
        "zh-hant": "zh",
        "zh-tw": "zh",
        "chinese": "zh",
        "mandarin": "zh",
        "yue": "yue",
        "cantonese": "yue",
        "english": "en",
    }
    return aliases.get(text, text)


def language_from_context(
    language: Any = None,
    text_key: Any = None,
    palette: Optional[dict[str, Any]] = None,
    text: str = "",
) -> str:
    for candidate in (
        language,
        text_key,
        palette.get("language") if isinstance(palette, dict) else None,
    ):
        normalized = _normalize_language(candidate)
        if normalized:
            return normalized
    if re.search(r"[\u3040-\u30FF]", text):
        return "ja"
    if re.search(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]", text):
        return "zh"
    if re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", text):
        return "en"
    return ""


def _palette_types(palette: Optional[dict[str, Any]]) -> set[str]:
    if not isinstance(palette, dict):
        return set()
    types = palette.get("types")
    if isinstance(types, dict):
        return {str(key) for key in types}
    return {str(key) for key in palette if key not in {"language", "name", "label"}}


def _type_for_palette(token_type: str, palette: Optional[dict[str, Any]], language: str) -> str:
    token_type = str(token_type or "").strip() or "other"
    palette_types = _palette_types(palette)
    if not palette_types or token_type in palette_types:
        return token_type
    if language == "ja" and token_type == "particle" and "particle_other" in palette_types:
        return "particle_other"
    if "other" in palette_types:
        return "other"
    return token_type


def _is_cjk(text: str) -> bool:
    return bool(re.fullmatch(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]+", text))


def _is_hiragana(text: str) -> bool:
    return bool(re.fullmatch(r"[\u3040-\u309F]+", text))


def _is_katakana(text: str) -> bool:
    return bool(re.fullmatch(r"[\u30A0-\u30FFー]+", text))


def _is_kana(text: str) -> bool:
    return _is_hiragana(text) or _is_katakana(text)


def _is_number(text: str) -> bool:
    return bool(re.fullmatch(r"\d+(?:[.,]\d+)*(?:\s*(?:[%°℃℉]|[A-Za-zµμ/%]+))?", text))


def _is_word(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[’'\-][A-Za-zÀ-ÖØ-öø-ÿ]+)*", text))


def _is_punctuation(text: str) -> bool:
    return bool(text and not text.isspace() and re.fullmatch(r"[^\w\s]+", text, flags=re.UNICODE))


def _is_japanese_verb_like(text: str) -> bool:
    return bool(
        re.search(
            r"(ます|ました|ません|ない|なかった|たい|られる|れる|せる|させる|する|した|して|"
            r"った|んだ|いた|いて|える|ける|げる|せる|てる|れる|る|う|く|ぐ|す|つ|ぬ|ぶ|む)$",
            text,
        )
    )


def _guess_japanese_type(text: str) -> str:
    if text.isspace():
        return "other"
    if _is_number(text):
        return "number"
    if _is_punctuation(text):
        return "punctuation"
    if text in _JA_PARTICLES:
        return _JA_PARTICLES[text]
    if text in {"です", "でした", "だ", "である"}:
        return "copula"
    if text in {"ます", "ました", "ない", "た", "て", "れる", "られる"}:
        return "auxiliary"
    if text in {"この", "その", "あの", "どの", "これ", "それ", "あれ", "どれ"}:
        return "demonstrative"
    if text in {"何", "誰", "どこ", "いつ", "なぜ", "どう"}:
        return "question_word"
    if _is_japanese_verb_like(text):
        return "verb"
    if _is_katakana(text):
        return "noun"
    if _is_cjk(text) or _is_kana(text):
        return "noun"
    return _guess_default_type(text)


def _guess_chinese_type(text: str) -> str:
    if text.isspace():
        return "other"
    if _is_number(text):
        return "number"
    if _is_punctuation(text):
        return "punctuation"
    if text in {"的", "了", "着", "过", "吗", "呢", "吧", "啊", "地", "得"}:
        return "particle"
    if text in {"我", "你", "他", "她", "它", "们", "这", "那", "谁"}:
        return "pronoun"
    if text in {"是", "有", "做", "说", "去", "来", "看", "想", "要", "会", "能", "让"}:
        return "verb"
    if text in {"在", "把", "被", "从", "到", "向", "跟", "和", "给", "对"}:
        return "preposition"
    if text in {"和", "或", "但是", "如果", "因为", "所以"}:
        return "conjunction"
    if _is_cjk(text):
        return "noun"
    return _guess_default_type(text)


def _guess_default_type(text: str) -> str:
    if text.isspace():
        return "other"
    if _is_number(text):
        return "number"
    if _is_punctuation(text):
        return "punctuation"
    lowered = text.lower()
    if lowered in _EN_PRONOUNS:
        return "pronoun"
    if lowered in _EN_DETERMINERS:
        return "determiner"
    if lowered in _EN_PREPOSITIONS:
        return "preposition"
    if lowered in _EN_CONJUNCTIONS:
        return "conjunction"
    if lowered in _EN_AUXILIARIES:
        return "auxiliary"
    if lowered.endswith("ly"):
        return "adverb"
    if lowered.endswith(("ing", "ed")):
        return "verb"
    if lowered.endswith(("ous", "ive", "al", "ful", "less", "able", "ible")):
        return "adjective"
    if _is_word(text):
        return "noun"
    return "other"


def guess_token_type(text: str, language: str, palette: Optional[dict[str, Any]] = None) -> str:
    normalized = language_from_context(language, palette=palette, text=text)
    if normalized == "ja":
        guessed = _guess_japanese_type(text)
    elif normalized in {"zh", "yue"}:
        guessed = _guess_chinese_type(text)
    else:
        guessed = _guess_default_type(text)
    return _type_for_palette(guessed, palette, normalized)


def _base_parts(text: str) -> list[str]:
    return [match.group(0) for match in _TOKEN_RE.finditer(str(text or "")) if match.group(0)]


def _split_japanese_text(text: str) -> list[str]:
    parts = _base_parts(text)
    merged: list[str] = []
    idx = 0
    while idx < len(parts):
        part = parts[idx]
        next_part = parts[idx + 1] if idx + 1 < len(parts) else ""
        if _is_cjk(part) and _is_hiragana(next_part) and next_part not in _JA_PARTICLES:
            merged.append(part + next_part)
            idx += 2
            continue
        merged.append(part)
        idx += 1
    return merged


def _split_chinese_text(text: str) -> list[str]:
    parts: list[str] = []
    for part in _base_parts(text):
        if _is_cjk(part):
            parts.extend(part)
        else:
            parts.append(part)
    return parts


def split_text_for_language(text: str, language: str) -> list[str]:
    normalized = language_from_context(language, text=text)
    if normalized == "ja":
        return _split_japanese_text(text)
    if normalized in {"zh", "yue"}:
        return _split_chinese_text(text)
    return _base_parts(text)


def has_content_token(tokens_payload: Any) -> bool:
    if not isinstance(tokens_payload, list):
        return False
    for token in tokens_payload:
        if not isinstance(token, dict):
            continue
        token_type = str(token.get("type") or token.get("pos") or token.get("tag") or "").strip().lower()
        token_text = token.get("text") or token.get("word") or token.get("token") or ""
        if token_type == "speaker":
            continue
        if str(token_text).strip():
            return True
    return False


def is_speaker_only_tokens(tokens_payload: Any) -> bool:
    if not isinstance(tokens_payload, list) or not tokens_payload:
        return False
    saw_speaker = False
    for token in tokens_payload:
        if not isinstance(token, dict):
            return False
        token_type = str(token.get("type") or token.get("pos") or token.get("tag") or "").strip().lower()
        token_text = token.get("text") or token.get("word") or token.get("token") or ""
        if token_type == "speaker":
            saw_speaker = True
            continue
        if str(token_text).strip():
            return False
    return saw_speaker


def _normalize_token_dict(
    token: dict[str, Any],
    language: str,
    palette: Optional[dict[str, Any]],
) -> dict[str, Any] | None:
    token_type = token.get("type") or token.get("pos") or token.get("tag")
    text = token.get("text") or token.get("word") or token.get("token")
    if text is None or text == "":
        if str(token_type or "").strip().lower() != "speaker":
            return None
        text = ""
    text = str(text)
    ruby = token.get("ruby") or token.get("reading") or token.get("furigana") or token.get("pinyin")
    normalized_type = str(token_type or "").strip()
    if normalized_type.lower() == "speaker":
        normalized_type = "speaker"
    else:
        normalized_type = normalized_type or guess_token_type(text, language, palette)
        normalized_type = _type_for_palette(normalized_type, palette, language)

    row: dict[str, Any] = {"text": text, "type": normalized_type}
    if ruby is not None:
        row["ruby"] = str(ruby)
    color = token.get("color")
    if isinstance(color, str) and color.strip():
        row["color"] = color
    return row


def normalize_tokens_payload(
    tokens_payload: Any,
    *,
    text: str = "",
    language: Any = None,
    text_key: Any = None,
    palette: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    resolved_language = language_from_context(language, text_key, palette, text)
    normalized: list[dict[str, Any]] = []
    if isinstance(tokens_payload, list):
        for token in tokens_payload:
            if not isinstance(token, dict):
                continue
            row = _normalize_token_dict(token, resolved_language, palette)
            if row:
                normalized.append(row)

    visible = [token for token in normalized if token.get("type") != "speaker" and str(token.get("text") or "").strip()]
    if len(visible) == 1 and text and visible[0].get("text") == text and not visible[0].get("ruby"):
        speakers = [token for token in normalized if token.get("type") == "speaker"]
        return speakers + tokens_from_text(text, language=resolved_language, palette=palette)
    return normalized


def tokens_from_text(
    text: str,
    *,
    language: Any = None,
    text_key: Any = None,
    palette: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    resolved_language = language_from_context(language, text_key, palette, text)
    tokens: list[dict[str, Any]] = []
    for part in split_text_for_language(text, resolved_language):
        token_type = guess_token_type(part, resolved_language, palette)
        tokens.append({"text": part, "type": token_type})
    return tokens


def tokens_from_pairs(
    pairs: Any,
    *,
    language: Any = None,
    text_key: Any = None,
    palette: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    tokens: list[dict[str, Any]] = []
    if not isinstance(pairs, list):
        return tokens
    for pair in pairs:
        if not isinstance(pair, (list, tuple)) or len(pair) < 1:
            continue
        text = str(pair[0] or "")
        if not text:
            continue
        ruby = str(pair[1]) if len(pair) > 1 and pair[1] is not None else None
        resolved_language = language_from_context(language, text_key, palette, text)
        row = {
            "text": text,
            "type": guess_token_type(text, resolved_language, palette),
        }
        if ruby:
            row["ruby"] = ruby
        tokens.append(row)
    return tokens
