#!/usr/bin/env python3
"""
Quick smoke test for LazyEdit Postgres usage.

Runs the following against the `lazyedit_db` database (or LAZYEDIT_DATABASE_URL):
  - Ensures tables exist
  - Inserts a sample video and caption
  - Reads them back and prints results
  - Cleans up the inserted rows

Usage:
  python db_smoke_test.py

Optionally set LAZYEDIT_DATABASE_URL or DATABASE_URL for non-default connections.
"""
from __future__ import annotations

import time
from lazyedit import db as ldb


def main() -> int:
    # Ensure base schema exists
    ldb.ensure_schema()

    title = f"Sample Video {int(time.time())}"
    video_id = ldb.add_video("DATA/sample.mp4", title)
    caption_id = ldb.add_caption(video_id, "en", "DATA/sample.srt")

    captions = ldb.get_captions_for_video(video_id)
    print(f"Inserted video_id={video_id}, caption_id={caption_id}")
    print(f"Fetched captions: {captions}")

    # Clean up: delete rows we just created
    with ldb.get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM captions WHERE video_id = %s", (video_id,))
        cur.execute("DELETE FROM videos WHERE id = %s", (video_id,))

    print("Cleanup complete; smoke test OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

