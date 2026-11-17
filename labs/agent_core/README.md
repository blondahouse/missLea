# Agent Core — synthetic research implementation

**Status: offline-tested with a separate Cloudflare Agents SDK adapter; live validation pending.** This lab is not connected to the running Cloudflare two-wake experiment, to Telegram, to real models, or to personal memories. No real credentials, paid APIs, funds, or provider-side actions are available.

Agent Core provides a replaceable state machine and injected model, storage, and scheduler ports. Each scheduled wake allows the model to choose or change a provisional intention, optionally call one of two pure fabricated tools, record a short working note, and select the next wake or pause. No mandatory topic, objective, personality, or scripted two-step task is assigned.

The current test harness has a strict JSON decision contract, explicit tool allowlist, bounded working context, a limit of 4 wakes per UTC day and 12 total wakes, stale-run rejection, and a non-replay rule: persist a model-call attempt before inference. Uncertain interrupted calls remain in running state for future reconciliation. Safe receipts omit notes and intents.

**This is not Living Memory.** The short operational note buffer is not a subjective or autobiographical store; later memory integration must use the adopted Memory Manager contract, with D1 as the first candidate. No recovery, monitoring service, model router, privileged Operator delegation, or Telegram is implemented here. The separate Cloudflare SDK adapter does not provide Living Memory.

Run the offline tests (no credits required):

    node --test labs/agent_core/test/*.test.mjs

**Next integration milestone:** connect the core to an isolated Cloudflare Agents SDK instance using synthetic state and a real free model call, without changing the existing verified two-wake lab. Prove that decisions, tool observations, and scheduled wake times survive a fresh runtime instance.
