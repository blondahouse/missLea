# Memory research: methodology v1

## Purpose

Select or combine existing memory solutions for a long-lived agent. Candidate names do not imply endorsement. No real agent memory is used until a separate, explicitly approved migration.

## Questions we intend to answer

All future comparative trials must follow the [project-wide evaluation policy](../../../docs/evaluation-policy.md): define selection gates, trade-offs and stopping conditions **before** writing candidate-specific tests. The following questions are research interests, not yet a frozen threshold or a pre-registered winner-selection rule. Before adding another memory backend, determine which decision-critical question the experiment would settle.

1. **Experience** — does the system distill useful lessons from hundreds of events rather than endlessly repeat transcripts?
2. **Revision and forgetting** — can it demote irrelevant details and obsolete beliefs while retaining traceable reasons for changes?
3. **Causal recall** — can it retrieve the decision, alternatives, evidence, and later consequences months after the event?
4. **Autonomy and price** — what model calls, tokens, compute, maintenance, and storage are required for routine memory operations?
5. **Portability** — can state be exported, restored, and verified in a fresh environment or a different memory engine?

## The first implemented experiment

The versioned, entirely fabricated `memory_v1` history contains changed decisions, old beliefs, rejected proposals, obligations, noisy irrelevant events, and interference from a different project. Every candidate ingests the same event text, timestamp, and ID. The benchmark retains expected and obsolete evidence IDs privately from candidates.

The current score measures **evidence recall at k** and **obsolete evidence intrusion**. An obsolete event can still be needed for an explicitly historical question; therefore an event is labelled obsolete per question, not globally erased.

This is **not** a measure of answer accuracy, memory consolidation, autonomous forgetting, understanding, personality, or consciousness. All such metrics are explicitly `not_tested` until implemented.

The SQLite baseline deliberately has no LLM and no semantic embedding. A specialist engine must demonstrate benefits relative to that simple, low-cost baseline. Its portable snapshot test proves same-engine recovery only, not cross-framework migration.

## Fair comparison and combinations

- Pin dependencies and model versions for each experiment.
- Use the same evidence and probe sets; separately disclose any candidate that cannot process the same input contract.
- Measure cold starts and end-to-end time in addition to model-token cost. Never substitute a claim of a free tier for a measured zero-dollar bill.
- Record model and embedding choices separately from memory-system choices. If results cannot use equivalent models, report the confound.
- Run a second, private held-out synthetic suite before adopting any winner to avoid optimizing for the public test fixtures.
- Combinations must justify added cost, complexity, and migration risk against individual components.
- Test crash/restart, inconsistent updates, export/restore, privacy, and safe rollback before a production migration.
- Do not put personal or operational data from the running Miss Lea instance into public repositories or unreviewed third-party memory services.

## Next experiments (not yet implemented)

- Add real Letta, Mem0 and Graphiti adapters, each in an isolated profile with documented prerequisites; mark failures and unavailable credentials instead of silently skipping.
- Evaluate working-memory compaction after long noisy histories.
- Compare semantic question-answer quality with source-based grading under equalized model budgets.
- Simulate contradictory updates, interruption between side effect and save, export/import into a different backend, and multi-session continuity.
- Evaluate fusion architectures only after single systems have comparable measurements.

The lab is itself a future capability of Miss Lea: it may propose, test, and eventually replace its components, but initially **does not deploy or migrate production data**.
