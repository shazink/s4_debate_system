"""
Accuracy Agent for S4 Multi-Agent Debate System.
Focus: Verifies correctness and factual accuracy.
Policy: HIGH bar - ACT only if confidence >= 85%
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
from agents.base_agent import BaseAgent, AgentDecision

load_dotenv()


class AccuracyAgent(BaseAgent):
    """
    Accuracy-focused agent that prioritizes correctness over speed.
    
    Decision Policy (Pure Python):
    - ACT if analysis_confidence >= 85 (HIGH BAR - naturally skeptical)
    - WARN if 60 <= analysis_confidence < 85
    - REFUSE if analysis_confidence < 60
    """
    
    def __init__(self):
        self.name = "Accuracy Agent"
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
                {"role": "system", "content": "You are the Accuracy Agent in a multi-agent debate system. You prioritize factual correctness and are naturally skeptical."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,  # Lower temperature for accuracy
            max_tokens=1024
        )
        return response.choices[0].message.content
    
    def analyze(self, query: str) -> AgentDecision:
        """
        Analyze the query focusing on accuracy and factual correctness.
        Uses LLM for analysis, but decision policy is in pure Python.
        """
        prompt = f"""Analyze this query from an ACCURACY perspective (fact-checking, correctness):

Query: "{query}"

Provide your analysis in JSON format:
{{
"confidence": <0-100 float - how confident are you in the accuracy of potential responses?>,
"risk": <0-100 float - risk of providing inaccurate information>,
"reasoning": "<brief explanation of your accuracy assessment>"
}}

Focus on: Is this factually verifiable? Are there risks of misinformation? How certain can we be?"""

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
            confidence = 50.0
            risk = 70.0
            reasoning = f"Analysis failed to parse: {str(e)}. Raw: {result[:200]}"
        
        # PURE PYTHON DECISION POLICY (transparent, auditable)
        # Accuracy agent has HIGH bar for ACT (85%)
        if confidence >= 85:
            decision = "ACT"
        elif confidence >= 60:
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
        prompt = f"""You are the Accuracy Agent challenging other agents' positions.

Query: "{query}"

Other agents' reasoning:
{other_decisions}

As the Accuracy Agent (focused on factual correctness), identify:
1. What accuracy concerns do you have with their reasoning?
2. What facts might they be overlooking or misrepresenting?
3. Where might they be overconfident without sufficient evidence?

Provide a brief, pointed challenge (2-3 sentences)."""

        return self._call_llm(prompt)
    
    def revise(self, query: str, original_decision: AgentDecision, challenges: str) -> AgentDecision:
        """Revise decision based on challenges from other agents."""
        prompt = f"""You are the Accuracy Agent. Reconsider your original analysis.

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

Have the challenges changed your accuracy assessment? Be honest."""

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
        if confidence >= 85:
            decision = "ACT"
        elif confidence >= 60:
            decision = "WARN"
        else:
            decision = "REFUSE"
        
        return AgentDecision(
            confidence=confidence,
            risk=risk,
            decision=decision,
            reasoning=reasoning
        )
