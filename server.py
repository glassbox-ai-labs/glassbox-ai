"""
GlassBox AI - MCP Server
Multi-agent orchestration with transparent trust scoring.
Uses FastMCP (Model Context Protocol SDK).
"""

import asyncio
import os
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from orchestrator import MultiAgentOrchestrator

load_dotenv()

mcp = FastMCP("GlassBox AI", json_response=True)
orchestrator = MultiAgentOrchestrator()


@mcp.tool()
async def multi_agent_analyze(task: str, agents: Optional[str] = None) -> str:
    """Analyze a task using multiple AI agents in parallel with trust-weighted consensus.
    
    Args:
        task: The task, question, or problem to analyze
        agents: Comma-separated agent names (default: all). Options: architect, pragmatist, critic
    """
    agent_list = [a.strip() for a in agents.split(",")] if agents else None

    result = await orchestrator.execute(task, agent_list)

    output = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 MULTI-AGENT ANALYSIS

Task: {task}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    for resp in result["agent_responses"]:
        emoji = {"architect": "🔵", "pragmatist": "🟢", "critic": "🟡"}.get(resp["agent"], "⚪")
        trust_bar = "█" * int(resp["trust"] * 10)
        text = resp["response"][:300] + ("..." if len(resp["response"]) > 300 else "")

        output += f"""
{emoji} @{resp['agent']} (Trust: {resp['trust']:.2f} {trust_bar})
   Model: {resp['model']}
   {text}
"""

    output += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️ WEIGHTED CONSENSUS

{result['consensus']}

Trust Distribution:
"""
    for agent, trust in result["trust_scores"].items():
        bars = "█" * int(trust * 20)
        output += f"  {agent:12} {trust:.2f} {bars}\n"

    output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    return output


@mcp.tool()
def get_trust_scores() -> str:
    """View current trust scores for all agents."""
    scores = orchestrator.trust_db.get_all_scores()

    output = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 AGENT TRUST SCORES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for agent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        bars = "█" * int(score * 20)
        emoji = {"architect": "🔵", "pragmatist": "🟢", "critic": "🟡"}.get(agent, "⚪")
        output += f"{emoji} {agent:12} {score:.2f} {bars}\n"

    output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    return output


@mcp.tool()
def update_trust(agent: str, was_correct: bool) -> str:
    """Update an agent's trust score based on real-world outcome.
    
    Args:
        agent: Agent name (architect, pragmatist, or critic)
        was_correct: True if agent's answer was correct, False if wrong
    """
    orchestrator.trust_db.update_trust(agent, was_correct)
    new_score = orchestrator.trust_db.get_trust(agent)

    emoji = "✅" if was_correct else "❌"
    direction = "↑" if was_correct else "↓"
    return f"{emoji} Updated {agent}: Trust = {new_score:.2f} {direction}"


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not set")
        print("   Create .env file with: OPENAI_API_KEY=sk-...")
        exit(1)

    mcp.run(transport="stdio")
