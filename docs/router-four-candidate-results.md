# LLM Router Lab — four candidate comparison

The same deterministic synthetic providers are used for LiteLLM, GoModel, Bifrost and Portkey. A **PASS** always requires observed mock-provider traffic; a configured feature alone cannot earn a passing grade.

| Criterion | LiteLLM | GoModel | Bifrost | Portkey |
| --- | --- | --- | --- | --- |
| Primary chat | PASS (PR #2) | PASS (PR #2) | PENDING | PENDING |
| Primary 429 → free backup | PASS | NOT TESTED | PENDING | PENDING |
| Free outage → zero paid calls | PASS | PASS | PENDING | PENDING |
| Tool calling | PASS | PASS | PENDING | PENDING |
| SSE streaming | PASS | PASS | PENDING | PENDING |
| Explicit synthetic paid route | PASS | NOT TESTED | PENDING | PENDING |
| Peak RAM / cold start | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Budget enforcement with real keys | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |

This table begins with the verified results of PR #2, not guessed results for new candidates. Update it from successful and failed PR #3 GitHub Actions artifacts. Do not infer ranking from one CI run or raw latency across independently allocated runners.

Each gateway runs as its own Docker image against **three fake local model APIs**. No real provider calls or charges. Reports in GitHub Actions artifacts include per-case results, simulated paid-request counter, and a single CPU/RAM snapshot (not peak usage). Build images are pinned to digests after initial CI validation.

**Security qualification:** Portkey releases through 1.15.2 have published SSRF advisories concerning routing through custom hosts; see [CVE-2026-82270](https://github.com/advisories/ghsa-rv66-rgwx-xfrj) and [CVE-2026-110719](https://www.vulncheck.com/advisories/portkey-ai-gateway-1.14.0-through-1.15.2-ssrf-via-x-portkey-custom-host-header). Do not reuse this synthetic test setup with real keys, expose it on the public network, or treat observed test success as a security audit.

No selected winner or production deployment is implied.
