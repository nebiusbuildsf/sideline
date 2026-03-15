# CLAUDE.md

## Project: Sideline

Sideline is an agentic AI sports referee built at Nebius.Build SF hackathon (March 15, 2026). It watches sports video, reasons about plays using chain-of-thought, and acts through physical robots and digital interfaces.

**Track:** Statement 1 — Edge Inference & Agents

## Builder Principles

We do not build to impress. We take care of things that make an impression on everything.

- **Problem first.** State the problem in one sentence or we don't understand it.
- **Accuracy over ambition.** Honest claim over impressive one. Credibility compounds.
- **Production is the bar.** Demo is not done. Prototype is not shipped.
- **Cut scope, not quality.** Smaller thing that works > bigger thing that kind of works.
- **Evidence, not opinion.** Back claims with data. Measure it.
- **Pick what's easier to change later.** Name tradeoffs explicitly.

### For Claude
1. Do not pad
2. Do not assume — ask
3. Do not overclaim
4. Show reasoning
5. Push back when it matters
6. Match the pace
7. Everything moves toward something that runs in the real world

### Voice
- No "in today's rapidly evolving landscape"
- No "delve" or "cutting edge"
- Contrast to reframe
- Credit the humans
- Invite, do not lecture

## How We Work

- **Demo-first development.** Build what the audience sees first, then wire the brain.
- **One command to run.** Every component must start with a single command.
- **Mock everything first.** Every external dependency (VLM, robot, TTS) has a mock adapter so we can develop without them.
- **Swap, don't rewrite.** Model IDs, robot backends, and TTS providers are env vars — one line change to swap.
- **Commit without Claude Code co-authoring.** Never add `Co-authored-by: Claude` to commits.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SIDELINE AGENT                               │
│                                                                     │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  VIDEO    │───▶│  PERCEPTION  │───▶│  REASONING   │              │
│  │  INPUT    │    │  (Nebius VLM)│    │  (CoT Agent) │              │
│  └──────────┘    └──────────────┘    └──────┬───────┘              │
│                                             │                       │
│                        ┌────────────────────┼────────────────┐      │
│                        │                    │                │      │
│                        ▼                    ▼                ▼      │
│                 ┌────────────┐    ┌──────────────┐  ┌────────────┐ │
│                 │ TOOL CALLS │    │     MCP      │  │    A2A     │ │
│                 │ (internal) │    │  (external   │  │ (agent-to- │ │
│                 │            │    │   tools)     │  │  agent)    │ │
│                 └──────┬─────┘    └──────┬───────┘  └─────┬──────┘ │
│                        │                 │                │        │
└────────────────────────┼─────────────────┼────────────────┼────────┘
                         │                 │                │
              ┌──────────▼──────────┐      │                │
              │      ACTIONS        │      │                │
              │                     │      │                │
              │  • Score update     │◀─────┘                │
              │  • Voice announce   │                       │
              │  • Dashboard update │◀──────────────────────┘
              │  • Robot gesture    │
              │  • Robot movement   │
              └─────────────────────┘
```

## Three Action Protocols

### 1. Function Calls (Internal Tools)
Direct function invocations within the agent pipeline. Used for score updates, state management, and local actions.

```python
# Agent decides to update score
tools = [
    {"name": "update_score", "params": {"player": "player1", "points": 15}},
    {"name": "announce", "params": {"text": "Fault! Second serve."}},
    {"name": "gesture", "params": {"type": "arm_raise_right"}},
]
```

### 2. MCP — Model Context Protocol (External Tools)
Standardized protocol for connecting the agent to external data sources and tools. The agent is an MCP client that connects to MCP servers exposing capabilities.

```
Agent (MCP Client)
    │
    ├──▶ MCP Server: Sports Rules DB
    │    └── tool: lookup_rule(sport, situation)
    │    └── tool: get_scoring_rules(sport)
    │
    ├──▶ MCP Server: Tavily Search
    │    └── tool: search_rules(query)
    │
    ├──▶ MCP Server: Robot Control
    │    └── tool: move(direction, speed)
    │    └── tool: speak(text)
    │    └── tool: gesture(type)
    │
    └──▶ MCP Server: Scoreboard
         └── tool: update_score(player, points)
         └── resource: current_score
