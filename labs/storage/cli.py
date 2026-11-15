"""Synthetic failure-and-recovery demonstration. No external storage or keys."""
from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
from pathlib import Path

from labs.storage.snapshot import (
    InvalidSnapshot, create_snapshot, restore_to_quarantine, verify_snapshot,
)


def demo() -> dict:
    with tempfile.TemporaryDirectory(prefix="misslea-storage-lab-") as tmp:
        root = Path(tmp)
        db = root / "primary.sqlite"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE memory_events (id INTEGER PRIMARY KEY, event TEXT)")
            conn.executemany("INSERT INTO memory_events (event) VALUES (?)",
                             [("synthetic-foundation",), ("synthetic-choice",)])
        first = root / "mirror_a"
        mirror = root / "mirror_b"
        manifest = create_snapshot(db, first)
        shutil.copytree(first, mirror)
        db.unlink()
        # Fail mirror A deliberately. B is independently recoverable.
        with (first / "state.sqlite").open("r+b") as file:
            file.seek(100)
            file.write(b"CORRUPTED")
        primary_rejected = False
        try:
            verify_snapshot(first)
        except InvalidSnapshot:
            primary_rejected = True
        secondary_valid = verify_snapshot(mirror)["sha256"] == manifest["sha256"]
        output = root / "quarantine.sqlite"
        result = restore_to_quarantine(mirror, output)
        with sqlite3.connect(output) as conn:
            rows = [row[0] for row in conn.execute("SELECT event FROM memory_events ORDER BY id")]
        return {
            "synthetic": True,
            "external_calls": 0,
            "primary_lost": not db.exists(),
            "corrupted_backup_rejected": primary_rejected,
            "independent_backup_valid": secondary_valid,
            "recovered_events": rows,
            "restored_inactive": result["active_instance_started"] is False,
            "authority_restored": result["authority_restored"],
            "encrypted": manifest["encrypted"],
        }


def main() -> int:
    result = demo()
    print(json.dumps(result, indent=2))
    return 0 if (result["corrupted_backup_rejected"] and
                 result["independent_backup_valid"] and
                 result["restored_inactive"] and
                 len(result["recovered_events"]) == 2) else 1


if __name__ == "__main__":
    raise SystemExit(main())
