import time

import psycopg2

from lazyedit import db as ldb


def test_can_connect_and_ensure_schema():
    # Should not raise
    ldb.ensure_schema()
    with ldb.get_cursor() as cur:
        # Verify key tables exist
        cur.execute(
            """
            SELECT to_regclass('public.videos') IS NOT NULL,
                   to_regclass('public.captions') IS NOT NULL
            """
        )
        exists_videos, exists_captions = cur.fetchone()
        assert exists_videos and exists_captions


def test_insert_and_query_rollback():
    """Insert sample rows within a transaction and roll back to avoid side effects."""
    title = f"pytest-sample-{int(time.time())}"
    conn = ldb.connect()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO videos (file_path, title) VALUES (%s, %s) RETURNING id",
                    ("DATA/sample.mp4", title),
                )
                (video_id,) = cur.fetchone()
                cur.execute(
                    """
                    INSERT INTO captions (video_id, language_code, subtitle_path)
                    VALUES (%s, %s, %s) RETURNING id
                    """,
                    (video_id, "en", "DATA/sample.srt"),
                )
                (caption_id,) = cur.fetchone()

                # Query back
                cur.execute(
                    "SELECT language_code, subtitle_path FROM captions WHERE video_id = %s",
                    (video_id,),
                )
                rows = cur.fetchall()
                assert rows == [("en", "DATA/sample.srt")]

            # Explicitly roll back entire transaction
            conn.rollback()
    finally:
        conn.close()

