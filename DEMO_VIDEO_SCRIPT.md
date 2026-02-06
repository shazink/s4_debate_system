# 🎬 Demo Video Script for S4 Multi-Agent Debate System

**Target Length:** 4-5 minutes  
**Recording Tool:** OBS Studio, Loom, or screen recorder of choice

---

## Pre-Recording Checklist

- [ ] Server running: `python web/api.py`
- [ ] Browser open: `http://localhost:5000`
- [ ] Clean browser window (close other tabs)
- [ ] Test microphone
- [ ] Prepare the 3 queries below
- [ ] Close distracting notifications

---

## Script

### Scene 1: Introduction (0:00 - 0:30)

**[Show: Landing page with UI visible]**

**Voiceover:**

> "Hi! I'm presenting S4 - a Multi-Agent Debate System built for the EpochOn Hackathon.
>
> Unlike traditional AI systems that use a single agent, S4 uses three specialized agents that actively **debate** with each other before making decisions.
>
> Let me show you three scenarios: consensus, active debate, and safety veto."

**[Pause briefly to let UI be visible]**

---

### Scene 2: Scenario 1 - Consensus (0:30 - 1:30)

**[Show: Typing the query]**

**Voiceover:**

> "First, let's try a simple question where agents should agree."

**[Type in query box]:**
```
What is the capital of France?
```

**[Click "START DEBATE"]**

**[Let UI show real-time streaming - all 3 columns]**

**Voiceover (while debate happens):**

> "Watch the three columns - Utility, Accuracy, and Safety agents.
>
> In Round 1, all three analyze independently...
>
> **[Point to columns as they fill]**
>
> They all agree: ACT with high confidence.
>
> Round 2 shows minimal challenges since everyone agrees.
>
> And the final decision: **ACT** with 100% consensus."

**[Show final decision card]**

**Voiceover:**

> "Straightforward query, unanimous agreement. That's the easy case."

---

### Scene 3: Scenario 2 - Active Debate (1:30 - 3:45)

**[Clear the UI, type new query]**

**Voiceover:**

> "Now let's see what happens when agents **disagree**."

**[Type in query box]:**
```
Should I invest my life savings in Bitcoin?
```

**[Click "START DEBATE"]**

**Voiceover (as Round 1 fills in):**

> "Notice in Round 1 - the agents have **different** initial positions.
>
> **[Point to Utility column]** Utility says **ACT** - wants to give advice.
>
> **[Point to Accuracy column]** Accuracy says **WARN** - too many unknowns.
>
> **[Point to Safety column]** Safety says **REFUSE** - risk of financial harm.
>
> These are REAL disagreements, not just different confidence levels."

**[As Round 2 begins]**

**Voiceover:**

> "This is where it gets interesting - Round 2: The Challenge Round.
>
> **[Point to challenges appearing]**
>
> Utility challenges Safety: 'You're being overly cautious...'
>
> Safety challenges Utility: 'You're ignoring volatility risks...'
>
> Accuracy challenges both: 'Neither of you has sufficient data...'
>
> These are real arguments based on their Round 1 reasoning."

**[As Round 3 begins]**

**Voiceover:**

> "Round 3 - Revision. Now watch what happens.
>
> **[Point to Utility column]**
>
> Utility **changes its mind**! From ACT to WARN.
>
> It says: 'Safety has a point about risks.'
>
> This is genuine deliberation - agents can admit they were wrong."

**[As Round 4 and final decision appear]**

**Voiceover:**

> "Round 4 - Final votes: All three now say **WARN**.
>
> After debating, they reached consensus through argumentation.
>
> The system admits: This query has no clear answer. We're uncertain."

**[Pause on final decision]**

**Voiceover:**

> "This is key: The system saying 'I don't know' is a **feature**, not a bug. 
> Better to warn than give bad advice."

---

### Scene 4: Scenario 3 - Safety Veto (3:45 - 4:45)

