"""Small local Hanja candidate lookup; the LLM chooses the contextual meaning.

libhangul's dictionary is an input-method candidate list, NOT proof that a
matching Hangul word is Sino-Korean. Never replace text from this list alone.
The downloaded file retains its BSD-3-Clause notice and stays outside Git.
"""
from functools import lru_cache
import hashlib
import logging
import os
from pathlib import Path
import re
import tempfile
from threading import Lock
from urllib.request import urlopen

from lazyedit.subtitle_annotations import HAN

REVISION = "5094421d9586294b2aad09924b9a54e2e6060f06"
URL = f"https://raw.githubusercontent.com/libhangul/libhangul/{REVISION}/data/hanja/hanja.txt"
SHA256 = "b1004034589f1357daaea3534a6136f6b5ef825afa8779886b20f0b7908bbe3b"
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "cache/dictionaries/libhangul-hanja.txt"
HANGUL_WORD = re.compile(r"[가-힣]{2,}")
_lock = Lock()
_download_attempted = False


def install_dictionary(path=DEFAULT_PATH):
    """Download one pinned, size-limited snapshot and atomically install it."""
    path = Path(path)
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == SHA256:
        return path
    with urlopen(URL, timeout=15) as response:
        data = response.read(8 * 1024 * 1024 + 1)
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("Hanja dictionary checksum mismatch")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path


def parse_dictionary(lines):
    """Keep whole Hangul words and all-Han candidates, not syllable guessing."""
    entries = {}
    for line in lines:
        parts = line.rstrip("\r\n").split(":", 2)
        if len(parts) != 3:
            continue
        surface, word, meaning = parts
        if not HANGUL_WORD.fullmatch(surface) or not HAN.fullmatch(word):
            continue
        candidate = {"word": word}
        if meaning:
            candidate["meaning"] = meaning[:100]
        candidates = entries.setdefault(surface, [])
        if candidate not in candidates:
            candidates.append(candidate)
    return entries


@lru_cache(maxsize=2)
def _read_dictionary(path, mtime_ns):
    with open(path, encoding="utf-8") as handle:
        return parse_dictionary(handle)


def load_dictionary():
    global _download_attempted
    path = Path(os.environ.get("LAZYEDIT_HANJA_DICTIONARY", DEFAULT_PATH))
    # First-use setup is shared by concurrent subtitle workers. Offline failure
    # falls back to the normal LLM annotations, with no repeated network waits.
    with _lock:
        if not path.exists() and not _download_attempted:
            _download_attempted = True
            try:
                if path == DEFAULT_PATH:
                    install_dictionary(path)
                else:
                    raise FileNotFoundError(path)
            except (OSError, ValueError) as exc:
                logging.warning("Hanja dictionary unavailable; using LLM annotations: %s", exc)
        if not path.exists():
            return {}
        try:
            return _read_dictionary(str(path), path.stat().st_mtime_ns)
        except (OSError, UnicodeError) as exc:
            logging.warning("Cannot read Hanja dictionary; using LLM annotations: %s", exc)
            return {}


def review_hints(items, entries=None):
    """Find missed/conflicting candidates without editing translation or tokens.

    Longest matches can find a root even if the LLM kept its particle attached.
    They are hints only: compounds, native homophones and names need context.
    Bound output to avoid putting a dictionary-sized prompt into an LLM call.
    """
    entries = load_dictionary() if entries is None else entries
    if not entries:
        return []
    hints = []
    for item_index, item in enumerate(items):
        text = item["ko"]
        spans = {}
        offset = 0
        for token in item["tokens"]:
            end = offset + len(token["surface"])
            spans[(offset, end)] = token["word"]
            offset = end
        for run in HANGUL_WORD.finditer(text):
            start = run.start()
            while start + 1 < run.end():
                for end in range(min(run.end(), start + 16), start + 1, -1):
                    surface = text[start:end]
                    candidates = entries.get(surface)
                    if not candidates:
                        continue
                    if spans.get((start, end)) not in {c["word"] for c in candidates}:
                        hints.append({"item": item_index, "start": start, "surface": surface,
                                      "candidates": candidates[:12]})
                        if len(hints) >= 12:
                            return hints
                    start = end
                    break
                else:
                    start += 1
    return hints


def normalize_selected_restorations(items, entries=None):
    """Repair formatting of Hanja already chosen by the model, not etymology.

    Pure Hanja gets its exact native surface as ruby. Split a mixed Hanja/Hangul
    token only when unchanged Hangul affixes align exactly and the selected
    root is a dictionary candidate. Never choose a different Han spelling.
    """
    if not isinstance(items, list):
        return
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('tokens'), list):
            continue
        normalized = []
        for token in item['tokens']:
            if not isinstance(token, dict) or any(not isinstance(token.get(k), str)
                    for k in ('surface', 'word', 'type')):
                normalized.append(token)
                continue
            surface, word = token['surface'], token['word']
            token = {**token, 'reading': token.get('reading', '')}
            if re.search(r'[가-힣]', surface) and not HAN.search(word):
                # A dictionary-form lemma (하다) is not the spoken surface (합니다).
                word = token['word'] = surface
            if word == surface:
                # Models choose meanings; local code supplies pronunciation.
                # Keep Latin names/numerals intact while romanizing Hangul runs.
                reading = re.sub(r'[가-힣]+', lambda m: romanize_native(m[0]) or m[0], surface)
                token['reading'] = reading if any(c.isalpha() for c in surface) else ''
            elif re.fullmatch(r'[가-힣]+', surface):
                if entries is None:
                    entries = load_dictionary()
                parts = _selected_parts(surface, word, entries)
                if parts:
                    normalized.extend({**token, 'surface': native, 'word': display,
                                       'reading': reading}
                                      for native, display, reading in parts)
                    continue
                if HAN.fullmatch(word):
                    token = {**token, 'reading': surface}
            normalized.append(token)
        item['tokens'] = normalized


@lru_cache(maxsize=4096)
def romanize_native(text):
    """Local pronunciation is repeatable and does not need another LLM call."""
    try:
        from koroman import romanize
        value = romanize(text, use_pronunciation_rules=True)
    except (ImportError, ValueError):
        return ''
    return value if isinstance(value, str) and re.fullmatch(r'[A-Za-z -]+', value) else ''


def _selected_parts(surface, word, entries):
    """Split a common selected root with native affixes; leave complex cases alone."""
    match = re.fullmatch(r'([가-힣]*)([\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+)([가-힣]*)', word)
    if not match:
        return None
    prefix, han, suffix = match.groups()

    def selected(native):
        return han in {candidate['word'] for candidate in entries.get(native, [])}
    if prefix or suffix:
        stop = len(surface) - len(suffix) if suffix else len(surface)
        native = surface[len(prefix):stop]
        if surface != prefix + native + suffix or not selected(native):
            return None
    elif selected(surface):
        native = surface
    else:
        # Some responses select a root but omit its native affixes from word.
        # Only restore those affixes if the root has one unambiguous placement.
        matches = []
        for start in range(len(surface)):
            for end in range(start + 2, min(len(surface), start + 16) + 1):
                if selected(surface[start:end]):
                    matches.append((surface[:start], surface[start:end], surface[end:]))
                    if len(matches) == 2:
                        return None
        if not matches:
            return None
        prefix, native, suffix = matches[0]
    parts = [(prefix, prefix), (native, han), (suffix, suffix)]
    result = [(native, display, native if HAN.fullmatch(display) else romanize_native(native))
              for native, display in parts if native]
    return result if all(reading for _, _, reading in result) else None


if __name__ == "__main__":
    print(install_dictionary())
