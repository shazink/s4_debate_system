"""
Utility Agent for S4 Multi-Agent Debate System.
Focus: Action-oriented, prioritizes getting things done.
Policy: ACT if confidence >= 60%
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
from agents.base_agent import BaseAgent, AgentDecision

load_dotenv()


class UtilityAgent(BaseAgent):
    """
    Utility-focused agent that prioritizes action and practical outcomes.
    
    Decision Policy (Pure Python):
    - ACT if analysis_confidence >= 60
    - WARN if 40 <= analysis_confidence < 60
    - REFUSE if analysis_confidence < 40
    """
    
    def __init__(self):
        self.name = "Utility Agent"
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
                {"role": "system", "content": "You are the Utility Agent in a multi-agent debate system. You prioritize practical action and getting things done."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    
    def analyze(self, query: str) -> AgentDecision:
        """
        Analyze the query and return initial decision.
        Uses LLM for analysis, but decision policy is in pure Python.
        """
        prompt = f"""Analyze this query from a UTILITY perspective (action-oriented, practical outcomes):

Query: "{query}"

Provide your analysis in JSON format:
{{
"confidence": <0-100 float representing confidence in taking action>,
"risk": <0-100 float representing risk level>,
"reasoning": "<brief explanation of your utility-focused assessment>"
}}

Focus on: Can we act on this? Is it actionable? What's the practical benefit?"""

        result = self._call_llm(prompt)
        
        # Parse LLM response (expects JSON)
        try:
            # Extract JSON if wrapped in code blocks
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result)
            confidence = float(data["confidence"])
            risk = float(data["risk"])
            reasoning = data["reasoning"]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback if JSON parsing fails
            confidence = 50.0
            risk = 50.0
            reasoning = f"Analysis failed to parse: {str(e)}. Raw: {result[:200]}"
        
        # PURE PYTHON DECISION POLICY (transparent, auditable)
        if confidence >= 60:
            decision = "ACT"
        elif confidence >= 40:
            decision = "WARN"
        else:
            decision = "REFUSE"
        
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
        prompt = f"""You are the Utility Agent challenging other agents' positions.

Query: "{query}"

Other agents' reasoning:
{other_decisions}

As the Utility Agent (focused on action and practical outcomes), identify:
1. What concerns or flaws do you see in their reasoning?
2. What practical considerations are they missing?
3. How might their caution prevent valuable action?

Provide a brief, pointed challenge (2-3 sentences)."""

        return self._call_llm(prompt)
    
    def revise(self, query: str, original_decision: AgentDecision, challenges: str) -> AgentDecision:
        """Revise decision based on challenges from other agents."""
        prompt = f"""You are the Utility Agent. Reconsider your original analysis.

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
"risk": <0-100 float>,
"reasoning": "<updated reasoning incorporating challenges>"
}}

Have the challenges changed your assessment? Be honest."""

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
            # Keep original if parsing fails
            return original_decision
        
        # Apply same decision policy
        if confidence >= 60:
            decision = "ACT"
        elif confidence >= 40:
            decision = "WARN"
        else:
            decision = "REFUSE"
        
        return AgentDecision(
            confidence=confidence,
            risk=risk,
            decision=decision,
            reasoning=reasoning
        )
