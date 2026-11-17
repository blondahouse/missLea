# Unified Living Memory — D1 Phase 1

Status: offline implementation and tests only. No Cloudflare D1 database was provisioned by this change.

Cloudflare D1 is a managed SQLite database with FTS5, not an AI memory service. A replaceable Memory Manager provides remember, read, revise, reinterpret, budgeted recall, current-state export and an explicit unavailable external-evidence interface. D1 handles persistent records, parameterized SQL and full-text indexing.

Subjective records include a stable ID, schema version, mutable content, kind, strength, confidence, significance, accessibility, stability, revision, timestamps and an optional source link. Reinterpretation produces a new present-day memory, not a rollback. Read access does not increase memory strength.

There is no voluntary whole-record delete, age-based TTL, routine snapshot of former personalities, arbitrary record-count limit or automatic eviction until genuine storage pressure can be measured. Associations, non-linear decay, protected documents and historical inspection are future phases.

Worker operational state, credentials, signed contracts, financial obligations and granted authority must remain outside this subjective store. Neither the D1 adapter nor current export can be accessed over a public HTTP endpoint.

Offline tests, no external accounts or credits:

    node --test labs/living_memory/test/*.test.mjs
    python -m unittest discover -s labs/living_memory/test -p 'test_*.py' -v

Before live deployment, the trusted operator must provision a dedicated D1 database, apply the migration, bind the immutable database ID to a separate synthetic Worker, and verify permissions and Free quotas. The existing live Agent Core Worker remains unchanged.
