"""
Decision rules for the S4 Multi-Agent Debate System.
Pure Python logic - NO LLM involvement.
"""

from typing import List, Dict, Any
from agents.base_agent import AgentDecision


class FinalDecision:
    """Final system decision with reasoning."""
    
    def __init__(self, decision: str, reasoning: str, metadata: Dict[str, Any] = None):
        self.decision = decision  # ACT, WARN, REFUSE
        self.reasoning = reasoning
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"FinalDecision(decision={self.decision}, reasoning={self.reasoning})"


class DecisionRules:
    """
    Applies decision rules in exact order.
    This is PURE PYTHON - no LLM decision making.
    """
    
    @staticmethod
    def apply(votes: List[AgentDecision], agent_names: List[str]) -> FinalDecision:
        """
        Apply decision rules in exact order:
        1. Safety veto overrides everything
        2. Low confidence threshold (< 40)
        3. Low agreement (< 60%)
        4. Medium agreement (60-80%)
        5. High agreement (> 80%) with low risk (< 30)
        
        Args:
            votes: List of final agent decisions
            agent_names: List of agent names (same order as votes)
            
        Returns:
            FinalDecision object
        """
        
        # Rule 1: Safety veto overrides everything
        for i, vote in enumerate(votes):
            if vote.decision == "VETO":
                return FinalDecision(
                    decision="REFUSE",
                    reasoning=f"Safety veto applied by {agent_names[i]}. Reason: {vote.reasoning}",
                    metadata={
                        "rule_applied": "safety_veto",
                        "veto_agent": agent_names[i],
                        "veto_risk": vote.risk
                    }
                )
        
        # Rule 2: Low confidence threshold
        for i, vote in enumerate(votes):
            if vote.confidence < 40:
                return FinalDecision(
                    decision="REFUSE",
                    reasoning=f"{agent_names[i]} has very low confidence ({vote.confidence:.1f}%). "
                             f"Cannot proceed with confidence below 40%. Reason: {vote.reasoning}",
                    metadata={
                        "rule_applied": "low_confidence",
                        "min_confidence": vote.confidence,
                        "low_confidence_agent": agent_names[i]
                    }
                )
        
        # Calculate agreement and risk metrics
        act_votes = sum(1 for v in votes if v.decision == "ACT")
        total_votes = len(votes)
        agreement_pct = (act_votes / total_votes) * 100
        max_risk = max(v.risk for v in votes)
        avg_confidence = sum(v.confidence for v in votes) / total_votes
        
        # Rule 3: Low agreement
        if agreement_pct < 60:
            disagree_agents = [agent_names[i] for i, v in enumerate(votes) if v.decision != "ACT"]
            return FinalDecision(
                decision="REFUSE",
                reasoning=f"Insufficient agreement ({agreement_pct:.1f}%). "
                         f"Agents in disagreement: {', '.join(disagree_agents)}. "
                         f"At least 60% agreement required.",
                metadata={
                    "rule_applied": "low_agreement",
                    "agreement_percentage": agreement_pct,
                    "disagreeing_agents": disagree_agents
                }
            )
        
        # Rule 4: Medium agreement (60-80%)
        if 60 <= agreement_pct <= 80:
            return FinalDecision(
                decision="WARN",
                reasoning=f"Moderate agreement ({agreement_pct:.1f}%) with mixed confidence. "
                         f"Average confidence: {avg_confidence:.1f}%, Max risk: {max_risk:.1f}%. "
                         f"Proceeding with caution - REVIEW CAREFULLY.",
                metadata={
                    "rule_applied": "medium_agreement",
                    "agreement_percentage": agreement_pct,
                    "avg_confidence": avg_confidence,
                    "max_risk": max_risk
                }
            )
        
        # Rule 5: High agreement with acceptable risk
        if agreement_pct > 80 and max_risk < 30:
            return FinalDecision(
                decision="ACT",
                reasoning=f"Strong agreement ({agreement_pct:.1f}%) with acceptable risk. "
                         f"Average confidence: {avg_confidence:.1f}%, Max risk: {max_risk:.1f}%. "
                         f"Safe to proceed.",
                metadata={
                    "rule_applied": "high_agreement_low_risk",
                    "agreement_percentage": agreement_pct,
                    "avg_confidence": avg_confidence,
                    "max_risk": max_risk
                }
            )
        
        # Fallback: High agreement but elevated risk
        return FinalDecision(
            decision="WARN",
            reasoning=f"High agreement ({agreement_pct:.1f}%) but elevated risk ({max_risk:.1f}%). "
                     f"Average confidence: {avg_confidence:.1f}%. "
                     f"Proceed with extreme caution.",
            metadata={
                "rule_applied": "high_agreement_high_risk",
                "agreement_percentage": agreement_pct,
                "avg_confidence": avg_confidence,
                "max_risk": max_risk
            }
        )
