"""Validate migration SQL with real SQLite + FTS5 without paid providers."""
import pathlib
import sqlite3
import unittest

SQL = pathlib.Path(__file__).resolve().parents[1] / "migrations" / "0001_living_memory.sql"

class MigrationTests(unittest.TestCase):
    def test_fts_insert_update_and_strict_record_kind(self):
        db = sqlite3.connect(":memory:")
        db.executescript(SQL.read_text(encoding="utf-8"))
        db.execute(
            "INSERT INTO living_memory(id,kind,content,strength,confidence,"
            "significance,accessibility,stability,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            ("memory_1","experience","A cobalt synthetic river",.6,.7,.8,.5,.5,"t","t")
        )
        search = ("SELECT living_memory.seq,living_memory.id,living_memory.content "
                  "FROM living_memory JOIN living_memory_fts "
                  "ON living_memory_fts.rowid=living_memory.seq "
                  "WHERE living_memory_fts MATCH ?")
        self.assertEqual(db.execute(search, ('"cobalt"*',)).fetchall(), [(1,"memory_1","A cobalt synthetic river")])
        db.execute("UPDATE living_memory SET content=?,revision=2 WHERE id=?",
                   ("River now looks green","memory_1"))
        self.assertEqual(db.execute(search, ('"cobalt"*',)).fetchall(), [])
        self.assertEqual(db.execute(search, ('"green"*',)).fetchall(), [(1,"memory_1","River now looks green")])
        self.assertEqual(db.execute("SELECT count(*) FROM living_memory").fetchone()[0],1)
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO living_memory(id,kind,content,strength,confidence,"
                "significance,accessibility,stability,created_at,updated_at) "
                "VALUES('bad','contract','x',.5,.5,.5,.5,.5,'t','t')"
            )
        db.close()

if __name__ == "__main__":
    unittest.main()
