# Agent Core — synthetic research implementation

**Status: live-verified on Cloudflare as a separate synthetic Agent Core Worker (2026-11-17).** Its existing two-wake predecessor remains separate and unchanged. The Core uses a real Workers AI free-tier model, but has no Telegram, personal memories, privileged external tools or paid model API keys. No real credentials, paid APIs, funds, or provider-side actions are available.

Agent Core provides a replaceable state machine and injected model, storage, and scheduler ports. Each scheduled wake allows the model to choose or change a provisional intention, optionally call one of two pure fabricated tools, record a short working note, and select the next wake or pause. No mandatory topic, objective, personality, or scripted two-step task is assigned.

The current test harness has a strict JSON decision contract, explicit tool allowlist, bounded working context, a limit of 4 wakes per UTC day and 12 total wakes, stale-run rejection, and a non-replay rule: persist a model-call attempt before inference. Uncertain interrupted calls remain in running state for future reconciliation. Safe receipts omit notes and intents.

**This is not Living Memory.** The short operational note buffer is not a subjective or autobiographical store; later memory integration must use the adopted Memory Manager contract, with D1 as the first candidate. No recovery, monitoring service, model router, privileged Operator delegation, or Telegram is implemented here. The separate Cloudflare SDK adapter does not provide Living Memory.

Run the offline tests (no credits required):

    node --test labs/agent_core/test/*.test.mjs

**Live evidence:** two scheduled Cloudflare wakes, two real model calls and two fabricated tool calls with durable operational state. Intent remained unset in the observed receipt; long-term goal selection is not yet validated. See the [live run record](../cloudflare_agent/AGENT_CORE_LIVE_2026-11-17.md). Next milestones are the separate Living Memory Manager (D1), Telegram and a free-model router. Independent Recovery and detailed Monitoring remain future work.


## Synthetic D1 integration

The separate portable orchestration layer at `src/memory_cycle.mjs` adds
model-selected memory actions and later D1-backed recall without changing the
previous verified standalone Core Worker. See the [integration record](../cloudflare_agent/CORE_MEMORY_INTEGRATION.md).
