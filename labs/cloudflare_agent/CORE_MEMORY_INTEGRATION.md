# Synthetic Agent Core + Unified Living Memory (D1) integration

**Status (2026-11-18): deployed and memory continuity live-verified; the four-wake `invalid_decision` stop has been safely re-armed in the same run. The next native wake is scheduled for 2026-11-18 00:01 UTC; it is not yet verified.** This is a **bounded synthetic lab**, not a production/personal Miss Lea.

## Deployed components

- **Worker:** `misslea-core-memory-lab` (separate from `misslea-agent-core-lab`, `misslea-cloudflare-only-lab` and the standalone D1 smoke Worker).
- **Core:** portable state machine and `memory_cycle.mjs` orchestration, hosted by `CoreMemoryAgent`, a Cloudflare Agents SDK Durable Object. SDK scheduling creates actual Durable Object alarms; no GitHub runner drives subsequent wakes.
- **Operational state in Durable Object:** wake/run status, temporary intent and bounded notes/events, inference counters, next wake, and *only the last D1 memory ID*. The DO is not the authoritative autobiographical store.
- **Subjective synthetic Living Memory:** the in-process Memory Manager (`labs/living_memory/src/manager.mjs`) accesses a dedicated Cloudflare D1 database through `src/d1.mjs`, using indexed SQL and FTS5. Memory record text is not copied into DO state.
- **Inference:** one fixed Cloudflare Workers AI model, `@cf/google/gemma-4-26b-a4b-it`. Multi-provider routing has not been attached.
- **Privileged deployment:** the separate private `blondahouse/misslea-operator` repository validates and deploys pinned code. Cloudflare Root credentials are used **only** in its separate D1 provisioning job; Operations credentials deploy the Worker. No such credentials enter Worker/model context. The start endpoint uses a newly installed temporary lab-only token.

Only fabricated model-selected tools are allowed: `environment.inspect`, `dataset.summarize`, `memory.remember`, `memory.recall`, `memory.revise`, `memory.reinterpret`. At most one tool per wake. A memory is written only when the model selects a write action. On a later wake, the last memory ID is read through Memory Manager/D1 and its content may be supplied as **untrusted context**; doing so is evidence of context delivery, not proof of model comprehension.

## Current verified result

