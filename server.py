"""
GlassBox AI - MCP Server
Multi-agent orchestration with transparent trust scoring.
"""

import asyncio
import json
import os
from typing import Any, Dict, List

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
except ImportError:
    print("ERROR: MCP library not installed. Run: pip install mcp")
    exit(1)

from orchestrator import MultiAgentOrchestrator

# Initialize MCP server
app = Server("glassbox-ai")
orchestrator = MultiAgentOrchestrator()


@app.list_tools()
async def list_tools() -> List[Dict[str, Any]]:
    """List available tools for Windsurf/MCP clients."""
    return [
        {
            "name": "multi_agent_analyze",
            "description": "Analyze a task using multiple AI agents in parallel with trust-weighted consensus",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task, question, or problem to analyze"
                    },
                    "agents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agents to use (default: all available)",
                        "default": None
                    }
                },
                "required": ["task"]
            }
        },
        {
            "name": "get_trust_scores",
            "description": "View current trust scores for all agents with history",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "update_trust",
            "description": "Manually update an agent's trust score based on real-world outcome",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent name (architect, pragmatist, or critic)"
                    },
                    "was_correct": {
                        "type": "boolean",
                        "description": "True if agent's answer was correct, False if wrong"
                    }
                },
                "required": ["agent", "was_correct"]
            }
        }
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, str]]:
    """Handle tool calls from MCP clients."""
    
    if name == "multi_agent_analyze":
        task = arguments.get("task")
        agent_names = arguments.get("agents")
        
        if not task:
            return [{"type": "text", "text": "❌ Error: 'task' parameter required"}]
        
        # Execute multi-agent analysis
        try:
            result = await orchestrator.execute(task, agent_names)
            
            # Format for display
            output = format_analysis_result(task, result)
            return [{"type": "text", "text": output}]
            
        except Exception as e:
            return [{"type": "text", "text": f"❌ Error during analysis: {str(e)}"}]
    
    elif name == "get_trust_scores":
        scores = orchestrator.trust_db.get_all_scores()
        output = format_trust_scores(scores)
        return [{"type": "text", "text": output}]
    
    elif name == "update_trust":
        agent = arguments.get("agent")
        was_correct = arguments.get("was_correct")
        
        if not agent:
            return [{"type": "text", "text": "❌ Error: 'agent' parameter required"}]
        
        try:
            orchestrator.trust_db.update_trust(agent, was_correct)
            new_score = orchestrator.trust_db.get_trust(agent)
            
            emoji = "✅" if was_correct else "❌"
            direction = "↑" if was_correct else "↓"
            
            return [{
                "type": "text",
                "text": f"{emoji} Updated {agent}: Trust = {new_score:.2f} {direction}"
            }]
        except Exception as e:
            return [{"type": "text", "text": f"❌ Error updating trust: {str(e)}"}]
    
    else:
        return [{"type": "text", "text": f"❌ Unknown tool: {name}"}]


def format_analysis_result(task: str, result: Dict[str, Any]) -> str:
    """Format multi-agent analysis result for display."""
    
    output = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 MULTI-AGENT ANALYSIS

Task: {task}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agent Responses:
"""
    
    for resp in result['agent_responses']:
        emoji = {"architect": "🔵", "pragmatist": "🟢", "critic": "🟡"}.get(resp['agent'], "⚪")
        trust_bar = "█" * int(resp['trust'] * 10)
        
        output += f"""
{emoji} @{resp['agent']} (Trust: {resp['trust']:.2f} {trust_bar})
   Model: {resp['model']}
   
   {resp['response'][:300]}{"..." if len(resp['response']) > 300 else ""}

"""
    
    output += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️ WEIGHTED CONSENSUS

{result['consensus']}

Trust Distribution:
"""
    
    for agent, trust in result['trust_scores'].items():
        bars = "█" * int(trust * 20)
        output += f"  {agent:12} {trust:.2f} {bars}\n"
    
    output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    return output


def format_trust_scores(scores: Dict[str, float]) -> str:
    """Format trust scores for display."""
    
    output = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 AGENT TRUST SCORES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for agent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        bars = "█" * int(score * 20)
        emoji = {"architect": "🔵", "pragmatist": "🟢", "critic": "🟡"}.get(agent, "⚪")
        
        output += f"{emoji} {agent:12} {score:.2f} {bars}\n"
    
    output += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Tip: Use update_trust to adjust scores based on outcomes
"""
    
    return output


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not set in environment")
        print("   Set it in .env file or export OPENAI_API_KEY=sk-...")
        exit(1)
    
    print("🚀 GlassBox AI MCP Server starting...")
    print("   Agents: architect, pragmatist, critic")
    print("   Ready for Windsurf integration")
    
    asyncio.run(stdio_server(app))
