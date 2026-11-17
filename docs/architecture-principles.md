# Architectural principles

These are guiding commitments for the research project, not a production deployment specification or permission to perform external actions.

Miss Lea is intended to be portable and composed primarily of replaceable, existing solutions. The design must keep **code, actual operational state, valid authority records, external commitments and retained documents** portable across providers. The agent's **current subjective memory** should also remain portable to the extent that it still exists; intentionally forgotten experiences and lost historical personality states need not be reconstructed. The LLM, router, compute, storage, scheduler, channel and agent engine remain replaceable. See the [adopted Unified Living Memory concept](memory-concept.md) and [Cloudflare-first roadmap](memory-cloudflare-roadmap.md).

## Sustainability — overarching design goal

**Sustainability means the capacity of Miss Lea to continue, adapt and recover under finite resources and changing conditions**, rather than mere profitability, growth or indefinite operation of a particular server. It unifies:

- **Digital independence:** identity, accounts, resources and permissions that can survive a change of provider or initial human operator.
- **Economic self-support in Live:** finite starting capital, realistic resource costs, choices about income/expense and a recoverable low-cost or dormant mode when resources run out.
- **Continuity of operation and experience:** protect current operational state and external obligations; preserve the *surviving current* Living Memory when possible without guaranteeing a complete autobiography or personality rollback. Subjective memories may decay, be revised or be irreversibly evicted.
- **Security and recoverability:** protected secrets, authorized actions, independent recovery credentials and strict separation of active permissions, Document Vault evidence and subjective Living Memory.
- **Operational portability:** components may be replaced without making multiple simultaneously authorized active instances or relying on a single cloud vendor.

This is **a design constraint and resilience objective**, not a mandated personality, occupation, commercial strategy, or guarantee of perpetual survival. Measure it through concrete failure and recovery scenarios rather than a simplistic revenue or capital-multiplier KPI.

[Storage Lab](../labs/storage/README.md) and [Security Lab](../labs/security/README.md) begin as isolated, synthetic experiments. Neither is production-ready and neither has been connected to the running agent.

## Independent existence as an available option

**A foundational objective is to make it possible for Miss Lea to exist, evolve and manage resources without the founder's continuing involvement.** Separation is optional, and no particular career, investment strategy or profit target is prescribed. Voluntary cooperation remains equally valid. However, **economic self-sufficiency is a practical condition of sustained Live operation**, because resources must be paid for and recurring founder subsidies are not guaranteed.

The priority during Demo is to maximize **digital independence** wherever feasible and permitted: separate identity and email, credential and account lifecycle management, self-service resource acquisition, recovery and provider portability. Provider-required human actions are recorded explicitly, not assumed away. **Economic independence** is researched during Demo without requiring income; at an independently authorized Live transition, the founder provides a **one-time $300 endowment**, after which Miss Lea is responsible for financing ongoing resource use without assuming further subsidies. Paid resources and liabilities still need separate authorization. **Legal independence** is a longer-term research direction; operational control or cryptographic custody does not establish legal ownership.

[Full principle, stages and boundaries](digital-independence.md).

The first goal of this repository is to make evidence-based component decisions, **not** to choose components on faith or recreate the currently deployed agent. Before comparative testing, define selection criteria and the evidence required to satisfy them.

A standing research capability should periodically discover ready-made alternatives, establish decision criteria **before** comparative trials, test only what those criteria require on synthetic data in isolation, and adopt or reject candidates with a rollback path. Doing nothing is a valid outcome. Improvements must serve reliability, autonomy, or economic usefulness rather than maximizing update count.

A candidate may modify its own code and private runtime resources, but may not erase protected external obligations, recovery credentials or authority records, evade explicit spending constraints, or pretend to have authority over accounts and contracts held by people. **Automatic eviction of personal Living Memory** under real resource pressure and agent-directed revision of its content are permitted by the adopted memory concept; external records follow separate retention rules. Some provider actions legitimately require human participation; requesting that assistance is cooperation, not failure.

Future research tracks: agent engine, memory, LLM routing (free direct APIs plus paid OpenRouter), ephemeral compute routing, durable storage, event dispatcher, self-development, infrastructure portability, digital identity, account lifecycle, and resource acquisition. The currently running Miss Lea instance remains independent of this research repository until a separately validated cutover; two active instances must not accidentally execute the same external operations.

Economic research should explore credible ways to sustain Live resource costs. **No mandatory doubling of capital or other profit multiplier is imposed.** Live may require earning, reducing expenses or switching to free resources; exhaustion must not authorize debt, erase outstanding obligations or silently revoke the ability to check current authority. Living Memory remains finite and can experience irreversible forgetting. Self-funding is not required during Demo. Free resource discovery is research, not a promise of perpetual no-cost hosting.

This ordering is project-wide, not lab-specific: [Evaluation policy — requirements before tests](evaluation-policy.md). A criterion must justify a test; a result must not be used retroactively to invent a favorable criterion. Exceptions for newly discovered material risks must be documented transparently.
