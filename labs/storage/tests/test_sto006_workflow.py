"""Offline STO-006 workflow wiring regression tests, not a security audit.

The real provider operations only happen after manual environment approval;
these checks catch obvious accidental secret mixing or artifact bypasses.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "storage-sto006-dual-provider.yml"


def jobs(source: str) -> dict[str, str]:
    sections = re.split(r"(?m)^  (?=[a-z][a-z0-9-]+:\n)", source.split("\njobs:\n", 1)[1])
    return {text.split(":\n", 1)[0]: text for text in sections if ":\n" in text}


class DualProviderWorkflowContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text(encoding="utf-8")
        cls.jobs = jobs(cls.source)

    def test_manual_and_read_only(self):
        self.assertIn("on:\n  workflow_dispatch:\n", self.source)
        self.assertNotIn("  pull_request:", self.source)
        self.assertNotIn("  push:", self.source)
        self.assertIn("permissions:\n  contents: read\n", self.source)

    def test_five_stage_protocol(self):
        self.assertEqual(set(self.jobs), {
            "build-one-generation", "upload-b2", "upload-drive",
            "restore-from-b2-without-drive", "restore-from-drive-without-b2",
        })
        self.assertNotIn("secrets.", self.jobs["build-one-generation"])
        for name in ("restore-from-b2-without-drive", "restore-from-drive-without-b2"):
            body = self.jobs[name]
            self.assertIn("needs: [upload-b2, upload-drive]", body)
            self.assertIn("name: sto006-source-checksums-only", body)
            self.assertNotIn("name: sto006-common-encrypted-synthetic-archive", body)
            self.assertIn("labs.storage.remote_recovery validate", body)
            self.assertIn("restic", body)

    def test_no_cross_provider_secret_access(self):
        for name in ("upload-b2", "restore-from-b2-without-drive"):
            text = self.jobs[name]
            self.assertIn("environment: sto004-b2", text)
            self.assertIn("secrets.STO004_B2_", text)
            self.assertNotIn("secrets.STO005_DRIVE_", text)
        for name in ("upload-drive", "restore-from-drive-without-b2"):
            text = self.jobs[name]
            self.assertIn("environment: sto005-drive", text)
            self.assertIn("secrets.STO005_DRIVE_", text)
            self.assertNotIn("secrets.STO004_B2_", text)

    def test_one_common_archive_versus_two_recovery_sources(self):
        self.assertEqual(self.source.count(
            "name: sto006-common-encrypted-synthetic-archive"), 3)
        self.assertIn("--archive \"$RUNNER_TEMP/sto006-common-encrypted.tar.gz\"", self.source)
        self.assertIn("aws s3api get-object", self.jobs["restore-from-b2-without-drive"])
        self.assertIn("labs.storage.drive_probe download",
                      self.jobs["restore-from-drive-without-b2"])
        self.assertEqual(self.source.count("archive.sha256"), 3)


if __name__ == "__main__":
    unittest.main()