```

**Why MCP:** The agent doesn't need to know HOW to control a robot or look up rules. It just calls tools. Swap the MCP server, swap the robot — agent code stays the same.

### 3. A2A — Agent-to-Agent Protocol (Multi-Agent)
Google's open protocol for agents to discover and communicate with each other. Each Sideline agent exposes an AgentCard describing its capabilities.

```json
{
    "name": "sideline-referee",
    "description": "AI sports referee agent — watches video, reasons about plays, makes calls",
    "capabilities": ["tennis", "cricket", "pickleball"],
    "input": "video_frame",
    "output": "referee_decision",
    "endpoint": "http://localhost:8000/a2a"
}
```

**Multi-agent scenarios:**
- **Multiple cameras:** Each Sideline agent watches a different angle, they compare decisions via A2A
- **Specialist agents:** One agent for ball tracking, one for rules, one for scoring — coordinate via A2A
- **Commentary agent:** Receives referee decisions via A2A, generates play-by-play
- **Robot agent:** Receives calls via A2A, translates to physical actions

```
┌─────────────┐  A2A  ┌─────────────┐  A2A  ┌─────────────┐
│  Camera 1   │◀─────▶│ Coordinator │◀─────▶│  Camera 2   │
│  Referee    │       │   Agent     │       │  Referee    │
└─────────────┘       └──────┬──────┘       └─────────────┘
                             │ A2A
                      ┌──────▼──────┐
                      │   Robot     │
                      │   Agent     │
                      └─────────────┘
```

## Physical Embodiment Tiers

| Tier | Hardware | Capability | Status |
|------|----------|------------|--------|
| 0 | Dashboard only | Video + reasoning + scoreboard | Always works |
| 1 | MentorPi (HiWonder) | Camera, speaker, mecanum wheels, servos, ROS2 | Confirmed at event |
| 2 | SO-101 (LeRobot/HuggingFace) | 6-DOF arm, Feetech servos, leader-follower | Available at event |
| 3 | Unitree G1 Humanoid | Full body, walking, gestures | Request at event |

### MentorPi (Tier 1)
- Tracked chassis with mecanum wheels
- Camera module (Pi Camera or similar)
- Speaker grille for TTS
- Lidar + depth camera
- ROS2 + Python control
- Docs: https://docs.hiwonder.com/projects/MentorPi/en/latest/

### SO-101 Robotic Arm (Tier 2)
- 6x STS3215 Feetech servo motors
- Leader-follower teleoperation
- LeRobot SDK: `pip install lerobot[feetech]`
- Calibration: `lerobot-calibrate`
- Can signal calls with arm gestures (point out, raise for goal, etc.)

### Unitree G1 Humanoid (Tier 3)
- Full body humanoid — walking, gesturing, head tracking
- Shared fleet at event (8-10 units), subject to safety review
- Request access at 9 AM

## Nebius Model Configuration

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ["NEBIUS_API_KEY"]
)

# Primary: Vision model for frame analysis
MODEL_VISION = os.environ.get("SIDELINE_VISION_MODEL", "Qwen/Qwen2-VL-72B-Instruct")

# Secondary: Text model for commentary
MODEL_TEXT = os.environ.get("SIDELINE_TEXT_MODEL", "deepseek-ai/DeepSeek-V3-0324-fast")

# If Cosmos Reason 2 available on Nebius — swap in:
# MODEL_VISION = "nvidia/Cosmos-Reason2-8B"
```

**Available Nebius models:**
| Model | Type | Use |
|-------|------|-----|
| `Qwen/Qwen2-VL-72B-Instruct` | Vision-Language | Frame analysis (default) |
| `NVIDIA Nemotron Nano 2 VL` | Vision-Language | Video understanding |
| `Cosmos Reason 2` | Video reasoning | Sports CoT (confirm availability) |
| `deepseek-ai/DeepSeek-R1-0528` | Text reasoning | Deep CoT text |
| `deepseek-ai/DeepSeek-V3-0324-fast` | Text | Fast commentary |

