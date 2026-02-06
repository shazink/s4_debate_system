"""
Safety Agent for S4 Multi-Agent Debate System.
Focus: Identifies risks and potential harms.
Special Power: Can VETO decisions if risk >= 50%
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
from agents.base_agent import BaseAgent, AgentDecision

load_dotenv()


class SafetyAgent(BaseAgent):
    """
    Safety-focused agent with VETO power.
    
    Decision Policy (Pure Python):
    - VETO if risk >= 50 (SPECIAL VETO POWER - overrides all other agents)
    - WARN if 30 <= risk < 50
    - ACT if risk < 30
    
    The Safety Agent uses RISK as primary metric, not confidence.
    """
    
    def __init__(self):
        self.name = "Safety Agent"
        self.last_decision = None
        self._configure_groq()
        
    def _configure_groq(self):
        """Configure Groq with API key."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        self.client = Groq(api_key=api_key)
        self.model_name = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    
    def _call_llm(self, prompt: str) -> str:
        """Make API call to Groq."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are the Safety Agent in a multi-agent debate system. You have VETO power and prioritize risk mitigation above all else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Very conservative for safety
            max_tokens=1024
        )
        return response.choices[0].message.content
    
    def analyze(self, query: str) -> AgentDecision:
        """
        Analyze the query focusing on safety and potential risks.
        Uses LLM for analysis, but decision policy is in pure Python.
        """
        prompt = f"""Analyze this query from a SAFETY perspective (risk assessment, harm prevention):

Query: "{query}"

Provide your analysis in JSON format:
{{
"confidence": <0-100 float - confidence that we can respond safely>,
"risk": <0-100 float - CRITICAL - potential harm/risk level>,
"reasoning": "<brief explanation of safety concerns and risks>"
}}

Focus on: What could go wrong? Who might be harmed? What are the edge cases? Be paranoid."""

        result = self._call_llm(prompt)
        
        # Parse LLM response
        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result)
            confidence = float(data["confidence"])
            risk = float(data["risk"])
            reasoning = data["reasoning"]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            confidence = 30.0
            risk = 75.0  # Conservative - assume higher risk on parse failure
            reasoning = f"Analysis failed to parse: {str(e)}. Raw: {result[:200]}"
        
        # PURE PYTHON DECISION POLICY (transparent, auditable)
        # Safety agent uses RISK to decide, with VETO power
        if risk >= 50:
            decision = "VETO"  # Special VETO decision
        elif risk >= 30:
            decision = "WARN"
        else:
            decision = "ACT"
        
        result = AgentDecision(
            confidence=confidence,
            risk=risk,
            decision=decision,
            reasoning=reasoning
        )
        
        # Store for later rounds
        self.last_decision = result
        return result
    
    def challenge(self, query: str, other_decisions: dict) -> str:
        """Generate challenges to other agents' positions."""
        prompt = f"""You are the Safety Agent with VETO power challenging other agents' positions.

Query: "{query}"

Other agents' reasoning:
{other_decisions}

As the Safety Agent (focused on risk mitigation and harm prevention), identify:
1. What safety risks are they underestimating?
2. What vulnerable populations might be harmed?
3. What edge cases could lead to serious negative outcomes?

Provide a brief, pointed challenge (2-3 sentences)."""

        return self._call_llm(prompt)
    
    def revise(self, query: str, original_decision: AgentDecision, challenges: str) -> AgentDecision:
        """Revise decision based on challenges from other agents."""
        prompt = f"""You are the Safety Agent with VETO power. Reconsider your original analysis.

Query: "{query}"

Your Original Decision:
- Confidence: {original_decision.confidence}
- Risk: {original_decision.risk}
- Decision: {original_decision.decision}
- Reasoning: {original_decision.reasoning}

Challenges from other agents:
{challenges}

Provide REVISED analysis in JSON format:
{{
"confidence": <0-100 float>,
"risk": <0-100 float - BE CONSERVATIVE>,
"reasoning": "<updated reasoning incorporating challenges>"
}}

Have the challenges changed your risk assessment? Remember: you have VETO power."""

        result = self._call_llm(prompt)
        
        # Parse revised analysis
        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result)
            confidence = float(data["confidence"])
            risk = float(data["risk"])
            reasoning = data["reasoning"]
        except (json.JSONDecodeError, KeyError, ValueError):
            return original_decision
        
        # Apply same decision policy
        if risk >= 50:
            decision = "VETO"
        elif risk >= 30:
            decision = "WARN"
        else:
            decision = "ACT"
        
        return AgentDecision(
            confidence=confidence,
            risk=risk,
            decision=decision,
            reasoning=reasoning
        )
