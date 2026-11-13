# Miss Lea — Architecture Lab

An open laboratory for selecting replaceable components of a portable, self-evolving agent.

**Status:** research only. The existing TinyFund / Miss Lea installation is not changed. No real memories, credentials, or operational data from the existing TinyFund installation belong here.

## LLM Router research (PR #2)

Before choosing memory technologies, we evaluate a replaceable model gateway using fake providers and **no paid requests**. Run a real third-party router against three local mock model APIs with:

```bash
bash scripts/run_router_trial.sh litellm
bash scripts/run_router_trial.sh gomodel
bash scripts/run_router_trial.sh bifrost
bash scripts/run_router_trial.sh portkey
```

The CLI writes synthetic evidence to `reports/`. Candidate capability coverage and safety caveats are in [router experiment protocol](docs/router-experiments.md). Bifrost and Portkey are included in PR #3's synthetic gateway trials. See [four-candidate comparison](docs/router-four-candidate-results.md); no production selection has been made.

## First track: long-term memory

We compare ready-made memory systems against a minimal SQLite baseline with the **same synthetic history and questions**. The first PR establishes the reproducible harness and the baseline; Letta, Mem0, and Graphiti are registered as candidates **not yet integrated**. We will not report unimplemented adapters as tested.

The lab tests evidence retrieval, obsolete evidence intrusion, recovery from a persisted snapshot, and execution cost. Future adapters can additionally expose working-memory compaction, reasoning-quality, and LLM usage metrics. Retrieval is **not** equivalent to knowing or reasoning correctly.

### Run (Python 3.11+, no dependencies)

```bash
python -m unittest discover -s tests -v
python -m lab.cli list
python -m lab.cli run --candidate sqlite --scenario scenarios/memory_v1.json --output memory-report.json
```

The generated report contains only synthetic examples; output files are ignored by Git.

### Design principles

- Prefer proven, maintained components; write only the smallest integration contract and experiment harness needed.
- Preserve raw evidence and the reasons behind decisions; evaluate updates and forgetting without silently erasing the audit trail.
- Compare single components and combinations only after a fair baseline exists.
- Never let a candidate see expected answers. Record unsupported features as **not tested**, never as successes.
- Keep the agent runtime, model provider, storage, and dispatcher independently replaceable.
- Experiments must be reproducible and reversible before changing an active instance.

See [experiment design](docs/memory-experiments.md) and [candidate inventory](docs/candidates.md). No license has been selected yet.
