"""Reflexion memory — save/load/query past failure reflections (Paper 1: Reflexion)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass
class Reflection:
    issue_number: int
    issue_title: str
    template_id: str = ""
    failure_modes: list[str] = field(default_factory=list)
    reflection: str = ""


class MemoryStore:
    """Stores verbal failure reflections as JSON. Queryable by keyword."""

    def __init__(self, path: str = ""):
        self._path = path
        self._reflections: list[Reflection] = []
        if path and os.path.exists(path):
            self._load()

    def _load(self) -> None:
        with open(self._path) as f:
            data = json.load(f)
        self._reflections = [Reflection(**r) for r in data]

    def save_reflection(self, reflection: Reflection) -> None:
        self._reflections.append(reflection)
        if self._path:
            self._persist()

    def _persist(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w") as f:
            json.dump([r.__dict__ for r in self._reflections], f, indent=2)

    def query(self, keyword: str, limit: int = 5) -> list[Reflection]:
        """Find reflections matching keyword in title or reflection text."""
        keyword_lower = keyword.lower()
        matches = [
            r for r in self._reflections
            if keyword_lower in r.issue_title.lower() or keyword_lower in r.reflection.lower()
        ]
        return matches[-limit:]

    def format_for_prompt(self, title: str) -> str:
        """Format relevant reflections for injection into LLM prompt."""
        relevant = self.query(title if title else "", limit=3)
        if not relevant:
            return ""
        lines = ["PAST REFLECTIONS (learn from these):"]
        for r in relevant:
            lines.append(f"- Issue #{r.issue_number} ({r.template_id}): {r.reflection}")
        return "\n".join(lines)

    def all(self) -> list[Reflection]:
        return list(self._reflections)
