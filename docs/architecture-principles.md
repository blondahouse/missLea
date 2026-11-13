# Initial architectural direction (non-binding)

Miss Lea is intended to be portable and composed primarily of replaceable, existing solutions. The continuity that must be demonstrably preserved is **code + accumulated state, evidence, decisions, unresolved obligations, and active-operation records**; the LLM, model router, compute provider, storage provider, scheduler, communications channel, and even agent engine are replaceable.

The first goal of this repository is to make evidence-based component decisions, **not** to choose components on faith or recreate the currently deployed agent. Before comparative testing, define selection criteria and the evidence required to satisfy them.

A standing research capability should periodically discover ready-made alternatives, establish decision criteria **before** comparative trials, test only what those criteria require on synthetic data in isolation, and adopt or reject candidates with a rollback path. Doing nothing is a valid outcome. Improvements must serve reliability, autonomy, or economic usefulness rather than maximizing update count.

A candidate may modify its own code and private runtime resources, but cannot irreversibly erase independently retained recovery copies, evade explicit spending constraints, or pretend to have authority over accounts and contracts held by people. Some provider actions legitimately require human participation; requesting that assistance is cooperation, not failure.

Future research tracks: agent engine, memory, LLM routing (free direct APIs plus paid OpenRouter), ephemeral compute routing, durable storage, event dispatcher, self-development, infrastructure portability, and resource acquisition. The currently running Miss Lea instance remains independent of this research repository until a separately validated cutover; two active instances must not accidentally execute the same external operations.

Economic intent remains to explore sustainable activity, with a separately authorized Live starting capital and a target of doubling it. Free resource discovery is a research direction, not an unverified promise of perpetual no-cost hosting.

This ordering is project-wide, not lab-specific: [Evaluation policy — requirements before tests](evaluation-policy.md). A criterion must justify a test; a result must not be used retroactively to invent a favorable criterion. Exceptions for newly discovered material risks must be documented transparently.
