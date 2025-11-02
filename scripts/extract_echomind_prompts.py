#!/usr/bin/env python3
"""
Extract prompt JSONs from the external `echomind` symlink and emit Markdown per language.

Creates files under `docs/prompts/<lang>.md` for:
  english/chinese/cantonese/japanese/korean/arabic/vietnamese/french/spanish

Heuristics:
  - Scans *.json and *.json5
  - If top-level contains keys like "prompt", "prompts", "system", "user", it is included.
  - Language inferred from path or keys containing language names or codes.
  - If language cannot be inferred, file is listed under a special section in english.md for manual triage.

This script does not modify the `echomind` repository—only reads it.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

ROOT = Path(__file__).resolve().parents[1]
ECHO = ROOT / "echomind"
OUT_DIR = ROOT / "docs" / "prompts"

LANG_MAP = {
    "english": "english",
    "en": "english",
    "chinese": "chinese",
    "zh": "chinese",
    "cantonese": "cantonese",
    "yue": "cantonese",
    "japanese": "japanese",
    "ja": "japanese",
    "korean": "korean",
    "ko": "korean",
    "arabic": "arabic",
    "ar": "arabic",
    "vietnamese": "vietnamese",
    "vi": "vietnamese",
    "french": "french",
    "fr": "french",
    "spanish": "spanish",
    "es": "spanish",
}

TARGET_LANGS = [
    "english",
    "chinese",
    "cantonese",
    "japanese",
    "korean",
    "arabic",
    "vietnamese",
    "french",
    "spanish",
]

PROMPT_KEYS = {"prompt", "prompts", "system", "user", "assistant", "instruction", "messages"}


def infer_lang_from_path(path: Path) -> str | None:
    lower = str(path).lower()
    for key, lang in LANG_MAP.items():
        if re.search(rf"[\\/_\-\.]({re.escape(key)})[\\/_\-\.]", lower):
            return lang
    return None


def infer_lang_from_json(obj: Any) -> str | None:
    if isinstance(obj, dict):
        text = json.dumps(obj, ensure_ascii=False).lower()
        for key, lang in LANG_MAP.items():
            if re.search(rf"\b{re.escape(key)}\b", text):
                return lang
    return None


def collect_prompts() -> Dict[str, List[Tuple[Path, Any]]]:
    by_lang: Dict[str, List[Tuple[Path, Any]]] = {l: [] for l in TARGET_LANGS}
    unknown: List[Tuple[Path, Any]] = []

    if not ECHO.exists():
        raise SystemExit(f"Missing symlink: {ECHO}")

    for path in ECHO.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        # Find if file looks like prompt config
        looks_like_prompt = False
        if isinstance(data, dict):
            for k in PROMPT_KEYS:
                if k in data:
                    looks_like_prompt = True
                    break
        if not looks_like_prompt:
            continue

        lang = infer_lang_from_path(path) or infer_lang_from_json(data)
        if lang in by_lang:
            by_lang[lang].append((path, data))
        else:
            unknown.append((path, data))

    return by_lang | {"_unknown": unknown}  # type: ignore[return-value]


def write_markdown(by_lang: Dict[str, List[Tuple[Path, Any]]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for lang in TARGET_LANGS:
        out = OUT_DIR / f"{lang}.md"
        items = by_lang.get(lang, [])
        lines: List[str] = []
        lines.append(f"# {lang.title()} Prompts\n")
        if not items:
            lines.append("No prompts discovered yet.\n")
        for p, data in items:
            rel = os.path.relpath(p, ROOT)
            lines.append(f"## Source: `{rel}`\n")
            lines.append("```json")
            try:
                lines.append(json.dumps(data, ensure_ascii=False, indent=2))
            except Exception:
                lines.append("{ /* unable to serialize */ }")
            lines.append("````\n".replace("````", "```"))
        out.write_text("\n".join(lines), encoding="utf-8")

    # Unknowns go to english.md under a special heading for triage
    unknown_items = by_lang.get("_unknown", [])
    if unknown_items:
        eng_path = OUT_DIR / "english.md"
        content = eng_path.read_text(encoding="utf-8") if eng_path.exists() else "# English Prompts\n\n"
        content += "\n## Unclassified\n"
        for p, data in unknown_items:
            rel = os.path.relpath(p, ROOT)
            content += f"\n### Source: `{rel}`\n\n````json\n"
            try:
                content += json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                content += "{ /* unable to serialize */ }"
            content += "\n````\n".replace("````", "```")
        eng_path.write_text(content, encoding="utf-8")


def main() -> int:
    by_lang = collect_prompts()
    write_markdown(by_lang)
    print(f"Wrote prompt docs to: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

