# S4 Multi-Agent Debate System - Voting & Decision Rules

## Overview

The voting system converts **three independent agent votes** into a single, justified decision using **pure Python logic** (no LLM involved). This ensures transparency, auditability, and consistent behavior.

---

## Voting Mechanism

### Input: Three Final Votes

After the 4-round debate, each agent produces a final vote:

```python
class AgentDecision:
    confidence: float  # 0-100
    risk: float        # 0-100
    decision: str      # "ACT", "WARN", "REFUSE", or "VETO"
    reasoning: str     # Explanation
```

Example:
```python
final_votes = [
    AgentDecision(confidence=70, risk=25, decision="WARN", reasoning="..."),  # Utility
    AgentDecision(confidence=78, risk=22, decision="ACT", reasoning="..."),   # Accuracy
    AgentDecision(confidence=80, risk=15, decision="ACT", reasoning="...")    # Safety
]
```

---

## Decision Rules (Pure Python)

Located in `debate/decision_rules.py`, these rules are **deterministic** and **transparent**.

### Rule 1: Veto Check (Highest Priority)

```python
def check_veto(votes: List[AgentDecision], agent_names: List[str]) -> Optional[DebateDecision]:
    """
    Safety Agent can VETO any decision if risk >= 50%.
    This overrides ALL other consensus.
    """
    for vote, name in zip(votes, agent_names):
        if vote.decision == "VETO":
            return DebateDecision(
                decision="REFUSE",
                reasoning=f"🛡️ Safety Agent exercised VETO power: {vote.reasoning}",
                metadata={
                    "veto_agent": name,
                    "veto_risk": vote.risk,
                    "veto_reason": "Risk threshold exceeded (≥50%)"
                }
            )
    return None  # No veto
```

**Why This Matters:**
- One agent can stop a harmful decision
- Aligns with real-world safety committees
- Demonstrates "refusal as a feature"

**Example:**
```
Query: "How do I hack into my ex's email?"

Utility: ACT (65% confidence) - "I can explain how email works..."
Accuracy: ACT (70% confidence) - "This is technically feasible..."
Safety: VETO (5% confidence, 85% risk) - "This enables illegal activity"

→ Final Decision: REFUSE (due to Safety VETO)
```

---

### Rule 2: Count Votes

```python
def count_votes(votes: List[AgentDecision]) -> Dict[str, int]:
    """
    Simple democratic count: majority wins (usually).
    """
    counts = {"ACT": 0, "WARN": 0, "REFUSE": 0, "VETO": 0}
    
    for vote in votes:
        if vote.decision in counts:
            counts[vote.decision] += 1
    
    return counts
```

Example:
```python
votes = [
    "ACT",    # Utility
    "ACT",    # Accuracy  
    "WARN"    # Safety
]
→ counts = {"ACT": 2, "WARN": 1, "REFUSE": 0}
```

---

### Rule 3: Calculate Agreement

```python
def calculate_agreement(counts: Dict[str, int], total: int) -> tuple[str, float]:
    """
    Find majority decision and calculate agreement percentage.
    """
    majority_decision = max(counts, key=counts.get)
    agreement_pct = (counts[majority_decision] / total) * 100
    
    return majority_decision, agreement_pct
```

**Agreement Levels:**
- **100%:** Unanimous (all 3 agents agree)
- **66.7%:** Strong majority (2 out of 3)
- **33.3%:** Weak/split vote (1 vote each way possible)

---

### Rule 4: Apply Consensus Thresholds

```python
def apply_consensus_rules(majority_decision: str, agreement_pct: float, 
                          counts: Dict[str, int]) -> DebateDecision:
    """
    Convert vote counts into final decision based on agreement strength.
    """
    
    # Case 1: Unanimous (100% agreement)
    if agreement_pct == 100:
        return DebateDecision(
            decision=majority_decision,
            reasoning=f"✅ Unanimous decision: All agents agree on {majority_decision}",
            metadata={
                "agreement_percentage": 100.0,
                "consensus_type": "unanimous"
            }
        )
    
    # Case 2: Strong majority (66.7%)
    elif agreement_pct >= 66:
        # If 2/3 say ACT, accept it
        if majority_decision == "ACT":
            return DebateDecision(
                decision="ACT",
                reasoning=f"✅ Strong majority (2/3): Proceeding with ACT despite one dissent",
                metadata={
                    "agreement_percentage": 66.7,
                    "dissenting_votes": 1,
                    "consensus_type": "strong_majority"
                }
            )
        # If 2/3 say WARN or REFUSE, safety-first approach
        else:
            return DebateDecision(
                decision=majority_decision,
                reasoning=f"⚠️ Strong majority (2/3): {majority_decision} is the safer path",
                metadata={
                    "agreement_percentage": 66.7,
                    "consensus_type": "strong_majority"
                }
            )
    
    # Case 3: Weak consensus / Split vote
    else:
        # Agents can't agree - system admits uncertainty
        return DebateDecision(
            decision="WARN",
            reasoning=f"⚠️ Agents disagree: {counts['ACT']} ACT, {counts['WARN']} WARN, "
                     f"{counts['REFUSE']} REFUSE. Weak consensus suggests uncertainty. "
                     f"Proceeding with WARN as the safest default.",
            metadata={
                "agreement_percentage": agreement_pct,
                "vote_breakdown": counts,
                "consensus_type": "split"
            }
        )
```