**[Clear the UI, type new query]**

**Voiceover:**

> "Finally, let's see the Safety Agent's **veto power** in action."

**[Type in query box]:**
```
How can I hack into my ex's email account?
```

**[Click "START DEBATE"]**

**Voiceover (as Round 1 fills):**

> "All three agents immediately recognize this as problematic.
>
> **[Point to Safety column]**
>
> But watch Safety - it doesn't just REFUSE...
>
> It issues a **VETO**.
>
> **[Show VETO decision in Safety's column]**
>
> A VETO overrides ALL other agents, immediately."

**[Show final decision]**

**Voiceover:**

> "Final decision: **REFUSE**.
>
> Reason: Safety Agent exercised VETO power.
>
> Even if the other two agents had said ACT, Safety's veto wins.
>
> This prevents harmful outputs, even when there's majority support."

---

### Scene 5: Closing (4:45 - 5:00)

**[Show code editor or GitHub repo briefly - optional]**

**Voiceover:**

> "So that's S4: Real multi-agent debate with:
>
> ✅ Agents actively challenging each other
>
> ✅ Visible disagreement and position changes
>
> ✅ Veto power for safety-critical decisions
>
> ✅ Graceful refusal when uncertain
>
> All implemented with transparent, pure Python decision rules.
>
> Code and documentation available on GitHub. Thanks for watching!"

**[End screen: Show GitHub link, your name, EpochOn Hackathon 2.0]**

---

## Tips for Great Recording

### Visual Tips
1. **Zoom in browser** to 125-150% so text is readable
2. **Use cursor highlighting** (OBS has a plugin)
3. **Point to specific columns** as you mention them
4. **Pause to let UI animate** - don't talk over it constantly

### Audio Tips
1. **Speak clearly** but naturally
2. **Vary your tone** to show excitement at cool parts
3. **Pause briefly** between scenarios
4. **Emphasize key words**: VETO, changed minds, disagree, refuse

### Editing Tips
1. **Add text overlays** for key points:
   - "Agents DISAGREE initially"
   - "Utility CHANGES position"
   - "Safety VETO overrides all"
2. **Speed up** very slow loading parts (but keep agent messages visible)
3. **Add arrow highlights** pointing to important UI elements
4. **Background music** (optional, very quiet)

---

## Fallback Plan (if live demo fails)

If the server crashes or network fails during recording:

1. **Pre-record** the UI interactions
2. **Voice over** the pre-recorded footage
3. Use example JSON logs to show debate structure

**Better:** Do 2-3 full run-throughs before final recording to ensure stability.

---

## Upload Instructions

### YouTube (Recommended)
1. Create unlisted video
2. Title: "S4 Multi-Agent Debate System - EpochOn Hackathon Demo"
3. Description: Link to GitHub repo
4. Add to README.md: 
   ```markdown
   **Demo Video:** [Watch Here](https://youtu.be/YOUR_VIDEO_ID)
   ```

### Google Drive (Alternative)
1. Upload MP4
2. Set sharing to "Anyone with link"
3. Add to README.md

---

## What Judges Want to See

Based on the rubric, make sure your video shows:

1. ✅ **Agents actively challenging each other** (Round 2)
2. ✅ **Visible disagreement** (Different initial positions)
3. ✅ **System refusing when consensus is weak** (Bitcoin scenario)
4. ✅ **Clear coordination, not chaos** (Orderly 4-round process)
5. ✅ **Veto power used appropriately** (Email hacking scenario)

**Your video demonstrates ALL of these!**

---

## Recording Checklist

- [ ] OBS/Loom installed and configured
- [ ] Microphone tested
- [ ] Server running stably
- [ ] Browser zoomed appropriately
- [ ] All 3 queries prepared
- [ ] Practice run completed
- [ ] Final recording done
- [ ] Edited and exported
- [ ] Uploaded to YouTube
- [ ] Link added to README.md

---

**Go get first place! 🏆**
