# Compute Lab — disposable remote execution

Three **independent experiments**, not a Compute Router and not a TinyFund migration. Source, probes, credentials and reports are separate from the running Miss Lea. No real user data or LLM calls are sent to compute providers.

## Question, criteria, evidence (recorded before any live trials)

Question: can each of three execution classes start a deterministic synthetic workload, deliver the exact result and leave no active trial resources?

Mandatory criteria for this exploratory integration (no winner is being chosen):

1. An explicit operator-triggered run, no credentials in source or public CI.
2. Exact result `{"count":3,"sum":10,"squares":38}` from values 2, 3, 5, or report FAIL.
3. Attempt cleanup even when execution or result collection fails; a failed cleanup means FAIL and requires operator inspection.
4. Record end-to-end wall time, resource identifier, cleanup outcome, and unavailable CPU/memory/billing data as `null` rather than invented measurements.

Evidence: offline unit tests and one explicitly authorized live smoke per provider. **PASS means one synthetic remote execution only**, not reliable scheduling, low cost, security assurance or production readiness. Stop after all three have one observed PASS or a concrete unresolved blocker; no comparative rankings or adapter framework now. Criteria may be revised prospectively if material new findings emerge; see [evaluation policy](../../docs/evaluation-policy.md).

## Offline, no credits

Run from repository root, Python 3.11+:

```bash
python -m labs.compute.cli list
python -m unittest discover -s labs -t . -p 'test_*.py' -v
```

**Nothing runs remotely without both `--live` and `--acknowledge-cost`.** These flags are intentional because trial credits are not guaranteed, and none of the providers supplies a proven hard spending cap through this lab.

## One remote trial at a time

### E2B (Linux sandbox)

Install `pip install e2b` in an isolated environment. Set `E2B_API_KEY` locally (never commit it). The trial creates a sandbox with a 90-second timeout and internet egress disabled, executes Python, optionally samples memory and calls `kill()` in `finally`.

```bash
python -m labs.compute.cli run e2b --live --acknowledge-cost --output reports/e2b-report.json
```

### Cloudflare Workers (HTTP function)

Install Node.js and `npm install --prefix labs/compute/worker`. Configure `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` locally, and enable the account's workers.dev subdomain. For digital independence, prefer an **account-owned** token from a dedicated Cloudflare account rather than the founder's personal user token. **This trial creates a new Worker**, so it requires **Workers product-level Admin**; a token with per-Worker Editor cannot execute this particular trial. See [Cloudflare identity study](../identity/cloudflare-study.md) for the narrower pre-existing Worker option and safe verification. Optionally set `CF_WORKERS_SUBDOMAIN` if Wrangler does not print a URL. The token needs Workers Scripts Write; the experiment deploys a randomly named Worker, performs an authenticated synthetic POST and deletes the script via the official REST API. The short-lived `LAB_TOKEN` is generated per trial and stored only in an OS temporary configuration; it is not a production secret.

```bash
python -m labs.compute.cli run cloudflare --live --acknowledge-cost --output reports/cloudflare-report.json
```

### Google Cloud Run Jobs (container job)

Install/authenticate `gcloud`, enable the Cloud Run API and Cloud Logging access and set `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_REGION`. Appropriate IAM permissions are required to create, execute, delete jobs and read their logs. The trial creates a uniquely named one-task Job from the public `python:3.12-alpine` image, invokes `python3 -c` with the same synthetic probe, waits, reads the result marker from Cloud Logging and deletes the Job. No image build or Artifact Registry upload is required for this experiment, but use of a public mutable image tag is not a production supply-chain guarantee.

```bash
python -m labs.compute.cli run cloud_run --live --acknowledge-cost --output reports/cloud_run-report.json
```

Cloud Logging can be delayed; missing logging permissions or marker produce FAIL even if the job completed. Deleting a Job ends its executions but does not delete retained Cloud Logging entries. Cloud Run may still charge for execution; do not assume image pull, logging, networking or quotas are cost-free.

## Interpreting reports and failures

`status: PASS` requires both exact synthetic result and confirmed cleanup. `cost_usd: null` and `remote_cpu_seconds: null` mean **not measured**, not zero. `remote_memory_bytes` is populated only if E2B exposes a sample. `wall_seconds` includes setup, execution, result retrieval and cleanup; it is **not billable CPU duration**. The report never includes credentials. Provider exception bodies are deliberately omitted to avoid leaking keys.

On `cleanup: failed`, search for the reported `resource_id` in the relevant provider account and remove it manually. For Cloudflare this is the Worker name; for Cloud Run the Job name; for E2B the sandbox ID. Failure during initial creation can leave a partially created resource, so cleanup is attempted when creation was initiated.

All public GitHub CI runs remain synthetic and credential-free. Actual account access, charges, performance and teardown are **NOT TESTED** until a live report is produced.

References: [E2B Python SDK](https://github.com/e2b-dev/E2B/blob/main/packages/python-sdk/README.md), [Cloudflare Wrangler](https://developers.cloudflare.com/workers/wrangler/commands/workers/), [Cloudflare Worker deletion](https://developers.cloudflare.com/api/resources/workers/subresources/scripts/methods/delete/), [Cloud Run Jobs](https://docs.cloud.google.com/run/docs/create-jobs), [Cloud Run logs](https://docs.cloud.google.com/run/docs/logging).
