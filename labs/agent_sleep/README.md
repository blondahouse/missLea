# Agent + Memory + Sleep Lab — free hybrid prototype

**Status:** synthetic offline implementation; actual cloud wake and execution **NOT TESTED**.
No real Miss Lea memory, personal data, cloud account mutation, paid work or TinyFund migration.

## Decision
Can a Cloudflare SQLite-backed Durable Object hold a wake schedule and small event log, while a separate Free-tier platform (first candidate: Deno Deploy) executes a bounded task and returns its result? Does the schedule and synthetic prior decision survive runtime replacement without a persistent owner computer or VM?

**Minimal acceptance, recorded before live execution:**
1. Authenticated schedule creates exactly two wakes, with one prior synthetic decision retained.
2. The second wake sees the first wake's stored result and executes on an independent cloud service.
3. Interrupted/denied tasks retry once and then stop; no silent paid fallback or infinite polling.
4. Actual Cloudflare Alarm, Deno HTTP response, state after the second wake and platform usage/cost receipts must be captured. Local tests do **not** establish cloud PASS.
5. Zero out-of-pocket spend and zero use of the owner's machines, real data or model API keys.

**Stop rule:** once a real two-wake cycle succeeds on both Free plans, record a credible fallback and proceed to choosing the actual memory/agent harness. If blocked, swap only the failing component. No four-provider compute tournament.

## Structure
- `worker.mjs`: owner-authenticated Cloudflare Worker + SQLite-backed Durable Object; persists `run_id`, a synthetic decision, two wake events and next alarm. It invokes the external executor but does no LLM inference.
- `executor.mjs`: stateless Deno Deploy endpoint accepting a restricted, authenticated, repeatable arithmetic task (2²+3²+5²=38). No external network access or storage.
- `tests.mjs`: runnable native Node tests with in-process fake storage, actual task contract and simulated alarms.
- `wrangler.toml`: isolated lab Worker name and SQLite Durable Object migration.

**Local/offline check** (on GitHub Actions, not the owner's PC): `node --test labs/agent_sleep/tests.mjs`.

## Operator-approved cloud trial (not deployed by this PR)
1. Confirm **Workers Free** and **new Deno Deploy Free** plans have zero-cost stop behavior; do not create paid subscriptions or enable automatic overage. The old Deno Deploy product is being sunset; use the current new platform, not a legacy app.
2. Deploy `executor.mjs` to a lab-only Deno app and set a fresh random 32+-character `LAB_EXECUTOR_TOKEN` in platform secrets.
3. Deploy `wrangler.toml` from this directory to a **new lab-only** Cloudflare Worker. Configure `LAB_ADMIN_TOKEN` (different 32+-character secret), `EXECUTOR_TOKEN` (matching Deno's lab token), and `EXECUTOR_URL` (HTTPS endpoint) as secrets.
4. With a trusted operator client, authenticated POST `/schedule` with `{"delay_seconds":10}`. Check `GET /status` later with the admin token. Never insert a token in source, URL, ChatGPT, shell command history, GitHub Actions or a screenshot.
5. Accept only actual `status=completed`, `wakes=2`, three ordered events, no paid usage, and distinct platform receipts. Revoke tokens and remove test services when evidence is collected.

**Limits:** shared header tokens are sufficient for harmless lab arithmetic, not a production broker. Remote execution is at-least-once; task retries are safe only because it is pure computation. Operator-only deployment rights must remain separate from any future self-modifying agent. Free quotas can change; exhausting a quota means sleep or block, never paid fallback.

## First provider roles, not winners
- **Cloudflare Workers + Durable Objects:** free scheduler, alarm, small durable memory.
- **Deno Deploy Free:** first remote compute candidate (published 10 active CPU hours and 150 GiB-hours memory/month as of 2026-11-16).
- **GitHub Actions:** test/CI executor, not assumed production general-purpose compute.
- **Modal Starter / Google Cloud Run Jobs:** later alternatives only after hard no-charge protections are established.
- **Cloudflare Pi harness / Memory engines:** next evaluation after the simple wake/offload contract is proven. This lab deliberately does not simulate semantic memory or a personality.

Sources (checked 2026-11-16):
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/durable-objects/platform/pricing/
- https://developers.cloudflare.com/durable-objects/api/alarms/
- https://deno.com/deploy/pricing
- https://developers.cloudflare.com/agents/runtime/
