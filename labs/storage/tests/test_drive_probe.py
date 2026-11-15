"""Credential-free tests for the STO-005 encrypted-repository transport archive.

The real Drive provider is accessed only in a manual protected workflow; these
tests do not import Google API libraries or require OAuth credentials.
"""
from __future__ import annotations

import io
import tarfile
import tempfile
import unittest
from pathlib import Path

from labs.storage.drive_probe import MAX_ARCHIVE_BYTES, pack_repository, unpack_repository, sha256


class DriveTransportTest(unittest.TestCase):
    def test_pack_unpack_preserves_encrypted_repo_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "live-repo"
            repo.mkdir()
            (repo / "config").write_bytes(b"dummy-restic-config")
            (repo / "data").mkdir()
            (repo / "data" / "fragment").write_bytes(bytes(range(256)) * 9)
            archive = base / "encrypted.tar.gz"
            pack_repository(repo, archive)
            restored = unpack_repository(archive, base / "quarantine")
            self.assertEqual((restored / "config").read_bytes(), b"dummy-restic-config")
            self.assertEqual((restored / "data" / "fragment").read_bytes(),
                             bytes(range(256)) * 9)
            self.assertEqual(sha256(restored / "data" / "fragment"),
                             sha256(repo / "data" / "fragment"))

    def test_reject_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive = base / "evil.tar.gz"
            with tarfile.open(archive, "w:gz") as stream:
                member = tarfile.TarInfo("repository/../../outside")
                payload = b"do-not-write"
                member.size = len(payload)
                stream.addfile(member, io.BytesIO(payload))
            with self.assertRaises(ValueError):
                unpack_repository(archive, base / "output")
            self.assertFalse((base / "outside").exists())

    def test_reject_links_and_oversized_extracted_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive = base / "links.tar.gz"
            with tarfile.open(archive, "w:gz") as stream:
                link = tarfile.TarInfo("repository/escape")
                link.type = tarfile.SYMTYPE
                link.linkname = "../../outside"
                stream.addfile(link)
            with self.assertRaises(ValueError):
                unpack_repository(archive, base / "quarantine")
            huge = base / "large.tar.gz"
            with tarfile.open(huge, "w:gz") as stream:
                member = tarfile.TarInfo("repository/huge")
                member.size = MAX_ARCHIVE_BYTES + 1
                # A sparse-ish payload isn't needed; this unit test only
                # validates the declared extraction bound.
                stream.addfile(member, io.BytesIO(b"0" * (MAX_ARCHIVE_BYTES + 1)))
            with self.assertRaises(ValueError):
                unpack_repository(huge, base / "quarantine2")

    def test_refuse_directory_without_repository_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "dir").mkdir()
            with self.assertRaises(ValueError):
                pack_repository(base / "dir", base / "out.tgz")


if __name__ == "__main__":
    unittest.main()
