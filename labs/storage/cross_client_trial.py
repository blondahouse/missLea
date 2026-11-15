"""Read-only cross-client restore: restic and rustic sharing a documented repo format.

No concurrent writers or pruning are used. Password and repository metadata
are transferred only inside the disposable CI container, not through an LLM.
"""
from __future__ import annotations

import hashlib
import json
import secrets
import shutil
import sqlite3
import tempfile
from pathlib import Path

from labs.storage.comparison_trial import Tool, make_snapshot
from labs.storage.snapshot import restore_to_quarantine, verify_snapshot


def run_direction(writer: str, reader: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="ml-restic-rustic-cross-") as temp:
        root = Path(temp)
        primary = root / "primary.sqlite"
        with sqlite3.connect(primary) as db:
            db.execute("CREATE TABLE source(kind TEXT, content TEXT, status TEXT)")
            db.execute("INSERT INTO source VALUES('obligation','synthetic','open')")
            db.execute("INSERT INTO source VALUES('grant','synthetic','revoked')")
        bundle = root / "snapshot"
        wanted = make_snapshot(primary, bundle, 1)
        password = root / "passphrase"
        password.write_text(secrets.token_urlsafe(48), encoding="utf-8")
        password.chmod(0o600)
        write_root = root / "source-host"
        read_root = root / "restore-host"
        write_root.mkdir()
        read_root.mkdir()
        writer_tool = Tool(writer, write_root, password)
        reader_tool = Tool(reader, read_root, password)
        writer_tool.init(bundle)
        writer_tool.backup(bundle, 1)
        # Read-only reconnect to the actual existing repository without copying
        # locally stored permission or client configuration.
        reader_tool.repo = writer_tool.repo
        if reader == "restic":
            reader_tool.prefix = ["restic", "--repo", str(writer_tool.repo),
                                  "--password-file", str(password)]
        else:
            reader_tool.env["RUSTIC_REPOSITORY"] = str(writer_tool.repo)
        reader_tool.check()
        primary.unlink()
        shutil.rmtree(bundle)
        output = root / "quarantine"
        output.mkdir()
        reader_tool.restore(bundle, output)
        matches = []
        for file in output.rglob("manifest.json"):
            restored = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in file.parent.iterdir() if p.is_file()}
            if restored == wanted:
                matches.append(file.parent)
        if len(matches) != 1:
            raise RuntimeError("Cross-client restore differs from source")
        verify_snapshot(matches[0])
        final_db = root / "inert.sqlite"
        receipt = restore_to_quarantine(matches[0], final_db)
        with sqlite3.connect(final_db) as db:
            values = db.execute("SELECT kind,content,status FROM source ORDER BY rowid").fetchall()
        if values != [("obligation", "synthetic", "open"),
                      ("grant", "synthetic", "revoked")]:
            raise RuntimeError("Cross-client state continuity failed")
        if receipt["authority_restored"] or receipt["active_instance_started"]:
            raise RuntimeError("Cross-client restore activated authority")
        return {"writer": writer, "reader": reader, "same_repository_format": True,
                "bit_exact_restore": True, "authority_inactive": True}


if __name__ == "__main__":
    print(json.dumps({
        "synthetic_only": True,
        "concurrent_writes_tested": False,
        "results": [run_direction("restic", "rustic"),
                    run_direction("rustic", "restic")],
    }, indent=2))
