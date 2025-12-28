import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# Upload folder for incoming videos. Override with LAZYEDIT_UPLOAD_DIR if needed.
UPLOAD_FOLDER = os.getenv("LAZYEDIT_UPLOAD_DIR") or str(BASE_DIR / "DATA")

# Backend port (matches existing env usage).
PORT = int(os.getenv("PORT") or os.getenv("LAZYEDIT_PORT") or 8787)
