# D1 Living Memory — provider-backed trial status (17 November 2026)

**Status: PARTIAL INFRASTRUCTURE PASS; APPLICATION ACCEPTANCE BLOCKED.**

The provider-backed test used one dedicated synthetic D1 database and a separate
Worker, not the previously verified autonomous Agent Core Worker.

## Verified

- Private operator created a D1 database with a fixed synthetic-only name.
- The Root token was available only to the isolated D1 provision/migration job.
- Cloudflare accepted the SQL schema and FTS5 setup; read-back verified the tables.
- A separate Workers-only Operations job deployed the memory Worker and bound D1.
- Local JavaScript tests, SQLite FTS5 migration and Wrangler dry-build passed.
- During one provider-backed run, remember and lexical recall completed, allowing
  the launcher to advance to the revision stage. This does not prove the whole
  cross-request memory lifecycle.

## Not accepted

- The initial test failed at the memory request (ambiguous SELECT in a
  joined FTS5 projection). This was fixed in PR #43.
- A subsequent run reached the revision request but failed before producing
  an accepted result. The adapter was changed in PR #44 to accept D1 metadata
  counts that include index/FTS changes.
- The next run again failed during the first memory trial request.
  The Worker deliberately suppresses provider error strings; the exact
  underlying reason for this final failure remains **unknown**.
- No successful three-request remember/revise/reinterpret/reopen receipt exists.
  No proof of consistent memory semantics across fresh requests, sustained
  availability or Free-plan quota headroom has been established.
- Real Cloudflare CPU, D1 row-read/write and billing metrics were not verified.

## Evidence

- First live workflow: https://github.com/blondahouse/misslea-operator/actions/runs/44117523593
- Second live workflow: https://github.com/blondahouse/misslea-operator/actions/runs/44118401180
- Third live workflow: https://github.com/blondahouse/misslea-operator/actions/runs/44119429817
- Separate public memory Worker source: labs/living_memory/src/cloudflare_smoke.mjs
- D1 SQL and adapter: labs/living_memory/migrations/0001_living_memory.sql,
  labs/living_memory/src/d1.mjs

## Next required work

Diagnose the first failing live memory endpoint with safe, bounded error
categories and D1 consistency/usage metrics. Preserve the database and existing
synthetic records; do not reset state or repeatedly deploy without evidence.
Only after a verified full create/revise/reinterpret/recall run should the
Memory Manager be connected to the autonomous Core. No personal memory import
or paid fallback is permitted for this synthetic trial.
