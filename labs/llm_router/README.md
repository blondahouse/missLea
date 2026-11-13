# LLM Router Lab

Evaluate off-the-shelf model gateways with identical synthetic local upstreams; do not treat routing functionality as evidence of secure operation.

- [Experiment protocol](docs/router-experiments.md)
- [First baseline findings](docs/router-first-results.md)
- [Four-candidate comparison and security diagnosis](docs/router-four-candidate-results.md)
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
