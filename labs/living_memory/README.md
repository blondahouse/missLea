# Unified Living Memory — D1 Phase 1

Status (17 November 2026): LIVE PASS for the isolated synthetic D1 memory service. The three-request trial verified creation, revision, reinterpretation, FTS5 index updates and persistence across requests. The autonomous Agent Core remains a separate Worker without a Memory Manager binding; complete Phase 1 acceptance is still pending.

Cloudflare D1 is a managed SQLite database with FTS5, not an AI memory service. A replaceable Memory Manager provides remember, read, revise, reinterpret, budgeted recall, current-state export and an explicit unavailable external-evidence interface. D1 handles persistent records, parameterized SQL and full-text indexing.

Subjective records include a stable ID, schema version, mutable content, kind, strength, confidence, significance, accessibility, stability, revision, timestamps and an optional source link. Reinterpretation produces a new present-day memory, not a rollback. Read access does not increase memory strength.

There is no voluntary whole-record delete, age-based TTL, routine snapshot of former personalities, arbitrary record-count limit or automatic eviction until genuine storage pressure can be measured. Associations, non-linear decay, protected documents and historical inspection are future phases.

Worker operational state, credentials, signed contracts, financial obligations and granted authority must remain outside this subjective store. Neither the D1 adapter nor current export can be accessed over a public HTTP endpoint.

Offline tests, no external accounts or credits:

    node --test labs/living_memory/test/*.test.mjs
    python -m unittest discover -s labs/living_memory/test -p 'test_*.py' -v

A dedicated D1 database is already provisioned with the migration and an isolated synthetic Worker binding. Before connecting it to Agent Core, verify the actual Free-plan quotas and add a narrowly scoped memory port. The existing live Agent Core Worker remains unchanged.

## Dedicated live D1 smoke adapter

A separate synthetic Worker source is available at src/cloudflare_smoke.mjs.
The related Wrangler configuration intentionally has no database identifier.
Only the private trusted operator may create a dedicated D1 database, apply the
SQL migration, add the runtime MEMORY_DB binding and deploy the Worker.

Its fixed synthetic trial uses three separate authenticated HTTP requests:
create and retrieve a fabricated memory, revise it and create an interpretation,
and verify persistence and FTS5 index changes from a fresh Worker invocation.
No private content, generic SQL, external record editing or public memory APIs
are exposed. This lab is distinct from the deployed autonomous Agent Core.

Successful live evidence and historical failures: [D1 live status](D1_LIVE_STATUS_2026-11-17.md).
