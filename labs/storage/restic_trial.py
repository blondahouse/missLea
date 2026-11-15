"""REAL restic encryption/integrity test using only synthetic data and local dirs.

This tests the restic binary, NOT independent cloud storage, retention
immutability, a primary database deployment, or live Miss Lea memory.
No real secrets. Ephemeral archive passwords never enter the backup source.
"""
from __future__ import annotations

import json
import os
import secrets
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path

from labs.storage.snapshot import create_snapshot, restore_to_quarantine, verify_snapshot


def restic(repo: Path, password_file: Path, *args: str, success=True) -> bool:
    completed = subprocess.run(
        ["restic", "--repo", str(repo), "--password-file", str(password_file), *args],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        timeout=120, env={**os.environ, "RESTIC_CACHE_DIR": str(repo.parent / "cache")},
    )
    if success and completed.returncode:
        raise RuntimeError("restic command failed (phase: " + args[0] + ")")
    return completed.returncode == 0


def run_trial() -> dict:
    if shutil.which("restic") is None:
        raise RuntimeError("restic CLI is not installed")
    version = subprocess.run(
        ["restic", "version"], capture_output=True, text=True, check=True, timeout=10
    ).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="ml-restic-synthetic-") as tmp:
        root = Path(tmp)
        source = root / "primary.sqlite"
        canary = "SYNTHETIC_ONLY_NOT_A_CREDENTIAL_" + secrets.token_hex(12)
        expected = [
            ("event", "source-1", canary, "observed"),
            ("decision", "rationale-2", "retain-primary-evidence", "current"),
            ("obligation", "source-3", "synthetic-pending", "open"),
            ("grant", "source-4", "canary-grant", "revoked"),
        ]
        with sqlite3.connect(source) as db:
            db.execute("""CREATE TABLE records (
                kind TEXT NOT NULL, provenance TEXT NOT NULL,
                content TEXT NOT NULL, status TEXT NOT NULL
            )""")
            db.executemany("INSERT INTO records VALUES (?,?,?,?)", expected)

        # Coherent SQLite bundle before any remote backup would be attempted.
        bundle = root / "snapshot"
        create_snapshot(source, bundle)
        repo_a = root / "archive-a"
        repo_b = root / "archive-b"
        pass_a = root / "unlock-a"
        pass_b = root / "unlock-b"
        for path in (pass_a, pass_b):
            path.write_text(secrets.token_urlsafe(48), encoding="utf-8")
            path.chmod(0o600)
        for repo, password in ((repo_a, pass_a), (repo_b, pass_b)):
            restic(repo, password, "init")
            restic(repo, password, "backup", str(bundle))
            restic(repo, password, "check", "--read-data")

        wrong_key_denied = not restic(repo_b, pass_a, "snapshots", success=False)
        if not wrong_key_denied:
            raise RuntimeError("Distinct repository key unexpectedly unlocked other archive")
        encrypted_at_rest = all(
            canary.encode() not in part.read_bytes()
            for repo in (repo_a, repo_b)
            for part in repo.rglob("*")
            if part.is_file()
        )
        if not encrypted_at_rest:
            raise RuntimeError("Synthetic plaintext unexpectedly present in archive")

        # Corrupt a single encrypted pack in A. restic must detect it; B still works.
        packs = list((repo_a / "data").rglob("*"))
        packs = [p for p in packs if p.is_file()]
        if not packs:
            raise RuntimeError("No restic data pack created")
        pack = packs[0]
        # restic intentionally protects packs as read-only; simulate a privileged
        # storage-layer corruption, not a normal backup-writer operation.
        pack.chmod(pack.stat().st_mode | 0o200)
        with pack.open("r+b") as stream:
            stream.seek(max(0, pack.stat().st_size // 2))
            byte = stream.read(1)
            stream.seek(max(0, pack.stat().st_size // 2))
            stream.write(bytes([byte[0] ^ 0xA5]))
        tamper_detected = not restic(repo_a, pass_a, "check", "--read-data", success=False)
        if not tamper_detected:
            raise RuntimeError("Tampered restic archive unexpectedly passed verification")

        # Lose the primary and its snapshot. The only usable copy is archive B.
        source.unlink()
        shutil.rmtree(bundle)
        recovery_root = root / "recovered"
        recovery_root.mkdir()
        restic(repo_b, pass_b, "restore", "latest", "--target", str(recovery_root))
        found = list(recovery_root.rglob("manifest.json"))
        if len(found) != 1:
            raise RuntimeError("Expected exactly one restored manifest")
        recovered_bundle = found[0].parent
        verify_snapshot(recovered_bundle)
        quarantined = root / "quarantine.sqlite"
        receipt = restore_to_quarantine(recovered_bundle, quarantined)
        with sqlite3.connect(quarantined) as db:
            actual = db.execute("SELECT kind,provenance,content,status FROM records ORDER BY rowid").fetchall()
        data_preserved = actual == expected
        authority_inactive = (
            not receipt["authority_restored"] and not receipt["active_instance_started"]
            and actual[-1][-1] == "revoked"
        )
        if not data_preserved or not authority_inactive:
            raise RuntimeError("Memory continuity or recovery authority check failed")

        return {
            "tool": version,
            "synthetic_only": True,
            "real_encryption_cli_used": True,
            "storage_topology": "two directories on one ephemeral GitHub Actions runner",
            "independent_failure_domains": False,
            "external_storage": False,
            "checks": {
                "distinct_repository_keys": wrong_key_denied,
                "no_plaintext_canary_in_repository_files": encrypted_at_rest,
                "tampered_encrypted_pack_detected": tamper_detected,
                "primary_loss_and_single_corrupt_mirror_recovered": data_preserved,
                "source_provenance_obligations_preserved": data_preserved,
                "restore_kept_inactive_and_revoked_state": authority_inactive,
            },
            "not_tested": [
                "two independent physical/cloud storage providers",
                "immutable off-site backup retention and deletion rights",
                "independent encrypted unlock key recovery",
                "real agent migration and single active writer lease",
                "live backup scheduling, RPO/RTO or billed storage",
            ],
            "status": "PASS_ENCRYPTED_LOCAL_ONLY",
        }


if __name__ == "__main__":
    print(json.dumps(run_trial(), indent=2, ensure_ascii=False))
