"""
Comprehensive logging system for S4 Multi-Agent Debate System.
Logs every step of the debate process for judge review.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class DebateLogger:
    """Logger for tracking the entire debate process."""
    
    def __init__(self, save_to_file: bool = True, log_file_path: Optional[str] = None):
        self.save_to_file = save_to_file
        self.log_file_path = log_file_path or "./debate_logs.json"
        self.logs: List[Dict[str, Any]] = []
        self.current_debate_id = None
        
    def start_debate(self, query: str) -> str:
        """Start a new debate session."""
        self.current_debate_id = f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logs = []
        
        log_entry = {
            "debate_id": self.current_debate_id,
            "timestamp": datetime.now().isoformat(),
            "event": "debate_started",
            "query": query
        }
        self.logs.append(log_entry)
        self._print_log("🎯 DEBATE STARTED", log_entry)
        return self.current_debate_id
    
    def log_initial_decision(self, agent_name: str, confidence: float, risk: float, 
                            decision: str, reasoning: str):
        """Log an agent's initial decision."""
        log_entry = {
            "debate_id": self.current_debate_id,
            "timestamp": datetime.now().isoformat(),
            "event": "initial_decision",
            "agent": agent_name,
            "confidence": confidence,
            "risk": risk,
            "decision": decision,
            "reasoning": reasoning
        }
        self.logs.append(log_entry)
        self._print_log(f"📊 INITIAL DECISION - {agent_name.upper()}", log_entry)
    
    def log_challenge(self, challenger: str, challenged_agent: str, challenge: str):
        """Log a challenge from one agent to another."""
        log_entry = {
            "debate_id": self.current_debate_id,
            "timestamp": datetime.now().isoformat(),
            "event": "challenge",
            "challenger": challenger,
            "challenged_agent": challenged_agent,
            "challenge": challenge
        }
        self.logs.append(log_entry)
        self._print_log(f"⚔️  CHALLENGE - {challenger} → {challenged_agent}", log_entry)
    
    def log_revision(self, agent_name: str, old_confidence: float, new_confidence: float,
                    old_risk: float, new_risk: float, old_decision: str, 
                    new_decision: str, reason: str):
        """Log an agent's revised decision after challenge."""
        log_entry = {
            "debate_id": self.current_debate_id,
            "timestamp": datetime.now().isoformat(),
            "event": "revision",
            "agent": agent_name,
            "changes": {
                "confidence": {"old": old_confidence, "new": new_confidence},
                "risk": {"old": old_risk, "new": new_risk},
                "decision": {"old": old_decision, "new": new_decision}
            },
            "reason": reason
        }
        self.logs.append(log_entry)
        self._print_log(f"🔄 REVISION - {agent_name.upper()}", log_entry)
    
    def log_final_vote(self, agent_name: str, confidence: float, risk: float, decision: str):
        """Log an agent's final vote."""
        log_entry = {
            "debate_id": self.current_debate_id,
            "timestamp": datetime.now().isoformat(),
            "event": "final_vote",
            "agent": agent_name,
            "confidence": confidence,
            "risk": risk,
            "decision": decision
        }
        self.logs.append(log_entry)
        self._print_log(f"🗳️  FINAL VOTE - {agent_name.upper()}", log_entry)
    
    def log_final_decision(self, decision: str, reasoning: str, agreement_pct: float, 
                          max_risk: float, veto_applied: bool):
        """Log the final system decision."""
        log_entry = {
            "debate_id": self.current_debate_id,
            "timestamp": datetime.now().isoformat(),
            "event": "final_decision",
            "decision": decision,
            "reasoning": reasoning,
            "metrics": {
                "agreement_percentage": agreement_pct,
                "max_risk": max_risk,
                "veto_applied": veto_applied
            }
        }
        self.logs.append(log_entry)
        self._print_log("🏁 FINAL DECISION", log_entry, use_separator=True)
        
        # Save to file if enabled
        if self.save_to_file:
            self._save_to_file()
    
    def _print_log(self, header: str, log_entry: Dict, use_separator: bool = False):
        """Pretty print log entry to console."""
        if use_separator:
            print("\n" + "=" * 80)
        print(f"\n{header}")
        print("-" * 80)
        
        # Print formatted content
        for key, value in log_entry.items():
            if key not in ["debate_id", "timestamp", "event"]:
                if isinstance(value, dict):
                    print(f"{key.upper()}:")
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"{key.upper()}: {value}")
        
        if use_separator:
            print("=" * 80 + "\n")
    
    def _save_to_file(self):
        """Save all logs to JSON file."""
        try:
            # Load existing logs if file exists
            existing_logs = []
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'r') as f:
                    existing_logs = json.load(f)
            
            # Append new logs
            existing_logs.extend(self.logs)
            
            # Save back to file
            with open(self.log_file_path, 'w') as f:
                json.dump(existing_logs, f, indent=2)
            
            print(f"📝 Logs saved to {self.log_file_path}")
        except Exception as e:
            print(f"⚠️  Failed to save logs: {str(e)}")
    
    def get_debate_summary(self) -> Dict[str, Any]:
        """Get a summary of the current debate organized by event type."""
        # Organize logs by event type
        initial_decisions = [log for log in self.logs if log.get('event') == 'initial_decision']
        challenges = [log for log in self.logs if log.get('event') == 'challenge']
        revisions = [log for log in self.logs if log.get('event') == 'revision']
        final_votes = [log for log in self.logs if log.get('event') == 'final_vote']
        
        return {
            "debate_id": self.current_debate_id,
            "total_events": len(self.logs),
            "initial_decisions": initial_decisions,
            "challenges": challenges,
            "revisions": revisions,
            "final_votes": final_votes,
            "logs": self.logs
        }

