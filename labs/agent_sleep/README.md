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

## Preferred external executor: Supabase Edge Functions Free

**Why the change (2026-11-16):** Deno announced that **Deno Deploy shuts down in April 2027** (https://deno.com/blog/cloudflare). Keep the Deno profile as a disposable compatibility option, **not** a long-term operational dependency. The current recommended second cloud is **Supabase Edge Functions Free**: 500,000 invocations/month, up to 2 CPU seconds/request and 150 s wall time on Free. Free projects may pause after a week of insufficient activity. No guarantee of indefinite free availability.

- Use a **separate Miss Lea laboratory Supabase account/project** on the Free plan, not the founder's other Supabase projects. Never use personal project credentials or upgrade to paid.
- Deploy a function named `anonymous-sleep-executor` with files: `index.ts` from `supabase_index.ts` and `executor.mjs` from this directory. The index module just boots the same tested handler.
- Configure **secret** `LAB_EXECUTOR_TOKEN` with a fresh random 32+-character value in that project.
- Deploy with **Supabase JWT pre-verification disabled**, because the handler performs its own exact Bearer-token check; no other operations are exposed. The function is intentionally limited to anonymous synthetic arithmetic. Supabase project management credentials must not enter the Worker.
- Verify public `GET https://<PROJECT_REF>.supabase.co/functions/v1/anonymous-sleep-executor/health` returns `{"role":"synthetic_executor","status":"ready"}`. Set Cloudflare `EXECUTOR_URL` to that function's base HTTPS URL (without `/health`).
- Set the exact same `LAB_EXECUTOR_TOKEN` value as Cloudflare Worker secret `EXECUTOR_TOKEN`. Do not put it in GitHub, reports, this chat, or the URL.
- A connected Supabase deployment capability can install the function once the dedicated project/account is accessible; alternatively use the Supabase dashboard. The 2-wake runtime runs without GitHub or a user computer.

Sources:
- https://supabase.com/docs/guides/functions/limits
- https://supabase.com/docs/guides/functions/pricing
- https://supabase.com/docs/guides/platform/free-project-pausing
- https://supabase.com/docs/guides/functions/quickstart-dashboard

## Cloudflare setup + real two-wake test

This research is **not deployed** just because CI passes. Only anonymous synthetic records are used. Do not modify the existing `late-glade-5dde` Worker or real TinyFund resources. The two clouds are independent at runtime; GitHub is only a source-code host for Cloudflare's one-time deployment.

1. Under Cloudflare Workers Free, create a **new** Worker linked to GitHub repository `blondahouse/missLea`; name it `misslea-anonymous-sleep-lab` and set **Root directory** to `labs/agent_sleep`. Use `npx wrangler deploy`, the committed `wrangler.toml`, and SQLite-backed Durable Objects; disable preview builds. Cloudflare's integrated build system can create its own deployment token without storing it in this repo.
2. In Worker Settings → Variables and Secrets, add `LAB_ADMIN_TOKEN` as a random 32+-character **Secret** (distinct from all other tokens), `EXECUTOR_TOKEN` as a **Secret** (same value as the external compute provider's `LAB_EXECUTOR_TOKEN`), and `EXECUTOR_URL` as the chosen executor's HTTPS URL (ordinary variable, since URLs are not confidential).
3. Open `https://<NEW-WORKER>.workers.dev/control` in a phone browser. Enter only the lab-specific admin token, then select **Start two wakes**. The page sends it through a same-origin HTTPS Authorization header and clears the field; it does not save it locally, add it to URLs, or call any third-party script.
4. Select **Check status**. Only real Cloudflare alarms can produce `{"role":"wake_dispatcher","status":"completed","wakes":2,"completed":true}`. No GitHub runner participates in the actual wake/compute cycle. The authorized `/status` endpoint gives full synthetic events; public `/health` gives sanitized state.
5. Check external executor logs for two authenticated POSTs, Cloudflare alarms and usage dashboards for a zero-cost run. Publish a sanitized receipt as the final PASS evidence. Do not treat local CI as proof of real cloud execution.

## Optional disposable Deno alternative (sunsets April 2027)

The experimental `executor.mjs` can also run on the **new** Deno Deploy Free (https://console.deno.com) as a second provider, but is **not preferred** for the first persistent assembly because Deno Deploy is being shut down. If used temporarily: create a Free app linked to `blondahouse/missLea`, App directory `labs/agent_sleep`, with the committed `deno.json`; configure Production Secret `LAB_EXECUTOR_TOKEN`, and set Cloudflare `EXECUTOR_URL` to the deployed HTTPS URL. No paid features or card.

**Not done by repository changes:** provider login, new isolated account/project creation, connecting GitHub to Cloudflare, configuring secrets, actual live invocation, and cleanup. These require authorized access to the provider dashboards.

**Limits:** shared header tokens are sufficient for harmless lab arithmetic, not a production broker. Remote execution is at-least-once; task retries are safe only because it is pure computation. Operator-only deployment rights must remain separate from any future self-modifying agent. Free quotas can change; exhausting a quota means sleep or block, never paid fallback.

## First provider roles, not winners
- **Cloudflare Workers + Durable Objects:** free scheduler, alarm, small durable memory.
- **Supabase Edge Functions Free:** preferred remote executor; single constrained HTTPS function and no VM. Free project idle-pausing is a documented risk.
- **Deno Deploy Free:** disposable portability comparator only; provider announced April 2027 shutdown.
- **GitHub Actions:** test/CI executor, not assumed production general-purpose compute.
- **Modal Starter / Google Cloud Run Jobs:** later alternatives only after hard no-charge protections are established.
- **Cloudflare Pi harness / Memory engines:** next evaluation after the simple wake/offload contract is proven. This lab deliberately does not simulate semantic memory or a personality.

Sources (checked 2026-11-16):
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/durable-objects/platform/pricing/
- https://developers.cloudflare.com/durable-objects/api/alarms/
- https://deno.com/deploy/pricing
- https://developers.cloudflare.com/agents/runtime/
