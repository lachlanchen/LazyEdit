"""Publication category routing for LazyEdit publish bundles."""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Any


CATEGORY_SIMPLELIFE = "simplelife"
CATEGORY_LALACHAN = "lalachan"
CATEGORY_MUSIC = "music"

_CATEGORY_ALIASES = {
    "simple": CATEGORY_SIMPLELIFE,
    "simplelife": CATEGORY_SIMPLELIFE,
    "simple life": CATEGORY_SIMPLELIFE,
    "简单生活": CATEGORY_SIMPLELIFE,
    "life": CATEGORY_SIMPLELIFE,
    "lalachan": CATEGORY_LALACHAN,
    "lala": CATEGORY_LALACHAN,
    "lala chan": CATEGORY_LALACHAN,
    "lala-chan": CATEGORY_LALACHAN,
    "lala_chAN".lower(): CATEGORY_LALACHAN,
    "啦啦侠": CATEGORY_LALACHAN,
    "music": CATEGORY_MUSIC,
    "musica": CATEGORY_MUSIC,
    "musia": CATEGORY_MUSIC,
    "慕莎": CATEGORY_MUSIC,
    "歌曲": CATEGORY_MUSIC,
    "音乐": CATEGORY_MUSIC,
}


def _env(name: str, default: str) -> str:
    return os.getenv(name, default).strip() or default


def normalize_publish_category(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    lowered = re.sub(r"[-_]+", " ", text.lower())
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return _CATEGORY_ALIASES.get(text) or _CATEGORY_ALIASES.get(lowered)


def publish_category_names(category: str) -> dict[str, str]:
    normalized = normalize_publish_category(category) or CATEGORY_SIMPLELIFE
    if normalized == CATEGORY_LALACHAN:
        return {
            "youtube_playlist": _env("LAZYEDIT_YOUTUBE_PLAYLIST_LALACHAN", "LALACHAN"),
            "shipinhao_collection": _env("LAZYEDIT_SHIPINHAO_COLLECTION_LALACHAN", "啦啦侠"),
        }
    if normalized == CATEGORY_MUSIC:
        return {
            "youtube_playlist": _env("LAZYEDIT_YOUTUBE_PLAYLIST_MUSIC", "Musia"),
            "shipinhao_collection": _env("LAZYEDIT_SHIPINHAO_COLLECTION_MUSIC", "Musia"),
        }
    return {
        "youtube_playlist": _env("LAZYEDIT_YOUTUBE_PLAYLIST_SIMPLELIFE", "SimpleLife"),
        "shipinhao_collection": _env("LAZYEDIT_SHIPINHAO_COLLECTION_SIMPLELIFE", "简单生活"),
    }


def infer_publish_category(
    metadata: dict[str, Any] | None = None,
    *,
    media_kind: str = "video",
    source_path: str | None = None,
    explicit: Any = None,
) -> tuple[str, str]:
    """Return (category, reason) for publish routing.

    Explicit fields are authoritative. Inference is intentionally conservative:
    unknown personal recordings remain SimpleLife.
    """

    explicit_category = normalize_publish_category(explicit)
    if explicit_category:
        return explicit_category, "explicit"

    metadata = metadata or {}
    for key in (
        "publish_category",
        "publishCategory",
        "content_category",
        "contentCategory",
        "series",
        "project",
    ):
        category = normalize_publish_category(metadata.get(key))
        if category:
            return category, f"metadata.{key}"

    if normalize_publish_category(media_kind) == CATEGORY_MUSIC:
        return CATEGORY_MUSIC, "media_kind"

    text_parts = [
        source_path or "",
        metadata.get("source_video_path") or "",
        metadata.get("source_path") or "",
        metadata.get("source_repo") or "",
        metadata.get("prompt_file") or "",
        metadata.get("title") or "",
        metadata.get("brief_description") or "",
        metadata.get("middle_description") or "",
        metadata.get("long_description") or "",
    ]
    text = "\n".join(str(part) for part in text_parts if part).lower()

    if "/lalachan/" in text or "projectslfs/lalachan" in text:
        return CATEGORY_LALACHAN, "source_path"
    if any(token in text for token in (
        "lalachan",
        "lala xia",
        "lala chan",
        "啦啦侠",
        "阿芽酱",
        "飒飒君",
        "小云雀",
        "xiaoyunque",
        "seedance",
        "duanpian",
    )):
        return CATEGORY_LALACHAN, "story_keywords"

    return CATEGORY_SIMPLELIFE, "default"


def apply_publish_category(
    metadata: dict[str, Any] | None,
    *,
    media_kind: str = "video",
    source_path: str | None = None,
    publish_category: Any = None,
    youtube_playlist: str | None = None,
    shipinhao_collection: str | None = None,
) -> dict[str, Any]:
    output = dict(metadata or {})
    category, reason = infer_publish_category(
        output,
        media_kind=media_kind,
        source_path=source_path,
        explicit=publish_category,
    )
    names = publish_category_names(category)
    youtube_name = (youtube_playlist or output.get("youtube_playlist") or output.get("playlist_name") or names["youtube_playlist"])
    shipinhao_name = (
        shipinhao_collection
        or output.get("shipinhao_collection")
        or output.get("shipinhao_album")
        or names["shipinhao_collection"]
    )
    output["publish_category"] = category
    output["publish_category_reason"] = reason
    output["youtube_playlist"] = str(youtube_name).strip()
    output["playlist_name"] = str(youtube_name).strip()
    output["shipinhao_collection"] = str(shipinhao_name).strip()
    return output
