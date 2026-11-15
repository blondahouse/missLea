"""Portable synthetic SQLite snapshot + restore exercise.

NO ENCRYPTION. NO AUTHENTICITY. Not suitable for real memory, keys or production
backups. SHA256 here detects accidental corruption, not malicious tampering.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path

FORMAT = "misslea-storage-lab-v1"
DATABASE = "state.sqlite"
MANIFEST = "manifest.json"


class InvalidSnapshot(ValueError):
    pass


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as inp:
        for block in iter(lambda: inp.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _integrity(path: Path) -> None:
    if not path.is_file():
        raise InvalidSnapshot("SQLite database missing")
    try:
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as conn:
            value = conn.execute("PRAGMA integrity_check").fetchone()[0]
    except (sqlite3.DatabaseError, OSError, TypeError, IndexError):
        raise InvalidSnapshot("SQLite integrity check failed") from None
    if value != "ok":
        raise InvalidSnapshot("SQLite integrity check failed")


def create_snapshot(source: str | Path, destination: str | Path) -> dict:
    """Take a SQLite-consistent snapshot, staged before an atomic directory rename."""
    src, dest = Path(source).resolve(), Path(destination).resolve()
    if dest.exists() or not src.is_file() or not dest.parent.is_dir():
        raise ValueError("Destination must be new, source must exist, parent must exist")
    _integrity(src)
    staging = Path(tempfile.mkdtemp(prefix=".storage-lab-", dir=dest.parent))
    try:
        output = staging / DATABASE
        with sqlite3.connect(src.as_uri() + "?mode=ro", uri=True) as source_db:
            with sqlite3.connect(output) as snapshot_db:
                source_db.backup(snapshot_db)
        _integrity(output)
        manifest = {
            "format": FORMAT,
            "created_at": int(time.time()),
            "file": DATABASE,
            "bytes": output.stat().st_size,
            "sha256": _hash(output),
            "encrypted": False,
            "synthetic_only": True,
            "authority_restored": False,
        }
        (staging / MANIFEST).write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        staging.rename(dest)
        return manifest
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def verify_snapshot(bundle: str | Path) -> dict:
    """Validate accidental-corruption markers + SQLite structure, not authenticity."""
    root = Path(bundle)
    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise InvalidSnapshot("Missing or invalid manifest") from None
    if not isinstance(manifest, dict) or any([
        manifest.get("format") != FORMAT,
        manifest.get("file") != DATABASE,
        manifest.get("encrypted") is not False,
        manifest.get("synthetic_only") is not True,
        manifest.get("authority_restored") is not False,
        not isinstance(manifest.get("bytes"), int),
        not isinstance(manifest.get("sha256"), str),
    ]):
        raise InvalidSnapshot("Unsupported or unsafe snapshot format")
    db = root / DATABASE
    if not db.is_file() or db.stat().st_size != manifest["bytes"]:
        raise InvalidSnapshot("Snapshot is missing or changed")
    if _hash(db) != manifest["sha256"]:
        raise InvalidSnapshot("Snapshot hash mismatch")
    _integrity(db)
    return manifest


def restore_to_quarantine(bundle: str | Path, destination: str | Path) -> dict:
    """Restore to a *new* file, never into live state, without activating authority."""
    manifest = verify_snapshot(bundle)
    dest = Path(destination).resolve()
    if dest.exists() or not dest.parent.is_dir():
        raise ValueError("Restore destination must be a new file in an existing directory")
    fd, temp = tempfile.mkstemp(prefix=".restore-lab-", dir=dest.parent)
    os.close(fd)
    try:
        shutil.copyfile(Path(bundle) / DATABASE, temp)
        if _hash(Path(temp)) != manifest["sha256"]:
            raise InvalidSnapshot("Restore copy differs from verified snapshot")
        _integrity(Path(temp))
        Path(temp).replace(dest)
    finally:
        Path(temp).unlink(missing_ok=True)
    return {"status": "restored_to_quarantine",
            "database": DATABASE, "synthetic_only": True,
            "active_instance_started": False, "authority_restored": False}
