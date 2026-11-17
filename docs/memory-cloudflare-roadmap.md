# Memory implementation roadmap — Cloudflare first, replaceable internals

**Status:** Proposed incremental delivery plan implementing the [adopted Unified Living Memory concept](memory-concept.md). The steps are design milestones, **not approved deployments, account creation, paid services or live-data migration**.

## Starting evidence

- [Cloudflare Agent Lab](../labs/cloudflare_agent/README.md) **verified** two native wakes, two Workers AI calls and persisted synthetic state on 17 Nov 2026. That proves a bounded lifecycle, **not** production memory quality, free-tier headroom or general agent reliability.
- [Memory Lab](../labs/memory/README.md) currently has a **synthetic SQLite lexical-retrieval baseline only**. No memory framework has won a fair comparison.
- The existing stateful agent uses a SQLite-backed Durable Object. Keep its wake coordination/operational state separate from the agent's **subjective** memory. This avoids accidental restoration of authorizations or pending operations through the memory interface.

## Non-negotiable interfaces from day one

Keep one small Memory Manager boundary between agent actions and storage. Stable conceptual operations: `remember`, `recall(exposure, situation, budget)`, `revise`, `reinterpret`, `inspect_external_evidence`. No direct D1-specific SQL in agent prompts or decision logic.

Records should support stable IDs, kind, mutable content, strength, confidence, significance, stability/decay settings, timestamps, version/revision and optional links. Keep records exportable in documented JSON/JSONL with explicit schema version. Keep credentials, signed documents and external obligations **out** of this payload. Preserve explicit mutation ordering; a later replicated store must not resurrect evicted records.

This is a **logical contract**: do not prematurely build microservices, dual-write coordination or unused indexes.

## Phase 0 — evidence and baseline (no production migration)

**Use:** Existing Memory Lab SQLite and fabricated histories.

Evaluate what the current retrieval baseline can and cannot do; specify comparable workloads, recall quality, error modes, context-token consumption and per-operation inference cost **before** choosing a new engine. Compare one maintained ready-made option only where its advantage could change a decision (e.g., Mem0 for fact extraction, Hindsight for reflection); Letta may be compared as a larger runtime alternative. Do not preselect a winner or force a framework.

**Ready when:** the baseline and missing capabilities are explicit, with bounded costs and reproducible synthetic tests. No personal memory enters the public lab.

**Implementation update (17 Nov 2026):** initial standalone Memory Manager, parameterized D1 adapter and FTS5 schema exist at labs/living_memory. Live D1 provisioning and Agent Core binding are not yet verified; Phase 1 acceptance remains open.

## Phase 1 — minimal native Living Memory

**Use:** Current Cloudflare Worker/Agents SDK + Durable Object for wake and operational coordination; **Cloudflare D1** as a simple, separate authoritative Living Memory database. Start with ordinary indexed SQL queries and D1's built-in SQLite **FTS5** for lexical search; no vector database, graph server, external memory SaaS or VM. D1 is an implementation candidate within the Cloudflare-only environment, not an instruction to migrate the existing agent session state.

Provide create, read, revise, short recall, explicit token/context budget and a small current-context assembler. Miss Lea may edit content, redact fragments and adjust subjective weights but cannot issue a whole-record delete; no full autobiographical logging is required. Protect the endpoint with existing agent capability boundaries.

**Ready when:** a synthetic agent can wake, create and later retrieve/revise a record, and use it without reading unrelated memory; quota, failed writes and model-token cost are measured on the Free configuration. Maintain one authoritative writer and no second active identity.

## Phase 2 — economical memory behavior

**Use:** Existing D1 tables and Manager adapter.

Introduce lazy strength decay based on wall time and meaningful-event counters; sparse weighted links if experiments justify them; configurable exposure levels with measured retrieval/model cost. Minimal exposure must bypass link traversal. Deep modes may traverse context-filtered edges and progressively expand records.

Exercise eviction under **test-only artificial pressure**. Enable eviction in live operation only on verified **real** resource pressure, not on arbitrary age or a hidden personal-size cap. Avoid LLM sweeps solely to refresh weights or reclaim space.

**Ready when:** controlled tests establish that more processing yields useful improvements, that cheap everyday recall stays bounded, and that decay does not depend on request counts. Record negative findings; a failed feature can be left out without changing the interface.

## Phase 3 — tools for external testimony

**Use:** Cloudflare-native object storage such as R2 if needed, with distinct data policy.

Add an independent Document / Contract Vault API for signed obligations and chosen artifacts, including a minimal active-obligation index. Keep documents separate from editable/evictable Living Memory. For Time Travel, expose read-only historical inspection **only after** a safe non-destructive historical read path exists. The D1 Time Travel restore operation **overwrites** its target database; it must never point at the active Living Memory. If safe inspection is unavailable, leave the feature explicitly unavailable rather than faking it.

**Ready when:** documents cannot be silently rewritten by autobiographical operations, and historical inspection creates new present-day interpretations without replacing the present state.

## Phase 4 — resilience and portability

**Use:** Current Cloudflare state initially; add a second independent provider only when the project explicitly widens beyond the **Cloudflare-only launch**.

Maintain one authoritative logical memory with stable IDs, versions, ordered mutations and deletion/redaction markers (including a policy for replica convergence). Separately evaluate mirroring the latest state against the additional complexity, quotas and failure domains. No routine personality snapshots or historical rollback mechanism is required.

**Ready when:** one store can fail without reviving deleted or revoked content, and a recovered runtime continues from surviving state without cloning active permissions. Cross-provider replication is **not claimed** while both stores share one Cloudflare account.

## Deliberately postponed unless evidence warrants

- Managed vector indexes or embeddings (D1 FTS5 may be enough initially).
- Dedicated graph engines and automatic LLM link creation for every memory.
- A mandatory full-memory reflection schedule or autonomous cleanup sweep.
- Extra VMs, third-party memory engines or new recurring subscriptions.
- Multiple concurrent active personal identities and personality rewind.

## Cost and provider constraints

Do not presume `Free` means unlimited. Current Cloudflare documents confirm: D1 supports FTS5; D1 Free has storage and daily row-read/write limits, with failures on exceeded daily quotas; Vectorize availability/pricing can differ by Workers plan; D1 Time Travel is a restore interface, **not a general read-only time query**. Verify actual current entitlement, quotas and usage before each live milestone. The memory policy should choose retrieval depth according to measured **interpretation cost** (search + input tokens + reasoning/inference), not simply by record count.

Official references (checked 17 Nov 2026):
- https://developers.cloudflare.com/d1/sql-api/sql-statements/
- https://developers.cloudflare.com/d1/platform/limits/
- https://developers.cloudflare.com/changelog/post/2026-09-01-d1-free-tier-limit-enforcement/
- https://developers.cloudflare.com/d1/reference/time-travel/
- https://developers.cloudflare.com/workers/platform/pricing/

**Adoption policy:** the [Unified Living Memory concept](memory-concept.md) is authoritative for subjective memory; this roadmap determines the smallest reversible engineering increments. It does not override external contracts, authority controls, safety obligations or the independent historical Storage Lab experiments.
