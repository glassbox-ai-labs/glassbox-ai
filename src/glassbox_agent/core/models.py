"""Pydantic models for the agent pipeline."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TriageResult(BaseModel):
    template_id: str = Field(description="e.g. typo_fix, wrong_value")
    difficulty: str = Field(default="easy")
    confidence: float = Field(ge=0.0, le=1.0)
    skip_reason: str | None = Field(default=None, description="feature_request, duplicate, etc.")
    soft_aspects: list[dict] = Field(default_factory=list)
    soft_challenges: list[dict] = Field(default_factory=list)
    edge_cases: list[EdgeCase] = Field(default_factory=list)


class EdgeCase(BaseModel):
    tier: str = Field(description="T1/T2/T3/T4")
    scenario: str = Field(description="e.g. get_trust('unknown') == 0.85")
    expected: str = Field(description="What should happen")


class LineEdit(BaseModel):
    file: str = Field(description="Relative path")
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    new_text: str = Field(description="Replacement text for those lines")


class Fix(BaseModel):
    edits: list[LineEdit]
    test_code: str = Field(default="", description="Optional pytest function")
    summary: str = Field(description="One-line commit message")
    strategy: str = Field(description="Brief approach description")


class TestFailure(BaseModel):
    test_name: str
    message: str
    file: str = ""
    line: int = 0


class TestResult(BaseModel):
    passed: bool
    total: int = 0
    failures: list[TestFailure] = Field(default_factory=list)
    output: str = ""
    diff_lines: int = 0


# Fix forward reference
TriageResult.model_rebuild()
