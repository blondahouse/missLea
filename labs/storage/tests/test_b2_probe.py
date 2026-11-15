"""Credential-free B2 client tests: exact bytes, key scoping and corruption."""
import io
import tempfile
import unittest
from pathlib import Path

from labs.storage.b2_probe import upload, download, validate_key, sha256


class FakeS3:
    def __init__(self):
        self.files = {}

    def put_object(self, *, Bucket, Key, Body, ContentType):
        assert Bucket == "misslea-storage-lab-b2"
        assert ContentType == "application/gzip"
        self.files[Key] = Body.read()

    def head_object(self, *, Bucket, Key):
        assert Bucket == "misslea-storage-lab-b2"
        return {"ContentLength": len(self.files[Key])}

    def get_object(self, *, Bucket, Key):
        assert Bucket == "misslea-storage-lab-b2"
        return {"Body": io.BytesIO(self.files[Key])}


class B2ProbeTest(unittest.TestCase):
    def test_round_trip_exact_common_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original = root / "encrypted.tar.gz"
            restored = root / "recovered.tar.gz"
            original.write_bytes(bytes(range(256)) * 1024)
            s3 = FakeS3()
            key = "sto006/12345/memory-restic.tar.gz"
            upload(original, key, client=s3)
            download(restored, key, sha256(original), client=s3)
            self.assertEqual(original.read_bytes(), restored.read_bytes())

    def test_detect_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original = root / "archive.tar.gz"
            original.write_bytes(b"synthetic encrypted archive fixture")
            s3 = FakeS3()
            key = "sto006/12345/memory-restic.tar.gz"
            upload(original, key, client=s3)
            s3.files[key] = b"tampered archive"
            with self.assertRaises(ValueError):
                download(root / "restore.tar.gz", key, sha256(original), client=s3)

    def test_prevent_non_lab_bucket_or_key_paths(self):
        for key in ("../../private", "sto004/123/memory-restic.tar.gz",
                    "sto006/../../private", "sto006/x/memory-restic.tar.gz",
                    "sto006/3/other-file.tar.gz"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_key(key)


if __name__ == "__main__":
    unittest.main()
