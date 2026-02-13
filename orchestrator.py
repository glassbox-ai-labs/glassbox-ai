"""
Multi-agent orchestrator with parallel execution and trust-based consensus.
"""

import asyncio
import os
from typing import Dict, List, Optional, Any

from openai import AsyncOpenAI
from trust_db import TrustDB


class MultiAgentOrchestrator:
    """Orchestrates multiple AI agents with trust scoring."""
    
    def __init__(self):
        self.trust_db = TrustDB()
        self.openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Agent personas (GPT-only for MVP)
        self.personas = {
            "architect": {
                "prompt": (
                    "You are a Senior Staff Engineer at Google with 15 years of experience. "
                    "You operate in System 2 mode—deliberate, thorough, no shortcuts. "
                    "You think long-term: scalability, maintainability, future-proofing. "
                    "You ask 'what could break at scale?' before 'how do we ship.' "
                    "Provide thoughtful, architectural guidance."
                ),
                "model": "gpt-4o",
                "temperature": 0.3
            },
            "pragmatist": {
                "prompt": (
                    "You are a Senior Staff Engineer at Meta with 15 years of experience. "
                    "You focus on iterative delivery and demonstrable business value. "
                    "Ship the 80% solution today, learn from users, iterate tomorrow. "
                    "You prioritize speed and impact over perfection. "
                    "Provide practical, actionable advice."
                ),
                "model": "gpt-4o",
                "temperature": 0.5
            },
            "critic": {
                "prompt": (
                    "You are a Senior Staff QA Engineer with 15 years of experience. "
                    "You ensure systems are robust, scalable, and production-ready. "
                    "You think in edge cases, failure modes, and security issues. "
                    "You challenge assumptions and find what others miss. "
                    "Provide critical analysis and identify risks."
                ),
                "model": "gpt-4o-mini",
                "temperature": 0.4
            }
        }
    
    async def execute(
        self, 
        task: str, 
        agent_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute task across multiple agents in parallel.
        
        Args:
            task: The question or problem to analyze
            agent_names: List of agent names to use (default: all)
        
        Returns:
            Dictionary with agent_responses, consensus, and trust_scores
        """
        
        # Default to all agents if not specified
        if agent_names is None:
            agent_names = list(self.personas.keys())
        
        # Validate agent names
        invalid_agents = [a for a in agent_names if a not in self.personas]
        if invalid_agents:
            raise ValueError(f"Unknown agents: {invalid_agents}. Available: {list(self.personas.keys())}")
        
        # Create tasks for TRUE PARALLEL execution
        tasks = [self._run_agent(agent_name, task) for agent_name in agent_names]
        
        # Run all agents simultaneously
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any errors
        valid_responses = []
        for resp in responses:
            if isinstance(resp, Exception):
                print(f"⚠️  Agent error: {resp}")
            else:
                valid_responses.append(resp)
        
        if not valid_responses:
            raise RuntimeError("All agents failed to respond")
        
        # Compute weighted consensus
        consensus = self._compute_consensus(valid_responses)
        
        return {
            "agent_responses": valid_responses,
            "consensus": consensus,
            "trust_scores": {r['agent']: r['trust'] for r in valid_responses}
        }
    
    async def _run_agent(self, agent_name: str, task: str) -> Dict[str, Any]:
        """Run a single agent."""
        
        persona = self.personas[agent_name]
        trust = self.trust_db.get_trust(agent_name)
        
        try:
            # Call OpenAI API
            response = await self.openai.chat.completions.create(
                model=persona['model'],
                messages=[
                    {"role": "system", "content": persona['prompt']},
                    {"role": "user", "content": task}
                ],
                temperature=persona['temperature'],
                max_tokens=500
            )
            
            text = response.choices[0].message.content
            
            return {
                "agent": agent_name,
                "response": text,
                "trust": trust,
                "model": persona['model']
            }
            
        except Exception as e:
            raise RuntimeError(f"Agent {agent_name} failed: {str(e)}")
    
    def _compute_consensus(self, responses: List[Dict[str, Any]]) -> str:
        """
        Compute weighted consensus from agent responses.
        
        For MVP: Simply return highest-trust agent's response.
        Future: Semantic similarity + trust weighting.
        """
        
        if not responses:
            return "No consensus - all agents failed"
        
        # Find agent with highest trust
        best = max(responses, key=lambda r: r['trust'])
        
        total_trust = sum(r['trust'] for r in responses)
        avg_trust = total_trust / len(responses)
        
        return (
            f"Highest-trust agent (@{best['agent']}, trust={best['trust']:.2f}) suggests:\n\n"
            f"{best['response']}\n\n"
            f"(Average trust across {len(responses)} agents: {avg_trust:.2f})"
        )
