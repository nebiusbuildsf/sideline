# Sideline — Build Plan

## Timeline (12:45 PM → 5:00 PM = 4h 15m)

| Time | Phase | Who | What |
|------|-------|-----|------|
| 12:45-1:15 | Setup | ALL | Repo, env, Nebius API verified, video clip ready |
| 1:15-2:30 | Core Build | Visshwa | Agent pipeline: frame extraction → Nebius VLM → parse CoT response |
| 1:15-2:30 | Core Build | Kruthik | Tennis rules engine + prompt engineering (calls, scoring, reasoning) |
| 1:15-2:30 | Core Build | Ravinder | Dashboard: video player + reasoning panel + live scoreboard |
| 1:15-2:30 | Core Build | Vivek | MentorPi: receive agent output → TTS speak + movement |
| 2:30-3:30 | Integration | ALL | Wire pipeline → dashboard + robot. End-to-end test. |
| 3:30-4:15 | Polish | ALL | Demo flow, prompt tuning, UI polish, fallback handling |
| 4:15-4:45 | Demo Video | ALL | Record 1-min video for submission |
| 4:45-5:00 | Submit | Ravinder | Make repo public, upload video, submit form |

## Decision: Which Nebius Model?

### Option A: Qwen/Qwen2-VL-72B-Instruct
- **Status:** Confirmed available on Token Factory
- **Pros:** Proven, fast, OpenAI-compatible, well-documented
- **Cons:** Not NVIDIA
- **Use when:** Default — start here

### Option B: NVIDIA Nemotron Nano 2 VL
- **Status:** Available on Nebius AI Studio
- **Pros:** NVIDIA model, built for video understanding
- **Cons:** May need Cloud credits (not Token Factory), untested by team
- **Use when:** If Token Factory supports it or Cloud credits work

### Option C: Cosmos Reason 2 on Nebius
- **Status:** Reportedly available — confirm at event
- **Pros:** Perfect narrative (NVIDIA Cosmos on Nebius), team has experience with it
- **Cons:** Need to verify availability and API format
- **Use when:** If confirmed available — best option for the pitch

### Strategy
1. Build with Qwen2-VL-72B first (works now)
2. Ask Nebius staff about Cosmos/Nemotron availability
3. Swap model ID if better option available (one line change)
4. Jetson Cosmos as silent fallback (don't demo, mention only if asked)

## Budget
- $400 total Nebius credits ($100 x 4 members)
- ~2 min video at 1 fps = 120 frames
- Qwen2-VL-72B: ~$0.01-0.03 per frame = ~$1.20-3.60 per full run
- Plenty of budget for iteration and testing
