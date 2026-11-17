# Synthetic Agent Core + Unified Living Memory (D1) integration

**Status: code and offline tests. Live provider acceptance is separate.**

A distinct Cloudflare Worker `misslea-core-memory-lab` runs a new Durable
Object class `CoreMemoryAgent` using the portable Agent Core wake machinery
and the existing Memory Manager / D1 store. The previous Agent Core, D1 smoke,
and original two-wake Cloudflare Workers remain unchanged.

## Intended runtime boundary

- Durable Object: scheduled wakes, inference-attempt counter, bounded operational
  notes, last D1 memory *ID* only, basic non-sensitive counters.
- D1: single authoritative record of subjective synthetic memories and changes.
  The DO does not retain copies of memory text or memory snapshots.
- Model: chooses a provisional intent, one action, whether/what to remember,
  read, revise or reinterpret, and its next wake delay or pause.
- At a later wake, the Memory Manager reads the last memory through D1 and
  passes it as **untrusted context** to the model within the bounded prompt.
  This is evidence of memory being supplied, not proof the model understood it.
- Memory Manager: D1-backed remember/read/recall/revise/reinterpret; no generic
  SQL, delete or export authority is exposed as a model tool.
- Operator: deployment and single authenticated lab start only; no Root token,
  personal content, paid API key or arbitrary external tool is passed to the
  autonomous Worker.
- Trial: at most 12 wakes and 4 UTC-day wakes, no paid fallback. The model may
  pause; that is not an error but may prevent a two-wake acceptance.

One write can succeed just before a crash, while DO state remains marked
`running`. Such uncertain operations are intentionally **not replayed**
automatically. Recovery and compensating reconciliation remain later work.

The model-action interface is minimal. For memory actions, the content is
self-authored by the model; for `memory.revise` and
`memory.reinterpret` the target is limited to the last recorded/recalled
memory ID (not arbitrary D1 data). A normal autonomous wake is never required
to write a memory.

The existing synthetic D1 database is reused for this isolated integration;
it contains **synthetic records only**. It is not a per-tenant memory service.
Before importing personal histories or opening external interactions, explicit
ownership/isolation controls will be required.

Offline tests:

    cd labs/cloudflare_agent
    npm install --ignore-scripts
    npm run check:integrated
    npm run build:integrated

**Live acceptance criterion:** at least two real Cloudflare-scheduled model
wakes, at least one *model-selected* memory write and a subsequent wake whose
inference input contains the D1-read content; no direct content leak in the
public receipt. Actual D1 quota, CPU/Neuron usage and billing must be measured
separately. Do not present a green dry build as live acceptance.
