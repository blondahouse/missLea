"""Cloudflare: deploy a uniquely named Worker, POST once, delete via REST API."""
from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from labs.compute.common import (EXPECTED, VALUES, command, failure, finish,
                                 report, require_environment)

WORKER = Path(__file__).resolve().parent / "worker"


def worker_url(output, name):
    matches = re.findall(r"https://[a-z0-9-]+[.][a-z0-9.-]+[.]workers[.]dev", output, flags=re.I)
    if matches:
        return matches[-1]
    subdomain = os.environ.get("CF_WORKERS_SUBDOMAIN")
    if subdomain and re.fullmatch(r"[a-zA-Z0-9-]+", subdomain):
        return f"https://{name}.{subdomain}.workers.dev"
    raise RuntimeError("Workers.dev URL not reported; set CF_WORKERS_SUBDOMAIN")


def delete_worker(account, token, name):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{name}"
    request = Request(url, method="DELETE", headers={"Authorization": "Bearer " + token})
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read()
    except HTTPError as exc:
        if exc.code == 404:
            return  # A failed deploy may never have created the Worker.
        raise
    if body and json.loads(body).get("success") is False:
        raise RuntimeError("Cloudflare reported Worker deletion failure")


def run():
    record = report("cloudflare_workers")
    started = time.monotonic()
    name = "misslea-lab-" + secrets.token_hex(8)
    token = secrets.token_urlsafe(24)
    attempted_deploy = False
    try:
        require_environment("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID")
        binary = WORKER / "node_modules" / ".bin" / ("wrangler.cmd" if os.name == "nt" else "wrangler")
        if not binary.is_file():
            raise RuntimeError("Wrangler is not installed in labs/compute/worker")
        with tempfile.TemporaryDirectory(prefix="misslea-worker-") as folder:
            root = Path(folder)
            shutil.copyfile(WORKER / "worker.mjs", root / "worker.mjs")
            config = root / "wrangler.json"
            config.write_text(json.dumps({
                "name": name, "main": "worker.mjs", "compatibility_date": "2026-11-01",
                "workers_dev": True, "vars": {"LAB_TOKEN": token}
            }), encoding="utf-8")
            attempted_deploy = True
            record["resource_id"] = name
            output = command([str(binary), "deploy", "--config", str(config)],
                             cwd=root, timeout=180, combined=True)
            url = worker_url(output, name)
            request = Request(url, data=json.dumps({"values": VALUES}).encode("utf-8"),
                              method="POST", headers={
                                  "Content-Type": "application/json", "X-Lab-Token": token})
            with urlopen(request, timeout=30) as response:
                record["result"] = json.load(response)["result"]
    except Exception as exc:
        failure(record, exc)
    finally:
        if attempted_deploy:
            try:
                delete_worker(os.environ["CLOUDFLARE_ACCOUNT_ID"],
                              os.environ["CLOUDFLARE_API_TOKEN"], name)
                record["cleanup"] = "complete"
            except Exception as exc:
                record["cleanup"] = "failed"
                failure(record, exc)
    return finish(record, started)
