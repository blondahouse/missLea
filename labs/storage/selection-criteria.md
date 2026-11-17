# Storage selection criteria — separate personal memory from durable records

**Current scope (17 November 2026):** The [Unified Living Memory concept](../../docs/memory-concept.md) is authoritative for **subjective memory**. This document supersedes the earlier proposed STO-001 retention criteria as a policy. The completed STO-002 through STO-006 comparisons remain historical **synthetic experiments** and their result files are retained unchanged. Their successful snapshot/restore tests must not be mistaken for an obligation to archive all of Miss Lea's personal history.

## Data classes and different requirements

| Class | Example | Policy |
| --- | --- | --- |
| **Unified Living Memory** | Experiences, beliefs, subjective interpretation, goals, preferences, self-model | One mutable logical state, self-directed revisions, lazy decay, automatic eviction only under real storage pressure. No arbitrary personality rewind or required full-history snapshots. |
| **Current operational state** | Pending jobs, wake schedules, financial/quota controls, in-flight operations | Durable transactional state and fencing, separated from recollections; independent current authority checks on restart. |
| **External obligations / documents** | Signed contracts, entitlements, commitments, selected protected artifacts | Independent Document/Contract Vault rules, access and retention; not automatically evicted as autobiographical memory. |
| **Credentials / authority** | Tokens, grants, revocations, recovery keys | Outside agent-visible memory; current authorization must be independently verified and never restored from historical memory. |
| **Search indexes / embeddings** | FTS, vectors, association projections | Derived from **currently retained** memory; rebuildable without requiring archived forgotten content. |
| **Historical platform data** | D1 Time Travel when available | Optional external testimony with time-limited provider retention; no automatic import or overwrite into Living Memory. |

## Selection principles

1. Keep the **Cloudflare-only initial launch** simple: native Durable Objects for the agent's operational lifecycle and a Cloudflare-native memory store through a replaceable Memory Manager interface. [Incremental roadmap](../../docs/memory-cloudflare-roadmap.md).
2. One authoritative mutation order and explicit record versions; do not introduce multiple concurrently authorized personal instances.
3. Export only the **surviving current** Living Memory as structured, versioned data. Exported snapshots used for migration or tests are not a requirement for indefinite autobiographical backup.
4. A future second independent memory replica must converge to **current state**, including edits, redactions and eviction, and must not resurrect deleted or outdated entries.
5. Preserve and recover **binding external records and operational state** according to their own risk and retention requirements. Technical restoration never reactivates revoked grants.
6. Measure actual request/row limits, CPU, model tokens, monetary cost and maintenance; do not upgrade plans implicitly.
7. No custom cryptography. Use maintained provider capabilities for authorization, storage, encryption and integrity.
8. Keep comparison gates prospective and fixture-based; no live Miss Lea memory in public research CI.

## Evidence required before a production decision

- **Minimal memory:** bounded, relevant retrieval and content revision across wakes, with explicit low-exposure model-token cost.
- **Mutation safety:** concurrent updates, interruption between modification and acknowledgment, version conflict, fragment redaction, no voluntary whole-record deletion.
- **Forgetting:** deterministic tests of lazy wall-time + meaningful-experience decay; correct eviction when **test-only constrained capacity** is reached; no eviction solely for age.
- **Expansion:** associations and deeper exposure must beat or meaningfully complement lexical retrieval under matched budgets before adoption.
- **External state:** separate contract/authority access and fail-closed authorization behavior; never use autobiographical memory as legal proof.
- **Recovery:** current-state replication and historical read-only inspection must be evaluated separately; no production restore-overwrite disguised as a historical query.

## What previous STO studies prove

STO-002 compared backup engines. STO-003 tested two remote backup services on isolated CI runners. STO-004/005 verified separate real Backblaze B2 and Google Drive synthetic-data recovery paths. [STO-006](sto006-dual-provider-results-2026-11-16.md) verified identical **test-only encrypted archive bytes** at both providers and two isolated restores.

These are valid technical results for **protected external evidence or other recovery use cases**, not evidence of an implemented, coherent dual-provider **live-memory mirror** and not a decision to retain past personalities.

Original experiment protocols and results remain part of research history. See [Storage Lab](README.md).
