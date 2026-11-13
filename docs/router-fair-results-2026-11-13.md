# Fair Comparison — first observed run, 2026-11-13

> **Historical functional-performance snapshot.** The [later security comparison](router-security-results-2026-11-13.md) uses 19 scoped probes and a hardened Bifrost configuration. It supersedes this page's implied safety coverage and Bifrost resource numbers, while preserving the original reproducible measurements.

**Source:** [GitHub Actions run 43434096989](https://github.com/blondahouse/missLea/actions/runs/43434096989); [download raw comparison evidence](https://github.com/blondahouse/missLea/actions/runs/43434096989/artifacts/14043930005).

These are **real third-party Docker gateway binaries**, each tested against the **same deterministic localhost mock providers**. All four ran on **one CI runner** (rather than one runner per gateway), with pinned images pre-pulled before measuring cold readiness.

| Candidate | 6 functional checks | Warm latency p50 / p95 | Cold-ready ms (one sample) | Memory snapshot (one sample) | Security |
| --- | --- | --- | ---: | ---: | --- |
| LiteLLM | 6/6 | 10.98 / 11.76 ms | 23119 | 658.1 MiB | NOT TESTED |
| GoModel | 6/6 | 0.99 / 1.12 ms | 248 | 14.49 MiB | NOT TESTED |
| Bifrost | 6/6 | 1.06 / 1.14 ms | 5169 | 138.9 MiB | NOT TESTED |
| Portkey | 6/6 | 2.49 / 3.73 ms | 1185 | 80.64 MiB | **VULNERABLE — BLOCKED** |

**Key corrected error:** Earlier GoModel was not configured for failover or a mock-paid route, so those capabilities were listed as `NOT TESTED`. Here GoModel uses a documented native virtual-model failover over two mock upstreams and a separately selected third mock-paid route. It passed both tests, as well as the other four common functional tests.

Each candidate also received **8 warmup + 40 unique sequential synthetic requests**. Our upstream audit confirmed a primary-model call for each request, with no backup/paid traffic during the warm benchmark. This minimizes direct comparison confounds but cannot eliminate gateway-native routing/config differences.

### No ranking yet

A single CI run is **not** a defensible performance leaderboard. These are localhost-only latencies, *not* LLM inference latencies. The memory data are post-trial container snapshots, not peak RSS; cold readiness is a single trial with different framework startup characteristics. Repeat comparisons on a controlled machine with balanced order and variability estimates before choosing based on these numbers.

**Real budget enforcement is NOT TESTED for any candidate**. The common six tests only prove routing and simulated paid-call boundaries with fake providers. Production security is **NOT TESTED** for LiteLLM, GoModel and Bifrost, not approved. The pinned Portkey image has a separately reproduced SSRF defect and is explicitly excluded from real-key use.

No winner selected; no production deployment approved. Follow the [Fair Comparison Protocol](router-fair-comparison.md) to interpret this and future runs.
