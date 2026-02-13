"""
SQLite-based trust score persistence with exponential moving average updates.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Optional


class TrustDB:
    """Manages agent trust scores with persistent storage."""
    
    def __init__(self, db_path: str = "trust_scores.db"):
        """
        Initialize trust database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create trust scores table and initialize default agents."""
        
        conn = sqlite3.connect(self.db_path)
        
        # Create table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trust_scores (
                agent TEXT PRIMARY KEY,
                score REAL DEFAULT 0.85,
                correct_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Initialize default agents
        default_agents = ["architect", "pragmatist", "critic"]
        for agent in default_agents:
            conn.execute("""
                INSERT OR IGNORE INTO trust_scores (agent, score) 
                VALUES (?, 0.85)
            """, (agent,))
        
        conn.commit()
        conn.close()
    
    def get_trust(self, agent: str) -> float:
        """
        Get trust score for an agent.
        
        Args:
            agent: Agent name
        
        Returns:
            Trust score (0.0 to 1.0), defaults to 0.85 if not found
        """
        conn = sqlite3.connect(self.db_path)
        result = conn.execute(
            "SELECT score FROM trust_scores WHERE agent = ?", 
            (agent,)
        ).fetchone()
        conn.close()
        
        return result[0] if result else 0.85
    
    def get_all_scores(self) -> Dict[str, float]:
        """
        Get all agent trust scores.
        
        Returns:
            Dictionary mapping agent name to trust score
        """
        conn = sqlite3.connect(self.db_path)
        results = conn.execute(
            "SELECT agent, score FROM trust_scores ORDER BY score DESC"
        ).fetchall()
        conn.close()
        
        return {agent: score for agent, score in results}
    
    def get_stats(self, agent: str) -> Optional[Dict[str, any]]:
        """
        Get detailed statistics for an agent.
        
        Args:
            agent: Agent name
        
        Returns:
            Dictionary with score, correct_count, total_count, accuracy
        """
        conn = sqlite3.connect(self.db_path)
        result = conn.execute(
            "SELECT score, correct_count, total_count FROM trust_scores WHERE agent = ?",
            (agent,)
        ).fetchone()
        conn.close()
        
        if not result:
            return None
        
        score, correct, total = result
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            "agent": agent,
            "trust_score": score,
            "correct_count": correct,
            "total_count": total,
            "accuracy": accuracy
        }
    
    def update_trust(self, agent: str, was_correct: bool):
        """
        Update trust score using exponential moving average.
        
        Formula: new_score = old_score + α * (outcome - old_score)
        Where α = 0.1 (learning rate)
        
        Args:
            agent: Agent name
            was_correct: True if agent's answer was correct
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get current score and counts
        result = conn.execute(
            "SELECT score, correct_count, total_count FROM trust_scores WHERE agent = ?",
            (agent,)
        ).fetchone()
        
        if not result:
            # Agent doesn't exist - create with default
            conn.execute(
                "INSERT INTO trust_scores (agent, score) VALUES (?, 0.85)",
                (agent,)
            )
            old_score, correct, total = 0.85, 0, 0
        else:
            old_score, correct, total = result
        
        # Update counts
        correct += 1 if was_correct else 0
        total += 1
        
        # Exponential moving average update
        alpha = 0.1  # Learning rate
        outcome = 1.0 if was_correct else 0.0
        new_score = old_score + alpha * (outcome - old_score)
        
        # Clamp between 0.3 and 1.0 (prevent total distrust or overconfidence)
        new_score = max(0.3, min(1.0, new_score))
        
        # Save to database
        conn.execute("""
            UPDATE trust_scores 
            SET score = ?, 
                correct_count = ?, 
                total_count = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE agent = ?
        """, (new_score, correct, total, agent))
        
        conn.commit()
        conn.close()
    
    def reset_agent(self, agent: str):
        """Reset an agent's trust score to default (0.85)."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE trust_scores 
            SET score = 0.85, correct_count = 0, total_count = 0 
            WHERE agent = ?
        """, (agent,))
        conn.commit()
        conn.close()
    
    def reset_all(self):
        """Reset all agents to default trust (0.85)."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE trust_scores 
            SET score = 0.85, correct_count = 0, total_count = 0
        """)
        conn.commit()
        conn.close()
