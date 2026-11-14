"""Offline only: checks protocol, reports and safety gates; never uses real keys."""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import types
import unittest
from unittest.mock import patch

from labs.compute import cli, common, e2b_trial, cloudflare_trial, cloud_run_trial
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

    def test_e2b_lifecycle_with_fake_sdk(self):
        class FakeSandbox:
            sandbox_id = "synthetic-sandbox"
            killed = False

            @classmethod
            def create(cls, **kwargs):
                self.assert_placeholder = kwargs
                return cls()

            def __init__(self):
                self.commands = types.SimpleNamespace(run=lambda *a, **kw: types.SimpleNamespace(
                    exit_code=0, stdout=common.MARKER + json.dumps(common.EXPECTED)))

            def get_metrics(self):
                return []

            def kill(self):
                self.killed = True
                return True

        instance = FakeSandbox()
        with patch.dict(os.environ, {"E2B_API_KEY": "synthetic"}, clear=False):
            with patch.dict(sys.modules, {"e2b": types.SimpleNamespace(Sandbox=types.SimpleNamespace(
                create=lambda **kw: instance))}):
                result = e2b_trial.run()
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(instance.killed)
        self.assertEqual(result["resource_id"], "synthetic-sandbox")

    def test_cloudflare_lifecycle_with_mocked_network(self):
        calls = []
        def fake_urlopen(request, timeout=None):
            calls.append(request.get_method())
            if request.get_method() == "POST":
                return io.BytesIO(json.dumps({"result": common.EXPECTED}).encode())
            return io.BytesIO(b'{"success": true}')

        with patch.dict(os.environ, {
            "CLOUDFLARE_API_TOKEN": "synthetic", "CLOUDFLARE_ACCOUNT_ID": "synthetic"
        }):
            with patch.object(cloudflare_trial.Path, "is_file", return_value=True):
                with patch.object(cloudflare_trial, "command",
                                  return_value="https://misslea-lab-test.team.workers.dev"):
                    with patch.object(cloudflare_trial, "urlopen", side_effect=fake_urlopen):
                        result = cloudflare_trial.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(calls, ["POST", "DELETE"])

    def test_cloud_run_lifecycle_with_mocked_gcloud(self):
        calls = []
        def fake_command(args, **kwargs):
            calls.append(args)
            if args[:3] == ["gcloud", "logging", "read"]:
                return json.dumps([{"textPayload": common.MARKER + json.dumps(common.EXPECTED)}])
            return ""
        with patch.dict(os.environ, {
            "GOOGLE_CLOUD_PROJECT": "synthetic", "GOOGLE_CLOUD_REGION": "europe-west1"
        }):
            with patch.object(cloud_run_trial, "command", side_effect=fake_command):
                result = cloud_run_trial.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual([c[3] for c in calls if c[:3] == ["gcloud", "run", "jobs"]],
                         ["create", "execute", "delete"])

    def test_cloud_run_deletes_on_missing_result(self):
        calls = []
        def fake_command(args, **kwargs):
            calls.append(args)
            if args[:3] == ["gcloud", "logging", "read"]:
                raise RuntimeError("synthetic logging outage")
            return ""
        with patch.dict(os.environ, {
            "GOOGLE_CLOUD_PROJECT": "synthetic", "GOOGLE_CLOUD_REGION": "europe-west1"
        }):
            with patch.object(cloud_run_trial, "command", side_effect=fake_command):
                result = cloud_run_trial.run()
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["cleanup"], "complete")
        self.assertTrue(any(c[:4] == ["gcloud", "run", "jobs", "delete"] for c in calls))


if __name__ == "__main__":
    unittest.main()
