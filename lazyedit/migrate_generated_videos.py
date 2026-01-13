import argparse
import shutil
from datetime import datetime
from pathlib import Path

from config import UPLOAD_FOLDER
from lazyedit import db as ldb


SKIP_ROOT_NAMES = {
    "translations",
    "metadata",
    "publish",
    "burn",
    "keyframes",
    "proxy_previews",
}

TABLE_COLUMNS = {
    "videos": ["file_path"],
    "generated_videos": ["file_path"],
    "captions": ["subtitle_path"],
    "transcriptions": ["output_json_path", "output_srt_path", "output_md_path"],
    "subtitle_translations": ["output_json_path", "output_srt_path", "output_ass_path"],
    "frame_captions": ["output_json_path", "output_srt_path", "output_md_path"],
    "video_metadata": ["output_json_path"],
    "subtitle_burns": ["output_path"],
    "keyframe_extractions": ["output_dir"],
}


def _resolve_target_dir(generated_root: Path, base_name: str) -> Path:
    target = generated_root / base_name
    if target.exists() and any(target.iterdir()):
        suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = generated_root / f"{base_name}_migrated_{suffix}"
    return target


def _queue_move(moves: list[tuple[Path, Path]], src: Path, dest: Path) -> None:
    if not src.exists():
        return
    if src.resolve() == dest.resolve():
        return
    moves.append((src, dest))


def _matches_prefix(name: str, base_name: str) -> bool:
    return name == f"{base_name}.mp4" or name.startswith(f"{base_name}_")


def _matches_publish(name: str, base_name: str) -> bool:
    if name == f"{base_name}.zip":
        return True
    return name.startswith(f"{base_name}_")


def _collect_prefixed_files(src_dir: Path, base_name: str, matcher, moves, target_dir: Path) -> None:
    if not src_dir.is_dir():
        return
    for path in src_dir.rglob("*"):
        if not path.is_file():
            continue
        if not matcher(path.name, base_name):
            continue
        rel = path.relative_to(src_dir)
        dest = target_dir / rel
        _queue_move(moves, path, dest)


def _apply_moves(moves: list[tuple[Path, Path]], dry_run: bool) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for src, dest in moves:
        if dry_run:
            print(f"[dry-run] move {src} -> {dest}")
            mapping[str(src)] = str(dest)
            src_resolved = str(src.resolve())
            dest_resolved = str(dest.resolve())
            if src_resolved != str(src):
                mapping[src_resolved] = dest_resolved
            continue
        if dest.exists():
            print(f"[skip] destination exists: {dest}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        mapping[str(src)] = str(dest)
        src_resolved = str(src.resolve())
        dest_resolved = str(dest.resolve())
        if src_resolved != str(src):
            mapping[src_resolved] = dest_resolved
        print(f"[moved] {src} -> {dest}")
    return mapping


def _update_db_paths(mapping: dict[str, str], dry_run: bool) -> None:
    if dry_run or not mapping:
        return
    ldb.ensure_schema()
    with ldb.get_cursor(commit=True) as cur:
        for table, columns in TABLE_COLUMNS.items():
            for column in columns:
                for old_path, new_path in mapping.items():
                    cur.execute(
                        f"UPDATE {table} SET {column} = %s WHERE {column} = %s",
                        (new_path, old_path),
                    )


def _cleanup_empty_dirs(paths: list[Path], dry_run: bool) -> None:
    for path in paths:
        if not path.exists() or not path.is_dir():
            continue
        if any(path.iterdir()):
            continue
        if dry_run:
            print(f"[dry-run] remove empty dir {path}")
            continue
        path.rmdir()
        print(f"[removed] empty dir {path}")


def migrate_generated_videos(dry_run: bool = True, only: list[str] | None = None) -> None:
    generated_root = Path(UPLOAD_FOLDER) / "generated"
    resolved_root = generated_root.resolve()
    if not generated_root.exists():
        print(f"Generated root not found: {generated_root}")
        return

    ldb.ensure_schema()
    with ldb.get_cursor() as cur:
        roots = {generated_root, resolved_root}
        where_clause = " OR ".join(["file_path LIKE %s"] * len(roots))
        params = [str(root) + "/%" for root in roots]
        cur.execute(f"SELECT id, file_path FROM videos WHERE {where_clause}", params)
        rows = cur.fetchall()

    seen_paths: set[str] = set()
    for video_id, file_path in rows:
        if not file_path:
            continue
        if file_path in seen_paths:
            continue
        seen_paths.add(file_path)
        src = Path(file_path)
        if not src.exists():
            print(f"[skip] missing file for video {video_id}: {file_path}")
            continue
        if src.parent != generated_root and src.parent != resolved_root:
            continue
        base_name = src.stem
        if only and base_name not in only:
            continue

        base_root = generated_root if src.parent == generated_root else resolved_root
        target_dir = _resolve_target_dir(base_root, base_name)
        moves: list[tuple[Path, Path]] = []
        for entry in base_root.iterdir():
            if entry.name in SKIP_ROOT_NAMES:
                continue
            if _matches_prefix(entry.name, base_name):
                _queue_move(moves, entry, target_dir / entry.name)

        _collect_prefixed_files(
            base_root / "translations",
            base_name,
            lambda name, base: name.startswith(f"{base}_"),
            moves,
            target_dir / "translations",
        )
        _collect_prefixed_files(
            base_root / "metadata",
            base_name,
            lambda name, base: name.startswith(f"{base}_"),
            moves,
            target_dir / "metadata",
        )
        _collect_prefixed_files(
            base_root / "publish",
            base_name,
            _matches_publish,
            moves,
            target_dir / "publish",
        )
        _collect_prefixed_files(
            base_root / "burn",
            base_name,
            lambda name, base: name.startswith(f"{base}_"),
            moves,
            target_dir / "burn",
        )

        mapping = _apply_moves(moves, dry_run)
        _update_db_paths(mapping, dry_run)

    _cleanup_empty_dirs(
        [
            generated_root / "translations",
            generated_root / "metadata",
            generated_root / "publish",
            generated_root / "burn",
        ],
        dry_run,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate generated videos into per-video folders.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply file moves and DB updates (default is dry-run).",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=None,
        help="Base filename to migrate (can be provided multiple times).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    migrate_generated_videos(dry_run=not args.apply, only=args.only)
