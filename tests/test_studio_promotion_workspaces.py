import importlib.util
import json
from pathlib import Path
import sqlite3

import pytest

helper = Path(__file__).resolve().parents[1] / "scripts/studio/promotion_workspaces.py"
spec = importlib.util.spec_from_file_location("promotion_workspaces", helper)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(tmp_path):
    database = tmp_path / "registry.sqlite"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE workspaces(id TEXT,status TEXT)")
        connection.executemany("INSERT INTO workspaces VALUES(?,?)", [
            ("a" * 24, "ready"), ("b" * 24, "deleted")])
    for identifier in ("a" * 24, "b" * 24):
        root = tmp_path / "workspaces" / identifier
        root.mkdir(parents=True)
        (root / "compose.json").write_text(json.dumps({"name": f"le-{identifier}",
            "services": {"worker": {"container_name": f"le-{identifier}-worker"}}}))
        (root / "account.json").write_text(json.dumps({"id": identifier}))
    # Deleted cleanup has already removed private bootstrap credentials.
    (tmp_path / "workspaces" / ("b" * 24) / "account.json").unlink()
    return database


def test_deleted_compose_receipt_does_not_recreate_worker(tmp_path):
    database = fixture(tmp_path)
    assert module.promotion_workspaces(tmp_path, database) == [
        tmp_path / "workspaces" / ("a" * 24) / "compose.json"]
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT status FROM workspaces WHERE id=?", ("b" * 24,)).fetchone() == ("deleted",)


def test_unfinished_cleanup_or_wrong_identity_prevents_promotion(tmp_path):
    database = fixture(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute("UPDATE workspaces SET status='deleting' WHERE id=?", ("b" * 24,))
    with pytest.raises(RuntimeError, match="Resolve"):
        module.promotion_workspaces(tmp_path, database)
    with sqlite3.connect(database) as connection:
        connection.execute("UPDATE workspaces SET status='deleted' WHERE id=?", ("b" * 24,))
    account = tmp_path / "workspaces" / ("a" * 24) / "account.json"
    account.write_text(json.dumps({"id": "b" * 24}))
    with pytest.raises(RuntimeError, match="identity mismatch"):
        module.promotion_workspaces(tmp_path, database)


def test_active_peer_acceptance_prevents_worker_replacement(tmp_path):
    database = fixture(tmp_path)
    lock = tmp_path / "workspaces" / ("a" * 24) / "acceptance.lock"
    lock.write_text("Reviewer client qualification owns this worker lifecycle.\n")
    with pytest.raises(RuntimeError, match="Acceptance lock"):
        module.promotion_workspaces(tmp_path, database)