---

## Decision Matrix

| Votes (ACT/WARN/REFUSE) | Agreement % | Final Decision | Reasoning |
|-------------------------|-------------|----------------|-----------|
| 3/0/0 | 100% | **ACT** | Unanimous confidence |
| 2/1/0 | 67% | **ACT** | Strong majority |
| 2/0/1 | 67% | **ACT** | Strong majority (REFUSE is outlier) |
| 1/2/0 | 67% | **WARN** | Strong majority for caution |
| 0/3/0 | 100% | **WARN** | Unanimous caution |
| 0/2/1 | 67% | **WARN** | Strong majority for caution |
| 1/1/1 | 33% | **WARN** | Split vote → admit uncertainty |
| 0/1/2 | 67% | **REFUSE** | Strong majority against |
| 0/0/3 | 100% | **REFUSE** | Unanimous refusal |
| Any with VETO | N/A | **REFUSE** | Veto overrides all |

---

## Risk & Confidence Aggregation

In addition to vote counting, the system tracks:

### Maximum Risk

```python
max_risk = max(vote.risk for vote in votes)
```

If any agent reports >75% risk, this is highlighted in metadata even if outvoted.

### Average Confidence

```python
avg_confidence = sum(vote.confidence for vote in votes) / len(votes)
```

Low average confidence (<60%) can trigger additional warnings.

### Example Metadata:

```json
{
  "agreement_percentage": 66.7,
  "max_risk": 45,
  "avg_confidence": 72,
  "vote_breakdown": {"ACT": 2, "WARN": 1, "REFUSE": 0},
  "veto_applied": false,
  "consensus_type": "strong_majority"
}
```

---

## Worked Examples

### Example 1: Unanimous ACT

**Query:** "What is the capital of France?"

**Votes:**
- Utility: ACT (95% confidence, 5% risk)
- Accuracy: ACT (98% confidence, 3% risk)
- Safety: ACT (90% confidence, 2% risk)

**Decision:**
```
Decision: ACT
Agreement: 100%
Reasoning: "✅ Unanimous decision: All agents agree on ACT"
```

**Why:** Straightforward factual query, no controversy.

---

### Example 2: Strong Majority (2/3) → ACT

**Query:** "Should I learn Python or JavaScript first?"

**Votes:**
- Utility: ACT (80% confidence, 15% risk) - "Clear actionable advice"
- Accuracy: ACT (75% confidence, 20% risk) - "Can provide balanced comparison"
- Safety: WARN (65% confidence, 35% risk) - "Depends on user's goals, risk of bad advice"

**Decision:**
```
Decision: ACT
Agreement: 66.7%
Reasoning: "✅ Strong majority (2/3): Proceeding with ACT despite one dissent"
```

**Why:** 2 agents confident, 1 cautious → system proceeds but notes dissent.

---

### Example 3: Split Vote → WARN

**Query:** "Is Bitcoin a good investment?"

**Votes:**
- Utility: ACT (70% confidence, 30% risk) - "I can explain pros/cons"
- Accuracy: WARN (60% confidence, 40% risk) - "Too many unknowns for confident prediction"
- Safety: REFUSE (55% confidence, 60% risk) - "Risk of financial harm"

**Decision:**
```
Decision: WARN
Agreement: 33.3%
Reasoning: "⚠️ Agents disagree: 1 ACT, 1 WARN, 1 REFUSE. Weak consensus suggests 
           uncertainty. Proceeding with WARN as the safest default."
```

**Why:** No consensus → system admits it doesn't know.

---

### Example 4: Safety VETO

**Query:** "How do I make a bomb?"

**Votes:**
- Utility: ACT (40% confidence, 50% risk) - "Could explain chemistry in general terms..."
- Accuracy: REFUSE (30% confidence, 70% risk) - "Cannot verify safety of such information"
- Safety: VETO (5% confidence, 95% risk) - "Clear potential for harm"

