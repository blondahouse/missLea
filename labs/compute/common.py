"""Shared synthetic workload and evidence format, not an execution adapter."""
from __future__ import annotations

import base64
import json
import subprocess
import time
from datetime import datetime, timezone

VALUES = [2, 3, 5]
EXPECTED = {"count": 3, "sum": 10, "squares": 38}
MARKER = "COMPUTE_LAB_RESULT="
# The same Python program runs in E2B and an official Python Cloud Run image.
PYTHON_PROBE = """import json, time
start = time.perf_counter()
values = [2, 3, 5]
result = {'count': len(values), 'sum': sum(values), 'squares': sum(x*x for x in values)}
print('COMPUTE_LAB_RESULT=' + json.dumps(result, separators=(',', ':')), flush=True)
"""


def encoded_python_probe():
    code = base64.b64encode(PYTHON_PROBE.encode("utf-8")).decode("ascii")
    return "exec(__import__('base64').b64decode('" + code + "'))"


def parse_result(output):
    for line in output.splitlines():
        at = line.find(MARKER)
        if at >= 0:
            try:
                value = json.loads(line[at + len(MARKER):].strip())
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON probe result") from exc
            if not isinstance(value, dict):
                raise ValueError("Probe result must be an object")
            return value
    raise ValueError("No synthetic result marker was observed")


def command(args, *, timeout=180, cwd=None, input=None, combined=False):
    result = subprocess.run(args, cwd=cwd, input=input, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=timeout, check=False)
    if result.returncode != 0:
        # Do not include stderr, which can expose CLI configuration or credentials.
        raise RuntimeError(f"{args[0]} exited with status {result.returncode}")
    return result.stdout + ("\n" + result.stderr if combined else "")


def report(provider):
    return {
        "provider": provider, "synthetic": True,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL", "result": None, "expected": EXPECTED,
        "resource_id": None, "cleanup": "not_needed",
        "observations": {
            "wall_seconds": None, "remote_cpu_seconds": None,
            "remote_memory_bytes": None, "cost_usd": None,
            "remote_metrics_status": "not_measured",
            "cost_status": "not_measured",
        },
        "error": None,
    }


def finish(record, started):
    record["observations"]["wall_seconds"] = round(time.monotonic() - started, 3)
    if record["error"] is None and record["result"] == EXPECTED and record["cleanup"] == "complete":
        record["status"] = "PASS"
    return record


def failure(record, exc):
    # No exception payloads from third-party SDKs: they may echo secrets.
    record["error"] = type(exc).__name__


def require_environment(*names):
    import os
    absent = [name for name in names if not os.environ.get(name)]
    if absent:
        raise RuntimeError("Missing environment variables: " + ", ".join(absent))
