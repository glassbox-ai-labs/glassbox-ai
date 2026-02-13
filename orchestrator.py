"""Multi-agent orchestrator with parallel execution and trust-based consensus."""

import asyncio, os
from typing import List, Optional
from openai import AsyncOpenAI
from trust_db import TrustDB

PERSONAS = {
    "architect": {
        "prompt": "You are a Senior Staff Engineer. Think long-term: scalability, maintainability. Ask 'what could break at scale?' Be concise.",
        "model": "gpt-4o", "temperature": 0.3,
    },
    "pragmatist": {
        "prompt": "You are a Senior Staff Engineer. Ship the 80% solution today, iterate tomorrow. Prioritize speed and impact. Be concise.",
        "model": "gpt-4o", "temperature": 0.5,
    },
    "critic": {
        "prompt": "You are a Senior QA Engineer. Think in edge cases, failure modes, security. Challenge assumptions. Be concise.",
        "model": "gpt-4o-mini", "temperature": 0.4,
    },
}


class MultiAgentOrchestrator:
    def __init__(self):
        self.trust_db = TrustDB()
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def execute(self, task: str, agent_names: Optional[List[str]] = None):
        agents = agent_names or list(PERSONAS.keys())
        tasks = [self._run(name, task) for name in agents if name in PERSONAS]
        responses = [r for r in await asyncio.gather(*tasks, return_exceptions=True) if not isinstance(r, Exception)]
        best = max(responses, key=lambda r: r["trust"])
        return {"agent_responses": responses, "consensus": best["response"], "trust_scores": {r["agent"]: r["trust"] for r in responses}}

    async def execute_formatted(self, task: str, agent_names: Optional[List[str]] = None) -> str:
        result = await self.execute(task, agent_names)
        lines = [f"Task: {task}\n"]
        for r in result["agent_responses"]:
            lines.append(f"@{r['agent']} (trust:{r['trust']:.2f}):\n{r['response']}\n")
        lines.append(f"--- Consensus (highest trust) ---\n{result['consensus']}")
        return "\n".join(lines)

    async def _run(self, name: str, task: str):
        p = PERSONAS[name]
        resp = await self.client.chat.completions.create(
            model=p["model"], temperature=p["temperature"], max_tokens=500,
            messages=[{"role": "system", "content": p["prompt"]}, {"role": "user", "content": task}],
        )
        return {"agent": name, "response": resp.choices[0].message.content, "trust": self.trust_db.get_trust(name), "model": p["model"]}
