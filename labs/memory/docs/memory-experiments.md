# Memory Lab — evaluation methodology (aligned to Unified Living Memory)

**Scope:** Compare low-cost memory approaches for an agent that can revise recollections, change its self-model and forget irreversibly. The [adopted architecture](../../../docs/memory-concept.md) defines desired behavior, but does not predetermine which engine or decay formula wins. See the [Cloudflare-first plan](../../../docs/memory-cloudflare-roadmap.md) and [evaluation policy](../../../docs/evaluation-policy.md).

## Research priorities

1. **Useful everyday recall:** correct current-context retrieval without dragging obsolete or unrelated memories into the prompt.
2. **Subjective revision:** change content, weights and confidence; redact fragments but prevent agent-directed whole-record deletion.
3. **Inference cost:** measure input tokens, LLM calls, query usage, latency and money for different exposures.
4. **Actual forgetting behavior:** test lazy time-and-experience decay, sparse associations and eviction under test-only resource pressure.
5. **Continuity without rewind:** preserve surviving current state across ordinary wakes; tolerate intentional forgetting; test failures without silently reviving forgotten information.
6. **Portability:** export the currently retained records and mutation semantics through an engine-neutral format, not an infinite event transcript.
7. **External boundary:** current obligations, authority and protected artifacts do not inherit the autobiographical retention policy.

Define measurable gates, workloads and stop conditions **before** candidate-specific comparisons. Favor the simplest maintained system that satisfies the real need.

## Existing baseline: historical retrieval test

The already committed synthetic `memory_v1` fixture contains changed decisions, rejected ideas, obligations, unrelated noise and competing evidence. The existing SQLite lab scores **evidence recall at k** and **obsolete evidence intrusion**. These tests still have value as **retrieval diagnostics**, including explicitly historical questions, but do not assert that all original events must be retained in a real Living Memory.

The baseline uses no LLM or embeddings. Its snapshot test proves only same-engine technical recovery on synthetic data. It **does not** test subjective revision, confidence calibration, cost of reflection, knowledge consolidation, purposeful links, context assembly, personal identity, automatic eviction or cross-framework portability. Report such features as `not_tested`.

## Fair experimental comparisons

- Keep model, candidate version, input history, query set and token budget comparable.
- Separate extraction/revision costs from retrieval costs and from optional deep reflection.
- Compare lexical SQLite/D1 FTS5 before introducing vectors, graph servers or large memory frameworks.
- A ready-made engine should be adopted only if its measured benefit justifies Cloudflare-only compatibility, operational footprint, recurring cost, lock-in and maintenance.
- Prevent automatic full-record deletion in the agent-facing layer, but allow infrastructure eviction on verified real pressure.
- Evaluate legal privacy requirements, redaction in current storage versus temporary provider history, and proper isolation of external documents.
- Test interruptions, conflicts, serialization/export, independent operational authorization and restore-without-resurrection.
- Run synthetic held-out suites to avoid tuning exclusively to published fixtures. Never put a real person's private messages, secrets or agent operational state into this public research repository.

## Next research actions (not deployed)

1. Establish a portable record format and a minimal Cloudflare D1 + FTS5 baseline through one Memory Manager API; retain the old lab unchanged as a diagnostic reference.
2. Run a comparable maintained candidate (e.g., Mem0 for extraction, Hindsight for reflection, Letta as a runtime alternative) only where a material decision hinges on it.
3. Measure simple exposure levels, optional weighted associations and decay/eviction variants under matched compute budgets.
4. Add the first memory-enabled agent wake only after a bounded synthetic test passes. Treat actual cost and provider limits as evidence, not assumptions.

The Memory Lab is a research capability, not an instruction to migrate or modify the running TinyFund instance.
