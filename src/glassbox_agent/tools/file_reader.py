"""FileReader — read source files with line numbers (Paper 2: SWE-agent style)."""

from __future__ import annotations

import os


class FileReader:
    """Reads files relative to repo root, returns line-numbered content."""

    def __init__(self, repo_root: str):
        self._root = repo_root

    def read(self, rel_path: str) -> tuple[bool, str]:
        """Read a file. Returns (ok, content_with_line_numbers) or (False, error)."""
        full = os.path.join(self._root, rel_path)
        if not os.path.isfile(full):
            return False, f"File not found: {rel_path}"
        with open(full) as f:
            lines = f.readlines()
        numbered = "".join(f"{i+1}: {line}" for i, line in enumerate(lines))
        return True, numbered

    def read_lines(self, rel_path: str, start: int, end: int) -> tuple[bool, str]:
        """Read specific line range (1-indexed, inclusive)."""
        full = os.path.join(self._root, rel_path)
        if not os.path.isfile(full):
            return False, f"File not found: {rel_path}"
        with open(full) as f:
            lines = f.readlines()
        if start < 1 or end > len(lines):
            return False, f"Line range {start}-{end} out of bounds (file has {len(lines)} lines)"
        selected = lines[start - 1:end]
        numbered = "".join(f"{start + i}: {line}" for i, line in enumerate(selected))
        return True, numbered

    def read_raw(self, rel_path: str) -> tuple[bool, str]:
        """Read raw content without line numbers."""
        full = os.path.join(self._root, rel_path)
        if not os.path.isfile(full):
            return False, f"File not found: {rel_path}"
        with open(full) as f:
            return True, f.read()

    def list_files(self, extensions: tuple[str, ...] = (".py",)) -> list[str]:
        """List source files in repo matching extensions."""
        result = []
        for root, _, files in os.walk(self._root):
            if any(skip in root for skip in (".git", ".venv", "__pycache__", "node_modules")):
                continue
            for fname in sorted(files):
                if any(fname.endswith(ext) for ext in extensions):
                    result.append(os.path.relpath(os.path.join(root, fname), self._root))
        return result
