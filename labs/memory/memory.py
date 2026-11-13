"""A minimal candidate contract and a deliberately unsophisticated SQLite baseline.

The SQLite baseline is *not* an intelligent memory system. It is an immutable
event store with deterministic lexical retrieval, useful for comparing real
memory engines against something simple and auditable.
"""

from __future__ import annotations

import re
import sqlite3
import tempfile
from pathlib import Path
from typing import Protocol, TypedDict


class MemoryHit(TypedDict):
    event_id: str
    text: str


class MemoryCandidate(Protocol):
    name: str

    def add(self, event: dict[str, str]) -> None: ...
    def search(self, question: str, limit: int) -> list[MemoryHit]: ...
    def close(self) -> None: ...


_STOP = {
    "a", "an", "are", "as", "at", "be", "by", "did", "do", "does",
    "for", "from", "has", "how", "in", "is", "it", "of", "on",
    "our", "the", "to", "was", "were", "what", "when", "which",
    "who", "why", "with",
}


def _terms(text: str) -> set[str]:
    return {term for term in re.findall(r"\w+", text.casefold()) if term not in _STOP}


class SQLiteBaseline:
    name = "sqlite"

    def __init__(self, path: str) -> None:
        self.path = path
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS events ("
            "event_id TEXT PRIMARY KEY, event_time TEXT NOT NULL,"
            "text TEXT NOT NULL, inserted_at INTEGER NOT NULL)"
        )
        self.db.commit()

    def add(self, event: dict[str, str]) -> None:
        if not all(event.get(key) for key in ("id", "at", "text")):
            raise ValueError("event must have nonempty id, at, and text")
        position = self.db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        self.db.execute(
            "INSERT INTO events(event_id,event_time,text,inserted_at) VALUES (?,?,?,?)",
            (event["id"], event["at"], event["text"], position),
        )
        self.db.commit()

    def search(self, question: str, limit: int = 3) -> list[MemoryHit]:
        if limit < 1:
            raise ValueError("limit must be positive")
        query = _terms(question)
        if not query:
            return []
        scored = []
        for event_id, text, position in self.db.execute(
            "SELECT event_id, text, inserted_at FROM events"
        ):
            overlap = len(query & _terms(text))
            if overlap:
                # Most overlapping terms first, newest event to break ties.
                scored.append((overlap, position, event_id, text))
        scored.sort(key=lambda row: (-row[0], -row[1], row[2]))
        return [
            {"event_id": event_id, "text": text}
            for _, _, event_id, text in scored[:limit]
        ]

    def snapshot(self) -> bytes:
        """A consistent portable SQLite snapshot; does not depend on a VM."""
        self.db.commit()
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "snapshot.sqlite"
            target = sqlite3.connect(str(file))
            try:
                self.db.backup(target)
            finally:
                target.close()
            return file.read_bytes()

    @classmethod
    def from_snapshot(cls, raw: bytes, path: str) -> "SQLiteBaseline":
        file = Path(path)
        if file.exists():
            raise FileExistsError("never overwrite a potential existing state")
        if not raw.startswith(b"SQLite format 3\x00"):
            raise ValueError("invalid SQLite snapshot")
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(raw)
        return cls(str(file))

    def close(self) -> None:
        self.db.close()
