"""Select active private workspaces without resurrecting deleted accounts."""
import json
from pathlib import Path
import re
import sqlite3


def promotion_workspaces(state: Path, database: Path) -> list[Path]:
    connection = sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        rows = connection.execute("SELECT id,status FROM workspaces ORDER BY id").fetchall()
    finally:
        connection.close()
    selected = []
    for identifier, status in rows:
        # Cleanup retains a Compose receipt after removing a member's volumes.
        # That receipt is evidence, not permission to recreate its worker.
        if status == "deleted":
            continue
        if status != "ready":
            raise RuntimeError("Resolve pending, failed or deleting workspaces before promotion")
        if not re.fullmatch(r"[a-f0-9]{24}", identifier):
            raise RuntimeError("Invalid registry workspace identity")
        file = state / "workspaces" / identifier / "compose.json"
        if (file.parent / "acceptance.lock").exists():
            raise RuntimeError("Acceptance lock: do not replace this worker until its owning qualification finishes")
        document = json.loads(file.read_text())
        account = json.loads((file.parent / "account.json").read_text())
        if (document.get("name") != f"le-{identifier}"
                or document["services"]["worker"].get("container_name") != f"le-{identifier}-worker"
                or account.get("id") != identifier):
            raise RuntimeError("Promotion workspace identity mismatch")
        selected.append(file)
    return selected
