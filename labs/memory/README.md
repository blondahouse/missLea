# Memory Lab

Research topic: long-term memory extraction, updating obsolete knowledge, historical decision rationale, cost, and independent restore/portability.

- [Research design](docs/memory-experiments.md)
- [Candidate inventory](docs/candidates.md)
- Synthetic scenario: [memory_v1.json](scenarios/memory_v1.json)
- Entry point: `python -m labs.memory.cli`

From repository root:

```bash
python -m labs.memory.cli list
python -m labs.memory.cli run --candidate sqlite --scenario labs/memory/scenarios/memory_v1.json --output memory-report.json
```

Only the standard-library SQLite retrieval baseline is currently implemented. No LLM is used. This does **not** measure semantic answer quality or validate production memory migration.
