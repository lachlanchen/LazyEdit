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
    entries = load_dictionary() if entries is None else entries
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('tokens'), list):
            continue
        normalized = []
        for token in item['tokens']:
            if not isinstance(token, dict) or any(not isinstance(token.get(k), str)
                    for k in ('surface', 'word', 'reading', 'type')):
                normalized.append(token)
                continue
            surface, word = token['surface'], token['word']
            if word == surface and re.fullmatch(r'[가-힣]+', surface) and re.fullmatch(
                    r'[A-Za-z -]+', token['reading']):
                try:
                    from koroman import romanize
                    token = {**token, 'reading': romanize(surface, use_pronunciation_rules=True)}
                except (ImportError, ValueError):
                    pass
            # A native prefix may surround an already selected Sino-Korean root.
            # Preserve it rather than interpreting the whole token as Hanja.
            prefixed = re.fullmatch(r'([가-힣]+)([\u3400-\u4dbf\u4e00-\u9fff]+)([가-힣]*)', word)
            if prefixed:
                prefix, selected, ending = prefixed.groups()
                stop = len(surface) - len(ending) if ending else len(surface)
                native = surface[len(prefix):stop]
                if (surface == prefix + native + ending and native
                        and selected in {c['word'] for c in entries.get(native, [])}):
                    try:
                        from koroman import romanize
                        parts = [(prefix, prefix, romanize(prefix, use_pronunciation_rules=True)),
                                 (native, selected, native)]
                        if ending:
                            parts.append((ending, ending, romanize(ending, use_pronunciation_rules=True)))
                    except (ImportError, ValueError):
                        parts = []
                    if parts and all(reading for _, _, reading in parts):
                        normalized.extend({**token, 'surface': native_part, 'word': display,
                                           'reading': reading}
                                          for native_part, display, reading in parts)
                        continue
            mixed = re.fullmatch(r'([\u3400-\u4dbf\u4e00-\u9fff]+)([가-힣]+)', word)
            root, suffix = mixed.groups() if mixed else (word, '')
            native_root = surface[:-len(suffix)] if suffix and surface.endswith(suffix) else ''
            if HAN.fullmatch(word) and re.fullmatch(r'[가-힣]+', surface):
                token = {**token, 'reading': surface}
                # A model can omit an ending from word while retaining it in
                # surface/ruby (축하해 -> 祝賀). Preserve that visible ending too.
                if word not in {c['word'] for c in entries.get(surface, [])}:
                    for end in range(len(surface) - 1, 1, -1):
                        if word in {c['word'] for c in entries.get(surface[:end], [])}:
                            native_root, suffix = surface[:end], surface[end:]
                            break
            if suffix and root in {c['word'] for c in entries.get(native_root, [])}:
                try:
                    from koroman import romanize
                    reading = romanize(suffix, use_pronunciation_rules=True)
                except (ImportError, ValueError):
                    reading = ''
                if isinstance(reading, str) and re.search(r'[A-Za-z]', reading):
                    normalized.append({**token, 'surface': native_root,
                                       'word': root, 'reading': native_root})
                    token = {**token, 'surface': suffix, 'word': suffix,
                             'reading': reading}
            normalized.append(token)
        item['tokens'] = normalized


if __name__ == "__main__":
    print(install_dictionary())
