"""Debate package for S4 Multi-Agent Debate System."""
from .protocol import DebateProtocol
from .decision_rules import DecisionRules, FinalDecision

__all__ = ['DebateProtocol', 'DecisionRules', 'FinalDecision']
