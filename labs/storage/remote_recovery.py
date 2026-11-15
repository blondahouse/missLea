"""STO-003: synthetic canonical records + quarantined validation across CI runners.

THIS IS A TEST ONLY. Source and archive unlock material are synthetic and may
not be used with real identities or provider accounts. There is no production
backup service or key escrow implemented here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from labs.storage.snapshot import create_snapshot, restore_to_quarantine, verify_snapshot

RECORDS = [
    ("evidence", "original-chat#1", "synthetic firsthand observation", "retained"),
    ("decision", "decision#2", "use independent recovery domains", "current"),
    ("obligation", "issue#3", "synthetic unresolved obligation", "open"),
    ("grant", "revoked-grant#4", "simulated provider scope", "revoked"),
]
ATTACHMENT = bytes(range(256)) * 1024


def create_fixture(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    db = root / "original.sqlite"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE events (kind TEXT, provenance TEXT, content TEXT, status TEXT)")
        conn.executemany("INSERT INTO events VALUES (?,?,?,?)", RECORDS)
    source = root / "snapshot"
    create_snapshot(db, source)
    (source / "attachment.bin").write_bytes(ATTACHMENT)
    (source / "notes.txt").write_text("synthetic original facts preserved\n", encoding="utf-8")
    hashes = {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
              for file in source.iterdir() if file.is_file()}
    expected = {
        "format": "sto003-synthetic-v1",
        "hashes": hashes,
        "record_count": len(RECORDS),
        "authority_after_restore": "inactive",
        "real_provider_independence": False,
        "real_key_escrow": False,
    }
    (root / "expected.json").write_text(
        json.dumps(expected, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return expected


def validate_restored(root: Path, expected_file: Path) -> dict:
    expected = json.loads(expected_file.read_text(encoding="utf-8"))
    if expected.get("format") != "sto003-synthetic-v1":
        raise ValueError("Unsupported experiment fixture")
    matches = []
    for manifest in root.rglob("manifest.json"):
        candidate = manifest.parent
        found = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in candidate.iterdir() if p.is_file()}
        if found == expected["hashes"]:
            matches.append(candidate)
    if len(matches) != 1:
        raise ValueError("Expected exactly one fully matching synthetic snapshot")
    bundle = matches[0]
    verify_snapshot(bundle)
    if (bundle / "attachment.bin").read_bytes() != ATTACHMENT:
        raise ValueError("Attachment does not match source evidence")
    quarantine = root / "inert-recovered.sqlite"
    outcome = restore_to_quarantine(bundle, quarantine)
    with sqlite3.connect(quarantine) as conn:
        actual = conn.execute(
            "SELECT kind,provenance,content,status FROM events ORDER BY rowid"
        ).fetchall()
    if actual != RECORDS:
        raise ValueError("Primary evidence, ordering or revocation changed")
    if outcome["authority_restored"] or outcome["active_instance_started"]:
        raise ValueError("Restoration activated agent permissions")
    return {
        "exact_record_and_attachment_recovery": True,
        "record_count": len(RECORDS),
        "revocation_record_preserved": actual[-1][-1] == "revoked",
        "authority_restored": False,
        "agent_started": False,
        "quarantine": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "validate"])
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--expected", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare":
        result = create_fixture(args.root)
        print(json.dumps({
            "synthetic": True, "files": sorted(result["hashes"]),
            "original_records": len(RECORDS), "key_escrow": "NOT_TESTED",
        }))
    else:
        if args.expected is None:
            parser.error("--expected required when validating restore")
        print(json.dumps(validate_restored(args.root, args.expected)))


if __name__ == "__main__":
    main()
