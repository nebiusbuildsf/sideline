# Sideline — Task Board

## Ravinder — Agent Pipeline + Dashboard
- [x] Agent core (observe → perceive → reason → decide → act)
- [x] Tool definitions (update_score, announce_call, robot_gesture, no_call)
- [x] Tennis scoring engine (points, games, sets, deuce/AD)
- [x] FastAPI server (REST + WebSocket + A2A endpoint)
- [x] Dashboard (scoreboard, video, reasoning panel, events)
- [x] Mock mode working
- [ ] Test with real Nebius API key
- [ ] Wire video upload to dashboard (drag & drop or file picker)
- [ ] MCP server (actions/mcp_server.py)
- [ ] Marketing page stubs for Kruthik
- [ ] Polish dashboard styling
- [ ] Pre-cache analysis for demo reliability

## Vivek — Hardware / Robotics
- [ ] MentorPi SSH + ROS2 connection
- [ ] ROSA integration (natural language → ROS2)
- [ ] MentorPi speak (TTS through speaker)
- [ ] MentorPi gesture mapping (arm signals for calls)
- [ ] SO-101 arm setup (if available)
- [ ] SO-101 gesture mapping (point out, arm up, signal fault)
- [ ] Robot controller base class (actions/robot/base.py)
- [ ] Wire robot to agent pipeline via WebSocket

## Visshwa — Model Work
- [ ] Nebius API key verified + test call working
- [ ] Evaluate Qwen2-VL-72B vs Nemotron vs Cosmos on tennis frames
- [ ] Prompt engineering for accurate tennis calls
- [ ] Multi-frame context optimization (how many frames for best accuracy?)
- [ ] Structured output parsing (ensure tool calls come back clean)
- [ ] Latency profiling (calls per second, cost per frame)
- [ ] Fallback handling (API errors, malformed responses)

## Kruthik — Marketing / Pitch
- [ ] Landing page content (what is Sideline, why it matters)
- [ ] Architecture diagram (clean SVG/image for pitch)
- [ ] About Us page (team bios + LinkedIn)
- [ ] 3-minute pitch script (see docs/DEMO.md)
- [ ] Q&A prep (see docs/DEMO.md)
- [ ] Record 1-minute demo video
- [ ] Write submission description
- [ ] Make repo public before 5 PM

## Integration (ALL — 3:30 PM)
- [ ] Agent → Dashboard end-to-end with real API
- [ ] Agent → Robot (MentorPi speaks calls)
- [ ] Full demo run-through with tennis clip
- [ ] Record backup video

## Submit (4:45 PM)
- [ ] Public GitHub repo
- [ ] 1-min demo video uploaded (YouTube/Loom)
- [ ] Submit at cerebralvalley.ai/e/nebius-build-sf/hackathon/submit
