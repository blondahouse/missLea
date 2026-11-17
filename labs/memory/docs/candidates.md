# Memory candidates — research inventory, not rankings

The [adopted concept](../../../docs/memory-concept.md) and [Cloudflare-first roadmap](../../../docs/memory-cloudflare-roadmap.md) are the requirements; **no memory engine has been selected as a production winner**.

| Candidate | Possible role | Current state | Critical consideration |
| --- | --- | --- | --- |
| **Cloudflare D1 + SQLite FTS5** | Native baseline for mutable Living Memory | Proposed next lab, not yet implemented | Cloudflare-only Free-capable path, with daily query/storage limits; requires our policy and API |
| **Existing SQLite lab** | Cheap lexical retrieval reference | Implemented, synthetic-only | No semantic revision, budgeted exposure, decay or link retrieval |
| **Mem0** | Fact extraction and retrieval | Not integrated | Evaluate inference overhead, update behavior, Cloudflare compatibility and portablility |
| **Hindsight** | Richer reflection and consolidation | Not integrated | Extra runtime/memory/LLM cost; not a native Workers drop-in |
| **Letta / Letta Code** | Self-managed agent context and memory | Not integrated | May replace a larger part of the agent runtime; evaluate rather than assume drop-in memory |
| **Graphiti** | Weighted/temporal relation research | Not integrated | Specialized graph backend and model extraction cost likely excessive at launch |
| **LangGraph** | Durable execution/checkpointing | Not integrated | Operational state framework, **not** a semantic-memory equivalent |

Some candidates solve **different problems**. A working-context engine, lexical store and external documents need not be bundled into one product. Compare integrations against the simplest native baseline using matched workloads and costs. Keep every result explicit: `pass`, `fail`, or `not_tested`.

No automatic provider migration, paid key use or real memory ingestion is permitted by this inventory.
