import subprocess
from typing import Any


try:
    from opencc import OpenCC
except Exception:  # pragma: no cover - optional dependency
    OpenCC = None


_OPENCC = None
if OpenCC:
    try:
        _OPENCC = OpenCC("t2s.json")
    except Exception:
        try:
            _OPENCC = OpenCC("t2s")
        except Exception:
            _OPENCC = None


def _convert_with_opencc(text: str) -> str | None:
    if not _OPENCC:
        return None
    try:
        return _OPENCC.convert(text)
    except Exception:
        return None


def _convert_with_cli(text: str) -> str | None:
    try:
        result = subprocess.run(
            ["opencc", "-c", "t2s"],
            input=text,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout
    except Exception:
        return None


def convert_traditional_to_simplified(text: str) -> str:
    if not text:
        return text
    converted = _convert_with_opencc(text)
    if converted is not None:
        return converted
    converted = _convert_with_cli(text)
    if converted is not None:
        return converted
    return text


def convert_items_to_simplified(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    converted_items: list[dict[str, Any]] = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        updated = dict(item)
        if "zh" in updated and isinstance(updated["zh"], str):
            updated["zh"] = convert_traditional_to_simplified(updated["zh"])
        converted_items.append(updated)
    return converted_items
