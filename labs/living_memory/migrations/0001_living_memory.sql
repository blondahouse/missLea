-- Current subjective memories only; not the operating ledger, vault or contracts.
CREATE TABLE IF NOT EXISTS living_memory (
 seq INTEGER PRIMARY KEY AUTOINCREMENT,
 id TEXT NOT NULL UNIQUE,
 schema_version INTEGER NOT NULL DEFAULT 1 CHECK(schema_version=1),
 revision INTEGER NOT NULL DEFAULT 1 CHECK(revision>=1),
 kind TEXT NOT NULL CHECK(kind IN ('experience','fact','skill','belief','goal','value','interpretation')),
 content TEXT NOT NULL CHECK(length(content)>0),
 strength REAL NOT NULL CHECK(strength>=0 AND strength<=1),
 confidence REAL NOT NULL CHECK(confidence>=0 AND confidence<=1),
 significance REAL NOT NULL CHECK(significance>=0 AND significance<=1),
 accessibility REAL NOT NULL CHECK(accessibility>=0 AND accessibility<=1),
 stability REAL NOT NULL CHECK(stability>=0 AND stability<=1),
 derived_from TEXT REFERENCES living_memory(id),
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS living_memory_access_idx
 ON living_memory(accessibility DESC,significance DESC,seq DESC);
CREATE INDEX IF NOT EXISTS living_memory_source_idx ON living_memory(derived_from);
CREATE VIRTUAL TABLE IF NOT EXISTS living_memory_fts USING fts5(
 content,content='living_memory',content_rowid='seq',tokenize='unicode61'
);
CREATE TRIGGER IF NOT EXISTS living_memory_fts_ai AFTER INSERT ON living_memory BEGIN
 INSERT INTO living_memory_fts(rowid,content) VALUES(new.seq,new.content);
END;
CREATE TRIGGER IF NOT EXISTS living_memory_fts_au AFTER UPDATE OF content ON living_memory BEGIN
 INSERT INTO living_memory_fts(living_memory_fts,rowid,content) VALUES('delete',old.seq,old.content);
 INSERT INTO living_memory_fts(rowid,content) VALUES(new.seq,new.content);
END;
CREATE TRIGGER IF NOT EXISTS living_memory_fts_ad AFTER DELETE ON living_memory BEGIN
 INSERT INTO living_memory_fts(living_memory_fts,rowid,content) VALUES('delete',old.seq,old.content);
END;
