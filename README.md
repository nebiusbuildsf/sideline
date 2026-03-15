# Sideline — AI Referee Agent

An agentic AI that watches sports video, reasons about every play with chain-of-thought, and acts through any physical form — dashboards, robotic arms, or humanoid robots.

**Built at Nebius.Build SF Hackathon — March 15, 2026**

## What It Does

Sideline is not an image classifier. It's an agent. It observes video frames, reasons with chain-of-thought using Nebius Token Factory VLMs, decides on referee calls with confidence scores, and acts through three protocols: Function Calls, MCP, and A2A.

```
Video → Frame Extraction → Nebius VLM (Qwen2.5-VL-72B)
    → Agent Reasoning (CoT: what happened → rule → call → confidence)
        → Actions:
           ├── Dashboard (scoreboard + reasoning panel)
           ├── Voice (TTS announcements)
           ├── MCP Server (any AI client can use referee tools)
           ├── A2A Protocol (multi-agent coordination)
           └── Robot (SO-101 arm / MentorPi / Unitree G1)
```

## Three Action Protocols

| Protocol | What | How |
|----------|------|-----|
| **Function Calls** | VLM decides which tools to invoke | Native OpenAI tool_use via Nebius API |
| **MCP Server** | Expose referee as external tools | Any MCP client (Claude, ChatGPT, Cursor) can use Sideline |
| **A2A Protocol** | Multi-agent coordination | Multiple cameras, agents coordinate via Google's A2A |

## Physical Embodiment

Same brain, any body:

| Tier | Hardware | Capability |
|------|----------|------------|
| 0 | Dashboard | Video + reasoning + scoreboard |
| 1 | MentorPi | Camera, speaker, mecanum wheels, ROSA/ROS2 |
| 2 | SO-101 Arm | 6-DOF gesture signals via HuggingFace LeRobot |
| 3 | Unitree G1 | Full humanoid referee |

## Sports Modules

- **Tennis** — Fault, out, ace, winner, let, double fault, full scoring (points/games/sets/deuce/AD)
- **Pickleball** — Kitchen violations, line calls, scoring
- **Volleyball** — Line calls, rotation tracking

## Quick Start

```bash
git clone git@github.com:nebiusbuildsf/sideline.git
cd sideline
uv sync
export NEBIUS_API_KEY="your-key"
uv run python server.py
# Open http://localhost:8000
```

### Pages

| Route | Page |
|-------|------|
| `/` | Landing page |
| `/referee` | Live referee dashboard with 3D robot sim |
| `/playground` | Model comparison + protocol visualization |
| `/robots` | Full 3D robot simulation (SO-101, Unitree G1, MentorPi) |
| `/architecture` | Interactive DAG — sensors to actuators |
| `/simulation` | 2D court simulation with physics |
| `/future` | Roadmap — edge deployment → world models → humanoid |

## Tech Stack

- **Inference:** Nebius Token Factory (Qwen2.5-VL-72B-Instruct)
- **Backend:** Python + FastAPI + WebSocket
- **Frontend:** Vanilla HTML/JS + Three.js (3D robots) + Tailwind
- **Protocols:** OpenAI Tool Calling + MCP + Google A2A
- **Robotics:** ROSA (NASA JPL) + LeRobot (HuggingFace) + ROS2
- **Simulation:** Three.js (3D) + Canvas (2D court + physics)

## Team

| Name | Role | LinkedIn |
|------|------|----------|
| Ravinder Jilkapally | Agent Pipeline + Dashboard | [jravinder](https://linkedin.com/in/jravinder) |
| Vivek Gopal Ramaswamy | Robotics + Architecture | [vivekgr](https://linkedin.com/in/vivekgr) |
| Kruthik Hulisandra | Domain Rules + Pitch | [kruthik-hulisandra](https://linkedin.com/in/kruthik-hulisandra) |
| Visshwa Balasubramanian | Model Work + Backend | [visshbala](https://linkedin.com/in/visshbala) |

## License

Built at Nebius.Build SF 2026. MIT License.
