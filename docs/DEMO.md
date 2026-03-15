# Sideline Demo Plan

## Demo Flow (3 minutes)

### Minute 1 — The Problem
"Amateur sports have no referees. 240 million tennis matches played annually with zero officiating. Players argue calls. Games slow down. People stop playing."

### Minute 2 — The Solution
"Sideline is an agentic AI referee. Watch."
- Play tennis clip on dashboard
- Agent reasoning appears in real-time: "Ball trajectory... landed outside baseline... calling OUT"
- Scoreboard updates: "15-Love"
- MentorPi announces: "Out! 15-Love" (voice)
- Robot gestures/moves

### Minute 3 — The Tech + Vision
"Sideline uses Nebius Token Factory VLM for perception, chain-of-thought reasoning for decisions, and standard protocols (function calls, MCP, A2A) to act through any physical form."
- Show architecture diagram
- "Today it's a tank bot. Tomorrow it's a humanoid referee walking the court."
- "Bring your own game footage. Sideline reasons about any sport."

## Q&A Prep

**Q: How is this different from Hawk-Eye?**
A: Hawk-Eye costs $100K+ per court, requires fixed cameras. Sideline is a single camera + cloud AI. Democratizes officiating.

**Q: Can it handle other sports?**
A: The agent is sport-agnostic. Swap the rules engine and prompt. Tennis today, cricket and pickleball next.

**Q: Why not just use a single VLM call?**
A: Because it's agentic — it maintains state, tracks score across rallies, remembers context, and takes physical actions. Not a one-shot classifier.

**Q: What about latency?**
A: Cloud inference ~1-2s per frame. Fast enough for post-rally calls. Edge deployment on Jetson brings it under 500ms.

## 1-Minute Video Script
1. (0-10s) Title card: "Sideline — AI Referee Agent"
2. (10-30s) Dashboard: tennis clip + live reasoning + score updating
3. (30-45s) MentorPi announcing a call out loud, moving
4. (45-55s) Architecture diagram overlay
5. (55-60s) "Built with Nebius Token Factory. From watching to calling."
