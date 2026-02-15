"""Phase 5 tests: CodeEditor + FileReader tools."""

import os
import tempfile
import pytest

from glassbox_agent.tools.code_editor import CodeEditor
from glassbox_agent.tools.file_reader import FileReader
from glassbox_agent.core.models import LineEdit


@pytest.fixture
def tmp_repo(tmp_path):
    """Create a temporary repo with a sample file."""
    src = tmp_path / "src" / "glassbox"
    src.mkdir(parents=True)
    sample = src / "trust_db.py"
    sample.write_text(
        "# Trust DB\n"
        "class TrustDB:\n"
        "    def get_trust(self, agent):\n"
        "        result = self.db.get(agent)\n"
        "        return result[0] if result else 0.50\n"
        "    def update(self):\n"
        "        pass\n"
    )
    return tmp_path


class TestFileReader:
    def test_read_full(self, tmp_repo):
        r = FileReader(str(tmp_repo))
        ok, content = r.read("src/glassbox/trust_db.py")
        assert ok
        assert "1: # Trust DB" in content
        assert "5:" in content

    def test_read_lines(self, tmp_repo):
        r = FileReader(str(tmp_repo))
        ok, content = r.read_lines("src/glassbox/trust_db.py", 4, 5)
        assert ok
        assert "4:" in content
        assert "5:" in content
        assert "1:" not in content

    def test_read_missing_file(self, tmp_repo):
        r = FileReader(str(tmp_repo))
        ok, err = r.read("nonexistent.py")
        assert not ok
        assert "not found" in err.lower()

    def test_read_lines_out_of_bounds(self, tmp_repo):
        r = FileReader(str(tmp_repo))
        ok, err = r.read_lines("src/glassbox/trust_db.py", 1, 999)
        assert not ok
        assert "out of bounds" in err.lower()

    def test_read_raw(self, tmp_repo):
        r = FileReader(str(tmp_repo))
        ok, content = r.read_raw("src/glassbox/trust_db.py")
        assert ok
        assert "class TrustDB" in content
        assert "1:" not in content  # no line numbers

    def test_list_files(self, tmp_repo):
        r = FileReader(str(tmp_repo))
        files = r.list_files((".py",))
        assert any("trust_db.py" in f for f in files)


class TestCodeEditor:
    def test_apply_single_line(self, tmp_repo):
        editor = CodeEditor(str(tmp_repo))
        edit = LineEdit(file="src/glassbox/trust_db.py", start_line=5, end_line=5,
                        new_text="        return result[0] if result else 0.85\n")
        ok, err = editor.apply(edit)
        assert ok, err
        with open(os.path.join(str(tmp_repo), "src/glassbox/trust_db.py")) as f:
            content = f.read()
        assert "0.85" in content
        assert "0.50" not in content

    def test_apply_missing_file(self, tmp_repo):
        editor = CodeEditor(str(tmp_repo))
        edit = LineEdit(file="nope.py", start_line=1, end_line=1, new_text="x")
        ok, err = editor.apply(edit)
        assert not ok
        assert "not found" in err.lower()

    def test_apply_out_of_bounds(self, tmp_repo):
        editor = CodeEditor(str(tmp_repo))
        edit = LineEdit(file="src/glassbox/trust_db.py", start_line=1, end_line=999, new_text="x")
        ok, err = editor.apply(edit)
        assert not ok
        assert "out of bounds" in err.lower()

    def test_apply_all(self, tmp_repo):
        editor = CodeEditor(str(tmp_repo))
        edits = [
            LineEdit(file="src/glassbox/trust_db.py", start_line=5, end_line=5,
                     new_text="        return result[0] if result else 0.85\n"),
        ]
        ok, err = editor.apply_all(edits)
        assert ok, err

    def test_apply_all_stops_on_error(self, tmp_repo):
        editor = CodeEditor(str(tmp_repo))
        edits = [
            LineEdit(file="nope.py", start_line=1, end_line=1, new_text="x"),
            LineEdit(file="src/glassbox/trust_db.py", start_line=5, end_line=5, new_text="y"),
        ]
        ok, err = editor.apply_all(edits)
        assert not ok

    def test_diff_line_count(self, tmp_repo):
        editor = CodeEditor(str(tmp_repo))
        edit = LineEdit(file="f.py", start_line=5, end_line=5, new_text="one line")
        assert editor.diff_line_count(edit) == 1

    def test_fuzzy_find_exact(self):
        content = "line 1\nreturn result[0] if result else 0.50\nline 3"
        line, ratio = CodeEditor.fuzzy_find(content, "return result[0] if result else 0.50")
        assert line == 2
        assert ratio > 0.9

    def test_fuzzy_find_close(self):
        content = "line 1\nreturn result[0] if result else 0.50\nline 3"
        line, ratio = CodeEditor.fuzzy_find(content, "return result[0] if result else 0.85")
        assert line == 2
        assert ratio > 0.8

    def test_fuzzy_find_no_match(self):
        content = "line 1\nline 2\nline 3"
        line, ratio = CodeEditor.fuzzy_find(content, "completely different text here")
        assert line == 0

    def test_file_preserved_after_edit(self, tmp_repo):
        """Ensure non-edited lines are untouched."""
        editor = CodeEditor(str(tmp_repo))
        edit = LineEdit(file="src/glassbox/trust_db.py", start_line=5, end_line=5,
                        new_text="        return result[0] if result else 0.85\n")
        editor.apply(edit)
        reader = FileReader(str(tmp_repo))
        ok, content = reader.read_raw("src/glassbox/trust_db.py")
        assert "class TrustDB" in content
        assert "def update" in content
