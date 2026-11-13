# Initial architectural direction (non-binding)

Miss Lea is intended to be portable and composed primarily of replaceable, existing solutions. The continuity that must be demonstrably preserved is **code + accumulated state, evidence, decisions, unresolved obligations, and active-operation records**; the LLM, model router, compute provider, storage provider, scheduler, communications channel, and even agent engine are replaceable.

The first goal of this repository is to test components, **not** to choose them on faith or to recreate TinyFund.

A standing research capability should periodically discover ready-made alternatives, compare them against documented acceptance criteria, trial them on synthetic data in isolation, and adopt or reject them with a rollback path. Doing nothing is a valid outcome. Improvements must serve reliability, autonomy, or economic usefulness rather than maximizing update count.

A candidate may modify its own code and private runtime resources, but cannot irreversibly erase independently retained recovery copies, evade explicit spending constraints, or pretend to have authority over accounts and contracts held by people. Some provider actions legitimately require human participation; requesting that assistance is cooperation, not failure.

Future research tracks: agent engine, memory, LLM routing (free direct APIs plus paid OpenRouter), ephemeral compute routing, durable storage, event dispatcher, self-development, infrastructure portability, and resource acquisition. The existing TinyFund stays independent until a separately validated cutover; two active copies must not accidentally execute the same external operations.

Economic intent remains to explore sustainable activity, with a separately authorized Live starting capital and a target of doubling it. Free resource discovery is a research direction, not an unverified promise of perpetual no-cost hosting.
