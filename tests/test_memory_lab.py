"""Executable baseline checks; no external credentials or network required."""

import tempfile
import unittest
from pathlib import Path

from lab.benchmark import load_scenario, run_scenario
from lab.memory import SQLiteBaseline


SCENARIO = Path(__file__).resolve().parents[1] / "scenarios" / "memory_v1.json"


class MemoryLabTests(unittest.TestCase):
    def test_scenario_is_synthetic_and_valid(self):
        suite = load_scenario(SCENARIO)
        self.assertTrue(suite["synthetic"])
        self.assertEqual(len(suite["events"]), 10)
        self.assertEqual(len(suite["probes"]), 6)

    def test_baseline_retrieval_is_measured_not_fabricated(self):
        suite = load_scenario(SCENARIO)
        with tempfile.TemporaryDirectory() as directory:
            candidate = SQLiteBaseline(str(Path(directory) / "test.sqlite"))
            try:
                report = run_scenario(candidate, suite)
            finally:
                candidate.close()
        summary = report["summary"]
        self.assertEqual(summary["probe_count"], 6)
        self.assertEqual(summary["event_count"], 10)
        self.assertGreaterEqual(summary["retrieval_recall_at_k"], 0)
        self.assertLessEqual(summary["retrieval_recall_at_k"], 1)
        self.assertGreaterEqual(summary["obsolete_intrusion_rate"], 0)
        self.assertLessEqual(summary["obsolete_intrusion_rate"], 1)
        self.assertEqual(summary["memory_compaction"], "not_tested")
        self.assertEqual(summary["semantic_answer_quality"], "not_tested")
        self.assertEqual(summary["model_cost_usd"], 0.0)

    def test_snapshot_restores_evidence_and_search(self):
        suite = load_scenario(SCENARIO)
        with tempfile.TemporaryDirectory() as directory:
            original = SQLiteBaseline(str(Path(directory) / "original.sqlite"))
            try:
                for event in suite["events"]:
                    original.add(event)
                before = [
                    original.search(probe["question"], 3)
                    for probe in suite["probes"]
                ]
                snapshot = original.snapshot()
            finally:
                original.close()
            restored = SQLiteBaseline.from_snapshot(
                snapshot, str(Path(directory) / "copy.sqlite")
            )
            try:
                after = [
                    restored.search(probe["question"], 3)
                    for probe in suite["probes"]
                ]
                self.assertEqual(before, after)
            finally:
                restored.close()

    def test_snapshot_refuses_to_replace_existing_state(self):
        with tempfile.TemporaryDirectory() as directory:
            source = SQLiteBaseline(str(Path(directory) / "original.sqlite"))
            try:
                snapshot = source.snapshot()
            finally:
                source.close()
            with self.assertRaises(FileExistsError):
                SQLiteBaseline.from_snapshot(
                    snapshot, str(Path(directory) / "original.sqlite")
                )

    def test_evaluator_does_not_send_answers_to_candidate(self):
        class SpyCandidate:
            name = "spy"

            def __init__(self):
                self.events = []

            def add(self, event):
                self.events.append(event)

            def search(self, question, limit):
                return []

            def close(self):
                pass

        spy = SpyCandidate()
        run_scenario(spy, load_scenario(SCENARIO))
        self.assertEqual(
            set(spy.events[0]), {"id", "at", "text"}
        )

    def test_rejects_non_synthetic_scenarios(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private.json"
            path.write_text(
                '{"schema_version":1,"synthetic":false,"events":[],"probes":[]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "synthetic"):
                load_scenario(path)


if __name__ == "__main__":
    unittest.main()
