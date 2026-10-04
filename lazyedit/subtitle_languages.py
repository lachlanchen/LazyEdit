"""Subtitle targets, independent of UI locales and Whisper's input languages."""
from functools import lru_cache
import re

from babel import Locale
from babel.core import UnknownLocaleError

from lazyedit.languages import LANGUAGES, TO_LANGUAGE_CODE


class SubtitleLanguageError(ValueError):
    """An explicit subtitle-language choice cannot be used safely."""


# Deliberately exclude extensions/private-use tags and path-like input. A custom
# target must have a CLDR language/script/region name the translator can use.
TAG = re.compile(r"[a-zA-Z]{2,3}(?:-[a-zA-Z]{4})?(?:-(?:[a-zA-Z]{2}|[0-9]{3}))?\Z")
ALIASES = {
    "zh": "zh-Hant", "chinese": "zh-Hant", "mandarin": "zh-Hant",
    "zh-tw": "zh-Hant", "zh-hk": "zh-Hant", "zh-mo": "zh-Hant",
    "zh-cn": "zh-Hans", "zh-yue": "yue", "zh-yue-hk": "yue",
    "türkçe": "tr",
}
CANONICAL_CODES = {code.lower(): code for code in LANGUAGES}
READINGS = {"ja": "furigana", "zh-Hant": "pinyin", "zh-Hans": "pinyin",
            "yue": "jyutping", "ko": "hanja", "vi": "chu-han"}


@lru_cache(maxsize=512)
def _resolve(raw: str) -> str | None:
    lowered = raw.lower().replace("_", "-")
    if lowered in ALIASES:
        return ALIASES[lowered]
    if lowered in CANONICAL_CODES:
        return CANONICAL_CODES[lowered]
    named = TO_LANGUAGE_CODE.get(raw.lower())
    if named:
        return ALIASES.get(named, named)
    if not TAG.fullmatch(raw.replace("_", "-")):
        return None
    try:
        locale = Locale.parse(raw.replace("_", "-"), sep="-", resolve_likely_subtags=False)
    except (ValueError, UnknownLocaleError):
        return None
    return str(locale).replace("_", "-")


def resolve_subtitle_language(value: object) -> str | None:
    return _resolve(value.strip()) if isinstance(value, str) and value.strip() else None


def require_subtitle_language(value: object) -> str:
    code = resolve_subtitle_language(value)
    if not code:
        raise SubtitleLanguageError(f"Unsupported subtitle language: {value!r}. Use a known language code such as pt-BR or sr-Latn.")
    return code


def normalize_subtitle_languages(value, *, default=None) -> list[str]:
    if value is None:
        return list(default or [])
    if not isinstance(value, (list, tuple)):
        raise SubtitleLanguageError("Subtitle languages must be an ordered list of language codes")
    if len(value) > 40:
        raise SubtitleLanguageError("Too many subtitle languages (maximum 40)")
    codes = []
    for item in value:
        code = require_subtitle_language(item)
        if code not in codes:
            codes.append(code)
    # An explicit empty choice stays empty; only missing settings inherit defaults.
    return codes


def subtitle_languages_from_options(payload: dict, *, default=None) -> list[str]:
    choices = []
    for key in ("translationLanguages", "translation_languages"):
        if key not in payload:
            continue
        if not isinstance(payload[key], (list, tuple)):
            raise SubtitleLanguageError(f"{key} must be an ordered language list")
        choices.append(normalize_subtitle_languages(payload[key]))
    if len(choices) == 2 and choices[0] != choices[1]:
        raise SubtitleLanguageError("Conflicting subtitle-language choices")
    return choices[0] if choices else list(default or [])


@lru_cache(maxsize=512)
def _description(code: str) -> dict:
    name = LANGUAGES.get(code, code).replace("_", " ").title()
    rtl = code.split("-")[0] in {"ar", "he", "fa", "ur", "yi", "ps", "sd"}
    try:
        locale = Locale.parse(code, sep="-", resolve_likely_subtags=False)
        name, rtl = locale.get_display_name("en"), locale.character_order == "right-to-left"
    except (ValueError, UnknownLocaleError):
        pass  # Keep legacy registered targets such as Whisper's jw.
    result = {"code": code, "name": name, "plugin": LANGUAGES.get(code, "generic"),
            "rtl": rtl, "grammarColors": True, "reading": READINGS.get(code),
            "requiresPreview": True}
    if rtl:
        result["renderingWarning"] = "Review the preview: grammar-token word order in right-to-left subtitles is not yet verified."
    return result


def subtitle_language(value: object) -> dict:
    return dict(_description(require_subtitle_language(value)))


def list_subtitle_languages() -> list[dict]:
    # Legacy ASR names are read-only seeds, not a target whitelist. Extra known
    # locales are resolved on demand without global mutation or registration DBs.
    codes = dict.fromkeys(require_subtitle_language(code) for code in [*LANGUAGES, "fil", "eo"])
    return [subtitle_language(code) for code in codes]


def subtitle_language_family(value: object) -> str | None:
    code = resolve_subtitle_language(value)
    if not code:
        return None
    base = code.split("-")[0]
    return "jv" if base == "jw" else base
