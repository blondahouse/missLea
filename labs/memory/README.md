# Memory Lab

This laboratory evaluates small, replaceable memory engines against the **[adopted Unified Living Memory concept](../../docs/memory-concept.md)** and its [incremental Cloudflare-first roadmap](../../docs/memory-cloudflare-roadmap.md). The concept applies to subjective memories; external operational state and contractual records follow different policies.

- [Evaluation methodology](docs/memory-experiments.md)
- [Candidate inventory](docs/candidates.md)
- [Synthetic scenario](scenarios/memory_v1.json)
- CLI: `python -m labs.memory.cli`

From repository root:

```bash
python -m labs.memory.cli list
python -m labs.memory.cli run --candidate sqlite --scenario labs/memory/scenarios/memory_v1.json --output memory-report.json
```

**Implemented:** standard-library SQLite evidence retrieval baseline on fabricated records, plus its existing tests. It performs no LLM calls. It does **not** provide production Living Memory, free-form semantic revision, dynamic context assembly, decay, association traversal or automatic eviction. Historical evidence-recall scores remain a diagnostic baseline, not a mandate to archive every memory.

**Next:** build the smallest stable Memory Manager boundary and Cloudflare-native D1/FTS5 experiment, measure token and query cost, and only then compare optional maintained frameworks or enhancements. See the [roadmap](../../docs/memory-cloudflare-roadmap.md). No deployment or migration is authorized by this document.
