# Miss Lea — Architecture Lab

Research workspace for evaluating **replaceable components** of Miss Lea before deploying any of them. This repository is **not** the running agent. It contains no memory, credentials, or operational state from the running Miss Lea instance.

## Structure

```text
labs/
  memory/             # Evidence retrieval and future long-term memory engines
    cli.py
    scenarios/
    tests/
    docs/
  llm_router/         # Gateway selection, synthetic providers and security probes
    bench.py
    profiles/
    scripts/
    tests/
    docs/
docs/
  architecture-principles.md
.github/workflows/     # Reproducible tests for the entire repository
```

Every lab owns its source code, synthetic fixtures, scripts, tests and findings. Shared repository-wide policy and CI stay at the root. Python package names are deliberately lowercase; the layout also works on case-sensitive filesystems.

## Run tests (Python 3.11+, no third-party Python dependencies)

From the repository root:

```bash
python -m unittest discover -s labs -t . -p 'test_*.py' -v
python -m labs.memory.cli list
python -m labs.memory.cli run --candidate sqlite --scenario labs/memory/scenarios/memory_v1.json --output memory-report.json
```

The SQLite baseline is deliberately simplistic. Letta, Mem0 and Graphiti are *research candidates*, not yet wired up or benchmarked.

## LLM Router experiments (Linux Docker required)

```bash
bash labs/llm_router/scripts/run_router_trial.sh litellm
bash labs/llm_router/scripts/run_router_trial.sh gomodel
bash labs/llm_router/scripts/run_router_trial.sh bifrost
bash labs/llm_router/scripts/run_router_trial.sh portkey
```

These runs use disposable, deterministic **local mock providers only**, never real AI accounts or paid requests. Reports and resource snapshots go into the ignored `reports/` directory. Read the [Fair Comparison Protocol](docs/router-fair-comparison.md) and [Security Suite](docs/router-security-comparison.md) and [Router Lab protocol](labs/llm_router/docs/router-experiments.md) and [four-candidate results](labs/llm_router/docs/router-four-candidate-results.md) before using results.

**Portkey security warning:** the pinned image reproducibly bypasses its localhost host-validation policy on the deprecated proxy route. It is **not approved for deployment with real keys**. Reproduce *only* in an isolated synthetic environment:

```bash
bash labs/llm_router/scripts/run_portkey_security_trial.sh
```

The diagnostic may exit successfully while reporting `VULNERABLE`; that is a successfully observed security defect, **not** a security pass.

## Research principles

Start with [architecture principles](docs/architecture-principles.md), then the [Memory Lab](labs/memory/README.md) and [LLM Router Lab](labs/llm_router/README.md). Compare maintained existing technologies with a transparent baseline; label absent features `not_tested`. Keep the production agent, its models, storage and infrastructure independent from experiments.
