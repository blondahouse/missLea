"""Run the lab without installing packages: python -m lab.cli."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from lab.benchmark import load_scenario, run_scenario
from lab.memory import SQLiteBaseline

CANDIDATES = {
    "sqlite": "implemented — no API, no model cost",
    "letta": "planned — not integrated or evaluated",
    "mem0": "planned — not integrated or evaluated",
    "graphiti": "planned — not integrated or evaluated",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Miss Lea synthetic memory laboratory")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="Show implemented and planned candidates")
    run = sub.add_parser("run", help="Run a synthetic evaluation")
    run.add_argument("--candidate", choices=sorted(CANDIDATES), default="sqlite")
    run.add_argument("--scenario", default="scenarios/memory_v1.json")
    run.add_argument("--output")
    run.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    if args.command == "list":
        for name, status in CANDIDATES.items():
            print(f"{name}: {status}")
        return
    if args.candidate != "sqlite":
        parser.error(
            f"{args.candidate} is not integrated yet; no fabricated results"
        )
    scenario = load_scenario(args.scenario)
    with tempfile.TemporaryDirectory() as folder:
        candidate = SQLiteBaseline(str(Path(folder) / "baseline.sqlite"))
        try:
            report = run_scenario(candidate, scenario, top_k=args.top_k)
            baseline_hits = [
                candidate.search(probe["question"], args.top_k)
                for probe in scenario["probes"]
            ]
            archive = candidate.snapshot()
        finally:
            candidate.close()
        restored = SQLiteBaseline.from_snapshot(
            archive, str(Path(folder) / "restored.sqlite")
        )
        try:
            restored_hits = [
                restored.search(probe["question"], args.top_k)
                for probe in scenario["probes"]
            ]
        finally:
            restored.close()
        report["summary"]["same_candidate_snapshot_recovery"] = (
            "passed" if baseline_hits == restored_hits else "failed"
        )
    output = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
