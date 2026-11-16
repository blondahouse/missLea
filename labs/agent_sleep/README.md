# Agent + Memory + Sleep Lab — free hybrid prototype

**Status:** deploy-ready synthetic implementation; actual cross-cloud alarms/compute **NOT YET TESTED**.
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
- `deno.json`: documented Deno Deploy dynamic entrypoint when application directory is `labs/agent_sleep`.
- `GET /control` on Cloudflare: small mobile-friendly **lab-only** control panel; enters token only in memory, sends it in an HTTPS authorization header and clears the field. `GET /health` on both services gives only synthetic readiness/cycle status.

**Local/offline check** (on GitHub Actions, not the owner's PC): `node --test labs/agent_sleep/tests.mjs`.

## Live cloud trial — minimal dashboard setup (not yet performed)

The source repository is public, but all runtime secrets remain within each provider's **Secret** settings. Do not use the existing `late-glade-5dde` Worker or any live TinyFund accounts. User login/consent may be needed for linking GitHub to providers.

**1. Deno Deploy Free** (https://console.deno.com): Create a separate Free organization/app if necessary, select GitHub repository `blondahouse/missLea`, set **App directory** to `labs/agent_sleep`, use the supplied `deno.json` (Dynamic / `executor.mjs`). Do not add a payment method or paid plan. In app Environment Variables add secret `LAB_EXECUTOR_TOKEN` (at least 32 random characters) for Production. Deploy and note the actual HTTPS app URL. Verify `GET /health` returns `{"role":"synthetic_executor","status":"ready"}`.

**2. Cloudflare Workers Free** (https://dash.cloudflare.com): Create a NEW Worker connected to the same GitHub repository, Worker name `misslea-anonymous-sleep-lab`, **Root directory** `labs/agent_sleep`, deploy via `npx wrangler deploy` using `wrangler.toml` and its SQLite Durable Object migration. Keep preview builds disabled. Cloudflare's native Git integration can manage a deployment token internally, avoiding owner-supplied API credentials. In Worker Settings → Variables and Secrets configure:
- `LAB_ADMIN_TOKEN` — a different random 32+-character **Secret**;
- `EXECUTOR_TOKEN` — the exact same random value as Deno `LAB_EXECUTOR_TOKEN`, **Secret**;
- `EXECUTOR_URL` — actual Deno HTTPS endpoint URL, **plaintext variable** (not a credential).

**3. Real two-wake run, no GitHub runner**: Open `https://<YOUR-NEW-WORKER>.workers.dev/control` in a browser; enter the lab-only admin token, click **Запустить два пробуждения**, then refresh **Проверить состояние**. The HTML does not persist the entered token or send it to other origins. After two actual alarms, unauthenticated `GET /health` on Cloudflare must report `{"role":"wake_dispatcher","status":"completed","wakes":2,"completed":true}`. Authorized `GET /status` (via trusted HTTP client) gives full synthetic events. The Cloudflare alarm, state writes and Deno calls execute in the two providers alone; GitHub supplies deployment source but **does not perform scheduling or execution**.

**4. Evidence and exit**: Observe Deno request logs (two authenticated POSTs) and Cloudflare Durable Object alarms/state. Record sanitized receipt, actual Free-plan usage and any quota failures. Delete/revoke the two lab tokens or remove the lab services afterward. No claims of actual cloud PASS until these observations exist.

**Not done by repository changes:** signing into provider accounts, connecting GitHub applications, setting runtime secrets and clicking Deploy. These are interactive provider-side operations.

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
