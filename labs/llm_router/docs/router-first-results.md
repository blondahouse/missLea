# LLM Router Lab — first observed results (2026-11-13)

These are **real gateway binaries** exercised only against local synthetic providers on public GitHub Actions runners. No paid AI services, real vendor credentials, private conversations, or production data were used.

- [CI run: LLM Router Lab](https://github.com/blondahouse/missLea/actions/runs/43413371923) — three successful jobs: unit tests, LiteLLM integration, GoModel integration.
- JSON artifacts: `router-report-litellm` and `router-report-gomodel` under that run.
- Profiles and benchmark code are in this PR. The gateway Docker image digests from the first run are now pinned in `labs/llm_router/scripts/run_router_trial.sh` for reproducibility.

| Probe | LiteLLM | GoModel | Interpretation |
| --- | --- | --- | --- |
| Mock free primary chat | PASS | PASS | Correct response from primary |
| HTTP 429 → different free mock | PASS | NOT TESTED | Only LiteLLM profile configured a backup |
| All free mocks return 503, no paid call | PASS | PASS | No accidental paid fallback observed in these profiles |
| Tool-call response | PASS | PASS | A synthetic tool call survived the gateway |
| SSE streaming | PASS | PASS | Mock stream survived the gateway |
| Explicit mock-paid route | PASS | NOT TESTED | LiteLLM sent exactly one intentionally selected mock-paid request |
| Real cost enforcement | NOT TESTED | NOT TESTED | Zero real money spent is not a proof of robust budget controls |
| RAM, CPU and cold start | NOT MEASURED | NOT MEASURED | First run was functional, not a resource benchmark |

Details observed in first run:

- LiteLLM: primary chat 200, 262.62 ms; 429 fallback 200, 28.91 ms; all-free outage 503, 140.42 ms, **0 paid mock calls**.
- GoModel: primary chat 200, 3.67 ms; 429 returned 429 without a configured backup, 7043.9 ms; outage returned 503 in 7104.45 ms with **0 paid mock calls**.
- GoModel made several retries against the same primary (11 primary mock calls total); the current profile **cannot demonstrate independent provider failover**.
- Latencies come from separate CI jobs and include different retry/config behaviour. Do **not** rank raw performance from this trial; use fixed workloads and resource sampling.

## Preliminary finding

Both gateways can serve simple and tool-calling tasks and stream through a synthetic OpenAI-compatible upstream. **Only LiteLLM's tested configuration demonstrated free-to-free failover with a separately selectable paid route.** It also requires careful budget architecture: without a database, LiteLLM's global budget setting is not an effective payment cap. We have intentionally tested no real payment authorization.

This is not sufficient to select a winner. Before adoption: evaluate Bifrost and Portkey with the same fixtures; measure memory and cold starts on equivalent hardware; verify provider-specific free quotas, SDK parameters, independent paid-provider limits, and authenticated configuration changes. Preserve a zero-credential local suite in public CI.

Do not confuse the simulated `paid` endpoint with an actual OpenRouter connection; the former is just a counter to detect forbidden routing.
