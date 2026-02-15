"""Template dataclass + loader — reads YAML templates at runtime."""

from __future__ import annotations

import os
import glob
from dataclasses import dataclass, field

import yaml


@dataclass(frozen=True)
class Template:
    id: str
    name: str
    difficulty: str
    description: str
    keywords: tuple[str, ...]
    soft_aspects_menu: tuple[str, ...] = ()
    max_files: int = 1
    max_diff_lines: int = 3
    coder_instructions: str = ""
    max_attempts: int = 2
    on_fail: str = ""


class TemplateLoader:
    """Glob-scans a directory for YAML templates. No code change to add new ones."""

    def __init__(self, templates_dir: str):
        self._dir = templates_dir
        self._templates: dict[str, Template] = {}
        self._load_all()

    def _load_all(self) -> None:
        pattern = os.path.join(self._dir, "*.yaml")
        for path in sorted(glob.glob(pattern)):
            t = self._parse(path)
            self._templates[t.id] = t

    @staticmethod
    def _parse(path: str) -> Template:
        with open(path) as f:
            d = yaml.safe_load(f)
        signals = d.get("signals", {})
        retry = d.get("retry", {})
        return Template(
            id=d["id"],
            name=d["name"],
            difficulty=d.get("difficulty", "easy"),
            description=d.get("description", ""),
            keywords=tuple(signals.get("keywords", [])),
            soft_aspects_menu=tuple(d.get("soft_aspects_menu", [])),
            max_files=d.get("max_files", 1),
            max_diff_lines=d.get("max_diff_lines", 3),
            coder_instructions=d.get("coder_instructions", ""),
            max_attempts=retry.get("max_attempts", 2),
            on_fail=retry.get("on_fail", ""),
        )

    def get(self, template_id: str) -> Template | None:
        return self._templates.get(template_id)

    def all(self) -> list[Template]:
        return list(self._templates.values())

    def match(self, text: str) -> list[tuple[Template, int]]:
        """Score templates by keyword hits in text. Returns [(template, score)] sorted desc."""
        text_lower = text.lower()
        scored = []
        for t in self._templates.values():
            score = sum(1 for kw in t.keywords if kw.lower() in text_lower)
            if score > 0:
                scored.append((t, score))
        return sorted(scored, key=lambda x: x[1], reverse=True)
