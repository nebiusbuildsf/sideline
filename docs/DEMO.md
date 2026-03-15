# Sideline — Demo & Pitch Plan

## Demo Flow (3 minutes for judges)

### Setup (before judges arrive)
- Dashboard open on laptop: video player + reasoning panel + scoreboard
- MentorPi on the table, powered on, connected
- Tennis clip queued up
- Agent running, waiting for start command

### Minute 1: The Problem (30 sec) + First Wow (30 sec)
"240 million tennis matches are played every year. Almost none have a referee. Players argue calls. Games slow down. People stop playing."

"We built Sideline — an agentic AI referee."

**[Hit start]** — Tennis clip begins playing. Agent starts analyzing.
- Reasoning panel shows chain-of-thought appearing in real-time
- First call: "Out! 15-Love" — appears on dashboard
- MentorPi announces it out loud through speaker

### Minute 2: The Tech
"Sideline is not an image classifier. It's an agent."

Point at the dashboard:
- "It **observes** each frame through Nebius Token Factory's vision model"
- "It **reasons** with chain-of-thought — you can see the thinking right here"
- "It **decides** — fault, ace, out — with a confidence score"
- "It **acts** — through tool calls: update the score, announce the call, signal the robot"

Show the three protocols:
- "Function calls for internal actions"
- "MCP server so any AI client can use our referee"
- "A2A protocol for multi-agent — imagine three cameras, three Sideline agents, one coordinator"

### Minute 3: The Vision
"Today, Sideline watches through a webcam and acts through this robot."

**[Point at MentorPi]**

"But the agent doesn't care what body it has. Same brain, any form."
- "A robotic arm that signals calls" *(gesture at SO-101 if available)*
- "A humanoid that walks the court" *(mention Unitree G1)*
- "Or just your phone — camera in, voice out"

"Bring your own game footage. Sideline reasons about any sport."

**End with the robot making a dramatic call.**

---

## Q&A Prep

**Q: How is this different from Hawk-Eye?**
A: Hawk-Eye costs $100K+ per court with fixed cameras and custom hardware. Sideline is a single camera and a cloud API. We're not replacing Hawk-Eye at Wimbledon — we're bringing refereeing to the 99.9% of matches that have nothing.

**Q: Can it handle other sports?**
A: The agent is sport-agnostic. The rules engine and prompt are pluggable. Tennis today, cricket and pickleball are straightforward extensions.

**Q: What about real-time latency?**
A: Cloud inference is 1-2 seconds per frame. For tennis, calls happen between points — plenty of time. For real-time tracking during a rally, you'd run a smaller model on edge hardware.

**Q: Why not just use a single VLM call?**
A: Because it's agentic. It maintains game state across the entire match. It tracks score through rallies. It remembers what happened three points ago. A single VLM call has no memory.

**Q: What model are you using?**
A: Nebius Token Factory — [name the model]. OpenAI-compatible API, so we can swap models with a single env var change.

**Q: How does MCP help here?**
A: MCP makes the referee pluggable. Right now our agent calls referee tools. But expose those same tools via MCP and any AI assistant — Claude, ChatGPT, Cursor — can use our referee as a tool. You could ask Claude "was that ball out?" and it calls our MCP server.

**Q: What about the A2A protocol?**
A: Imagine three cameras around a court, each running a Sideline agent. A coordinator agent receives all three analyses via A2A and makes the final call — like VAR in soccer but autonomous. That's multi-agent refereeing.

**Q: Did you build this all today?**
A: Yes. Fresh repo at 10:40. The domain knowledge is in our heads — one teammate is an actual sports referee who's managed 14 leagues, another has a CMU robotics degree. But every line of code was written here.

---

## 1-Minute Demo Video Script

| Time | Visual | Audio/Text |
|------|--------|------------|
| 0-5s | Title card: "Sideline — AI Referee Agent" | Music fade in |
| 5-15s | Dashboard: tennis clip playing, reasoning panel empty | "Sideline watches sports video..." |
| 15-30s | First analysis appears — CoT reasoning, call made, score updates | "...reasons about every play..." |
| 30-40s | Multiple calls happening, scoreboard tracking the match | "...tracks the score autonomously..." |
| 40-50s | MentorPi announces "Fault! Second serve" — camera shows robot | "...and acts through any physical form." |
| 50-55s | Architecture diagram overlay: Video → Agent → Tools/MCP/A2A → Actions | "Built with Nebius Token Factory." |
| 55-60s | Sideline logo + team names + "Nebius.Build SF 2026" | End card |

### Recording Tips
- Screen record the dashboard with QuickTime
- Phone camera for the robot clip
- Edit in iMovie or just screen record with voiceover
- Upload to YouTube as unlisted
- Have the link ready by 4:45 PM

---

## Demo Failure Modes & Recovery

| Failure | Recovery |
|---------|----------|
| Nebius API slow/down | Pre-cache 10 frames of analysis, play from cache |
| Robot won't connect | "Here's what it looks like" + show pre-recorded clip |
| Dashboard WebSocket drops | Refresh browser, agent auto-reconnects |
| Wrong call from VLM | "The agent shows its reasoning — judges love seeing the thinking even on wrong calls" |
| Score tracking breaks | Reset score, pick up from current frame |
| Video won't play | Switch to live camera pointed at phone showing tennis video |
