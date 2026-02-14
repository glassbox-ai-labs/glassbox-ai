"""GlassBox Agent v0.3-beta - Phase 1: THINK before coding."""

import json

from openai import OpenAI

from .config import MODEL, TEMPERATURE_ANALYZE
from .memory import Memory
from .models import Analysis


ANALYZE_PROMPT = """You are a senior engineer about to fix a GitHub issue. BEFORE writing any code, think deeply.

Issue #{issue_number}: {issue_title}
{issue_body}

Source files:
{sources}

{past_reflections}

Generate a structured analysis in JSON:
{{
  "aspects": [
    {{
      "id": "A1",
      "emoji": "relevant emoji",
      "name": "short name",
      "why": "why this aspect matters for THIS issue",
      "ideal": "how the ideal solution performs on this aspect"
    }}
  ],
  "challenges": [
    {{
      "id": "C1",
      "name": "short name",
      "risk": "what could go wrong",
      "mitigation": "how to avoid it"
    }}
  ],
  "edge_cases": [
    {{
      "id": "E1",
      "scenario": "specific input or scenario",
      "expected": "what should happen"
    }}
  ]
}}

Rules:
- 5-10 aspects covering: correctness, test safety, minimal diff, backward compat, cross-boundary (SQL/HTML/regex), API types, imports
- 5-10 challenges covering: what could break, what traps exist, what the agent might get wrong
- 15-30 edge cases covering: boundary conditions, embedded languages, type mismatches, concurrent access, empty inputs, existing data
- CRITICAL: if the issue involves code that contains SQL strings, regex, HTML templates, or any embedded DSL, at least 3 edge cases MUST cover cross-boundary scenarios
- CRITICAL: if the issue involves an external SDK (OpenAI, requests, etc.), at least 2 edge cases MUST cover return type verification
- Think about what would make a PR reviewer reject the fix
- Think about what would make tests fail"""


class Analyzer:
    """Phase 1: generate aspects, challenges, edge cases before coding."""

    def __init__(self, client: OpenAI, memory: Memory):
        self.client = client
        self.memory = memory

    def analyze(
        self,
        issue_number: int,
        issue_title: str,
        issue_body: str,
        sources: dict[str, str],
    ) -> Analysis:
        """Generate structured analysis for the issue."""
        past = self.memory.format_for_prompt(issue_title)

        prompt = ANALYZE_PROMPT.format(
            issue_number=issue_number,
            issue_title=issue_title,
            issue_body=issue_body,
            sources=json.dumps(sources, indent=2),
            past_reflections=past,
        )

        response = self.client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE_ANALYZE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content)
        return Analysis(**data)
