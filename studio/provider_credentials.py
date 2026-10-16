"""Load explicitly configured server credentials without exposing their values."""
import os
from pathlib import Path
import stat


def load_openai_key_file():
    filename = os.environ.get('OPENAI_API_KEY_FILE')
    if not filename:
        return False
    path = Path(filename)
    with path.open('r') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077:
            raise ValueError('OpenAI key file must be an owner-only regular file')
        key = stream.read(4097).strip()
    if not key or len(key) > 4096 or any(c.isspace() for c in key):
        raise ValueError('OpenAI key file is invalid')
    os.environ['OPENAI_API_KEY'] = key
    return True
