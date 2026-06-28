#!/usr/bin/env python3
"""List or update LazyEdit music publish records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lazyedit import db as ldb  # noqa: E402


def _row_to_dict(row: tuple) -> dict:
    keys = [
        "id",
        "slug",
        "title",
        "artist",
        "language_code",
        "status",
        "audio_path",
        "zip_path",
        "metadata_path",
        "manifest_path",
        "cover_paths",
        "proof_paths",
        "source_url",
        "shipinhao_item_id",
        "shipinhao_item_url",
        "shipinhao_management_url",
        "remote_job_id",
        "remote_filename",
        "remote_status",
        "error",
        "created_at",
        "updated_at",
        "published_at",
        "deleted_at",
    ]
    output = dict(zip(keys, row))
    for key in ("created_at", "updated_at", "published_at", "deleted_at"):
        if output.get(key) is not None:
            output[key] = output[key].isoformat()
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List/update LazyEdit music publish records.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List recent music publish records.")
    list_parser.add_argument("--limit", type=int, default=20)

    update_parser = subparsers.add_parser("update", help="Attach remote Shipinhao metadata to a record.")
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("--status")
    update_parser.add_argument("--shipinhao-item-id")
    update_parser.add_argument("--shipinhao-item-url")
    update_parser.add_argument("--shipinhao-management-url")
    update_parser.add_argument("--remote-status")
    update_parser.add_argument("--error")
    update_parser.add_argument("--published", action="store_true")
    update_parser.add_argument("--deleted", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "list":
        rows = [_row_to_dict(row) for row in ldb.list_music_publish_items(args.limit)]
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    if args.command == "update":
        ldb.update_music_publish_item(
            args.id,
            status=args.status,
            shipinhao_item_id=args.shipinhao_item_id,
            shipinhao_item_url=args.shipinhao_item_url,
            shipinhao_management_url=args.shipinhao_management_url,
            remote_status=args.remote_status,
            error=args.error,
            published=args.published,
            deleted=args.deleted,
        )
        rows = [_row_to_dict(row) for row in ldb.list_music_publish_items(100)]
        match = next((row for row in rows if row["id"] == args.id), None)
        print(json.dumps(match or {"id": args.id, "updated": True}, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
