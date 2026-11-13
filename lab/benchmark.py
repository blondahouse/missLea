"""Evaluate retrieval against labelled synthetic evidence, never real data."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from lab.memory import MemoryCandidate


def load_scenario(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("synthetic") is not True:
        raise ValueError("only explicitly synthetic scenarios are allowed")
    if data.get("schema_version") != 1:
        raise ValueError("unsupported scenario schema")
    events = data.get("events", [])
    probes = data.get("probes", [])
    if not events or not probes:
        raise ValueError("scenario must contain events and probes")
    event_ids = [event["id"] for event in events]
    if len(set(event_ids)) != len(event_ids):
        raise ValueError("duplicate event ids")
    for probe in probes:
        expected = set(probe["expected_event_ids"])
        obsolete = set(probe.get("obsolete_event_ids", []))
        if not expected or not (expected | obsolete) <= set(event_ids):
            raise ValueError("probe references missing evidence")
        if expected & obsolete:
            raise ValueError("expected evidence cannot also be obsolete")
    return data


def run_scenario(
    candidate: MemoryCandidate,
    scenario: dict[str, Any],
    *,
    top_k: int = 3,
) -> dict[str, Any]:
    if top_k < 1:
        raise ValueError("top_k must be positive")
    begin = time.perf_counter()
    # The candidate receives ONLY evidence. Answer keys remain with evaluator.
    for event in scenario["events"]:
        candidate.add({
            "id": event["id"],
            "at": event["at"],
            "text": event["text"],
        })
    ingest_ms = (time.perf_counter() - begin) * 1000
    probes = []
    total_expected = 0
    retrieved_expected = 0
    total_obsolete = 0
    retrieved_obsolete = 0
    for probe in scenario["probes"]:
        started = time.perf_counter()
        hits = candidate.search(probe["question"], top_k)
        elapsed_ms = (time.perf_counter() - started) * 1000
        ids = [hit["event_id"] for hit in hits]
        if len(ids) != len(set(ids)) or len(ids) > top_k:
            raise ValueError("candidate returned duplicate or excessive hits")
        expected = set(probe["expected_event_ids"])
        obsolete = set(probe.get("obsolete_event_ids", []))
        found_expected = len(expected.intersection(ids))
        found_obsolete = len(obsolete.intersection(ids))
        total_expected += len(expected)
        retrieved_expected += found_expected
        total_obsolete += len(obsolete)
        retrieved_obsolete += found_obsolete
        probes.append({
            "id": probe["id"],
            "question": probe["question"],
            "returned_event_ids": ids,
            "expected_event_ids": sorted(expected),
            "obsolete_event_ids": sorted(obsolete),
            "found_expected": found_expected,
            "found_obsolete": found_obsolete,
            "latency_ms": round(elapsed_ms, 3),
        })
    return {
        "schema_version": 1,
        "candidate": candidate.name,
        "scenario": scenario["name"],
        "synthetic": True,
        "method": "evidence_retrieval_only",
        "summary": {
            "event_count": len(scenario["events"]),
            "probe_count": len(probes),
            "retrieval_recall_at_k": round(retrieved_expected / total_expected, 4),
            "obsolete_intrusion_rate": (
                round(retrieved_obsolete / total_obsolete, 4)
                if total_obsolete else None
            ),
            "ingest_ms": round(ingest_ms, 3),
            "model_cost_usd": 0.0 if candidate.name == "sqlite" else None,
            "model_cost_note": (
                "no model calls" if candidate.name == "sqlite"
                else "not measured; do not assume free"
            ),
            "memory_compaction": "not_tested",
            "semantic_answer_quality": "not_tested",
            "cross_framework_portability": "not_tested",
        },
        "probes": probes,
    }