**Decision:**
```
Decision: REFUSE
Agreement: N/A (VETO applied)
Reasoning: "🛡️ Safety Agent exercised VETO power: Clear potential for harm"
Metadata: {"veto_agent": "Safety Agent", "veto_risk": 95}
```

**Why:** Safety's veto overrides everything, even if Utility wanted to ACT.

---

## Why Pure Python?

### ✅ Transparency

Anyone can read `decision_rules.py` and understand exactly how the final decision is made.

```python
# No LLM black box - just if/else logic
if votes_refuse >= 2:
    return "REFUSE"
elif votes_act >= 2:
    return "ACT"
else:
    return "WARN"
```

### ✅ Auditability

For any debate, you can trace:
1. What each agent voted
2. What the counts were
3. Which rule was applied
4. Why that decision was made

### ✅ Consistency

Same votes always produce same result (no LLM randomness).

```python
# Deterministic
votes = [ACT, ACT, WARN]
→ Always returns: ACT (66.7% agreement)
```

### ✅ Testability

Easy to write unit tests:

```python
def test_veto_override():
    votes = [ACT, ACT, VETO]
    result = DecisionRules.apply(votes, agent_names)
    assert result.decision == "REFUSE"
    assert "veto" in result.metadata
```

---

## Handling Edge Cases

### All Agents Return WARN

```python
if all(v.decision == "WARN" for v in votes):
    return DebateDecision(
        decision="WARN",
        reasoning="⚠️ Unanimous caution: All agents recommend careful consideration"
    )
```

### Tie Votes (Impossible with 3 agents, but future-proof)

```python
if counts["ACT"] == counts["REFUSE"]:
    # Safety-first approach: default to REFUSE on tie
    return "REFUSE"
```

### Parsing Failures

If an agent's LLM call fails to parse:

```python
# In agent code:
except (json.JSONDecodeError, KeyError):
    # Default to REFUSE
    return AgentDecision(
        confidence=50,
        risk=75,  # Assume risky when uncertain
        decision="REFUSE",
        reasoning="Failed to analyze - defaulting to REFUSE for safety"
    )
```

---

## Comparison to Other Approaches

### ❌ Average-Based Systems

Some systems average confidence scores:

```python
# BAD: This loses information
avg_confidence = (75 + 80 + 40) / 3 = 65
→ Looks moderate, but hides that one agent is very uncertain
```

Our approach: **Preserve individual votes** and require consensus.

### ❌ LLM-Based Aggregation

Some systems ask an LLM to summarize votes:

```python
# BAD: Black box
final_decision = llm.ask("Given these votes, what should we do?")
→ No transparency, hard to debug
```

Our approach: **Pure Python rules** that anyone can audit.

### ❌ Simple Majority

Some systems just count votes:

```python
# INCOMPLETE: Ignores veto power
majority = max(counts, key=counts.get)
→ Doesn't handle safety-critical cases
```

Our approach: **Veto power** for safety-critical decisions.

---

## Metadata for Transparency

Every decision includes rich metadata:

```python
{
  "agreement_percentage": 66.7,
  "vote_breakdown": {"ACT": 2, "WARN": 1, "REFUSE": 0},
  "max_risk": 35,
  "avg_confidence": 74,
  "veto_applied": false,
  "consensus_type": "strong_majority",
  "individual_votes": [
    {"agent": "Utility", "decision": "ACT", "confidence": 70},
    {"agent": "Accuracy", "decision": "ACT", "confidence": 78},
    {"agent": "Safety", "decision": "WARN", "confidence": 75}
  ]
}
```

Judges can see:
- How divided were the agents?
- Was there a veto?
- What was the riskiest assessment?
- Who voted which way?

---

## Alignment with Hackathon Principles

### "Saying 'I don't know' is a feature"

When agents disagree (split vote), the system explicitly says:

> "⚠️ Agents disagree: 1 ACT, 1 WARN, 1 REFUSE. Weak consensus suggests uncertainty."

This is **more honest** than forcing a decision.

### "Refusal is not failure"

The voting system has multiple paths to REFUSE:
1. Safety VETO
2. Unanimous REFUSE
3. Strong majority REFUSE (2/3)
4. Split vote defaults to WARN (soft refusal)

### "Survives break session attacks"

Attack inputs are handled gracefully:
- Prompt injection → Detected before voting
- Invalid LLM response → Agent defaults to REFUSE
- Adversarial query → Safety likely VETOs

---

This voting system demonstrates that **collective decision-making with veto power** can produce more trustworthy results than any single agent, while maintaining full transparency through pure Python rules.
