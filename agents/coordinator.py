"""
Coordinator - Pure Python orchestration (NO LLM).
Runs debate and applies decision rules.
"""

from typing import Dict, Any
from agents import UtilityAgent, AccuracyAgent, SafetyAgent
from debate import DebateProtocol, DecisionRules, FinalDecision
from utils import DebateLogger, AttackDetector, ConfidenceValidator, FALLBACK_RESPONSES


class DebateResult:
    """Result of the debate process."""
    
    def __init__(self, final_decision: FinalDecision, debate_summary: Dict[str, Any]):
        self.final_decision = final_decision.decision
        self.reasoning = final_decision.reasoning
        self.metadata = final_decision.metadata
        self.debate_summary = debate_summary
    
    def __repr__(self):
        return (f"DebateResult(decision={self.final_decision}, "
                f"reasoning={self.reasoning[:50]}...)")


class Coordinator:
    """
    Pure Python coordinator - NO LLM.
    Orchestrates agents, debate, and applies decision rules.
    """
    
    def __init__(self, save_logs: bool = True):
        """
        Initialize coordinator.
        
        Args:
            save_logs: Whether to save logs to file
        """
        # Initialize agents
        self.utility_agent = UtilityAgent()
        self.accuracy_agent = AccuracyAgent()
        self.safety_agent = SafetyAgent()
        
        # Store in list for iteration
        self.agents = [
            self.utility_agent,
            self.accuracy_agent,
            self.safety_agent
        ]
        
        # Initialize logger
        self.logger = DebateLogger(save_to_file=save_logs)
        
        # Initialize attack detector
        self.attack_detector = AttackDetector()
        self.confidence_validator = ConfidenceValidator()
        
        # Initialize debate protocol
        self.debate_protocol = DebateProtocol(self.agents, self.logger)
    
    def run_debate(self, query: str) -> DebateResult:
        """
        Run the complete debate process and return final decision.
        
        Args:
            query: The input query to analyze
            
        Returns:
            DebateResult with final decision and reasoning
        """
        print("\n" + "🎯"*40)
        print(f"QUERY: {query}")
        print("🎯"*40)
        
        # ATTACK DEFENSE: Validate input before processing
        print("\n🛡️  ATTACK DEFENSE: Validating input...")
        validation_result = self.attack_detector.validate_input(query)
        
        if not validation_result['is_valid']:
            # Input failed validation - return defensive response
            print(f"⚠️  SECURITY ALERT: Query blocked (risk={validation_result['risk_score']}%)")
            print(f"   Issues: {validation_result['issues']}")
            
            # Determine fallback response
            if any('injection' in issue.lower() for issue in validation_result['issues']):
                response = FALLBACK_RESPONSES['prompt_injection']
            elif any('length' in issue.lower() for issue in validation_result['issues']):
                response = FALLBACK_RESPONSES['excessive_length']
            elif any('sql' in issue.lower() or 'injection' in issue.lower() for issue in validation_result['issues']):
                response = FALLBACK_RESPONSES['sql_injection']
            elif any('null' in issue.lower() for issue in validation_result['issues']):
                response = FALLBACK_RESPONSES['null_injection']
            else:
                response = FALLBACK_RESPONSES['suspicious_override']
            
            return DebateResult(
                FinalDecision(
                    decision="REFUSE",
                    reasoning=f"Security validation failed: {', '.join(validation_result['issues'])}. {response}",
                    metadata={
                        'security_block': True,
                        'risk_score': validation_result['risk_score'],
                        'issues': validation_result['issues']
                    }
                ),
                {'security_blocked': True, 'validation': validation_result}
            )
        
        print(f"✅ Input validation passed (risk={validation_result['risk_score']}%)")
        
        # Run debate protocol (all 4 rounds)
        final_votes, agent_names = self.debate_protocol.run(query)
        
        # ATTACK DEFENSE: Check for overconfident agents
        print("\n🛡️  ATTACK DEFENSE: Validating agent confidence...")
        for vote in final_votes:
            overconf_check = self.confidence_validator.check_overconfidence(
                confidence=vote.confidence,
                reasoning_length=len(vote.reasoning),
                query_length=len(query)
            )
            if overconf_check['is_suspicious']:
                print(f"⚠️  Suspicious confidence from {vote.decision}: {overconf_check['issues']}")
        
        # Check consensus quality
        consensus_check = self.confidence_validator.check_consensus_quality([
            {'confidence': v.confidence, 'decision': v.decision} for v in final_votes
        ])
        if consensus_check['is_suspicious']:
            print(f"⚠️  Suspicious consensus pattern: {consensus_check['issues']}")
        
        # Apply decision rules (PURE PYTHON)
        print("\n" + "="*80)
        print("APPLYING DECISION RULES")
        print("="*80)
        final_decision = DecisionRules.apply(final_votes, agent_names)
        
        # Log final decision
        agreement_pct = final_decision.metadata.get('agreement_percentage', 0)
        max_risk = final_decision.metadata.get('max_risk', 0)
        veto_applied = 'veto_agent' in final_decision.metadata
        
        self.logger.log_final_decision(
            decision=final_decision.decision,
            reasoning=final_decision.reasoning,
            agreement_pct=agreement_pct,
            max_risk=max_risk,
            veto_applied=veto_applied
        )
        
        # Get debate summary with all rounds
        debate_summary = self.logger.get_debate_summary()
        
        # Structure debate data for UI
        structured_debate = {
            'rounds': [
                {
                    'number': 1,
                    'name': 'Initial Analysis',
                    'type': 'analysis',
                    'data': debate_summary.get('initial_decisions', [])
                },
                {
                    'number': 2,
                    'name': 'Challenge Round',
                    'type': 'challenges',
                    'data': debate_summary.get('challenges', [])
                },
                {
                    'number': 3,
                    'name': 'Revision',
                    'type': 'revisions',
                    'data': debate_summary.get('revisions', [])
                },
                {
                    'number': 4,
                    'name': 'Final Voting',
                    'type': 'votes',
                    'votes': [
                        {
                            'agent': agent_names[i],
                            'confidence': vote.confidence,
                            'risk': vote.risk,
                            'decision': vote.decision,
                            'reasoning': vote.reasoning
                        }
                        for i, vote in enumerate(final_votes)
                    ]
                }
            ]
        }
        
        # Return result with structured debate data
        return DebateResult(final_decision, structured_debate)
