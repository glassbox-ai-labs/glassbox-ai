"""Multi-agent orchestrator with parallel execution and multi-round debate."""

import asyncio, os
from typing import List, Optional
from openai import AsyncOpenAI
from .trust_db import TrustDB

AGENTS = {
    "architect": ("gpt-4o", 0.3, "You are @architect. Think long-term, scalability, what breaks at scale. In debates: reference @pragmatist/@critic by name, agree/disagree explicitly. Be concise, opinionated."),
    "pragmatist": ("gpt-4o", 0.5, "You are @pragmatist. Ship fast, iterate. In debates: reference @architect/@critic by name, push back on overengineering. Be concise, opinionated."),
    "critic":     ("gpt-4o-mini", 0.4, "You are @critic. Edge cases, failure modes, security. In debates: reference @architect/@pragmatist by name, challenge assumptions. Be concise, opinionated."),
}
ROUNDS = ["ROUND 1: State your position.", "ROUND 2: React to others. Agree/disagree with @names.", "ROUND 3: Final position. Say if you changed your mind and why. Converge."]
EMOJIS = {"architect": "🔵", "pragmatist": "🟢", "critic": "🟡"}


class MultiAgentOrchestrator:
    def __init__(self):
        self.trust_db = TrustDB()
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return self._client

    async def _ask(self, agent, system, user_msg):
        try:
            model, temp, _ = AGENTS[agent]
            r = await self.client.chat.completions.create(model=model, temperature=temp, max_tokens=400, messages=[{"role": "system", "content": system}, {"role": "user", "content": user_msg}])
            return r.choices[0].message.content
        except Exception as e:
            return f"[ERROR: {agent} failed — {type(e).__name__}: {e}]"

    # ── V1: parallel single-shot ──

    async def execute(self, task, agent_names=None):
        agents = agent_names or list(AGENTS.keys())
        async def run(a): return {"agent": a, "response": await self._ask(a, AGENTS[a][2], task), "trust": self.trust_db.get_trust(a), "model": AGENTS[a][0]}
        responses = [r for r in await asyncio.gather(*[run(a) for a in agents if a in AGENTS], return_exceptions=True) if not isinstance(r, Exception)]
        best = max(responses, key=lambda r: r["trust"])
        return {"agent_responses": responses, "consensus": best["response"], "trust_scores": {r["agent"]: r["trust"] for r in responses}}

    async def execute_formatted(self, task, agent_names=None):
        result = await self.execute(task, agent_names)
        lines = [f"Task: {task}\n"] + [f"@{r['agent']} (trust:{r['trust']:.2f}):\n{r['response']}\n" for r in result["agent_responses"]]
        return "\n".join(lines + [f"--- Consensus (highest trust) ---\n{result['consensus']}"])

    # ── V2: multi-round debate (the 20 lines) ──

    async def debate(self, task, agents=None):
        agents = [a for a in (agents or list(AGENTS.keys())) if a in AGENTS]
        log, out = [], [f"━━ TOPIC ━━\n{task}\n"]
        for i, rd in enumerate(ROUNDS):
            out.append(f"━━ {rd.split(':')[0]} ━━\n")
            for a in agents:
                history = "\n".join(f"{EMOJIS[e['a']]} @{e['a']}: {e['t']}" for e in log) if log else "(no prior messages)"
                text = await self._ask(a, AGENTS[a][2], f"TASK: {task}\n\nConversation so far:\n{history}\n\n{rd}\n\nRespond as @{a}:")
                log.append({"a": a, "r": i, "t": text})
                out.append(f"{EMOJIS[a]} @{a} (trust:{self.trust_db.get_trust(a):.2f}):\n{text}\n")
        transcript = "\n".join(f"@{e['a']}: {e['t']}" for e in log)
        summary = await self._ask("architect", "Summarize this debate into a converged action plan. Be concise.", f"Task: {task}\n\n{transcript}\n\nConverged action plan:")
        out.append(f"━━ CONVERGENCE ━━\n{summary}")
        for e in log:
            if e["r"] == len(ROUNDS) - 1:
                for other in agents:
                    if other != e["a"] and f"@{other}" in e["t"].lower() and any(p in e["t"].lower() for p in ["agree", "fair point", "changed", "i accept", "good point", "i now"]):
                        self.trust_db.update_trust(other, True)
                        out.append(f"  @{other} ↑ {self.trust_db.get_trust(other):.2f} (persuaded @{e['a']})")
        return "\n".join(out)
