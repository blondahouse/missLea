# Cloudflare-only Agent + Memory + Sleep Lab

**Status: LIVE VERIFIED (2026-11-17) for bounded synthetic test.** Trusted operator deployed to `misslea-cloudflare-only-lab`. Actual receipt: `status=completed, wakes=2, modelCalls=2, events=3, blockedReason=null` after two native scheduled wakes, two Workers AI calls and retained tool output (38). [Verified private operator run](https://github.com/blondahouse/misslea-operator/actions/runs/43979791125) and [public synthetic status endpoint](https://misslea-cloudflare-only-lab.misslea931.workers.dev/status). Cloudflare Free usage/billing metrics have **not** been independently inspected; there is no claim of measured ongoing zero cost.
Independent of running TinyFund. No user data, personal conversations, model API keys, paid providers, autonomous purchases, or external side effects.

## Goal and scope

Test whether **Workers Free + Agents SDK + SQLite-backed Durable Object + Workers AI** is minimally sufficient to host a sleeping, self-waking agent with a model-selected allowed tool, durable original synthetic experience and a later model call that references that experience. This trial intentionally **does not choose against** other storage/compute labs; they remain validated fallbacks and independent recovery options.

Acceptance for the *real* experiment, not offline CI:
1. A fresh isolated Worker deploys under Workers Free without a billing upgrade; Worker AI free tier remains in effect (10,000 Neurons/day).
2. Operator starts one synthetic run from browser with lab-only token. Agent SDK schedules first wake; no GitHub Actions runner or local computer drives it.
3. Wake 1 calls real Workers AI `@cf/google/gemma-4-26b-a4b-it`, chooses the allowed `SQUARES` tool, and saves `38` in persisted agent state.
4. Wake 2 autonomously restarts via Agents SDK schedule, reads the stored earlier result, calls the model again and completes. Public receipt shows `status=completed,wakes=2,modelCalls=2`, with two events in addition to seed.
5. Workers and Durable Objects CPU, execution, and Workers AI Neuron usage are observed in Cloudflare dashboard. No paid fallback is configured; quota errors end as `blocked`.
6. If the model or SDK does not meet the Free CPU limit, record the concrete blocker rather than paying or hiding it. **STOP** after a completed cycle or a demonstrated blocking incompatibility.

## Design

The single `AnonymousFreeAgent` Agent SDK Durable Object instance stores event history in its SQLite-backed persistent state and owns scheduled callbacks. The Worker routes only fixed `/start`, `/status` and `/health` endpoints to the agent via internal RPC; it does not expose generic Agent RPC or untrusted model-provided URLs. A model chooses one of two plain-text actions from a fixed allowlist, with strict parsing. There are **only two model calls** in a successful cycle. The calculator is a deterministic pure function; the agent never gets real secrets or privileges. An unrecognized decision blocks without side effects. State resets only after explicit authenticated restart.

No KV database, separate VM, external router, Infisical, or memory SaaS is required for this *first synthetic experiment*. The adopted [Unified Living Memory concept](../../docs/memory-concept.md) and its [Cloudflare-first plan](../../docs/memory-cloudflare-roadmap.md) target a separate, replaceable personal-memory interface; this lab's Durable Object state is operational/session state, not a completed memory engine. Cloudflare KV may be useful later for immutable shared content, but **Durable Objects** are preferable for consistent agent state.

The login token `LAB_ADMIN_TOKEN` is stored as a Worker Secret, never in GitHub. `/status` is public only because this lab uses fabricated data; production agents must authenticate it. Public `/` shows a tiny mobile-friendly start/status page. The token is used once and cleared from the field.

## Cloudflare deployment options

**Verified path:** the separate private trusted operator `blondahouse/misslea-operator` deploys a pinned public lab commit with an Operations-only token from Infisical OIDC. An ephemeral random lab-only secret is installed and used to initiate the bounded trial; its value is **not** persisted. The alternative [public-repository deployment workflow](AUTONOMY.md) remains reference material and is not the live deployment path. The Cloudflare Git integration instructions below are another manual alternative.

## Deploy via Cloudflare's GitHub integration (manual provider access)

1. In the separate Miss Lea Cloudflare account, check Workers plan is **Free**; do not upgrade or add a payment method. Create a **new** Worker `misslea-cloudflare-only-lab`; keep the existing `late-glade-5dde` Worker unchanged.
2. Connect the existing repository `blondahouse/missLea` and set its **Root directory** to `labs/cloudflare_agent`. Build with `npm install`; deploy command `npm run deploy` (or `npx wrangler deploy`). The committed `wrangler.toml` provisions the SQLite-backed Durable Object and Workers AI binding. If the platform's Git integration prompts to authorize deployments, approve only the new Worker.
3. In this new Worker's Settings → Variables and Secrets, add **Secret** `LAB_ADMIN_TOKEN` containing a fresh random 32+ character value. Do not paste its value into ChatGPT, GitHub, screenshots or URLs. **The same token must not be reused from another lab or a personal project.**
4. Open the new `workers.dev` address on a phone. `/health` should return `{"lab":"cloudflare-only-free-agent","ready":true}`. At `/`, enter the secret and press **Start**. After scheduled execution, select **Check status**.
5. A genuine PASS requires a persisted public `/status` receipt with `completed, wakes=2, modelCalls=2`; check actual Free-plan usage in Workers / Durable Objects / Workers AI dashboards. Record only a sanitized receipt. The page itself cannot fake completed status: state comes from the Agent Durable Object.

**This public repo's offline CI does not deploy or call models.** The separate private trusted operator performed the proven real deployment and model calls. Local CI success alone is still not provider evidence. The optional external compute lab remains preserved at `labs/agent_sleep`.

## Known limits

- Workers Free CPU limit: 10 ms per request. Waiting for inference is excluded from CPU accounting, but running the Agents SDK and maintaining state is not. Agents SDK may prove too expensive for Workers Free; do not assume feasibility until a real measured run.
- Workers AI has a daily Free Neuron allowance, not unlimited inference. The chosen Gemma 4 model is current as of 2026-11-16; earlier Llama 3.2 and Llama 3.1 FP8 models are scheduled for retirement on Nov 20, 2026. No external/paid keys are present.
- This experiment tests short semantic continuity, not general agent intelligence, memory compression, autonomous self-development, credential stewardship, off-provider recovery, or handling arbitrary user prompts.
- Provider independence is a future deployment goal. Preserve simple portable synthetic event records and keep the other labs; do not copy real Miss Lea memories until independent recovery is ready.

Official references checked 2026-11-16:
- https://developers.cloudflare.com/agents/agent-class/
- https://developers.cloudflare.com/agents/agent-class/internals/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/durable-objects/platform/pricing/
- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://developers.cloudflare.com/changelog/product/workers-ai/


## Autonomous Agent Core adapter (separate Cloudflare Worker)

The portable Agent Core now has an isolated adapter in the Cloudflare lab
source, with its own Wrangler configuration and a distinct Worker name,
Durable Object class and instance. The previously verified AnonymousFreeAgent
and its two-wake Worker remain unchanged.

A trusted operator deployment targets only misslea-agent-core-lab, loads
an Operations-only Workers token, and installs a new per-run synthetic secret.
GET /health and GET /status expose safe counters and limited evidence only;
POST /start requires a temporary lab token.

Core notes are not Living Memory. No personal conversations, Telegram,
third-party actions, Root credentials, or paid models are connected.

Offline checks (no model credits):

    npm install --ignore-scripts
    npm run check:core
    npm run build:core

A dry-run build is not evidence of live operation. Live verification must
observe at least two separately scheduled wakes with durable state and no
blocked result. An agent-selected pause is valid but does not prove two-wake
continuity.

Live acceptance on 17 November 2026 confirmed two scheduled wakes, two model
calls and two fabricated tool uses. No durable subjective intent was selected.
See [Agent Core live evidence](AGENT_CORE_LIVE_2026-11-17.md). Actual
Cloudflare Free-tier billing/usage metrics were not independently captured.
