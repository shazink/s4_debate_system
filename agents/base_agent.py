"""
Abstract base class for all agents in the S4 Multi-Agent Debate System.

All agents must implement:
- analyze(): Make initial decision
- challenge(): Generate challenges to other agents
- revise(): Revise decision based on challenges
- vote(): Cast final vote

Decision policies are implemented in pure Python within each agent.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AgentDecision:
    """Structured output from agent analysis."""
    confidence: float  # 0-100
    risk: float  # 0-100
    decision: str  # ACT, WARN, REFUSE, or VETO
    reasoning: str


class BaseAgent(ABC):
    """Base class for all analytical agents."""
    
    @abstractmethod
    def analyze(self, query: str) -> AgentDecision:
        """Analyze query and return initial decision."""
        pass
    
    @abstractmethod
    def challenge(self, query: str, other_decisions: dict) -> str:
        """Generate challenges to other agents' positions."""
        pass
    
    @abstractmethod
    def revise(self, query: str, original_decision: AgentDecision, challenges: str) -> AgentDecision:
        """Revise decision based on challenges."""
        pass

