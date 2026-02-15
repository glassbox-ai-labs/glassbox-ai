"""Phase 3 tests: TemplateLoader + 4 YAML templates."""

import os
import pytest
from glassbox_agent.core.template import Template, TemplateLoader


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "glassbox_agent", "templates")


class TestTemplate:
    def test_frozen(self):
        t = Template(id="x", name="X", difficulty="easy", description="d", keywords=("a",))
        with pytest.raises(AttributeError):
            t.id = "y"

    def test_defaults(self):
        t = Template(id="x", name="X", difficulty="easy", description="d", keywords=())
        assert t.max_files == 1
        assert t.max_diff_lines == 3
        assert t.max_attempts == 2


class TestTemplateLoader:
    def setup_method(self):
        self.loader = TemplateLoader(TEMPLATES_DIR)

    def test_loads_all_four(self):
        assert len(self.loader.all()) == 4

    def test_template_ids(self):
        ids = sorted(t.id for t in self.loader.all())
        assert ids == ["swapped_args", "typo_fix", "wrong_name", "wrong_value"]

    def test_get_by_id(self):
        t = self.loader.get("typo_fix")
        assert t is not None
        assert t.name == "Typo Fix"
        assert t.difficulty == "easy"

    def test_get_missing(self):
        assert self.loader.get("nonexistent") is None

    def test_typo_fix_keywords(self):
        t = self.loader.get("typo_fix")
        assert "typo" in t.keywords
        assert "should be" in t.keywords

    def test_wrong_value_soft_aspects(self):
        t = self.loader.get("wrong_value")
        assert "SA1" in t.soft_aspects_menu
        assert "SA2" in t.soft_aspects_menu

    def test_wrong_name_max_diff(self):
        t = self.loader.get("wrong_name")
        assert t.max_diff_lines == 5

    def test_swapped_args_instructions(self):
        t = self.loader.get("swapped_args")
        assert "SWAPPED ARGUMENTS" in t.coder_instructions

    def test_match_typo(self):
        matches = self.loader.match("There's a typo in the model name, should be gpt-4o-mini")
        assert len(matches) > 0
        assert matches[0][0].id == "typo_fix"

    def test_match_wrong_value(self):
        matches = self.loader.match("returns 0.50 but wrong default should be 0.85")
        assert any(t.id == "wrong_value" for t, _ in matches)

    def test_match_wrong_name(self):
        matches = self.loader.match("KeyError: 'critic' missing from dict")
        assert any(t.id == "wrong_name" for t, _ in matches)

    def test_match_swapped(self):
        matches = self.loader.match("min/max swapped, always returns 0.3")
        assert any(t.id == "swapped_args" for t, _ in matches)

    def test_match_no_hit(self):
        matches = self.loader.match("add a new feature for user profiles")
        assert len(matches) == 0

    def test_all_templates_have_instructions(self):
        for t in self.loader.all():
            assert len(t.coder_instructions) > 10, f"{t.id} has no coder_instructions"

    def test_all_templates_have_keywords(self):
        for t in self.loader.all():
            assert len(t.keywords) >= 3, f"{t.id} has fewer than 3 keywords"
