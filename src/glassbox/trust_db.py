"""SQLite-based trust score persistence with exponential moving average updates."""

import sqlite3
from typing import Dict, Optional


class TrustDB:
    def __init__(self, db_path: str = "trust_scores.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trust_scores (
                agent TEXT PRIMARY KEY,
                score REAL DEFAULT 0.85,
                correct_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for agent in ["architect", "pragmatist", "critic"]:
            conn.execute("INSERT OR IGNORE INTO trust_scores (agent, score) VALUES (?, 0.85)", (agent,))
        conn.commit()
        conn.close()

    def get_trust(self, agent: str) -> float:
        conn = sqlite3.connect(self.db_path)
        result = conn.execute("SELECT score FROM trust_scores WHERE agent = ?", (agent,)).fetchone()
        conn.close()
        return result[0] if result else 0.85

    def get_all_scores(self) -> Dict[str, float]:
        conn = sqlite3.connect(self.db_path)
        results = conn.execute("SELECT agent, score FROM trust_scores ORDER BY score DESC").fetchall()
        conn.close()
        return {agent: score for agent, score in results}

    def get_stats(self, agent: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        result = conn.execute("SELECT score, correct_count, total_count FROM trust_scores WHERE agent = ?", (agent,)).fetchone()
        conn.close()
        if not result:
            return None
        score, correct, total = result
        return {"agent": agent, "trust_score": score, "correct_count": correct, "total_count": total, "accuracy": (correct / total * 100) if total > 0 else 0}

    def update_trust(self, agent: str, was_correct: bool):
        conn = sqlite3.connect(self.db_path)
        result = conn.execute("SELECT score, correct_count, total_count FROM trust_scores WHERE agent = ?", (agent,)).fetchone()
        if not result:
            conn.execute("INSERT INTO trust_scores (agent, score) VALUES (?, 0.85)", (agent,))
            old_score, correct, total = 0.85, 0, 0
        else:
            old_score, correct, total = result
        correct += 1 if was_correct else 0
        total += 1
        new_score = max(0.3, min(1.0, old_score + (1.0 / (1 + total)) * ((1.0 if was_correct else 0.0) - old_score)))
        conn.execute("UPDATE trust_scores SET score=?, correct_count=?, total_count=?, last_updated=CURRENT_TIMESTAMP WHERE agent=?", (new_score, correct, total, agent))
        conn.commit()
        conn.close()

    def reset_all(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE trust_scores SET score=0.85, correct_count=0, total_count=0")
        conn.commit()
        conn.close()
