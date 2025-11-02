import os
import psycopg2
from contextlib import contextmanager


def get_db_url() -> str:
    """
    Resolve the database URL for LazyEdit.
    Priority:
      1. LAZYEDIT_DATABASE_URL
      2. DATABASE_URL
      3. Local socket default to dbname=lazyedit_db
    """
    url = os.getenv("LAZYEDIT_DATABASE_URL") or os.getenv("DATABASE_URL")
    if url:
        return url
    # Default local connection via peer auth
    return "dbname=lazyedit_db"


def connect():
    """Create a new psycopg2 connection using the resolved DB URL."""
    url = get_db_url()
    return psycopg2.connect(url)


@contextmanager
def get_cursor(commit: bool = False):
    """
    Context manager yielding a cursor and handling commit/rollback.
    If commit=True, commits on success; always rolls back on exceptions.
    """
    conn = connect()
    try:
        cur = conn.cursor()
        try:
            yield cur
            if commit:
                conn.commit()
        finally:
            cur.close()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def ensure_schema():
    """Create minimal tables to track videos and captions if missing."""
    ddl_statements = [
        # Videos table stores basic metadata; extend as needed
        """
        CREATE TABLE IF NOT EXISTS videos (
            id SERIAL PRIMARY KEY,
            file_path TEXT NOT NULL,
            title TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        # Captions table for multilingual subtitle files
        """
        CREATE TABLE IF NOT EXISTS captions (
            id SERIAL PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            language_code TEXT NOT NULL,
            subtitle_path TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        # Helpful index for looking up captions by video and language
        """
        CREATE INDEX IF NOT EXISTS idx_captions_video_lang
            ON captions (video_id, language_code);
        """,
    ]

    with get_cursor(commit=True) as cur:
        for ddl in ddl_statements:
            cur.execute(ddl)


def add_video(file_path: str, title: str | None = None) -> int:
    """Insert a video row and return its ID."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO videos (file_path, title) VALUES (%s, %s) RETURNING id",
            (file_path, title),
        )
        (video_id,) = cur.fetchone()
        return video_id


def add_caption(video_id: int, language_code: str, subtitle_path: str) -> int:
    """Insert a caption row and return its ID."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO captions (video_id, language_code, subtitle_path)
            VALUES (%s, %s, %s) RETURNING id
            """,
            (video_id, language_code, subtitle_path),
        )
        (caption_id,) = cur.fetchone()
        return caption_id


def get_captions_for_video(video_id: int) -> list[tuple]:
    """Return list of (id, language_code, subtitle_path) for the video."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, language_code, subtitle_path FROM captions WHERE video_id = %s",
            (video_id,),
        )
        return cur.fetchall()

