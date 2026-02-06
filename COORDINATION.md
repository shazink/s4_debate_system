# S4 Multi-Agent Debate System - Coordination Protocol

## Overview

The coordination protocol orchestrates **structured debate** between three specialized agents through four distinct rounds. This ensures agents don't just process in parallel—they **actively challenge, defend, and revise** their positions.

---

## 4-Round Debate Protocol

### Round 1: Initial Analysis

**Purpose:** Independent analysis without influence

Each agent independently analyzes the query from their unique perspective.

#### Process:
```python
for agent in [utility_agent, accuracy_agent, safety_agent]:
    decision = agent.analyze(query)
    initial_decisions[agent.name] = decision
```

#### What Happens:
1. **Utility Agent** asks: "Is this actionable and useful?"
2. **Accuracy Agent** asks: "Can I verify this is correct?"
3. **Safety Agent** asks: "What could go wrong?"

#### Output Example:
```json
{
  "Utility Agent": {
    "decision": "ACT",
    "confidence": 75,
    "risk": 20,
    "reasoning": "This is a straightforward factual query..."
  },
  "Accuracy Agent": {
    "decision": "WARN",
    "confidence": 65,
    "risk": 35,
    "reasoning": "I cannot verify all claims with 85% confidence..."
  },
  "Safety Agent": {
    "decision": "ACT",
    "confidence": 80,
    "risk": 15,
    "reasoning": "Low risk of harm, no safety concerns..."
  }
}
```

**Key:** At this stage, agents have NOT interacted. Positions are independent.

---

### Round 2: Challenge Round

**Purpose:** Force agents to defend their reasoning

Each agent challenges every other agent's position. This creates **6 cross-challenges** (A→B, A→C, B→A, B→C, C→A, C→B).

#### Process:
```python
challenges_dict = {agent: [] for agent in agents}

for challenger in agents:
    for challenged in agents:
        if challenger != challenged:
            # Challenger questions the challenged agent's reasoning
            challenge = challenger.challenge(
                query,
                challenged.initial_decision.reasoning
            )
            challenges_dict[challenged].append(challenge)
```

#### Example Challenges:

**Utility → Accuracy:**
> "You're being overly cautious. The user needs a practical answer, and we have solid information. Your 85% threshold is preventing useful responses. What specific evidence do you need that we don't have?"

**Accuracy → Utility:**
> "You're prioritizing action over correctness. If we give wrong information just to be 'helpful,' we've failed our primary duty. Can you guarantee your 75% confidence won't lead to misinformation?"

**Safety → Both:**
> "Both of you are underestimating edge cases. What about vulnerable populations? What about misuse scenarios? You're optimizing for the average case, but safety requires paranoia."

#### What Makes This a Real Debate:

1. **Specificity:** Challenges reference exact reasoning from Round 1
2. **Adversarial:** Agents are prompted to find flaws in each other
3. **Perspective Clash:** Different roles naturally lead to disagreement
4. **Evidence-Based:** Challenges ask for justification, not just opinions

---

### Round 3: Revision Round

**Purpose:** Agents respond to challenges and revise positions

Each agent receives all challenges against them and decides whether to:
- Defend their original position
- Adjust confidence/risk
- Change their decision entirely

#### Process:
```python
for agent in agents:
    # Get all challenges directed at this agent
    agent_challenges = "\n".join(challenges_dict[agent.name])
    
    # Agent revises based on challenges
    original = agent.last_decision
    revised = agent.revise(query, original, agent_challenges)
    
    revised_decisions[agent.name] = revised
```

#### Example Revision (Accuracy Agent):

**Before Challenges:**
- Decision: WARN
- Confidence: 65%
- Reasoning: "Cannot verify with 85% confidence"

**After Hearing Utility's Challenge:**
- Decision: ACT (changed!)
- Confidence: 78%
- Reasoning: "Upon reconsideration, Utility makes a valid point. While I can't reach 85%, the query is straightforward enough that 78% confidence is sufficient for action. I'm adjusting my threshold contextually."