## Agent Loop

```python
class SidelineAgent:
    """
    Observe → Perceive → Reason → Decide → Act → Remember
    """

    def run(self, video_source):
        while self.game_active:
            # 1. OBSERVE — extract frame
            frame = self.video.next_frame()

            # 2. PERCEIVE — send to Nebius VLM
            perception = self.vlm.analyze(frame, self.state)

            # 3. REASON — chain of thought
            reasoning = self.reason(perception, self.rules, self.state)

            # 4. DECIDE — what's the call
            decision = self.decide(reasoning)

            # 5. ACT — execute through tools/MCP/A2A
            self.execute_actions(decision)

            # 6. REMEMBER — update game state
            self.state.update(decision)
```

## Game State

```python
state = {
    "sport": "tennis",
    "players": {"p1": "Player 1", "p2": "Player 2"},
    "score": {
        "points": {"p1": 0, "p2": 0},       # 0, 15, 30, 40, AD
        "games": {"p1": 0, "p2": 0},
        "sets": {"p1": 0, "p2": 0},
    },
    "server": "p1",
    "rally_active": False,
    "history": [],          # all calls
    "frame_count": 0,
    "last_call": None,
}
```

## Project Structure

```
sideline/
├── CLAUDE.md              # This file
├── README.md              # Project overview
├── pyproject.toml         # uv/pip config
├── server.py              # FastAPI main server
├── agent/
│   ├── core.py            # SidelineAgent class
│   ├── perception.py      # Nebius VLM integration
│   ├── reasoning.py       # CoT reasoning + decision making
│   ├── state.py           # Game state management
│   ├── rules/
│   │   ├── tennis.py      # Tennis rules + scoring
│   │   ├── cricket.py     # Cricket rules (stretch)
│   │   └── base.py        # Base rules interface
│   └── prompts.py         # Sport-specific VLM prompts
├── actions/
│   ├── tools.py           # Function call tools (score, announce)
│   ├── mcp_server.py      # MCP server exposing referee tools
│   ├── a2a_agent.py       # A2A AgentCard + task handling
│   ├── tts.py             # Text-to-speech (MiniMax / system)
│   └── robot/
│       ├── base.py        # Robot interface
│       ├── mentorpi.py    # MentorPi controller
│       ├── so101.py       # SO-101 arm controller
│       └── mock.py        # Mock robot for testing
├── dashboard/
│   └── index.html         # Video + reasoning + scoreboard UI
├── video/
│   ├── extractor.py       # Frame extraction from video
│   └── clips/             # Tennis demo clips
├── docs/
│   ├── PLAN.md
│   ├── AGENT.md
│   ├── DEMO.md
│   ├── MODELS.md
│   └── sketches/
└── tests/
    └── test_mock.py       # Dry-run tests with mock adapters
```

## Development Commands

```bash
# Setup
uv init
uv add openai fastapi uvicorn httpx opencv-python websockets

# Run server
export NEBIUS_API_KEY="..."
uv run python server.py

# Run with mock (no API needed)
uv run python server.py --mock

# Run agent standalone
uv run python -m agent.core --video video/clips/tennis.mp4 --sport tennis

# Run MCP server
uv run python -m actions.mcp_server

# Run tests
uv run python -m tests.test_mock
```

## Environment Variables

```bash
# Required
NEBIUS_API_KEY=             # Nebius Token Factory API key

# Optional — model override
SIDELINE_VISION_MODEL=      # Default: Qwen/Qwen2-VL-72B-Instruct
SIDELINE_TEXT_MODEL=         # Default: deepseek-ai/DeepSeek-V3-0324-fast

# Optional — partner integrations
OPENROUTER_API_KEY=         # Multi-model commentary
TAVILY_API_KEY=             # Rules search
MINIMAX_API_KEY=            # TTS for robot voice

# Optional — robot
MENTORPI_HOST=              # MentorPi IP address
SO101_PORT=                 # SO-101 serial port
```

## Team

