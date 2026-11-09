"""SQLite storage. No names, emails or student IDs are stored - only a random pseudonymous session id."""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = Path(os.environ.get("WELLSENSE_DB", ROOT / "data" / "processed" / "wellsense.db"))
FEEDBACK_VALUES = ("helpful", "not_helpful", "not_tried")

SCHEMA = """
CREATE TABLE IF NOT EXISTS assessments(assessment_id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,
  responses_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS predictions(prediction_id INTEGER PRIMARY KEY AUTOINCREMENT, assessment_id INTEGER NOT NULL,
  session_id TEXT NOT NULL, model_version TEXT, label TEXT, probability REAL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS recommendations(recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT, assessment_id INTEGER NOT NULL,
  session_id TEXT NOT NULL, rule_id TEXT, category TEXT, title TEXT, description TEXT, reason TEXT, ranking_score REAL,
  created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS feedback(feedback_id INTEGER PRIMARY KEY AUTOINCREMENT, recommendation_id INTEGER NOT NULL UNIQUE,
  session_id TEXT NOT NULL, value TEXT NOT NULL, note TEXT, created_at TEXT NOT NULL);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_session_id() -> str:
    return uuid.uuid4().hex


class Database:
    def __init__(self, path: Path | str | None = None):
        self.path = str(path or DEFAULT_DB)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._mem = sqlite3.connect(":memory:") if self.path == ":memory:" else None
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self):
        return self._mem if self._mem is not None else sqlite3.connect(self.path)

    def _run(self, sql, args=(), fetch=False):
        conn = self._conn()
        try:
            cur = conn.execute(sql, args)
            rows = cur.fetchall() if fetch else cur.lastrowid
            conn.commit()
            return rows
        finally:
            if self._mem is None:
                conn.close()

    def save_assessment(self, session_id: str, clean: dict) -> int:
        return self._run("INSERT INTO assessments(session_id,responses_json,created_at) VALUES(?,?,?)",
                         (session_id, json.dumps(clean), _now()))

    def save_prediction(self, assessment_id: int, session_id: str, pred: dict) -> int:
        return self._run("INSERT INTO predictions(assessment_id,session_id,model_version,label,probability,created_at) "
                         "VALUES(?,?,?,?,?,?)", (assessment_id, session_id, pred["model_version"], pred["label"],
                                                 pred["probability"], _now()))

    def save_recommendations(self, assessment_id: int, session_id: str, recs: list[dict]) -> list[dict]:
        out = []
        for r in recs:
            rid = self._run("INSERT INTO recommendations(assessment_id,session_id,rule_id,category,title,description,reason,"
                            "ranking_score,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                            (assessment_id, session_id, r["rule_id"], r["category"], r["title"], r["description"],
                             r["reason"], r["ranking_score"], _now()))
            out.append({**r, "recommendation_id": rid})
        return out

    def save_feedback(self, recommendation_id: int, session_id: str, value: str, note: str | None = None) -> None:
        if value not in FEEDBACK_VALUES:
            raise ValueError(f"feedback must be one of {FEEDBACK_VALUES}")
        owner = self._run("SELECT session_id FROM recommendations WHERE recommendation_id=?", (recommendation_id,), True)
        if not owner or owner[0][0] != session_id:
            raise ValueError("Unknown recommendation for this session.")
        note = (note or "").strip()[:300] or None
        self._run("INSERT INTO feedback(recommendation_id,session_id,value,note,created_at) VALUES(?,?,?,?,?) "
                  "ON CONFLICT(recommendation_id) DO UPDATE SET value=excluded.value, note=excluded.note, "
                  "created_at=excluded.created_at", (recommendation_id, session_id, value, note, _now()))

    def category_stats(self, session_id: str) -> dict[str, dict]:
        rows = self._run("SELECT r.category, f.value, COUNT(*) FROM feedback f JOIN recommendations r "
                         "ON r.recommendation_id=f.recommendation_id WHERE f.session_id=? GROUP BY r.category, f.value",
                         (session_id,), True)
        stats: dict[str, dict] = {}
        for cat, val, n in rows:
            stats.setdefault(cat, {"helpful": 0, "not_helpful": 0, "not_tried": 0})[val] = n
        return stats

    def history(self, session_id: str) -> list[dict]:
        rows = self._run("SELECT r.recommendation_id, r.category, r.title, r.ranking_score, r.created_at, f.value, f.note "
                         "FROM recommendations r LEFT JOIN feedback f ON f.recommendation_id=r.recommendation_id "
                         "WHERE r.session_id=? ORDER BY r.recommendation_id", (session_id,), True)
        keys = ["recommendation_id", "category", "title", "ranking_score", "created_at", "feedback", "note"]
        return [dict(zip(keys, r)) for r in rows]

    def reset_feedback(self, session_id: str) -> None:
        self._run("DELETE FROM feedback WHERE session_id=?", (session_id,))

    def delete_session(self, session_id: str) -> None:
        for t in ("feedback", "recommendations", "predictions", "assessments"):
            self._run(f"DELETE FROM {t} WHERE session_id=?", (session_id,))

    def count(self, table: str, session_id: str | None = None) -> int:
        assert table in ("assessments", "predictions", "recommendations", "feedback")
        q = f"SELECT COUNT(*) FROM {table}" + (" WHERE session_id=?" if session_id else "")
        return self._run(q, (session_id,) if session_id else (), True)[0][0]
