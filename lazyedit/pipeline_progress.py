"""Bounded live progress for async preparation within one backend process."""
from datetime import datetime, timezone


class PipelineProgress:
    def __init__(self, limit=128):
        self.rows = {}
        self.limit = limit

    def start(self, key, operation_id=None):
        if self.rows.get(key, {}).get("status") == "working":
            return False
        for old in list(self.rows):
            if len(self.rows) < self.limit:
                break
            if self.rows[old]["status"] != "working":
                del self.rows[old]
        if len(self.rows) >= self.limit and key not in self.rows:
            return False
        self.rows[key] = {"status": "working", "steps": {}}
        if operation_id:
            self.rows[key]["operation_id"] = operation_id
        self.touch(key)
        return True

    def touch(self, key):
        self.rows[key]["updated_at"] = datetime.now(timezone.utc).isoformat()

    def step(self, key, name, status, detail=None):
        self.rows[key]["steps"][name] = {"status": status, "detail": detail}
        self.touch(key)
        self.rows[key]["steps"][name]["updated_at"] = self.rows[key]["updated_at"]

    def finish(self, key, ok, error=None):
        self.rows[key].update(status="done" if ok else "error", error=error)
        self.touch(key)

    def get(self, key):
        return self.rows.get(key)
