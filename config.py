import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def _load_env():
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env()

# Upload folder for incoming videos. Override with LAZYEDIT_UPLOAD_DIR if needed.
UPLOAD_FOLDER = os.getenv("LAZYEDIT_UPLOAD_DIR") or str(BASE_DIR / "DATA")

# Backend port (matches existing env usage).
PORT = int(os.getenv("PORT") or os.getenv("LAZYEDIT_PORT") or 8787)

# Autopublish endpoint (AutoPublication service).
AUTOPUBLISH_URL = (
    os.getenv("LAZYEDIT_AUTOPUBLISH_URL")
    or os.getenv("AUTOPUBLISH_URL")
    or "http://localhost:8081/publish"
)
AUTOPUBLISH_TIMEOUT = int(os.getenv("LAZYEDIT_AUTOPUBLISH_TIMEOUT") or 60)

# Captioning configuration (frame captions).
CAPTION_PYTHON = os.getenv("LAZYEDIT_CAPTION_PYTHON") or "/home/lachlan/miniconda3/envs/caption/bin/python"
CAPTION_PRIMARY_SCRIPT = (
    os.getenv("LAZYEDIT_CAPTION_PRIMARY_SCRIPT")
    or "/home/lachlan/Projects/vit-gpt2-image-captioning/vit_captioner_video.py"
)

_default_primary_root = None
for root in (
    "/home/lachlan/ProjectsLFS/vit-gpt2-image-captioning",
    "/home/lachlan/Projects/vit-gpt2-image-captioning",
):
    if Path(root).is_dir():
        _default_primary_root = root
        break
CAPTION_PRIMARY_ROOT = os.getenv("LAZYEDIT_CAPTION_PRIMARY_ROOT") or _default_primary_root

CAPTION_FALLBACK_SCRIPT = (
    os.getenv("LAZYEDIT_CAPTION_FALLBACK_SCRIPT")
    or "/home/lachlan/Projects/image_captioning/clip-gpt-captioning/src/v2c.py"
)

_default_fallback_cwd = None
if (BASE_DIR / "weights" / "large" / "model.pt").exists():
    _default_fallback_cwd = str(BASE_DIR)
else:
    for root in (
        "/home/lachlan/ProjectsLFS/image_captioning/clip-gpt-captioning",
        "/home/lachlan/Projects/image_captioning/clip-gpt-captioning",
    ):
        if Path(root).is_dir():
            _default_fallback_cwd = root
            break
CAPTION_FALLBACK_CWD = os.getenv("LAZYEDIT_CAPTION_FALLBACK_CWD") or _default_fallback_cwd