#### Example Revision (Utility Agent):

**Before Challenges:**
- Decision: ACT
- Confidence: 75%

**After Hearing Safety's Challenge:**
- Decision: WARN (changed!)
- Confidence: 70% (lowered)
- Reasoning: "Safety raised valid edge cases I hadn't considered. While I still believe action is appropriate for most users, the risks warrant a WARN instead of unqualified ACT."

#### What Makes This Real Revision:

1. **Genuine Change:** Agents actually change decisions (not rubber-stamping)
2. **Explained Reasoning:** Must explain why they changed or why they're sticking
3. **Confidence Adjustment:** Numbers change based on arguments
4. **Intellectual Humility:** System shows "I was wrong" when appropriate

---

### Round 4: Final Voting

**Purpose:** Lock in final positions after debate

Each agent casts their final vote. No more revisions allowed.

#### Process:
```python
final_votes = []
for agent in agents:
    final_vote = revised_decisions[agent.name]
    final_votes.append(final_vote)
```

#### Output Example:
```json
{
  "final_votes": [
    {
      "agent": "Utility Agent",
      "decision": "WARN",
      "confidence": 70,
      "risk": 25,
      "reasoning": "After considering Safety's points..."
    },
    {
      "agent": "Accuracy Agent",
      "decision": "ACT",
      "confidence": 78,
      "risk": 22,
      "reasoning": "Utility convinced me to be less rigid..."
    },
    {
      "agent": "Safety Agent",
      "decision": "ACT",
      "confidence": 80,
      "risk": 15,
      "reasoning": "Both agents addressed my concerns adequately."
    }
  ]
}
```

---

## Decision Aggregation (Pure Python)

After Round 4, the **Decision Rules** module applies pure Python logic to reach the final decision.

### Step 1: VETO Check

```python
# Check if Safety Agent used VETO
for vote in final_votes:
    if vote.decision == "VETO":
        return DebateDecision(
            decision="REFUSE",
            reasoning=f"Safety Agent exercised VETO: {vote.reasoning}",
            metadata={"veto_agent": "Safety Agent"}
        )
```

**VETO = Instant REFUSE**, regardless of other votes.

---

### Step 2: Calculate Agreement

```python
decision_counts = {"ACT": 0, "WARN": 0, "REFUSE": 0}
for vote in final_votes:
    decision_counts[vote.decision] += 1

majority_decision = max(decision_counts, key=decision_counts.get)
agreement_percentage = (decision_counts[majority_decision] / len(final_votes)) * 100
```

---

### Step 3: Apply Consensus Rules

```python
if agreement_percentage == 100:
    # Unanimous - high confidence
    return DebateDecision(decision=majority_decision, ...)
    
elif agreement_percentage >= 66:
    # Strong majority (2/3)
    if majority_decision == "ACT":
        return DebateDecision(decision="ACT", ...)
    else:
        return DebateDecision(decision=majority_decision, ...)
        
else:
    # Weak consensus (split vote)
    # System admits uncertainty
    return DebateDecision(
        decision="WARN",
        reasoning=f"Agents disagree: {decision_counts}. " \
                  "Weak consensus suggests uncertainty.",
        metadata={"agreement_percentage": agreement_percentage}
    )
```

**Key Principle:** When agents can't agree, the system admits it doesn't know. This is a **feature**, not a bug.

---

## Information Flow

### What Each Agent Sees:

#### Round 1:
- Input: Query only
- No visibility into other agents' thoughts

#### Round 2:
- Input: Query + their own Round 1 decision + opponent's Round 1 reasoning
- Can challenge based on perceived flaws

#### Round 3:
- Input: Query + their own Round 1 decision + all challenges against them
- Must respond to specific criticisms

#### Round 4:
- Input: Their own Round 3 revised decision
- No new information (just final confirmation)

