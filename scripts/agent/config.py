"""GlassBox Agent - configuration and constants. Single source of truth."""

import os

AGENT_NAME = "GlassBox Agent"
AGENT_VERSION = "v0.3-beta"
AGENT_LABEL = f"{AGENT_NAME} {AGENT_VERSION}"

REPO = os.environ.get("GITHUB_REPOSITORY", "agentic-trust-labs/glassbox-ai")

MAX_RETRIES = 2

MODEL = "gpt-4o"
TEMPERATURE_ANALYZE = 0.3
TEMPERATURE_CODE = 0.1
TEMPERATURE_REVIEW = 0.3

SOURCE_FILES = [
    "src/glassbox/__init__.py",
    "src/glassbox/server.py",
    "src/glassbox/orchestrator.py",
    "src/glassbox/trust_db.py",
    "tests/test_glassbox.py",
]

DEBATE_AGENTS = {
    "architect": "Check correctness. Will SQL strings, imports, or runtime behavior break? Grade every aspect, challenge, and edge case.",
    "pragmatist": "Is this the minimal change? Any over-engineering? Grade every aspect, challenge, and edge case.",
    "critic": "Find flaws. Are Python variables leaking into SQL/HTML/regex? Try to BREAK the fix. Grade every aspect, challenge, and edge case.",
}

REFLECTIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "reflections.json")
