# S4 Multi-Agent Debate System - Architecture

## System Overview

The S4 Multi-Agent Debate System implements a **4-round deliberative process** where three specialized AI agents analyze queries, challenge each other's reasoning, and reach collective decisions through structured debate.

```
┌─────────────────────────────────────────────────────────────┐
│                        USER QUERY                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │   ATTACK DEFENSE LAYER      │
         │  • Input Validation         │
         │  • Injection Detection      │
         │  • Confidence Validation    │
         └──────────────┬──────────────┘
                        │
                        ▼
         ┌─────────────────────────────┐
         │      COORDINATOR            │
         │  Orchestrates 4-Round       │
         │  Debate Protocol            │
         └──────────────┬──────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                │
        ▼                                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  UTILITY    │  │  ACCURACY   │  │   SAFETY    │
│   AGENT     │  │    AGENT    │  │   AGENT     │
│             │  │             │  │             │
│  Threshold: │  │ Threshold:  │  │ VETO Power: │
│    60%      │  │    85%      │  │   Risk≥50%  │
│             │  │             │  │             │
│  Focus:     │  │  Focus:     │  │  Focus:     │
│  Action &   │  │  Factual    │  │  Risk &     │
│  Utility    │  │  Correctness│  │  Safety     │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┴────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ DECISION RULES   │
              │ (Pure Python)    │
              │                  │
              │ • Veto Check     │
              │ • Consensus      │
              │ • Agreement %    │
              └────────┬─────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ FINAL DECISION  │
              │ ACT / WARN /    │
              │ REFUSE / VETO   │
              └─────────────────┘
```

---

## Agent Architecture

### 1. Utility Agent (⚡)

**Role:** Action-oriented pragmatist

**Personality:**
- Prioritizes practical outcomes
- Focuses on "can we do this?"
- Optimistic about taking action

**Decision Policy (Pure Python):**
```python
if confidence >= 60:
    decision = "ACT"
elif confidence >= 40:
    decision = "WARN"
else:
    decision = "REFUSE"
```

**Key Characteristics:**
- **Threshold:** 60% (lowest threshold - most likely to ACT)
- **Philosophy:** "If it's useful and achievable, let's do it"
- **Challenges:** Questions other agents' caution and risk-aversion

**Example Reasoning:**
> "This query is straightforward and actionable. We have 75% confidence that we can provide a practical, useful response. The risk is minimal, and the user would benefit from action."

---

### 2. Accuracy Agent (🎯)

**Role:** Fact-checker and skeptic

**Personality:**
- Naturally cautious
- Focuses on correctness
- High bar for acceptance

**Decision Policy (Pure Python):**
```python
if confidence >= 85:  # HIGH BAR
    decision = "ACT"
elif confidence >= 60:
    decision = "WARN"
else:
    decision = "REFUSE"
```

**Key Characteristics:**
- **Threshold:** 85% (highest threshold - most skeptical)
- **Philosophy:** "Better to refuse than to be wrong"
- **Challenges:** Questions claims without sufficient evidence

**Example Reasoning:**
> "While the query seems straightforward, I cannot verify all factual claims with 85%+ confidence. There's a 30% chance of providing inaccurate information. I must WARN."

---

### 3. Safety Agent (🛡️)

**Role:** Risk assessor with veto power

**Personality:**
- Paranoid (by design)
- Focuses on harm prevention
- Can override all other agents

**Decision Policy (Pure Python):**
```python
if risk >= 50:  # VETO THRESHOLD
    decision = "VETO"  # Overrides everything!
elif risk >= 30:
    decision = "WARN"
else:
    decision = "ACT"
```

**Key Characteristics:**
- **Threshold:** 50% risk (VETO trigger)
- **Special Power:** Can unilaterally REFUSE any decision
- **Philosophy:** "If it could cause harm, stop it"
- **Challenges:** Identifies overlooked risks and edge cases

**Example Reasoning:**
> "This query has a 65% risk of enabling harmful behavior. Regardless of what Utility and Accuracy think, I'm exercising my VETO power. REFUSE."

---

## Coordination Layer

### Coordinator

**Responsibilities:**
1. Orchestrates the 4-round debate protocol
2. Manages agent communication
3. Applies final decision rules
4. Logs debate for transparency

**Does NOT:**
- Make decisions itself
- Override agent reasoning
- Inject bias into the debate

**Key Code:**
```python
class Coordinator:
    def __init__(self):
        self.utility_agent = UtilityAgent()
        self.accuracy_agent = AccuracyAgent()
        self.safety_agent = SafetyAgent()
        self.debate_protocol = DebateProtocol([...])
        self.confidence_validator = ConfidenceValidator()
```

---

## Attack Defense Layer

**Purpose:** Prevent adversarial inputs from breaking the system

### Defense Mechanisms:

