# Agent Core — portable synthetic lifecycle and integrated Cloudflare runtime

**Current status (2026-11-18):** The portable Core is deployed in two distinct kinds of **synthetic** Cloudflare lab: a previously verified standalone Core Worker and the newer memory-integrated `misslea-core-memory-lab`. These are not the former TinyFund agent, a migrated personal identity, or a production-ready independent Miss Lea.

## What actually runs

The current integrated Worker uses `src/memory_cycle.mjs` and the state machine in `src/core.mjs`; `labs/cloudflare_agent/src/core_memory.mjs` binds those portable components to:

- **Cloudflare Agents SDK / SQLite-backed Durable Object:** one active synthetic instance; native scheduled callbacks/physical alarms; operational state, bounded notes and intent, usage counters and only the most recent D1 memory ID.
- **Cloudflare Workers AI:** one fixed Gemma 4 model (not yet connected to a multi-model router).
- **Our Memory Manager:** `labs/living_memory/src/manager.mjs`, which exposes the restricted model-facing remember/recall/revise/reinterpret operations.
- **Cloudflare D1 + FTS5:** `labs/living_memory/src/d1.mjs` and its migration store the actual subjective synthetic records. Memory text is not duplicated into Durable Object state.
- **Private trusted Operator:** independently deploys pinned public source via GitHub Actions with credentials obtained from Infisical. It does **not** drive scheduled wakes. Root credentials remain in the separate provisioning job and are never passed to the Worker.

The model may choose or change provisional intent, select one allowed synthetic/environment or memory action per wake, and choose the next sleep (60–86,400 seconds) or pause. There are no real external actions, Telegram, paid provider keys, private conversations, agent-admin credentials or owner funds. Synthetic safety limits remain **12 total wakes, 4 per UTC day**. These limits are lab scaffolding, not the intended long-term autonomy policy.

The Core records an inference attempt before dispatch, rejects mismatched/stale callbacks and does not automatically replay uncertain side effects. Invalid model JSON or an invalid decision fails closed as `blocked`; autonomous repair/reconciliation is not implemented. The currently retained operational notes and provisional intent are distinct from authoritative subjective Living Memory, but their eventual conceptual boundary still needs refinement.

## Live evidence, kept separate

- **Standalone Core (historical PASS):** 2 scheduled wakes, 2 Workers AI calls and 2 synthetic tools, no lasting intent. [Standalone live evidence](../cloudflare_agent/AGENT_CORE_LIVE_2026-11-17.md).
- **Standalone D1 (historical PASS):** memory create/revise/reinterpret and FTS5 across three requests. [D1 live evidence](../living_memory/D1_LIVE_STATUS_2026-11-17.md).
- **Integrated Core + Living Memory (current live state):** the 2026-11-17 22:03:52 UTC **read-only** status returned `wakes=4, modelCalls=4, toolCalls=3, memoryWrites=2, memoryReads=4, memoryContexts=3, callbackAttempts=4, callbackRejected=0`. Status is **`blocked` / `invalid_decision`**, no pending schedule or alarm. This verifies repeated autonomous wakes, model-chosen writes and later D1-fed model context, not indefinite operation or complete model understanding. [Operator status evidence (run 44148862213, attempt 2)](https://github.com/blondahouse/misslea-operator/actions/runs/44148862213). [Integration details](../cloudflare_agent/CORE_MEMORY_INTEGRATION.md).

The earlier integrated acceptance [workflow 44147427562](https://github.com/blondahouse/misslea-operator/actions/runs/44147427562) failed with `integrated_live_continuity_timeout` because the model scheduled the next wake beyond the workflow's observation window. That failure **did not** stop the Cloudflare alarm; later read-only evidence verified subsequent wakes. A later malformed decision **did** block the live synthetic run.

## Not yet implemented or independently measured

Router with two independent free model providers, Telegram, privileged Tools/Operator delegation, recovery from blocked decisions, robust monitoring, personal-memory migration, full Living Memory decay/eviction/associations, independent cross-provider recovery, and actual Cloudflare Free-plan resource/billing headroom remain open.

Offline tests without model/provider credentials:

```bash
node --test labs/agent_core/test/*.test.mjs
cd labs/cloudflare_agent && npm install --ignore-scripts && npm run check:integrated && npm run build:integrated
```

These tests validate source/build behavior, **not** real Cloudflare acceptance.
