"""SQLite store for the retrieval corpus. Seeded from seeds.py; ready to grow to
mined real bug/fix pairs later without touching the rest of the pipeline."""

import sqlite3
from pathlib import Path

from boogeyman.retrieval.seeds import SEEDS

DB = Path(__file__).resolve().parents[3] / "corpus.db"  # gitignored


def connect(db_path: Path = DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS examples ("
        "id INTEGER PRIMARY KEY, code TEXT, bug_class TEXT, hint TEXT)"
    )
    return conn


def seed(db_path: Path = DB) -> None:
    conn = connect(db_path)
    if conn.execute("SELECT COUNT(*) FROM examples").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO examples (code, bug_class, hint) VALUES (?, ?, ?)",
            [(s["code"], s["bug_class"], s["hint"]) for s in SEEDS],
        )
        conn.commit()
    conn.close()


def all_examples(db_path: Path = DB) -> list[dict]:
    seed(db_path)
    conn = connect(db_path)
    rows = conn.execute("SELECT code, bug_class, hint FROM examples").fetchall()
    conn.close()
    return [dict(r) for r in rows]
