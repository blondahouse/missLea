"""E2B: create sandbox, execute synthetic Python, observe, kill."""
from __future__ import annotations

import os
import shlex
import time

from labs.compute.common import (command, encoded_python_probe, failure,
                                 finish, parse_result, report, require_environment)


def run():
    record = report("e2b")
    started = time.monotonic()
    sandbox = None
    try:
        require_environment("E2B_API_KEY")
        from e2b import Sandbox  # optional SDK; install only for this trial
        sandbox = Sandbox.create(timeout=90, allow_internet_access=False,
                                 metadata={"purpose": "misslea-compute-lab"})
        record["resource_id"] = sandbox.sandbox_id
        expression = encoded_python_probe()
        output = sandbox.commands.run("python3 -c " + shlex.quote(expression), timeout=45)
        if output.exit_code != 0:
            raise RuntimeError("Remote probe exited unsuccessfully")
        record["result"] = parse_result(output.stdout)
        # Optional remote metrics are not silently inferred from local wall time.
        try:
            samples = sandbox.get_metrics()
            if samples:
                latest = samples[-1]
                record["observations"]["remote_memory_bytes"] = getattr(latest, "mem_used", None)
                record["observations"]["remote_metrics_status"] = "sampled_memory_only"
        except Exception:
            record["observations"]["remote_metrics_status"] = "unavailable"
    except Exception as exc:
        failure(record, exc)
    finally:
        if sandbox is not None:
            try:
                sandbox.kill()
                record["cleanup"] = "complete"
            except Exception as exc:
                record["cleanup"] = "failed"
                failure(record, exc)
    return finish(record, started)
