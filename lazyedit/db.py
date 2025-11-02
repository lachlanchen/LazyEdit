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
    """Create minimal tables to track videos, captions, and generated videos if missing."""
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
        # Generated videos (e.g., Sora jobs) cache prompts and output paths
        """
        CREATE TABLE IF NOT EXISTS generated_videos (
            id SERIAL PRIMARY KEY,
            job_id TEXT UNIQUE NOT NULL,
            model TEXT NOT NULL,
            prompt TEXT NOT NULL,
            size TEXT,
            seconds INTEGER,
            status TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            file_path TEXT,
            error TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMPTZ
        );
        """,
        # Backfill/updates for evolving schema
        "ALTER TABLE generated_videos ADD COLUMN IF NOT EXISTS request_hash TEXT;",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_generated_videos_request_hash ON generated_videos (request_hash);",
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


# --- Generated video helpers (Sora) ---

def record_generated_video(
    *,
    job_id: str,
    model: str,
    prompt: str,
    size: str | None,
    seconds: int | None,
    status: str,
    progress: int | None = None,
    request_hash: str | None = None,
) -> None:
    ensure_schema()
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO generated_videos (job_id, model, prompt, size, seconds, status, progress, request_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (job_id) DO UPDATE SET
              model = EXCLUDED.model,
              prompt = EXCLUDED.prompt,
              size = EXCLUDED.size,
              seconds = EXCLUDED.seconds,
              status = EXCLUDED.status,
              progress = COALESCE(EXCLUDED.progress, generated_videos.progress),
              request_hash = COALESCE(EXCLUDED.request_hash, generated_videos.request_hash)
            """,
            (job_id, model, prompt, size, seconds, status, progress if progress is not None else 0, request_hash),
        )


def update_generated_video(
    *,
    job_id: str,
    status: str | None = None,
    progress: int | None = None,
    file_path: str | None = None,
    error: str | None = None,
    completed_at: str | None = None,
) -> None:
    ensure_schema()
    sets = []
    values = []
    if status is not None:
        sets.append("status = %s")
        values.append(status)
    if progress is not None:
        sets.append("progress = %s")
        values.append(progress)
    if file_path is not None:
        sets.append("file_path = %s")
        values.append(file_path)
    if error is not None:
        sets.append("error = %s")
        values.append(error)
    if completed_at is not None:
        sets.append("completed_at = to_timestamp(%s)")
        values.append(completed_at)
    if not sets:
        return
    values.append(job_id)
    query = f"UPDATE generated_videos SET {', '.join(sets)} WHERE job_id = %s"
    with get_cursor(commit=True) as cur:
        cur.execute(query, tuple(values))


def find_generated_by_hash(request_hash: str):
    """Return the most recent row for a given request hash, or None."""
    ensure_schema()
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT job_id, status, progress, file_path, error, created_at, completed_at
            FROM generated_videos
            WHERE request_hash = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (request_hash,),
        )
        row = cur.fetchone()
        return row
