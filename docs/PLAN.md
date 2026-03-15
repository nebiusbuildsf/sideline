# Sideline — Build Plan

## Time Budget: 6h 20m (10:40 AM → 5:00 PM)

### Phase 0: Setup (10:40 - 11:15) — 35 min
| Who | Task |
|-----|------|
| ALL | `uv init`, install deps, set NEBIUS_API_KEY |
| Ravinder | Create FastAPI server skeleton + WebSocket |
| Visshwa | Verify Nebius VLM call works (single frame test) |
| Kruthik | Write tennis rules engine + referee system prompt |
| Vivek | Connect MentorPi, verify SSH + ROS2 + speaker |

**Gate:** One successful VLM call returning a tennis analysis before moving on.

### Phase 1: Core Build (11:15 - 1:30) — 2h 15m
| Who | Task |
|-----|------|
| Visshwa | Agent pipeline: frame extraction → Nebius VLM → parse tool calls → execute |
| Kruthik | Tool definitions (update_score, announce_call, robot_gesture, no_call) + prompt iteration |
| Ravinder | Dashboard: video player left, reasoning panel right, scoreboard top, event timeline bottom |
| Vivek | Robot controller: MentorPi speak + gesture mapping + SO-101 arm if available |

**Gate:** Agent processes 5 frames from tennis clip and produces valid calls.

### Phase 2: Integration (1:30 - 3:00) — 1h 30m
| Who | Task |
|-----|------|
| Visshwa + Kruthik | Wire agent → dashboard via WebSocket (live reasoning + score updates) |
| Ravinder | MCP server exposing referee tools (analyze_frame, get_score, lookup_rule) |
| Vivek | Wire agent → MentorPi (speak calls, gesture on scoring events) |
| ALL at 2:30 | End-to-end test: video → agent → dashboard + robot |

**Gate:** Full pipeline works end-to-end. Video plays, reasoning appears, score updates, robot speaks.

### Phase 3: Polish + A2A (3:00 - 4:15) — 1h 15m
| Who | Task |
|-----|------|
| Kruthik | Tune prompts — reduce false calls, improve reasoning quality |
| Ravinder | A2A AgentCard + endpoint, dashboard styling |
| Visshwa | Multi-frame context (pass last 3 frames for rally continuity) |
| Vivek | Demo flow: pick best 90-second segment, rehearse robot timing |

### Phase 4: Submit (4:15 - 5:00) — 45 min
| Who | Task |
|-----|------|
| Ravinder | Make repo public, clean README |
| Vivek | Record 1-min demo video |
| Kruthik | Write submission description |
| ALL at 4:45 | Submit at cerebralvalley.ai/e/nebius-build-sf/hackathon/submit |

---

## Model Decision

### Strategy
1. Start building with `Qwen/Qwen2-VL-72B-Instruct` — confirmed, works
2. Ask Nebius staff at event about Cosmos Reason 2 / Nemotron availability
3. Swap model ID if better option (one line change in env var)

### Options

| Model | Availability | Tool Calling | Vision | Latency | Notes |
|-------|-------------|-------------|--------|---------|-------|
| `Qwen/Qwen2-VL-72B-Instruct` | Token Factory (confirmed) | Yes | Image | ~1-2s | Default choice |
| `NVIDIA Nemotron Nano 2 VL` | Nebius AI Studio | TBD | Image + video | TBD | NVIDIA model, ask at event |
| `Cosmos Reason 2` | TBD on Nebius | TBD | Video + CoT | TBD | Best narrative, confirm availability |
| `deepseek-ai/DeepSeek-R1-0528` | Token Factory (confirmed) | Yes | Text only | ~0.5s | Commentary generation |
| `deepseek-ai/DeepSeek-V3-0324-fast` | Token Factory (confirmed) | Yes | Text only | ~0.3s | Fast commentary |

### Budget
- $400 total ($100 x 4 members)
- 2-min video at 1 fps = ~120 frames
- At ~$0.01-0.03 per VLM call = ~$1.20-3.60 per full run
- Budget allows 100+ full iterations — plenty

---

## Fallback Plan

If at 3:00 PM something isn't working:

| Problem | Fallback |
|---------|----------|
| VLM tool calling doesn't work | Parse JSON from raw text response |
| MentorPi won't connect | Dashboard + laptop TTS (macOS `say` command) |
| SO-101 arm not available | Skip Tier 2, focus on MentorPi + dashboard |
| Humanoid not available | Expected — it's a stretch goal |
| Nebius API down | Use OpenRouter credits ($20) as backup |
| Video extraction broken | Use pre-extracted frames (static images) |

**The minimum viable demo:** Dashboard showing video + live reasoning + auto-updating scoreboard. Everything else is bonus.

---

## What Judges Want to See (Optimizing for Criteria)

### Live Demo (45%)
- Video playing with real-time AI analysis appearing
- Robot announcing calls — visceral, memorable
- Scoreboard updating autonomously
- Show it working live, not a recording

### Creativity & Originality (35%)
- Nobody has built an agentic AI referee before
- Three action protocols (tool calling, MCP, A2A) in one system
- Physical embodiment across different robot form factors
- Sports + AI + robotics intersection is novel

### Impact Potential (20%)
- 240M+ tennis matches annually with zero officiating
- Amateur sports is massively underserved
- Path to real product: phone camera → cloud → voice calls
- Applicable beyond sports: any domain needing autonomous judgment from video
