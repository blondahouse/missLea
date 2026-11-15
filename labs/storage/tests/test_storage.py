"""Synthetic state continuity tests. No secrets, crypto, cloud or live memory."""
from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from labs.storage.cli import demo
from labs.storage.snapshot import (
    InvalidSnapshot, create_snapshot, restore_to_quarantine, verify_snapshot,
)


class StorageLabTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        self.source = self.root / "source.sqlite"
        with sqlite3.connect(self.source) as conn:
            conn.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, value TEXT)")
            conn.execute("INSERT INTO events(value) VALUES ('synthetic')")
        self.bundle = self.root / "bundle"

    def tearDown(self):
        self.dir.cleanup()

    def test_snapshot_and_quarantine_restore(self):
        manifest = create_snapshot(self.source, self.bundle)
        self.assertFalse(manifest["encrypted"])
        self.assertTrue(manifest["synthetic_only"])
        self.assertEqual(verify_snapshot(self.bundle), manifest)
        self.source.unlink()
        restored = self.root / "quarantine.sqlite"
        receipt = restore_to_quarantine(self.bundle, restored)
        with sqlite3.connect(restored) as conn:
            self.assertEqual(conn.execute("SELECT value FROM events").fetchone()[0], "synthetic")
        self.assertFalse(receipt["authority_restored"])
        self.assertFalse(receipt["active_instance_started"])

    def test_existing_destination_is_never_overwritten(self):
        self.bundle.mkdir()
        with self.assertRaises(ValueError):
            create_snapshot(self.source, self.bundle)
        self.bundle.rmdir()
        create_snapshot(self.source, self.bundle)
        already = self.root / "exists.sqlite"
        already.write_bytes(b"never replace")
        with self.assertRaises(ValueError):
            restore_to_quarantine(self.bundle, already)
        self.assertEqual(already.read_bytes(), b"never replace")

    def test_hash_failure_rejects_corrupt_backup(self):
        create_snapshot(self.source, self.bundle)
        with (self.bundle / "state.sqlite").open("ab") as f:
            f.write(b"corrupted")
        with self.assertRaises(InvalidSnapshot):
            verify_snapshot(self.bundle)

    def test_manifest_must_indicate_synthetic_and_not_encrypted(self):
        create_snapshot(self.source, self.bundle)
        path = self.bundle / "manifest.json"
        for alteration in ({"encrypted": True},
                           {"synthetic_only": False},
                           {"authority_restored": True},
                           {"file": "../secrets"}):
            with self.subTest(alteration=alteration):
                manifest = json.loads(path.read_text())
                manifest.update(alteration)
                path.write_text(json.dumps(manifest))
                with self.assertRaises(InvalidSnapshot):
                    verify_snapshot(self.bundle)
                manifest.update({"encrypted": False, "synthetic_only": True,
                                 "authority_restored": False, "file": "state.sqlite"})
                path.write_text(json.dumps(manifest))

    def test_independent_mirror_survives_one_backup_corruption(self):
        create_snapshot(self.source, self.bundle)
        mirror = self.root / "independent_mirror"
        shutil.copytree(self.bundle, mirror)
        with (self.bundle / "state.sqlite").open("ab") as f:
            f.write(b"changed")
        with self.assertRaises(InvalidSnapshot):
            verify_snapshot(self.bundle)
        self.assertEqual(verify_snapshot(mirror)["file"], "state.sqlite")
        receipt = restore_to_quarantine(mirror, self.root / "quarantine.sqlite")
        self.assertEqual(receipt["status"], "restored_to_quarantine")

    def test_demo_recovers_two_events_without_network(self):
        result = demo()
        self.assertTrue(result["corrupted_backup_rejected"])
        self.assertTrue(result["independent_backup_valid"])
        self.assertTrue(result["restored_inactive"])
        self.assertFalse(result["authority_restored"])
        self.assertEqual(result["external_calls"], 0)
        self.assertEqual(result["recovered_events"],
                         ["synthetic-foundation", "synthetic-choice"])


if __name__ == "__main__":
    unittest.main()
