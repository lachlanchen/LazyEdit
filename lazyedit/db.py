import os
import json
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
            source TEXT,
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
        "ALTER TABLE videos ADD COLUMN IF NOT EXISTS source TEXT;",
        # Backfill/updates for evolving schema
        "ALTER TABLE generated_videos ADD COLUMN IF NOT EXISTS request_hash TEXT;",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_generated_videos_request_hash ON generated_videos (request_hash);",
        # Transcriptions table for raw speech-to-text outputs
        """
        CREATE TABLE IF NOT EXISTS transcriptions (
            id SERIAL PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            language_code TEXT NOT NULL,
            status TEXT NOT NULL,
            output_json_path TEXT,
            output_srt_path TEXT,
            output_md_path TEXT,
            error TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_transcriptions_video_created ON transcriptions (video_id, created_at DESC);",
        # Frame captions (visual captioning) outputs
        """
        CREATE TABLE IF NOT EXISTS frame_captions (
            id SERIAL PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            status TEXT NOT NULL,
            output_json_path TEXT,
            output_srt_path TEXT,
            output_md_path TEXT,
            error TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_frame_captions_video_created ON frame_captions (video_id, created_at DESC);",
        # Keyframe extraction outputs
        """
        CREATE TABLE IF NOT EXISTS keyframe_extractions (
            id SERIAL PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            status TEXT NOT NULL,
            output_dir TEXT,
            frame_count INTEGER,
            error TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_keyframe_extractions_video_created ON keyframe_extractions (video_id, created_at DESC);",
        # Subtitle translations (e.g., Japanese with furigana)
        """
        CREATE TABLE IF NOT EXISTS subtitle_translations (
            id SERIAL PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            language_code TEXT NOT NULL,
            status TEXT NOT NULL,
            output_json_path TEXT,
            output_srt_path TEXT,
            output_ass_path TEXT,
            error TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_subtitle_translations_video_lang
            ON subtitle_translations (video_id, language_code, created_at DESC);
        """,
        # Video metadata (e.g., Chinese social, YouTube)
        """
        CREATE TABLE IF NOT EXISTS video_metadata (
            id SERIAL PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            language_code TEXT NOT NULL,
            status TEXT NOT NULL,
            output_json_path TEXT,
            error TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_video_metadata_video_lang
            ON video_metadata (video_id, language_code, created_at DESC);
        """,
        # Burned subtitle videos
        """
        CREATE TABLE IF NOT EXISTS subtitle_burns (
            id SERIAL PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
            status TEXT NOT NULL,
            output_path TEXT,
            progress INTEGER NOT NULL DEFAULT 0,
            config JSONB,
            error TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_subtitle_burns_video_created ON subtitle_burns (video_id, created_at DESC);",
        "ALTER TABLE subtitle_burns ADD COLUMN IF NOT EXISTS progress INTEGER DEFAULT 0;",
        # UI preference storage (e.g., translation display styles)
        """
        CREATE TABLE IF NOT EXISTS ui_preferences (
            key TEXT PRIMARY KEY,
            value JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
    ]

    with get_cursor(commit=True) as cur:
        for ddl in ddl_statements:
            cur.execute(ddl)


def get_video_by_id(video_id: int) -> tuple | None:
    """Return a video row by id."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, file_path, title, source, created_at FROM videos WHERE id = %s",
            (video_id,),
        )
        return cur.fetchone()


def delete_videos_by_file_path(file_path: str) -> int:
    """Delete all videos with the given file_path and return the count."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM videos WHERE file_path = %s RETURNING id", (file_path,))
        rows = cur.fetchall()
    return len(rows)


def add_video(file_path: str, title: str | None = None, source: str | None = None) -> int:
    """Insert a video row and return its ID, reusing existing entries by file_path."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "SELECT id FROM videos WHERE file_path = %s ORDER BY id DESC LIMIT 1",
            (file_path,),
        )
        row = cur.fetchone()
        if row:
            video_id = row[0]
            cur.execute(
                """
                UPDATE videos
                SET title = COALESCE(%s, title),
                    source = COALESCE(%s, source),
                    created_at = NOW()
                WHERE id = %s
                """,
                (title, source, video_id),
            )
            return video_id
        cur.execute(
            "INSERT INTO videos (file_path, title, source) VALUES (%s, %s, %s) RETURNING id",
            (file_path, title, source),
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


def add_subtitle_translation(
    video_id: int,
    language_code: str,
    status: str,
    output_json_path: str | None = None,
    output_srt_path: str | None = None,
    output_ass_path: str | None = None,
    error: str | None = None,
) -> int:
    """Insert a subtitle translation row and return its ID."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO subtitle_translations (
                video_id,
                language_code,
                status,
                output_json_path,
                output_srt_path,
                output_ass_path,
                error
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                video_id,
                language_code,
                status,
                output_json_path,
                output_srt_path,
                output_ass_path,
                error,
            ),
        )
        (translation_id,) = cur.fetchone()
        return translation_id


def get_latest_subtitle_translation(video_id: int, language_code: str) -> tuple | None:
    """Return the most recent subtitle translation row for the video/language, or None."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, language_code, status, output_json_path, output_srt_path, output_ass_path, error, created_at
            FROM subtitle_translations
            WHERE video_id = %s AND language_code = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (video_id, language_code),
        )
        return cur.fetchone()


def get_subtitle_translations_for_video(video_id: int) -> list[tuple]:
    """Return list of subtitle translations for the video."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, language_code, status, output_json_path, output_srt_path, output_ass_path, error, created_at
            FROM subtitle_translations
            WHERE video_id = %s
            ORDER BY id DESC
            """,
            (video_id,),
        )
        return cur.fetchall()


def add_video_metadata(
    video_id: int,
    language_code: str,
    status: str,
    output_json_path: str | None = None,
    error: str | None = None,
) -> int:
    """Insert a video metadata row and return its ID."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO video_metadata (
                video_id,
                language_code,
                status,
                output_json_path,
                error
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                video_id,
                language_code,
                status,
                output_json_path,
                error,
            ),
        )
        (metadata_id,) = cur.fetchone()
        return metadata_id


def get_latest_video_metadata(video_id: int, language_code: str) -> tuple | None:
    """Return latest metadata row for the video/language."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, language_code, status, output_json_path, error, created_at
            FROM video_metadata
            WHERE video_id = %s AND language_code = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (video_id, language_code),
        )
        return cur.fetchone()


