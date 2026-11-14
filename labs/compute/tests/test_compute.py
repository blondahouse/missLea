"""Offline only: checks protocol, reports and safety gates; never uses real keys."""
from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from labs.compute import cli, common
from labs.compute.cloudflare_trial import worker_url


class ProtocolTests(unittest.TestCase):
    def test_probe_payload(self):
        local = io.StringIO()
        with contextlib.redirect_stdout(local):
            exec(common.PYTHON_PROBE, {})
        self.assertEqual(common.parse_result(local.getvalue()), common.EXPECTED)
        self.assertIn("b64decode", common.encoded_python_probe())

    def test_bad_remote_results_do_not_pass(self):
        record = common.report("fake")
        record["result"] = {"sum": 10}
        record["cleanup"] = "complete"
        common.finish(record, 0)
        self.assertEqual(record["status"], "FAIL")

    def test_cleanup_required(self):
        record = common.report("fake")
        record["result"] = common.EXPECTED
        common.finish(record, 0)
        self.assertEqual(record["status"], "FAIL")

    def test_missing_marker_fails(self):
        with self.assertRaises(ValueError):
            common.parse_result("finished")

    def test_worker_url_from_wrangler_output(self):
        output = "Deployed to https://misslea-lab-abc.team.workers.dev"
        self.assertEqual(worker_url(output, "misslea-lab-abc"),
                         "https://misslea-lab-abc.team.workers.dev")

    def test_worker_url_is_not_invented(self):
        with patch.dict("os.environ", {"CF_WORKERS_SUBDOMAIN": ""}):
            with self.assertRaises(RuntimeError):
                worker_url("no URL", "misslea-lab-abc")

    def test_no_remote_calls_without_both_flags(self):
        for flags in ([], ["--live"], ["--acknowledge-cost"]):
            with self.subTest(flags=flags):
                with patch("labs.compute.e2b_trial.run") as remote:
                    with contextlib.redirect_stderr(io.StringIO()):
                        with self.assertRaises(SystemExit):
                            cli.main(["run", "e2b", *flags])
                    remote.assert_not_called()

    def test_list_is_offline(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cli.main(["list"]), 0)
        self.assertIn("cloud_run", out.getvalue())


if __name__ == "__main__":
    unittest.main()
