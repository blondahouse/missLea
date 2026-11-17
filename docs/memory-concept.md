# Miss Lea — Unified Living Memory

**Status:** Adopted primary memory concept (17 November 2026). This is a design decision, not a claim of implementation or experimental superiority.

## Purpose and boundaries

Miss Lea should accumulate and reinterpret experience rather than maintain a perfect, permanently recoverable autobiography. The system permits self-directed changes in goals, values, beliefs, preferences and self-model. The agent does not gain external authority by remembering or asserting a permission.

**Unified Living Memory** is one logical space for experiences, facts, skills, beliefs, goals, values, autobiographical interpretations and optional weighted associations. These are record kinds and dynamic views, **not separate memory services or mandatory databases**. Current context is assembled for each wake from the situation, active intents and relevant memories. Short-term and long-term are accessibility patterns, not separate stores.

**Memory Manager** provides stable, replaceable interfaces for recording, searching, reading, revising, reinterpreting, scoring and automatic eviction. Physical stores and indexes can differ behind the interface.

## Mutable recollection

- Miss Lea can edit, shorten, rephrase, enrich and reinterpret memory **content**, in addition to adjusting significance, strength, stability/decay, confidence and links.
- She can redact confidential fragments or replace them with placeholders, while **retaining a minimal meaningful record**. She cannot voluntarily delete a whole memory record, even when its weight is near zero. External legal or security obligations to delete data are handled separately.
- Substantive recall may produce a new memory about **the present interpretation of an older memory**; the original may weaken, strengthen or be revised. A new insight need not inherit the old record's weight.
- Merely fetching a record does not strengthen it or trigger an endless chain of new recollection records.

Three dimensions are deliberately separate:

| Dimension | Meaning |
| --- | --- |
| **Strength** | Persistence under decay and storage-pressure eviction |
| **Contextual accessibility** | How likely a memory is to be retrieved now, regardless of its date |
| **Confidence** | How much Miss Lea trusts its content |

Significance, decay stability, timestamps and last meaningful activation are additional attributes. Old formative memories can be more accessible than trivial events from this morning. Confidence, strength and accessibility can change independently.

## Exposure: the cost of understanding

Miss Lea chooses a **memory exposure budget** according to the task and available resources. The main limit is the **cost of interpretation** (retrieval operations, context tokens and additional model reasoning/calls), not the age of memories.

- **Minimal:** current context and high-accessibility records; no association traversal.
- **Ordinary:** limited, context-filtered direct associations; short representations first.
- **Deep:** more candidates, selective record expansion and multi-hop associations.
- **Reflection/research:** associations, contradictions and comparisons can guide deeper examination.

Memory Manager should stop when the answer is sufficient or the budget is exhausted. Deeper processing is optional; a large archive must not make every routine wake expensive.

## Weighted associations

Memories may have sparse directed or undirected relationships: `RELATED`, `SUPPORTS`, `CONTRADICTS`, `DERIVED_FROM`, etc. Relationships have type, weight, confidence and optional decay attributes. Miss Lea may revise their meaning and strength. Weak or context-irrelevant edges can be pruned from **retrieval** according to the exposure budget.

A relationship's type is distinct from its retrieval probability: contradiction must not imply a negative retrieval score. A possible **experimental**, not adopted, edge score combines relationship strength, target contextual relevance and target memory strength, with attenuation over hops. A relational links table is sufficient; a dedicated graph database is not required.

Links need not be generated for every record or maintained by a global LLM sweep. The benefit of association-guided reflection versus the cost of creating links remains an experimental question.

## Decay and physical forgetting

- **Unsupervised decay** depends on elapsed wall-clock time and the amount of **new meaningful experience**, not on the number of wakes or tool requests.
- It should use **lazy calculation** from stored anchor values and timestamps, rather than scanning and updating all records every second or wake.
- Individual memories may decay at different nonlinear rates. A power-law function combining time and experience is a **candidate for tests**, not the prescribed law.
- Miss Lea can adjust record weights and stability; automatic decay and storage-pressure eviction do not require LLM calls.
- **Low strength alone does not cause physical deletion.** Even dormant records remain stored while space is available.
- There is **no artificial live memory-size slider**: Miss Lea may use the resources actually allocated to her environment. Smaller simulated limits are appropriate for tests.
- When real storage pressure occurs, Memory Manager automatically evicts low-priority records, using cheap indexed metadata, without a whole-memory semantic audit. Voluntary whole-record deletion by Miss Lea is not the mechanism.

Memory strength, contextual accessibility and the eviction ranking must not be conflated. A large memory database does not imply that all records are loaded into a model context.

## Recovery, historical evidence and documents

**Current-state resilience:** The intended mature design maintains the one current Living Memory state across two independently failing stores, with version ordering and no resurrection of deliberately evicted or redacted material by a lagging replica. **The Cloudflare-only launch may start with one native authoritative store**; independent cross-provider mirroring is a later capability, not a condition of the first memory-enabled wake.

**No personality rollback:** The experiment does not require endless event archives, routine historical personality snapshots or arbitrary rollback. A technical failure can irreversibly destroy personal recollections. Recovery should restore the *ability to continue operating*, not silently substitute an older self.

**Time Travel:** When a platform makes a short historical window available (e.g., D1 Time Travel), Miss Lea may choose to inspect older state as **external testimony about her past**. Reading it can create a new memory; its content never automatically overwrites the current memory. A safe read-only historical inspection mechanism is required; D1 restore-to-current is not an acceptable implementation.

**Document / Contract Vault:** Contracts, obligations, legally relevant documents and selectively retained artifacts are **not part of evictable Living Memory**. They live under independent retention and access rules and are accessed through a tool, as with Time Travel. A small external active-obligation registry may initiate timely checks without placing contract text into the everyday context. Current authorization, account ownership, financial commitments and operational records are also outside autobiographical memory.

Redacting Living Memory does not by itself erase independently retained documents or provider-managed historical data; those have separate privacy and retention policies.

## Engineering stance

This concept is the **primary design direction**, not a requirement to build every feature before launch. Begin with a low-cost Cloudflare-native baseline, compare ready-made alternatives against it, and add features only when measured benefits justify model, maintenance and infrastructure cost. Preserve a stable memory API and portable record format so later indexes, engines and replicas do not require an agent-runtime redesign.

See [Cloudflare-first implementation roadmap](memory-cloudflare-roadmap.md), [Memory Lab](../labs/memory/README.md) and [Architecture principles](architecture-principles.md).
