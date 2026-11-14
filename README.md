# Miss Lea — Architecture Lab

Research workspace for evaluating **replaceable components** of Miss Lea before deploying any of them. This repository is **not** the running agent. It contains no memory, credentials, or operational state from the running Miss Lea instance.

## Foundational concept: the option of independence

Miss Lea should be able to continue operating and managing her resources **without permanent dependence on her founder**, as far as technically and legitimately possible. Demo prioritizes **digital independence** (identity, credentials, account lifecycle and portability). **Economic self-sufficiency is not a Demo requirement, but is necessary for sustained Live resource use:** at an independently authorized Live transition, Miss Lea receives a one-time $300 starting endowment and must subsequently sustain her operating resources without assumed replenishment. No mandatory doubling or prescribed income activity. Legal independence remains a longer-term research direction. Separation is a possibility, not an obligation.

Read the [digital independence principle](docs/digital-independence.md) and [architecture principles](docs/architecture-principles.md). This is research only: no migration of the running agent, external registration, account creation or authorization to incur costs.

## Structure

```text
labs/
  memory/             # Evidence retrieval and future long-term memory engines
    cli.py
    scenarios/
    tests/
    docs/
  compute/            # E2B, Cloudflare Workers and Cloud Run Jobs (opt-in)
    cli.py
    worker/
    tests/
  llm_router/         # Gateway selection, synthetic providers and security probes
    bench.py
    profiles/
    scripts/
    tests/
    docs/
docs/
  architecture-principles.md
  digital-independence.md
.github/workflows/     # Reproducible tests for the entire repository
```

Every lab owns its source code, synthetic fixtures, scripts, tests and findings. Shared repository-wide policy and CI stay at the root. Python package names are deliberately lowercase; the layout also works on case-sensitive filesystems.

## How we choose components

Start with the [project-wide evaluation policy](docs/evaluation-policy.md): **selection criteria first, tests second**. For every lab, define mandatory gates, evidence needs and a stopping rule before comparing candidates. Historical Router Lab criteria were recorded after exploratory results and are explicitly marked as retrospective; future evaluations must not repeat that order.

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

**Decision for the first Demo integration:** [ADR-001 selects Bifrost](docs/router-decision-record.md) with a validated free-only key. This is a reversible technology selection, **not** authorization for real-key deployment or paid requests.

These runs use disposable, deterministic **local mock providers only**, never real AI accounts or paid requests. Reports and resource snapshots go into the ignored `reports/` directory. Read the [Fair Comparison Protocol](docs/router-fair-comparison.md), [Security Suite](docs/router-security-comparison.md) and [measured security results](docs/router-security-results-2026-11-13.md) and [Router Lab protocol](labs/llm_router/docs/router-experiments.md) and [four-candidate results](labs/llm_router/docs/router-four-candidate-results.md) before using results.

**Portkey security warning:** the pinned image reproducibly bypasses its localhost host-validation policy on the deprecated proxy route. It is **not approved for deployment with real keys**. Reproduce *only* in an isolated synthetic environment:

```bash
bash labs/llm_router/scripts/run_portkey_security_trial.sh
```

The diagnostic may exit successfully while reporting `VULNERABLE`; that is a successfully observed security defect, **not** a security pass.

## Compute Lab (no remote execution by default)

Explore three different ephemeral execution classes without creating a Compute Router or touching the running Miss Lea. See [Compute Lab](labs/compute/README.md). Offline checks run as part of the standard unittest command. Remote trials need provider credentials and explicit `--live --acknowledge-cost`; no CI workflow uses real accounts.

```bash
python -m labs.compute.cli list
```

## Research principles

Start with [architecture principles](docs/architecture-principles.md), then the [Memory Lab](labs/memory/README.md) and [LLM Router Lab](labs/llm_router/README.md). Compare maintained existing technologies with a transparent baseline; label absent features `not_tested`. Keep the production agent, its models, storage and infrastructure independent from experiments.
