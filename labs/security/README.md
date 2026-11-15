# Security Lab — sustainability, secrets, and trusted execution

**First slice:** manually submit one harmless computation to Miss Lea's existing Cloudflare Worker with a dedicated **task secret**, entirely separate from the Cloudflare account API token. This is research, not the running TinyFund agent, not a general agent executor, and **not a secret manager**.

## Decision and acceptance (defined before live execution)

Can an operator send an authorized, bounded synthetic task to an existing Worker **without** granting that task administrative Cloudflare permissions?

Mandatory checks:
1. An `/run` HTTP endpoint refuses all requests without a 32+ character high-entropy secret stored as a Cloudflare **Worker Secret** (not a plaintext variable).
2. The Worker accepts exactly one supported task: `sum_squares` over 1–16 integers in [-1000,1000]. No arbitrary code, browser action, URL fetching, file storage, persistence, payments, account or credential management.
3. The manual client never accepts the secret as a command-line argument, refuses non-HTTPS/non-`workers.dev` targets, refuses redirects, and does not echo the token or remote error bodies.
4. CI validates positive and negative cases without real provider credentials or an external network.
5. The operator can reproduce one manually triggered live result `count=3,sum=10,squares=38` and revoke access by changing/deleting the Worker Secret; live execution is **not tested** until the user runs it.

**Stop condition:** once offline CI and one separately authorized live task succeed, stop. Do not auto-enable agents, deploy code, allocate long-running compute or introduce a financial instrument.

## Why two tokens, not one?

- **Cloudflare Account API Token**: authorizes provisioning/updating/deleting Workers through Cloudflare's management API. It is needed by Wrangler or automated deployment, **not for invoking** the published HTTP Worker.
- **MISSLEA_TASK_SECRET**: an unrelated random secret held by the Worker. The local manual client sends it as a Bearer token in the HTTPS **Authorization header** to request one synthetic calculation.

Do not put an account token into the Worker's code, `MISSLEA_TASK_SECRET`, request body, URL, GitHub, a model prompt or a public report.

This is deliberately a simple shared-secret test; it is *not* robust agent identity, rate limiting, anti-replay, cryptographic signing, key rotation, secure vault custody, durable jobs, autonomous token provisioning or untrusted-input hardening. Since the operation is pure and side-effect free, replays cannot spend money or mutate state, but they can still consume request quota. Keep the Worker on Workers **Free** and remove access immediately if unexpected activity appears.

## Manual Cloudflare installation

Target: the existing `late-glade-5dde` Worker at `misslea931.workers.dev` (no need to create another Worker or a Cloudflare management API token).

1. In Cloudflare Dashboard, open **Workers & Pages → late-glade-5dde → Edit Code**. Replace only its Hello World source with [manual_worker/worker.mjs](manual_worker/worker.mjs), then deploy. `GET /health` returns a non-secret status.
2. Generate a fresh 48+-character URL-safe value using a trusted password generator; save it in a local password manager as **Miss Lea / Cloudflare Worker Task Secret**. Never send it through ChatGPT, GitHub, email or screenshots.
3. In **Settings → Variables and Secrets → Add**, choose **Secret** (not plaintext), name it `MISSLEA_TASK_SECRET`, paste the generated value and Deploy. Without this configuration, all `POST /run` requests are rejected.
4. On a trusted machine with Python 3.11+, run from the repository root:

```bash
python -m labs.security.dispatch --endpoint https://late-glade-5dde.misslea931.workers.dev/run
```

The command prompts **privately** for the task secret without including it in shell history or command-line arguments. For unattended *future* automation an OS-backed secret manager will be required; this initial test is manual only. If a `MISSLEA_TASK_TOKEN` environment variable is already present, the client uses it, but **do not export this value by typing it directly into shell history**.

Expected evidence:

```json
{"status":"PASS","result":{"count":3,"sum":10,"squares":38},"remote_job":"synchronous_synthetic"}
```

**Do not send real memory, passwords, personal information or provider credentials as tasks.** This Worker does not preserve results across requests, schedule jobs, or run arbitrary scripts. Its maximum useful work is deliberately tiny; Workers Free has a tight CPU limit. Modifying and redeploying the code remains a *manual dashboard action* until a separate, properly held management credential is authorized.

## Offline validation

```bash
node --test labs/security/tests/manual_worker.test.mjs
python -m unittest discover -s labs -t . -p 'test_*.py' -v
```

Neither command makes external calls.

## First live manual experiment — operator-reported evidence (2026-11-15)

The operator reported deploying the published Worker, configuring `MISSLEA_TASK_SECRET` as a Cloudflare **Secret**, and receiving **HTTP 200** with `{"status":"ok","result":{"count":3,"sum":10,"squares":38}}` for a manual authorized POST. The same synthetic POST **without Authorization** returned **HTTP 401**.

**Scope of this evidence:** one positive and one unauthenticated negative request as reported by the operator, without storing actual request credentials. Not an independently captured provider audit, robustness assessment, recovery test, rate-limit test or permission to provide cloud account master keys. The manual dispatch experiment is therefore sufficiently evidenced for its narrow initial stop condition.

## First real vault candidate experiments

[SEC-001 isolated vendor trials](trials/README.md) run real OpenBao (limited machine token access and revocation) and self-hosted Infisical (startup/health only) in ephemeral GitHub Actions. They use synthetic credentials and never deploy a master Cloudflare token. **The scopes of evidence differ; no winner or production authorization is implied.**

## Broader Security Lab — next research decisions (not implemented)

We need an independently authenticated **Credential Broker** that resolves secrets internally and exposes narrow operations to LLM-driven callers. It must guard against prompt injection and compromised agent tools, isolate any provisioning/root credentials, enforce budgets/allowed actions in code, provide audit and revoke/rotate keys without leaking them. Identity proof and an active-instance lease/fencing mechanism must survive model and compute changes without trusting stale backups.

Use the [proposed Security selection gates and candidate comparison](selection-criteria.md) before choosing a hosted or self-managed vault. Compare threat isolation, machine identity, unlock/recovery, owner-dependence, portability, cost, auditing, safe rotation and realistic operability. Do not invent cryptography or expose a root vault key to an LLM.

Root recovery materials must be separate from active compute, agent-readable memory, and the backups they unlock. Losing a vault cannot make decrypting all backups impossible.

See [Storage Lab](../storage/README.md) and [digital independence](../../docs/digital-independence.md).
