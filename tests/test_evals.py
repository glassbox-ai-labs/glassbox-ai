"""Eval tests - verify BugFactory inject/verify on 10 easy bugs."""

import pytest

from evals.bug_factory import BugFactory
from evals.catalog import EASY


@pytest.fixture
def factory():
    return BugFactory()


@pytest.fixture
def clean_sources():
    """Read actual source files from disk."""
    sources = {}
    for spec in EASY:
        if spec.file not in sources:
            with open(spec.file) as f:
                sources[spec.file] = f.read()
    return sources


@pytest.mark.parametrize("spec", EASY, ids=[b.id for b in EASY])
class TestEasyBugs:
    """Each easy bug: inject creates diff, verify rejects buggy, verify accepts clean."""

    def test_inject_creates_diff(self, factory, clean_sources, spec):
        mutated = factory.inject(spec, clean_sources)
        assert mutated[spec.file] != clean_sources[spec.file]

    def test_verify_rejects_buggy(self, factory, clean_sources, spec):
        mutated = factory.inject(spec, clean_sources)
        assert not factory.verify(spec, mutated)

    def test_verify_accepts_clean(self, factory, clean_sources, spec):
        assert factory.verify(spec, clean_sources)
