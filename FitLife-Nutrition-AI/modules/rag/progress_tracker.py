import sqlite3
from typing import Optional, List, Dict, Any
import datetime


class ProgressTracker:
    def __init__(self, db_path: str = "data/user_profiles.db"):
        self.db_path = db_path
        self._ensure_tables()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _ensure_tables(self):
        with self._conn() as c:
            cur = c.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    date TEXT,
                    weight REAL,
                    notes TEXT
                )
                """
            )
            c.commit()

    def add_entry(self, user_id: int, weight: float, notes: Optional[str] = None, date: Optional[str] = None) -> int:
        date = date or datetime.date.today().isoformat()
        with self._conn() as c:
            cur = c.cursor()
            cur.execute("INSERT INTO progress (user_id, date, weight, notes) VALUES (?, ?, ?, ?)", (user_id, date, weight, notes))
            c.commit()
            return cur.lastrowid

    def get_entries(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self._conn() as c:
            cur = c.cursor()
            if user_id is None:
                cur.execute("SELECT id, user_id, date, weight, notes FROM progress ORDER BY date")
            else:
                cur.execute("SELECT id, user_id, date, weight, notes FROM progress WHERE user_id=? ORDER BY date", (user_id,))
            rows = cur.fetchall()
            return [
                {"id": r[0], "user_id": r[1], "date": r[2], "weight": r[3], "notes": r[4]}
                for r in rows
            ]
