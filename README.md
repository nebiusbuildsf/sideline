# Sideline — Download a coach. Deploy a ref. Upgrade the game.

Sideline is a modular AI sports robot designed to solve the growing shortage of coaches and referees in youth sports — a **$40B industry** growing ~10% annually as NIL money and private equity raise competition levels.

Powered by a **Qwen vision-language model** on **Nebius Token Factory**, Sideline watches gameplay in real time, delivers technical coaching feedback, and can switch into referee mode to make unbiased calls. Users can download sport-specific modules like *Tennis Coach Pro* to get drill feedback, movement corrections, and automated officiating.

**Built at Nebius.Build SF Hackathon — March 15, 2026**

## Demo Video

[![Sideline Demo](https://cdn.loom.com/sessions/thumbnails/a26c5048f556496487415a852eac6a1c-with-play.gif)](https://www.loom.com/share/a26c5048f556496487415a852eac6a1c)

[Watch the full demo →](https://www.loom.com/share/a26c5048f556496487415a852eac6a1c)

**Live Site:** [sideline-beige.vercel.app](https://sideline-beige.vercel.app/)

## How It Works

Sideline is an agentic AI — not an image classifier. It observes video frames, reasons with chain-of-thought, decides on calls with confidence scores, and acts through three protocols: Function Calls, MCP, and A2A.

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