| Name | LinkedIn | Role |
|------|----------|------|
| Ravinder Jilkapally | linkedin.com/in/jravinder | Demo UI + agent pipeline |
| Vivek Gopal Ramaswamy | linkedin.com/in/vivekgr | Robotics + architecture + pitch |
| Kruthik Hulisandra | linkedin.com/in/kruthik-hulisandra | Domain rules + agent logic |
| Visshwa Balasubramanian | linkedin.com/in/visshbala | Backend engine + robot control |

## Hackathon Context

- **Event:** Nebius.Build SF — March 15, 2026
- **Location:** SHACK15, Ferry Building, SF
- **WiFi:** SHACK15_Members / M3mb3r$4L!f3
- **Hacking:** 10:40 AM - 5:00 PM (6h 20m)
- **Submission:** Public repo + 1-min demo video at https://cerebralvalley.ai/e/nebius-build-sf/hackathon/submit
- **Budget:** $400 Nebius credits ($100 x 4)
- **Credits link:** https://nebius.com/promo-code?utm_promo_event_code=2026-03-hackathon-nebius-build-sf&utm_promo_activation_code=NEBIUS-BUILD-SF
- **Contact:** ivan@cerebralvalley.ai or Discord

### Judging Criteria (UPDATED — from official page)

| Criteria | Weight | What They Want |
|----------|--------|----------------|
| **Live Demo** | **45%** | Does it work live? How well implemented? How is it presented? |
| **Creativity & Originality** | **35%** | Has this been seen before? How unique in the field? Unique approach to problem statements? |
| **Impact Potential** | **20%** | Long-term potential? Lasting impact beyond hackathon? |

**Key insight:** Creativity is 35% — not just "does it work" but "has anyone done this before?" An AI referee agent that acts through physical robots is novel.

### Partner Credits

| Partner | How to Claim |
|---------|-------------|
| Nebius | https://nebius.com/promo-code (code above) |
| OpenRouter | See Notion link at event |
| Tavily | https://docs.tavily.com/welcome |
| Toloka | Code `NEBIUSBUILD30` at registration |
| Cline | Form at event |
| HuggingFace | First 150 get 2mo HF Pro — join Nebius.Build SF org on HF |
| Oumi | Quickstart + training guide at event |

## Implementation Reference: Tool Calling with Nebius

Nebius uses OpenAI-compatible API. Tool calling works the same way:

```python
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ["NEBIUS_API_KEY"]
)

# Define tools the model can call
tools = [
    {
        "type": "function",
        "function": {
            "name": "update_score",
            "description": "Update the game score after a point is won",
            "parameters": {
                "type": "object",
                "properties": {
                    "player": {"type": "string", "enum": ["p1", "p2"]},
                    "reason": {"type": "string", "description": "Why the point was awarded"}
                },
                "required": ["player", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "announce_call",
            "description": "Announce a referee call (fault, out, let, ace)",
            "parameters": {
                "type": "object",
                "properties": {
                    "call_type": {"type": "string", "enum": ["fault", "out", "in", "let", "ace", "winner", "double_fault"]},
                    "announcement": {"type": "string", "description": "What to say out loud"},
                    "confidence": {"type": "number", "description": "0-1 confidence in the call"}
                },
                "required": ["call_type", "announcement"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "robot_gesture",
            "description": "Signal a call through physical robot gesture",
            "parameters": {
                "type": "object",
                "properties": {
                    "gesture": {"type": "string", "enum": ["point_out", "arm_up", "wave_off", "hold", "signal_fault"]},
                    "direction": {"type": "string", "enum": ["left", "right", "center"], "description": "Which direction to gesture"}
                },
                "required": ["gesture"]
            }
        }
    }
]

# Send frame + game state, let model decide which tools to call
response = client.chat.completions.create(
    model="Qwen/Qwen2-VL-72B-Instruct",
    messages=[
        {"role": "system", "content": REFEREE_SYSTEM_PROMPT},
        {"role": "user", "content": [
            {"type": "text", "text": f"Current score: {game_state}. Analyze this frame:"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}}
        ]}
    ],
    tools=tools,
    tool_choice="auto",
    max_tokens=500
)

# Process tool calls from the model
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        # Execute: update_score(**args), announce_call(**args), robot_gesture(**args)
```