def add_subtitle_burn(
    video_id: int,
    status: str,
    output_path: str | None,
    config: dict | None,
    error: str | None,
    progress: int = 0,
) -> int:
    """Insert a subtitle burn row and return its ID."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO subtitle_burns (
                video_id,
                status,
                output_path,
                progress,
                config,
                error
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (video_id, status, output_path, progress, json.dumps(config or {}), error),
        )
        (burn_id,) = cur.fetchone()
        return burn_id


def get_latest_subtitle_burn(video_id: int) -> tuple | None:
    """Return latest subtitle burn row for the video."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, status, output_path, progress, config, error, created_at
            FROM subtitle_burns
            WHERE video_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (video_id,),
        )
        return cur.fetchone()


def update_subtitle_burn_progress(burn_id: int, progress: int) -> None:
    progress_value = max(0, min(100, int(progress)))
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE subtitle_burns SET progress = %s WHERE id = %s",
            (progress_value, burn_id),
        )


def finalize_subtitle_burn(
    burn_id: int,
    status: str,
    output_path: str | None,
    error: str | None,
    progress: int | None = None,
) -> None:
    progress_value = None
    if progress is not None:
        progress_value = max(0, min(100, int(progress)))

    with get_cursor(commit=True) as cur:
        if progress_value is None:
            cur.execute(
                """
                UPDATE subtitle_burns
                SET status = %s,
                    output_path = %s,
                    error = %s
                WHERE id = %s
                """,
                (status, output_path, error, burn_id),
            )
        else:
            cur.execute(
                """
                UPDATE subtitle_burns
                SET status = %s,
                    output_path = %s,
                    error = %s,
                    progress = %s
                WHERE id = %s
                """,
                (status, output_path, error, progress_value, burn_id),
            )


def get_ui_preference(key: str) -> dict | None:
    with get_cursor() as cur:
        cur.execute("SELECT value FROM ui_preferences WHERE key = %s", (key,))
        row = cur.fetchone()
    if not row:
        return None
    value = row[0]
    if isinstance(value, dict):
        return value
    try:
        return json.loads(value)
    except Exception:
        return None


def set_ui_preference(key: str, value: dict) -> None:
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO ui_preferences (key, value, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (key) DO UPDATE SET
                value = EXCLUDED.value,
                updated_at = EXCLUDED.updated_at
            """,
            (key, json.dumps(value)),
        )


def add_transcription(
    video_id: int,
    language_code: str,
    status: str,
    output_json_path: str | None = None,
    output_srt_path: str | None = None,
    output_md_path: str | None = None,
    error: str | None = None,
) -> int:
    """Insert a transcription row and return its ID."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO transcriptions (
                video_id,
                language_code,
                status,
                output_json_path,
                output_srt_path,
                output_md_path,
                error
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                video_id,
                language_code,
                status,
                output_json_path,
                output_srt_path,
                output_md_path,
                error,
            ),
        )
        (transcription_id,) = cur.fetchone()
        return transcription_id


def get_latest_transcription(video_id: int) -> tuple | None:
    """Return the most recent transcription row for the video, or None."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, language_code, status, output_json_path, output_srt_path, output_md_path, error, created_at
            FROM transcriptions
            WHERE video_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (video_id,),
        )
        return cur.fetchone()


def add_frame_caption(
    video_id: int,
    status: str,
    output_json_path: str | None = None,
    output_srt_path: str | None = None,
    output_md_path: str | None = None,
    error: str | None = None,
) -> int:
    """Insert a frame caption row and return its ID."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO frame_captions (
                video_id,
                status,
                output_json_path,
                output_srt_path,
                output_md_path,
                error
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                video_id,
                status,
                output_json_path,
                output_srt_path,
                output_md_path,
                error,
            ),
        )
        (caption_id,) = cur.fetchone()
        return caption_id


def get_latest_frame_caption(video_id: int) -> tuple | None:
    """Return the most recent frame caption row for the video, or None."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, status, output_json_path, output_srt_path, output_md_path, error, created_at
            FROM frame_captions
            WHERE video_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (video_id,),
        )
        return cur.fetchone()


def add_keyframe_extraction(
    video_id: int,
    status: str,
    output_dir: str | None = None,
    frame_count: int | None = None,
    error: str | None = None,
) -> int:
    """Insert a keyframe extraction row and return its ID."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO keyframe_extractions (
                video_id,
                status,
                output_dir,
                frame_count,
                error
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                video_id,
                status,
                output_dir,
                frame_count,
                error,
            ),
        )
        (extract_id,) = cur.fetchone()
        return extract_id


def get_latest_keyframe_extraction(video_id: int) -> tuple | None:
    """Return the most recent keyframe extraction row for the video, or None."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, status, output_dir, frame_count, error, created_at
            FROM keyframe_extractions
            WHERE video_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (video_id,),
        )
        return cur.fetchone()


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
