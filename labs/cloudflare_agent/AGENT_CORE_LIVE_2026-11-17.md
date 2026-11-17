# Synthetic Agent Core — first Cloudflare live verification (17 November 2026)

**Result: LIVE PASS for bounded autonomous scheduled continuity.**

The trusted operator deployed a new isolated Cloudflare Worker and verified a real
two-wake autonomous loop without modifying the earlier two-wake demonstration.

- Worker: misslea-agent-core-lab
- Public synthetic status: https://misslea-agent-core-lab.misslea931.workers.dev/status
- Public reviewed source: blondahouse/missLea@43b52db34a485ed7967d973aebb7a9016c0915a4
- Private operator run: https://github.com/blondahouse/misslea-operator/actions/runs/44111379745
- Start confirmed: 2026-11-17 15:12:04 UTC
- Verified receipt: 2026-11-17 15:14:13 UTC
- Runtime: Cloudflare Workers + Agents SDK + SQLite-backed Durable Object + Workers AI
- Model: @cf/google/gemma-4-26b-a4b-it
- Separate Durable Object class: SyntheticCoreAgent

Sanitized operator receipt:

    {"status":"scheduled","wakes":2,"modelCalls":2,"toolCalls":2,"intentAssigned":false,"lastTool":"dataset.summarize","reason":null}

## What this demonstrates

The private operator fetched only Operations-scoped Cloudflare Worker credentials
through Infisical OIDC, tested the pinned public source, deployed the dedicated
Worker, installed an ephemeral start secret and initiated a single experiment.
Cloudflare scheduled subsequent wake callbacks; GitHub Actions only polled a
public synthetic status endpoint. Two model calls and two allowlisted fabricated
tool calls occurred, with persisted counters across callbacks.

The independent Agent Core can now run on Cloudflare while retaining its
replaceable inference/store/scheduler boundaries, bounded working notes,
strict JSON decision contract, replay fencing, and automatic wake limits.
The experiment allows model-selected intentions, tools and next wake times.
The observed model did **not** adopt a persistent intention; no claim is made
that it has demonstrated sustained self-defined goals.

## Boundaries and gaps

- The experiment is limited to 12 total model wake attempts, maximum 4 per UTC
  day. This is not indefinite autonomous service.
- The working note buffer in the Durable Object is operational state, not
  the adopted Unified Living Memory. D1/Memory Manager are not integrated.
- There is no Telegram, two-provider free LLM router, real external tools,
  privileged Operator delegation, personal conversation import or Live trading.
- Agent Core has no independently demonstrated backup/restore, cross-provider
  failover, quota headroom, or full operational monitoring.
- Workers AI used the native free-model path with no paid API fallback. Real
  Cloudflare CPU/Neuron usage and billing were **not independently inspected**;
  execution success is not proof of zero actual charges.
- The previous misslea-cloudflare-only-lab Worker was not changed. These two
  synthetic identities have no shared operational permissions or memories.

**Next planned implementation:** basic Unified Living Memory on Cloudflare D1
behind a replaceable Memory Manager interface. Telegram and a minimum two-free-
model LLM router are separate MVP milestones.