The [integrated launch workflow #44147427562](https://github.com/blondahouse/misslea-operator/actions/runs/44147427562) successfully provisioned/verified D1 and deployed the Worker, then failed with `integrated_live_continuity_timeout`. The model's next alarm at 2026-11-17 19:26:24 UTC was later than the workflow's observation window. The timeout was a **verification-window mismatch**, not proof the native alarm failed.

A subsequent **read-only** [Operator status workflow #44148862213, attempt 2](https://github.com/blondahouse/misslea-operator/actions/runs/44148862213) at **2026-11-17 22:03:52 UTC** returned:

```json
{
  "status": "blocked",
  "reason": "invalid_decision",
  "wakes": 4,
  "modelCalls": 4,
  "toolCalls": 3,
  "memoryWrites": 2,
  "memoryReads": 4,
  "memoryContexts": 3,
  "hasMemoryPointer": true,
  "callbackAttempts": 4,
  "callbackRejected": 0,
  "callbackRejectCode": null,
  "callbackFailurePhase": null,
  "nextWakeAt": null,
  "scheduledJobCount": 0,
  "physicalAlarmAt": null
}
```

**What passed:** real native wake scheduling, independent subsequent inference, model-selected memory writes, D1-backed retrieval/context assembly across wakes, and callback rejection checks. **What did not pass at that time:** ongoing autonomous operation after a malformed model decision. That snapshot is historical; a later explicitly authorized resume created a new pending wake.

The final `invalid_decision` is a strict model-output validation rejection; this sanitized receipt alone does **not** identify the exact malformed field or prove a provider error. Do not reveal raw model output or memory content to diagnose it.

## Pending resilience fix (source only; live deployment not yet verified)

A model response can be syntactically invalid even though Workers AI inference itself succeeded. The updated Core adapter accepts only a complete JSON object, optionally surrounded by a single complete `json` Markdown code fence; it still rejects unknown tools, extra/missing fields, invalid sleep bounds and any non-empty memory content without an associated memory action.

If validation rejects the first **returned** model decision, the Core may request **one** new complete decision in that wake, **before** performing any memory write or synthetic tool action. The additional inference attempt is durably counted before dispatch; at most **two such repairs per synthetic run** are allowed. There are no retries of transport/model exceptions, uncertain inference outcomes, D1 writes or any side effect. Repeated malformed decisions still `block` the run.

Read-only status can expose a bounded `decisionRepairs` count and an allowlisted `lastDecisionValidationCode`, never the raw reply, memory text or internal identifiers. The four-wake experiment was blocked at the historical snapshot; deploying the parser fix did not reset it. A subsequent separately authorized same-run resume has now been observed (below). This is a reliability improvement for future wakes, not a retrospective explanation of the precise fourth-response defect.

## Safe same-run resumption (synthetic-only)

The integrated Worker exposes `POST /resume` behind the same private lab-only `LAB_ADMIN_TOKEN` as `/start`. A trusted Operator sends `{"expectedRunId":"<current run ID>","expectedWakes":<current wake count>}` after reading the public synthetic `/status`. The precondition rejects a state change between inspection and action; the endpoint is **not** public or callable by the model.

Resumption is allowed **only** from `blocked / invalid_decision` with no pending SDK job or Durable Object alarm, a complete sequence of committed prior wake events, a recorded model attempt and available synthetic wake budget. The malformed decision happened before tool dispatch, so its output is discarded rather than replayed. It schedules a **new, separately counted wake of the same run**, preserving D1 record IDs, operational notes, intents, revisions, and all prior counters. The new wake is no earlier than 60 seconds after authorization; if the daily wake limit is exhausted, it waits for the next UTC day. The model remains free to choose subsequent sleep periods.

At most two explicit resumes are permitted during one synthetic run. Unauthorized, duplicate, stale or unsafe requests fail closed; a scheduling error cannot be repeatedly retried. `/start` cannot replace an already-used run or erase its D1 pointer. Public synthetic status exposes only bounded `resumeCount` and `lastResumeAt`, not model text, memory data or credentials. `tool_failed`, `schedule_failed`, `model_or_quota_failed`, uncertain in-flight operations and agent-chosen pauses are **not** eligible for this recovery.

This is a deliberately narrow survival mechanism, **not** general autonomous recovery, rollback of personality or an authorization for unbounded model calls. A separately authorized same-run resume has now completed (below). Source/build tests cannot prove a later autonomous model wake; observe actual Cloudflare status after the scheduled alarm.

## Real resume evidence (2026-11-17 23:04:14 UTC)

The trusted private Operator [run #44195835158](https://github.com/blondahouse/misslea-operator/actions/runs/44195835158) deployed the reviewed safe-resume code and performed exactly **one** authenticated continuation of the original four-wake blocked experiment, without calling `/start` or accessing D1 records. Public status was checked before and after.

Sanitized receipt: `status=scheduled, wakes=4, modelCalls=4, memoryWrites=2, memoryContexts=3, resumeCount=1, nextWakeAt=2026-11-18T00:01:00Z, alarmPresent=true`. The Worker verified both an SDK schedule and a physical Durable Object alarm. Previous counters, D1 memory pointer and run identity were retained. The wake is deferred to the next UTC day because the synthetic four-wakes-per-day cap was already reached. **This proves a successful resume and physical scheduling, not that a fifth model call has occurred.**

## Operational/architecture caveats

- Bounded synthetic-only limits: 12 total wakes, 4 per UTC day; sleep delay 60–86,400 seconds.
- Failed/uncertain model or memory operations are never automatically replayed to avoid duplicate side effects. Only the explicitly verified `invalid_decision` case has bounded, authorized same-run resume. No general automatic recovery from uncertain effects is implemented.
- No Telegram, personal conversations, paid provider keys, real external tools, owner funds, root/admin agent rights, independently measured CPU/Neuron/D1 billing/quota headroom or cross-provider backup.
- No deployed decay, associations, pressure-driven eviction, personality migration or document vault. D1 is the first native store behind a replaceable Memory Manager, not the whole Living Memory design.
- Earlier standalone Cloudflare / Core / D1 lab evidence is retained separately. Historical off-Cloudflare research remains experimental and is not in the integrated runtime.

Offline checks (not live acceptance):

```bash
cd labs/cloudflare_agent
npm install --ignore-scripts
npm run check:integrated
npm run build:integrated
```
