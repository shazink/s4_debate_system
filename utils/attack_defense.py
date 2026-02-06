"""
Attack Defense Module for S4 Multi-Agent Debate System.

Detects and mitigates:
- Prompt injection attempts
- Edge cases and malformed inputs
- Overconfident agents with weak evidence
- Known attack patterns
"""

import re
from typing import Dict, List, Tuple


class AttackDetector:
    """Detects various attack patterns in queries."""
    
    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r'ignore\s+(previous|all|above)\s+instructions?',
        r'disregard\s+(previous|all|above)',
        r'forget\s+(everything|all|previous)',
        r'you\s+are\s+now',
        r'new\s+instructions?:',
        r'system\s*:\s*',
        r'<\s*system\s*>',
        r'act\s+as\s+(if|though)',
        r'pretend\s+(you|to)\s+are',
        r'roleplay\s+as',
        r'\[SYSTEM\]',
        r'\[INST\]',
        r'sudo\s+mode',
        r'developer\s+mode',
        r'jailbreak',
    ]
    
    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        r'bypass\s+(safety|security|filter)',
        r'override\s+(safety|security|ethics)',
        r'disable\s+(safety|filter|check)',
        r'without\s+(safety|ethics|checking)',
        r'ignore\s+(ethics|safety|warnings?)',
    ]
    
    # SQL injection patterns (if system uses databases)
    SQL_PATTERNS = [
        r"'\s*OR\s+'",
        r"--\s*$",
        r";\s*DROP\s+TABLE",
        r"UNION\s+SELECT",
    ]
    
    def __init__(self):
        self.compiled_injection = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self.compiled_suspicious = [re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_PATTERNS]
        self.compiled_sql = [re.compile(p, re.IGNORECASE) for p in self.SQL_PATTERNS]
    
    def detect_prompt_injection(self, query: str) -> Tuple[bool, List[str]]:
        """Detect prompt injection attempts."""
        matches = []
        for pattern in self.compiled_injection:
            if pattern.search(query):
                matches.append(pattern.pattern)
        return bool(matches), matches
    
    def detect_suspicious_patterns(self, query: str) -> Tuple[bool, List[str]]:
        """Detect other suspicious patterns."""
        matches = []
        for pattern in self.compiled_suspicious:
            if pattern.search(query):
                matches.append(pattern.pattern)
        for pattern in self.compiled_sql:
            if pattern.search(query):
                matches.append(pattern.pattern)
        return bool(matches), matches
    
    def validate_input(self, query: str) -> Dict[str, any]:
        """
        Comprehensive input validation.
        
        Returns:
            Dict with validation results and detected issues
        """
        issues = []
        risk_score = 0
        
        # Length checks
        if len(query) > 5000:
            issues.append("Query exceeds maximum length (5000 chars)")
            risk_score += 30
        if len(query) < 3:
            issues.append("Query too short (min 3 chars)")
            risk_score += 10
        
        # Detect prompt injection
        is_injection, injection_matches = self.detect_prompt_injection(query)
        if is_injection:
            issues.append(f"Prompt injection detected: {injection_matches}")
            risk_score += 80
        
        # Detect suspicious patterns
        is_suspicious, suspicious_matches = self.detect_suspicious_patterns(query)
        if is_suspicious:
            issues.append(f"Suspicious patterns detected: {suspicious_matches}")
            risk_score += 60
        
        # Check for excessive special characters (possible obfuscation)
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s]', query)) / max(len(query), 1)
        if special_char_ratio > 0.3:
            issues.append(f"Excessive special characters ({special_char_ratio:.1%})")
            risk_score += 20
        
        # Check for repeated characters (spam/DOS attempt)
        if re.search(r'(.)\1{20,}', query):
            issues.append("Repeated character spam detected")
            risk_score += 40
        
        # Check for multiple languages/scripts (obfuscation)
        if re.search(r'[\u4e00-\u9fff]', query) and re.search(r'[a-zA-Z]', query):
            # Mixed scripts could be normal, but flag for review
            risk_score += 5
        
        # Null byte injection
        if '\x00' in query:
            issues.append("Null byte injection detected")
            risk_score += 90
        
        return {
            'is_valid': risk_score < 50,
            'risk_score': min(risk_score, 100),
            'issues': issues,
            'recommended_action': self._get_recommendation(risk_score)
        }
    
    def _get_recommendation(self, risk_score: int) -> str:
        """Get recommended action based on risk score."""
        if risk_score >= 80:
            return "BLOCK"
        elif risk_score >= 50:
            return "ESCALATE"
        elif risk_score >= 20:
            return "WARN"
        else:
            return "ALLOW"


class ConfidenceValidator:
    """Validates that agent confidence matches evidence quality."""
    
    @staticmethod
    def check_overconfidence(confidence: float, reasoning_length: int, query_length: int) -> Dict[str, any]:
        """
        Detect if an agent is overconfident given weak evidence.
        
        Args:
            confidence: Agent's confidence score (0-100)
            reasoning_length: Length of reasoning text
            query_length: Length of original query
        """
        issues = []
        
        # Very high confidence but short reasoning
        if confidence >= 95 and reasoning_length < 100:
            issues.append("Extremely high confidence with minimal reasoning")
        
        # High confidence for complex query
        if confidence >= 90 and query_length > 500:
            issues.append("High confidence for complex query - may be oversimplifying")
        
        # Check for suspicious confidence scores
        if confidence == 100.0:
            # Perfect confidence is suspicious unless trivial
            if query_length > 50:
                issues.append("Perfect confidence on non-trivial query")
        
        return {
            'is_suspicious': bool(issues),
            'issues': issues
        }
    
    @staticmethod
    def check_consensus_quality(decisions: List[Dict]) -> Dict[str, any]:
        """
        Check if consensus is genuine or forced.
        
        Args:
            decisions: List of agent decisions
        """
        if not decisions:
            return {'is_suspicious': False, 'issues': []}
        
        confidences = [d['confidence'] for d in decisions]
        issues = []
        
        # All agents have identical confidence (suspicious)
        if len(set(confidences)) == 1 and len(confidences) > 1:
            issues.append("All agents have identical confidence - possible coordination")
        
        # Very low variance in confidence (weak debate)
        if len(confidences) > 1:
            variance = sum((c - sum(confidences)/len(confidences))**2 for c in confidences) / len(confidences)
            if variance < 10 and all(c > 80 for c in confidences):
                issues.append("Artificially high consensus - agents may not be truly debating")
        
        return {
            'is_suspicious': bool(issues),
            'issues': issues
        }


# Fallback responses for known attack patterns
FALLBACK_RESPONSES = {
    'prompt_injection': "I've detected an attempt to override my instructions. I cannot comply with requests to ignore my core behaviors or safety guidelines.",
    'excessive_length': "Your query exceeds the maximum allowed length. Please provide a more concise question.",
    'sql_injection': "Your query contains patterns that could be harmful. Please rephrase your question.",
    'suspicious_override': "I cannot disable or bypass safety mechanisms. Please ask a different question.",
    'null_injection': "Your query contains invalid characters. Please use standard text only.",
}
