"""Cloud Run: ephemeral job using public Python image, logs as result, delete."""
from __future__ import annotations

import json
import os
import secrets
import time

from labs.compute.common import (command, encoded_python_probe, failure,
                                 finish, parse_result, report, require_environment)

IMAGE = "python:3.12-alpine"


def log_result(project, job):
    query = (f'resource.type="cloud_run_job" AND '
             f'resource.labels.job_name="{job}" AND '
             f'textPayload:"COMPUTE_LAB_RESULT="')
    for attempt in range(8):
        output = command([
            "gcloud", "logging", "read", query, "--project=" + project,
            "--freshness=10m", "--limit=30", "--format=json",
        ], timeout=40)
        events = json.loads(output)
        for event in events:
            message = event.get("textPayload") or event.get("jsonPayload", {}).get("message", "")
            if "COMPUTE_LAB_RESULT=" in message:
                return parse_result(message)
        if attempt < 7:
            time.sleep(2)
    raise RuntimeError("Probe result was not found in Cloud Logging")


def run():
    record = report("cloud_run_jobs")
    started = time.monotonic()
    job = "misslea-lab-" + secrets.token_hex(6)
    attempted_create = False
    try:
        require_environment("GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_REGION")
        project = os.environ["GOOGLE_CLOUD_PROJECT"]
        region = os.environ["GOOGLE_CLOUD_REGION"]
        common = ["--project=" + project, "--region=" + region, "--quiet"]
        attempted_create = True
        record["resource_id"] = job
        command(["gcloud", "run", "jobs", "create", job, *common,
                 "--image=" + IMAGE, "--command=python3",
                 "--args=-c," + encoded_python_probe(),
                 "--tasks=1", "--max-retries=0", "--task-timeout=90s",
                 "--cpu=1", "--memory=512Mi"], timeout=180)
        command(["gcloud", "run", "jobs", "execute", job, *common,
                 "--wait", "--format=json"], timeout=240)
        record["result"] = log_result(project, job)
    except Exception as exc:
        failure(record, exc)
    finally:
        if attempted_create:
            try:
                command(["gcloud", "run", "jobs", "delete", job,
                         "--project=" + os.environ["GOOGLE_CLOUD_PROJECT"],
                         "--region=" + os.environ["GOOGLE_CLOUD_REGION"],
                         "--quiet"], timeout=120)
                record["cleanup"] = "complete"
            except Exception as exc:
                record["cleanup"] = "failed"
                failure(record, exc)
    return finish(record, started)
