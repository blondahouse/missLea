# Unified Living Memory — Cloudflare D1 Phase 1

**Status (2026-11-18):** The standalone synthetic D1 service has an independent live PASS for create/revise/reinterpret/FTS5 across three authenticated requests. **It has since been connected** to an isolated autonomous Agent Core in `misslea-core-memory-lab`. Cross-wake writes and reads are live-verified, and its previous `invalid_decision` block was safely re-armed **in the same run** on 18 November (Kyiv local time). A native wake is scheduled for 2026-11-18 00:01 UTC; execution of that wake and full Phase 1 acceptance remain open.

## Actual boundaries

Cloudflare **D1** is the authoritative SQLite/FTS5 record store; it is **not** an AI memory service. Our replaceable `src/manager.mjs` is the Memory Manager (remember, read, revise, reinterpret, budgeted recall and batch export). `src/d1.mjs` is the parameterized D1 adapter. The integrated Cloudflare Worker calls them through a narrow in-process port; there is no independent memory daemon, paid memory SaaS, VM, public general-purpose SQL endpoint or second active writer.

D1 records have stable IDs, schema versions, revisions, mutable content, kind, five distinct weight fields, timestamps and optional derivation source. The manager does not expose whole-record voluntary deletion; read does not automatically strengthen a memory. The model is only allowed to remember, recall, revise or reinterpret using a bounded context and last-known record pointer, not arbitrary SQL or public exports.

The Agent SDK's SQLite-backed Durable Object stores the **operational wake state**, counters, provisional intent/notes and most recent D1 memory ID. It does not contain the authoritative subjective record text. Privileged credentials, legal documents, contracts and external authority do not belong in subjective memory.

## Current verified evidence

- [Standalone D1 smoke evidence](D1_LIVE_STATUS_2026-11-17.md): create/revise/reinterpret, persistence and full-text index updates across multiple HTTP requests.
- [Current integrated Core evidence](../cloudflare_agent/CORE_MEMORY_INTEGRATION.md): the read-only status at 2026-11-17 22:03:52 UTC reported **4 wakes, 2 memory writes, 4 memory reads and 3 memory contexts**. That historical status was `blocked` with `invalid_decision`, not a broken D1 binding. A later [one-time Operator resume](https://github.com/blondahouse/misslea-operator/actions/runs/44195835158) preserved the existing D1 pointer and counters, returned `scheduled` with `resumeCount=1`, and verified a native alarm for 2026-11-18 00:01 UTC; the future wake was not yet observed. [Operator diagnostic](https://github.com/blondahouse/misslea-operator/actions/runs/44148862213).

The integrated Worker and standalone D1 smoke Worker are distinct. The trusted private Operator provisions/reuses the dedicated synthetic D1 database, verifies its migration, binds it to the integrated Worker and deploys pinned source. GitHub Actions is **not** the agent's wake scheduler.

## Deliberately absent

Decay, link/association traversal, autonomously triggered consolidation, physical eviction on real storage pressure, safe historical testimony, personal memory import, independent replication and real provider quota/cost measurements are not implemented. The current interface is a staged implementation of the [adopted memory concept](../../docs/memory-concept.md), not the complete concept.

Offline verification (no Cloudflare credentials):

```bash
node --test labs/living_memory/test/*.test.mjs
python -m unittest discover -s labs/living_memory/test -p 'test_*.py' -v
```

See [Cloudflare-first roadmap](../../docs/memory-cloudflare-roadmap.md) and [integration record](../cloudflare_agent/CORE_MEMORY_INTEGRATION.md).
