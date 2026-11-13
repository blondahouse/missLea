# LLM Router Lab

Evaluate off-the-shelf model gateways with identical synthetic local upstreams; do not treat routing functionality as evidence of secure operation.

- [Experiment protocol](docs/router-experiments.md)
- [First baseline findings](docs/router-first-results.md)
- [Four-candidate comparison and security diagnosis](docs/router-four-candidate-results.md)
- [Fair Comparison Protocol](../../docs/router-fair-comparison.md)
- [Common Security Suite and threat coverage](../../docs/router-security-comparison.md)
- [Public advisory and pinned-version inventory](../../docs/router-security-advisories.md)
- [First observed fair comparison](../../docs/router-fair-results-2026-11-13.md)
- Gateway profiles: `profiles/`
- Invocations: `scripts/`
- Tests: `tests/`

From repository root (Linux Docker):

```bash
bash labs/llm_router/scripts/run_router_trial.sh litellm
bash labs/llm_router/scripts/run_router_trial.sh gomodel
bash labs/llm_router/scripts/run_router_trial.sh bifrost
bash labs/llm_router/scripts/run_router_trial.sh portkey
```

The pinned Portkey image has a reproducible SSRF bypass. Its dedicated synthetic test is:

```bash
bash labs/llm_router/scripts/run_portkey_security_trial.sh
```

Reports are written to the repository root's gitignored `reports/`. **Never use these fixtures with real keys, actual models, or a network-exposed gateway.**

### Fair comparison on a single Linux Docker host

```bash
bash labs/llm_router/scripts/run_fair_comparison.sh
```

This command measures equivalent warm requests and records a strict evidence matrix. It **does not** select a winner, approve real API spending or imply security clearance. The known Portkey SSRF remains a production blocker.
