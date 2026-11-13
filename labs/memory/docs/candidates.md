# Candidate inventory — research, not rankings

| Candidate | Role | Integration | Notes |
| --- | --- | --- | --- |
| [SQLite](https://www.sqlite.org/) | Immutable event store, lexical baseline | **Implemented** | Standard library only; no autonomous consolidation |
| [Letta](https://github.com/letta-ai/letta) / [Letta Code](https://github.com/letta-ai/letta-code) | Agent-driven context and memory | **Not integrated** | Evaluate memory capabilities *and* cost of the agent engine; verify export semantics on the selected version |
| [Mem0](https://github.com/mem0ai/mem0) | Extracted, indexed memories | **Not integrated** | Test update semantics, provenance, and dependence on external LLM or embeddings |
| [Graphiti](https://github.com/getzep/graphiti) | Temporal knowledge graph | **Not integrated** | Test contradictory facts, temporal relations, infrastructure footprint |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Durable execution and state checkpoints | **Not integrated** | Compare as a state-management tool, not as a drop-in semantic-memory competitor |

Candidates can occupy **different roles**. A useful combination might pair a working-context engine, long-term evidence retrieval, and durable execution checkpoints. It must be tested against a simpler baseline and may be rejected.

## Evaluation decision record

No candidate has been selected as production memory. Letta is **a candidate, not a winner**. The first completed comparison must report runnable configurations, missing features, results, resource usage and limitations before recommending adoption. Do not build new abstractions where an upstream tool already exposes a suitable stable interface.