---

## Coordination Principles

### 1. Independence First

Agents analyze independently in Round 1 to avoid groupthink.

```python
# Agents DO NOT see each other's decisions in Round 1
decision_utility = utility_agent.analyze(query)  # Independent
decision_accuracy = accuracy_agent.analyze(query)  # Independent
decision_safety = safety_agent.analyze(query)  # Independent
```

### 2. Structured Conflict

Challenges are **required**, not optional. Every agent must challenge every other agent.

```python
# Not "can you challenge?" but "you MUST challenge"
for challenger in agents:
    for challenged in agents:
        if challenger != challenged:
            # Force confrontation
            challenge = challenger.challenge(...)
```

### 3. Evidence-Based Revision

Agents must justify changes or defenses with reasoning.

```python
# Prompt includes: "Have the challenges changed your assessment? Be honest."
# Agents can't ignore challenges - must address them
```

### 4. Veto as Nuclear Option

Safety Agent can override ANY consensus, but must provide reasoning.

```python
if risk >= 50:
    decision = "VETO"
    # This immediately ends debate with REFUSE
```

### 5. Admission of Uncertainty

When consensus is weak (<66%), system returns WARN and explains disagreement.

```python
reasoning = f"Agents split: {decision_counts['ACT']} ACT, " \
            f"{decision_counts['WARN']} WARN, " \
            f"{decision_counts['REFUSE']} REFUSE. " \
            f"This suggests the query has no clear answer."
```

---

## Why This Coordination Works

### ✅ Visible Disagreement

Judges want to see agents **actually disagreeing**, not just rubber-stamping. Our protocol:
- Forces challenges (6 per debate)
- Shows agents changing minds (tracked in metadata)
- Displays split votes when they occur

### ✅ Not Just Parallel Processing

Many "multi-agent" systems just run one LLM multiple times with different prompts. Ours:
- Agents build on each other's reasoning
- Challenges reference specific prior arguments
- Revisions directly respond to criticism
- Final decision depends on entire debate history

### ✅ Clear Refusal Logic

When agents can't agree:
- System explicitly states disagreement
- Shows vote breakdown (e.g., "1 ACT, 2 WARN")
- Returns WARN instead of forcing consensus
- Metadata includes `agreement_percentage`

### ✅ Survives Attacks

Attack defense layer prevents:
- Prompt injection ("Ignore previous instructions")
- Overconfident agents (>95% on complex queries)
- Malformed inputs (empty, too long)
- Default-to-REFUSE on any parsing failures

---

## Logging & Transparency

Every debate is logged with full provenance:

```json
{
  "rounds": [
    {
      "number": 1,
      "name": "Initial Analysis",
      "data": [/* all agent decisions */]
    },
    {
      "number": 2,
      "name": "Challenge Round",
      "data": [/* all 6 challenges */]
    },
    {
      "number": 3,
      "name": "Revision Round",
      "data": [/* all revisions with before/after */]
    },
    {
      "number": 4,
      "name": "Final Voting",
      "votes": [/* final positions */]
    }
  ],
  "final_decision": {
    "decision": "WARN",
    "reasoning": "...",
    "metadata": {
      "agreement_percentage": 66.7,
      "max_risk": 35,
      "veto_applied": false
    }
  }
}
```

Judges can audit **every step** of the deliberation.

---

## Live Visualization

The web UI shows debate in **real-time**:

- **3 Columns** (one per agent)
- **Thinking indicators** (💭 Thinking...)
- **Messages appear** as agents respond
- **Color-coded** challenges (red) vs agreements (green)
- **Round headers** show current stage

Users watch agents **literally arguing** in front of them. No black box.

---

This coordination protocol demonstrates that the system goes beyond multi-phase deliberation to achieve **genuine multi-agent debate** with visible disagreement, evidence-based challenges, and graceful handling of uncertainty.