## Implementation Reference: MCP Server

Expose Sideline's referee capabilities as an MCP server so any MCP-compatible client (Claude, ChatGPT, Cursor, etc.) can use them.

```python
# actions/mcp_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sideline-referee")

@mcp.tool()
async def analyze_frame(frame_base64: str, sport: str = "tennis") -> str:
    """Analyze a sports video frame and return the referee's call.

    Args:
        frame_base64: Base64-encoded JPEG image of the frame
        sport: Sport being played (tennis, cricket, pickleball)
    """
    result = await agent.perceive_and_decide(frame_base64, sport)
    return json.dumps(result)

@mcp.tool()
async def get_score() -> str:
    """Get the current game score."""
    return json.dumps(agent.state["score"])

@mcp.tool()
async def get_call_history(last_n: int = 10) -> str:
    """Get the last N referee calls with reasoning.

    Args:
        last_n: Number of recent calls to return
    """
    return json.dumps(agent.state["history"][-last_n:])

@mcp.tool()
async def lookup_rule(sport: str, situation: str) -> str:
    """Look up the official rule for a given game situation.

    Args:
        sport: Sport (tennis, cricket, pickleball)
        situation: Description of the situation (e.g. "ball hits the net on serve")
    """
    # Uses Tavily search to find official rules
    result = await tavily_client.search(f"{sport} official rules: {situation}")
    return result

@mcp.tool()
async def robot_action(action: str, params: str = "{}") -> str:
    """Send a command to the connected robot.

    Args:
        action: Action type (speak, gesture, move)
        params: JSON string of action parameters
    """
    p = json.loads(params)
    await robot_controller.execute(action, **p)
    return f"Robot executed: {action}"

# Run: uv run python -m actions.mcp_server
if __name__ == "__main__":
    mcp.run(transport="stdio")  # or transport="sse" for HTTP
```

**MCP SDK:** `uv add "mcp[cli]"`
**Docs:** https://modelcontextprotocol.io/docs/getting-started/intro

## Implementation Reference: A2A Agent

Expose Sideline as an A2A-compatible agent so other agents can discover and interact with it.

```python
# actions/a2a_agent.py
# A2A uses JSON-RPC 2.0 over HTTP(S)
# SDK: pip install a2a-sdk

# AgentCard — published at /.well-known/agent.json
AGENT_CARD = {
    "name": "sideline-referee",
    "description": "AI sports referee — watches video, reasons about plays, makes calls",
    "url": "http://localhost:8000",
    "version": "1.0.0",
    "capabilities": {
        "streaming": True,
        "pushNotifications": False
    },
    "skills": [
        {
            "id": "analyze_play",
            "name": "Analyze Play",
            "description": "Analyze a sports video frame and make a referee call",
            "tags": ["sports", "tennis", "referee", "vision"]
        },
        {
            "id": "get_score",
            "name": "Get Score",
            "description": "Return current game score and match state"
        },
        {
            "id": "commentary",
            "name": "Generate Commentary",
            "description": "Generate play-by-play commentary for the current action"
        }
    ],
    "defaultInputModes": ["application/json"],
    "defaultOutputModes": ["application/json"]
}

# Task lifecycle: submitted → working → completed/failed
# JSON-RPC methods:
#   tasks/send     — send a message to create/continue a task
#   tasks/get      — poll task status
#   tasks/cancel   — cancel a running task

# Multi-agent example:
# 1. Commentary Agent discovers Sideline via AgentCard
# 2. Sends task: "What just happened in this frame?"
# 3. Sideline responds with referee analysis
# 4. Commentary Agent generates exciting play-by-play from the analysis
```

**A2A SDK:** `pip install a2a-sdk`
**Spec:** https://a2a-protocol.org/latest/specification/
**Repo:** https://github.com/a2aproject/A2A

## Key Constraint

**NEW WORK ONLY.** All code must be written from scratch at the event. No copying from RefereAI, Undervolt, or any other repo. Domain knowledge and patterns in our heads are fine. Code is not.
