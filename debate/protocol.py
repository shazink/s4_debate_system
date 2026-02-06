"""
Debate protocol implementation.
Manages the mandatory debate rounds: Initial → Challenge → Revision → Voting
"""

from typing import List, Dict, Tuple
from agents.base_agent import BaseAgent, AgentDecision
from utils.logger import DebateLogger


class DebateProtocol:
    """Orchestrates the mandatory debate process."""
    
    def __init__(self, agents: List[BaseAgent], logger: DebateLogger):
        """
        Initialize debate protocol.
        
        Args:
            agents: List of analytical agents (Utility, Accuracy, Safety)
            logger: Logger for tracking debate
        """
        self.agents = agents
        self.logger = logger
    
    def run(self, query: str) -> Tuple[List[AgentDecision], List[str]]:
        """
        Run the complete debate protocol.
        
        Args:
            query: The input query
            
        Returns:
            Tuple of (final_votes, agent_names)
        """
        # Start logging
        self.logger.start_debate(query)
        
        # Round 1: Initial Analysis
        print("\n" + "="*80)
        print("ROUND 1: INITIAL ANALYSIS")
        print("="*80)
        initial_decisions = self._run_initial_round(query)
        
        # Round 2: Challenge (MANDATORY)
        print("\n" + "="*80)
        print("ROUND 2: CHALLENGE ROUND (MANDATORY)")
        print("="*80)
        challenges = self._run_challenge_round(query, initial_decisions)
        
        # Round 3: Revision
        print("\n" + "="*80)
        print("ROUND 3: REVISION")
        print("="*80)
        revised_decisions = self._run_revision_round(query, challenges)
        
        # Round 4: Final Voting
        print("\n" + "="*80)
        print("ROUND 4: FINAL VOTING")
        print("="*80)
        final_votes = self._collect_final_votes(revised_decisions)
        
        agent_names = [agent.name for agent in self.agents]
        return final_votes, agent_names
    
    def _run_initial_round(self, query: str) -> Dict[str, AgentDecision]:
        """Run initial analysis round - all agents analyze independently."""
        initial_decisions = {}
        
        for agent in self.agents:
            print(f"\n🤖 {agent.name} analyzing...")
            decision = agent.analyze(query)
            initial_decisions[agent.name] = decision
            
            # Log decision
            self.logger.log_initial_decision(
                agent_name=agent.name,
                confidence=decision.confidence,
                risk=decision.risk,
                decision=decision.decision,
                reasoning=decision.reasoning
            )
        
        return initial_decisions
    
    def _run_challenge_round(self, query: str, 
                            initial_decisions: Dict[str, AgentDecision]) -> Dict[str, List[str]]:
        """
        Run challenge round - each agent challenges others.
        MANDATORY - even if all agents agree.
        """
        challenges = {agent.name: [] for agent in self.agents}
        
        for challenger in self.agents:
            for challenged in self.agents:
                if challenger.name != challenged.name:
                    print(f"\n⚔️  {challenger.name} challenging {challenged.name}...")
                    
                    # Get the challenge
                    challenged_reasoning = initial_decisions[challenged.name].reasoning
                    challenge = challenger.challenge(query, challenged_reasoning)
                    
                    # Store challenge
                    challenges[challenged.name].append(
                        f"[{challenger.name}]: {challenge}"
                    )
                    
                    # Log challenge
                    self.logger.log_challenge(
                        challenger=challenger.name,
                        challenged_agent=challenged.name,
                        challenge=challenge
                    )
        
        return challenges
    
    def _run_revision_round(self, query: str, 
                           challenges: Dict[str, List[str]]) -> Dict[str, AgentDecision]:
        """Run revision round - agents revise based on challenges."""
        revised_decisions = {}
        
        for agent in self.agents:
            print(f"\n🔄 {agent.name} revising...")
            
            # Get all challenges for this agent
            agent_challenges = "\n".join(challenges[agent.name])
            
            # Get original decision
            original = agent.last_decision
            
            # Revise
            revised = agent.revise(query, original, agent_challenges)
            revised_decisions[agent.name] = revised
            
            # Log revision
            self.logger.log_revision(
                agent_name=agent.name,
                old_confidence=original.confidence,
                new_confidence=revised.confidence,
                old_risk=original.risk,
                new_risk=revised.risk,
                old_decision=original.decision,
                new_decision=revised.decision,
                reason=revised.reasoning
            )
        
        return revised_decisions
    
    def _collect_final_votes(self, revised_decisions: Dict[str, AgentDecision]) -> List[AgentDecision]:
        """Collect final votes from all agents."""
        final_votes = []
        
        for agent in self.agents:
            decision = revised_decisions[agent.name]
            final_votes.append(decision)
            
            # Log final vote
            self.logger.log_final_vote(
                agent_name=agent.name,
                confidence=decision.confidence,
                risk=decision.risk,
                decision=decision.decision
            )
        
        return final_votes