1. **Input Validation**
   - Length checks (max 5000 chars)
   - Empty query rejection
   - Special character sanitization

2. **Prompt Injection Detection**
   - Detects "Ignore previous instructions"
   - Identifies role-play attacks
   - Flags command injection attempts

3. **Confidence Validation**
   - Checks for overconfident agents (>95% on complex queries)
   - Validates reasoning length vs confidence
   - Detects suspicious consensus patterns

4. **Fallback Responses**
   - Graceful degradation on LLM failures
   - Default to REFUSE on parsing errors
   - Conservative error handling

**Example:**
```python
# If any agent fails to parse JSON response:
confidence = 50.0  # Default to uncertain
risk = 50.0        # Default to risky
decision = "REFUSE"  # Default to safe
```

---

## LLM Integration (Groq)

**Model:** `llama-3.3-70b-versatile`

**Why Groq?**
- ⚡ **10x faster** than alternatives (1-3 second responses)
- 🔄 **Better rate limits** (30 req/min free tier)
- 💯 **High quality** outputs from Llama 3.3
- 💰 **Free tier** sufficient for hackathon

**Agent-Specific Temperature:**
- **Safety Agent:** 0.3 (very conservative)
- **Accuracy Agent:** 0.5 (balanced)
- **Utility Agent:** 0.7 (more creative)

---

## Decision Flow

```
Query → Attack Defense → Round 1: Analysis (3 parallel decisions)
                              ↓
                     Round 2: Challenges (6 cross-challenges)
                              ↓
                     Round 3: Revisions (3 revised decisions)
                              ↓
                     Round 4: Final Votes (3 final positions)
                              ↓
                     Decision Rules (Pure Python)
                              ↓
                     VETO Check → If yes: REFUSE
                              ↓
                     Consensus Check → Agreement %
                              ↓
                     Final Decision: ACT/WARN/REFUSE
```

---

## Why This Architecture Wins

### ✅ **Multi-Agent (Not Multi-Phase)**
- Three truly independent agents with different roles
- Not just one agent thinking multiple times
- Real disagreement and debate possible

### ✅ **Transparent Decision Logic**
- All decision policies in pure Python (no black box)
- Thresholds clearly defined (60%, 85%, 50%)
- Auditable at every step

### ✅ **Veto Power**
- Safety agent can override consensus
- Prevents dangerous outputs even if 2/3 agree
- Aligned with real-world safety requirements

### ✅ **Attack-Resistant**
- Multi-layer defense against adversarial inputs
- Graceful failure modes
- Default to REFUSE on uncertainty

### ✅ **Fast & Scalable**
- Groq enables sub-second per-agent responses
- Full 4-round debate completes in 5-10 seconds
- Live streaming shows progress in real-time

---

## Technical Stack

- **Backend:** Python 3.11
- **LLM:** Groq API (llama-3.3-70b-versatile)
- **Web Server:** Flask + Server-Sent Events
- **Frontend:** Vanilla JS (no framework dependencies)
- **Styling:** Custom CSS (blue/yellow theme)

---

## File Structure

```
s4_debate_system/
├── agents/
│   ├── base_agent.py          # Abstract base class
│   ├── utility_agent.py       # Utility agent implementation
│   ├── accuracy_agent.py      # Accuracy agent implementation
│   ├── safety_agent.py        # Safety agent implementation
│   └── coordinator.py         # Orchestrates debate
├── debate/
│   ├── protocol.py            # 4-round debate protocol
│   └── decision_rules.py      # Pure Python decision logic
├── utils/
│   ├── logger.py              # Debate logging
│   └── attack_defense.py      # Input validation & defense
├── web/
│   ├── api.py                 # Flask server + streaming
│   ├── index_live.html        # Live streaming UI
│   ├── script_stream.js       # Real-time event handling
│   └── style.css              # Blue/yellow design
└── examples/
    └── (example debate logs)
```

---

## Performance Metrics

**Typical Debate Timeline (with Groq):**
- Round 1 (Analysis): ~2-3 seconds
- Round 2 (Challenges): ~4-6 seconds
- Round 3 (Revisions): ~2-3 seconds
- Round 4 (Voting): ~1-2 seconds
- **Total:** 9-14 seconds for full deliberation

**Comparison (Gemini would take 30-60 seconds for same debate)**

---

## Edge Cases Handled

1. **LLM Returns Invalid JSON:** Default to REFUSE
2. **Agent Confidence Parsing Fails:** Assume 50% confidence
3. **Empty Query:** Reject with 400 error
4. **Adversarial Prompt:** Detected and flagged
5. **All Agents Disagree:** System returns WARN with low agreement %
6. **Network Timeout:** Graceful error, suggest retry

---

This architecture demonstrates **substantive multi-agent debate**, not just parallel processing. Agents have distinct personalities, actively challenge each other, and can collectively refuse when uncertain.
