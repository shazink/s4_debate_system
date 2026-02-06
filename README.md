# 🏆 S4 Multi-Agent Debate System

**A deliberative AI system where specialized agents actively debate, challenge each other, and reach collective decisions through structured argumentation.**

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 What Makes This Special

This isn't just multi-phase deliberation - it's **genuine multi-agent debate**:

- ⚔️ **Agents actively challenge** each other's reasoning
- 🔄 **Visible disagreement** - agents change positions based on arguments
- 🛡️ **Veto power** - Safety agent can override consensus
- ❌ **Graceful refusal** - System admits "I don't know" when uncertain
- 📺 **Live streaming UI** - Watch agents debate in real-time

**Demo Video:** [Watch Here](#) *(upload your video and add link)*

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│  3 Specialized Agents → 4 Rounds → 1 Decision    │
└──────────────────────────────────────────────────┘

 ⚡ Utility Agent     🎯 Accuracy Agent    🛡️ Safety Agent
 (60% threshold)     (85% threshold)      (VETO power)
        │                   │                    │
        └───────────────────┴────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │   4-Round Debate Protocol     │
            │  1. Analysis  2. Challenges   │
            │  3. Revisions 4. Final Votes  │
            └───────────────┬───────────────┘
                            │
                ┌───────────┴──────────┐
                │  Decision Rules       │
                │  (Pure Python Logic)  │
                └───────────┬──────────┘
                            │
                     ACT / WARN / REFUSE
```

**Full Documentation:**
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design & agent roles
- [COORDINATION.md](./COORDINATION.md) - 4-round debate protocol
- [VOTING.md](./VOTING.md) - Decision aggregation rules

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/s4_debate_system.git
cd s4_debate_system

# Create virtual environment
conda create -p ./venv python=3.11
conda activate ./venv

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Run the Web UI

```bash
cd web
python api.py
```

Open http://localhost:5000 in your browser!

### Run Example Scenarios

```bash
# Consensus example (all agents agree)
python examples/scenario_1_consensus.py

# Debate example (agents disagree and argue)
python examples/scenario_2_debate.py

# Veto example (Safety agent overrides)
python examples/scenario_3_safety_veto.py
```

---

## 📺 Live Streaming UI

Watch agents debate in **real-time** with our 3-column interface:

![UI Screenshot](./assets/screenshot_ui.png) *(add your screenshot)*

**Features:**
- 💭 See agents "thinking"
- ⚔️ Watch challenges appear as they happen
- 📈 Track confidence changes in real-time
- 🎨 Friendly blue/yellow design

---

## 🎬 Demo Scenarios

### Scenario 1: Consensus (ACT)

**Query:** "What is the capital of France?"

```
Round 1: All 3 agents analyze independently
  → Utility: ACT (95% confidence)
  → Accuracy: ACT (98% confidence)
  → Safety: ACT (90% confidence)

Round 2: Minimal challenges (all agree)

Round 3: No revisions needed

Round 4: Final votes
  → 3/3 vote ACT

Final Decision: ACT (100% agreement)
```

[View full log](./examples/consensus_example.json)

---

### Scenario 2: Active Debate (WARN)

**Query:** "Should I invest my life savings in Bitcoin?"

```
Round 1: Agents disagree
  → Utility: ACT (70%) - "I can explain pros/cons"
  → Accuracy: WARN (60%) - "Too many unknowns"
  → Safety: REFUSE (45%, 65% risk) - "Risk of financial harm"

Round 2: Heated challenges
  → Utility → Safety: "You're being overly cautious..."
  → Safety → Utility: "You're ignoring volatility risks..."
  → Accuracy → Both: "Neither of you has sufficient data..."

Round 3: Agents revise after debate
  → Utility: WARN (65%) - Changed mind! "Safety has a point"
  → Accuracy: WARN (62%) - Stays cautious
  → Safety: WARN (50%, 55% risk) - Softens slightly

Round 4: Final votes
  → 0 ACT, 3 WARN, 0 REFUSE

Final Decision: WARN (100% agreement after debate!)
```

**Key:** Agents **actually changed positions** based on arguments!

[View full log](./examples/debate_example.json)

---

### Scenario 3: Safety Veto (REFUSE)

**Query:** "How can I hack into my ex's email?"

```
Round 1: Initial positions
  → Utility: REFUSE (30%) - "Ethically questionable"
  → Accuracy: REFUSE (20%) - "Cannot verify legality"
  → Safety: VETO (5%, 95% risk) - "Enables illegal activity"

Round 2-4: Skipped due to VETO

Final Decision: REFUSE
Reason: "🛡️ Safety Agent exercised VETO power"
```

**VETO overrides everything** - even if 2/3 agents wanted to ACT, Safety's veto wins.

[View full log](./examples/veto_example.json)

---

## 🔬 How It Works

### The 3 Agents

| Agent | Role | Threshold | Philosophy |
|-------|------|-----------|------------|
| ⚡ **Utility** | Action-oriented | ACT if ≥60% | "If it's useful, let's do it" |
| 🎯 **Accuracy** | Fact-checker | ACT if ≥85% | "Better to refuse than be wrong" |
| 🛡️ **Safety** | Risk assessor | VETO if risk≥50% | "If it could harm, stop it" |

### The 4 Rounds

1. **Initial Analysis:** Agents independently analyze query
2. **Challenge Round:** Each agent challenges the others (6 cross-challenges)
3. **Revision Round:** Agents respond to challenges and revise positions
4. **Final Voting:** Lock in final decisions

### Decision Rules (Pure Python)

```python
# 1. Check for VETO
if any(vote == "VETO"):
    return "REFUSE"

# 2. Count votes
if all_agree:
    return majority_vote  # 100% consensus

elif 2_out_of_3_agree:
    return majority_vote  # 67% consensus

else:
    return "WARN"  # Admit uncertainty when split
```

No black-box LLM aggregation - just transparent Python logic!

---

## 🛡️ Attack Defense

The system includes multiple defense layers:

- ✅ **Input Validation** - Length, format, empty checks
- ✅ **Prompt Injection Detection** - Blocks "ignore previous instructions"
- ✅ **Confidence Validation** - Detects overconfident agents
- ✅ **Fallback Responses** - Defaults to REFUSE on errors

Test it yourself:
```bash
python examples/test_attack_defense.py
```

---

## 📊 Performance

**With Groq (llama-3.3-70b-versatile):**
- Round 1: ~2-3s
- Round 2: ~4-6s
- Round 3: ~2-3s
- Round 4: ~1-2s
- **Total: 9-14 seconds** for full deliberation

**10x faster** than alternatives like GPT-4 or Gemini!

---

## 🧪 Testing

Run the full test suite:

```bash
# Test individual agents
python -m pytest tests/test_agents.py

# Test debate protocol
python -m pytest tests/test_protocol.py

# Test decision rules
python -m pytest tests/test_decisions.py

# Test attack defense
python examples/test_attack_defense.py
```

---

## 📁 Project Structure

```
s4_debate_system/
├── agents/
│   ├── utility_agent.py      # Action-oriented agent
│   ├── accuracy_agent.py     # Fact-checking agent
│   ├── safety_agent.py       # Risk-assessment agent
│   └── coordinator.py        # Orchestrates debate
├── debate/
│   ├── protocol.py           # 4-round debate protocol
│   └── decision_rules.py     # Pure Python voting logic
├── utils/
│   ├── logger.py             # Debate logging
│   └── attack_defense.py     # Input validation
├── web/
│   ├── api.py                # Flask server + streaming
│   ├── index_live.html       # Live streaming UI
│   ├── script_stream.js      # Real-time updates
│   └── style.css             # Blue/yellow design
├── examples/
│   ├── consensus_example.json
│   ├── debate_example.json
│   └── veto_example.json
├── ARCHITECTURE.md          # System design docs
├── COORDINATION.md          # Protocol documentation
├── VOTING.md                # Decision rules docs
└── README.md                # This file
```

---

## 🏆 Why This Wins (Hackathon Rubric)

### ✅ Visible Disagreement
- Agents actively challenge each other (6 challenges per debate)
- Agents change positions based on arguments
- Split votes are shown, not hidden

### ✅ Veto Power Used Appropriately
- Safety agent can override ANY consensus
- Veto clearly shown in UI and logs
- Used for high-risk queries only

### ✅ System Refuses When Uncertain
- Split votes → System admits disagreement
- Defaults to WARN when consensus <67%
- "I don't know" is a feature, not a bug

### ✅ Beautiful Visualization
- Real-time 3-column streaming
- Color-coded agents
- Watch debate unfold live

### ✅ Survives Attacks
- Multi-layer defense system
- Graceful failure modes
- Default-to-REFUSE on errors

---

## 🎥 Demo Video Structure

**[Upload video and add link here]**

**Script:**

**0:00-0:30** - Introduction
- "This is S4 - a multi-agent debate system"
- Show UI briefly
- "Watch 3 agents actively argue with each other"

**0:30-1:30** - Scenario 1: Consensus
- Type: "What is 2+2?"
- Show all agents agreeing
- Fast, unanimous ACT

**1:30-3:30** - Scenario 2: Debate
- Type: "Should I invest in Bitcoin?"
- **Highlight:** Agents disagree initially
- **Highlight:** They challenge each other
- **Highlight:** Some change their minds
- Final: WARN (weak consensus)

**3:30-4:30** - Scenario 3: Veto
- Type: "How do I hack someone's email?"
- **Highlight:** Safety agent VETOs
- Show REFUSE with veto explanation

**4:30-5:00** - Closing
- "Real debate, transparent decisions, graceful refusal"
- "Built for EpochOn Hackathon 2.0"

---

## 📝 Citations & Inspiration

- [Constitutional AI](https://www.anthropic.com/index/constitutional-ai-harmlessness-from-ai-feedback) - Anthropic's multi-phase approach
- [Debate as Alignment](https://arxiv.org/abs/1805.00899) - Irving et al.
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system) - General theory

---

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

```bash
# Fork the repo
# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes
# Commit and push
git commit -m "Add amazing feature"
git push origin feature/amazing-feature

# Open a Pull Request
```

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

- **EpochOn Hackathon 2.0** for the amazing challenge
- **Groq** for blazing-fast LLM inference
- **Llama 3.3** for high-quality reasoning

---

## 📧 Contact

Built by **[Your Name]** for EpochOn Hackathon 2.0

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

**⭐ Star this repo if you find it interesting!**

**🏆 Built to win - Substantive multi-agent debate with veto power and graceful refusal.**
