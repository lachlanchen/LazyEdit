import argparse
from pathlib import Path

from config import UPLOAD_FOLDER
from lazyedit import db as ldb


FILE_COLUMNS = {
    "videos": ["file_path"],
    "generated_videos": ["file_path"],
    "captions": ["subtitle_path"],
    "transcriptions": ["output_json_path", "output_srt_path", "output_md_path"],
    "subtitle_translations": ["output_json_path", "output_srt_path", "output_ass_path"],
    "frame_captions": ["output_json_path", "output_srt_path", "output_md_path"],
    "video_metadata": ["output_json_path"],
    "subtitle_burns": ["output_path"],
}

DIR_COLUMNS = {
    "keyframe_extractions": ["output_dir"],
}


def _build_index(root: Path) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
    file_index: dict[str, list[Path]] = {}
    dir_index: dict[str, list[Path]] = {}
    for path in root.rglob("*"):
        if path.is_file():
            file_index.setdefault(path.name, []).append(path)
        elif path.is_dir():
            dir_index.setdefault(path.name, []).append(path)
    return file_index, dir_index


def _pick_best(candidates: list[Path]) -> Path | None:
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: (len(str(p)), str(p)), reverse=True)[0]


def _is_generated_path(path: str) -> bool:
    return "/generated/" in path or "\\generated\\" in path


def _find_keyframe_dir(video_dir: Path) -> Path | None:
    if not video_dir.exists() or not video_dir.is_dir():
        return None
    candidates: list[Path] = []
    for child in video_dir.iterdir():
        if not child.is_dir():
            continue
        name = child.name.lower()
        if "keyframe" not in name and "key_frame" not in name and name != "keyframes":
            continue
        if any(child.glob("*.jpg")) or any(child.glob("*.jpeg")) or any(child.glob("*.png")):
            candidates.append(child)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def sync_generated_db_paths(apply_changes: bool) -> None:
    generated_root = (Path(UPLOAD_FOLDER) / "generated").resolve()
    if not generated_root.exists():
        print(f"Generated root not found: {generated_root}")
        return

    file_index, dir_index = _build_index(generated_root)

    ldb.ensure_schema()
    total_updates = 0

    with ldb.get_cursor(commit=apply_changes) as cur:
        cur.execute("SELECT id, file_path FROM videos WHERE file_path IS NOT NULL")
        video_paths = {row_id: path for row_id, path in cur.fetchall()}

        for table, columns in FILE_COLUMNS.items():
            for column in columns:
                cur.execute(f"SELECT id, {column} FROM {table} WHERE {column} IS NOT NULL")
                for row_id, path_value in cur.fetchall():
                    if not path_value:
                        continue
                    if not _is_generated_path(path_value):
                        continue
                    if Path(path_value).exists():
                        continue
                    candidate = _pick_best(file_index.get(Path(path_value).name, []))
                    if not candidate:
                        continue
                    new_path = str(candidate.resolve())
                    if apply_changes:
                        cur.execute(
                            f"UPDATE {table} SET {column} = %s WHERE id = %s",
                            (new_path, row_id),
                        )
                    total_updates += 1
                    action = "update" if apply_changes else "dry-run"
                    print(f"[{action}] {table}.{column} id={row_id} -> {new_path}")

        for table, columns in DIR_COLUMNS.items():
            for column in columns:
                cur.execute(
                    f"SELECT id, video_id, {column} FROM {table} WHERE {column} IS NOT NULL"
                )
                for row_id, video_id, path_value in cur.fetchall():
                    if not path_value:
                        continue
                    if not _is_generated_path(path_value):
                        continue
                    video_path = video_paths.get(video_id)
                    if not video_path:
                        continue
                    candidate = _find_keyframe_dir(Path(video_path).parent)
                    if not candidate:
                        continue
                    new_path = str(candidate.resolve())
                    if Path(path_value).resolve() == Path(new_path).resolve():
                        continue
                    if apply_changes:
                        cur.execute(
                            f"UPDATE {table} SET {column} = %s WHERE id = %s",
                            (new_path, row_id),
                        )
                    total_updates += 1
                    action = "update" if apply_changes else "dry-run"
                    print(f"[{action}] {table}.{column} id={row_id} -> {new_path}")

    print(f"Updated {total_updates} paths." if apply_changes else f"Would update {total_updates} paths.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync generated file paths stored in the database.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply database updates (default is dry-run).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    sync_generated_db_paths(apply_changes=args.apply)
