# Sideline Agent Design

## Core Concept

Sideline is not a classifier. It's an agent — it observes, reasons, decides, acts, and remembers. Every frame is processed through a loop that maintains game state across the entire match.

## Agent Loop

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   ┌──────────┐                                      │
│   │ OBSERVE  │ Extract frame from video (1-2 fps)   │
│   └────┬─────┘                                      │
│        ▼                                            │
│   ┌──────────┐                                      │
│   │ PERCEIVE │ Send frame + state to Nebius VLM     │
│   └────┬─────┘                                      │
│        ▼                                            │
│   ┌──────────┐                                      │
│   │ REASON   │ Chain-of-thought: what → rule → call │
│   └────┬─────┘                                      │
│        ▼                                            │
│   ┌──────────┐                                      │
│   │ DECIDE   │ Classify call + confidence score     │
│   └────┬─────┘                                      │
│        ▼                                            │
│   ┌──────────┐                                      │
│   │ ACT      │ Tool calls / MCP / A2A → actions     │
│   └────┬─────┘                                      │
│        ▼                                            │
│   ┌──────────┐                                      │
│   │ REMEMBER │ Update game state + history          │
│   └────┬─────┘                                      │
│        │                                            │
│        └──────────────────── loop ──────────────────┘
```

## Agent Core

```python
class SidelineAgent:
    def __init__(self, sport: str, model: str, robot=None):
        self.sport = sport
        self.model = model
        self.robot = robot
        self.state = GameState(sport)
        self.vlm = NebiusVLM(model)
        self.rules = RulesEngine(sport)
        self.tools = ToolRegistry()
        self.history = []

    async def run(self, video_source):
        async for frame in video_source.frames():
            # PERCEIVE
            perception = await self.vlm.analyze(
                frame=frame,
                context=self.state.summary(),
                prompt=self.rules.referee_prompt()
            )

            # REASON + DECIDE (model returns tool calls)
            decision = self.parse_decision(perception)

            # ACT
            await self.execute(decision)

            # REMEMBER
            self.state.apply(decision)
            self.history.append(decision)

    async def execute(self, decision):
        for action in decision.actions:
            if action.type == "score_update":
                self.state.update_score(action.player, action.reason)
            elif action.type == "announcement":
                await self.announce(action.text)
            elif action.type == "gesture":
                if self.robot:
                    await self.robot.gesture(action.gesture_type)
            elif action.type == "commentary":
                await self.broadcast(action.text)
```

## Game State

```python
class GameState:
    def __init__(self, sport: str):
        self.sport = sport
        self.players = {"p1": "Player 1", "p2": "Player 2"}
        self.score = self._init_score(sport)
        self.server = "p1"
        self.rally_active = False
        self.frame_count = 0
        self.last_call = None
        self.events = []

    def _init_score(self, sport):
        if sport == "tennis":
            return {
                "points": {"p1": "0", "p2": "0"},
                "games": {"p1": 0, "p2": 0},
                "sets": {"p1": 0, "p2": 0},
            }
        # Extend for cricket, pickleball, etc.

    def summary(self) -> str:
        """One-line summary for VLM context."""
        if self.sport == "tennis":
            return (
                f"Tennis | {self.score['points']['p1']}-{self.score['points']['p2']} "
                f"(Games: {self.score['games']['p1']}-{self.score['games']['p2']}, "
                f"Sets: {self.score['sets']['p1']}-{self.score['sets']['p2']}) | "
                f"Server: {self.server} | Last: {self.last_call or 'none'}"
            )

    def apply(self, decision):
        if decision.score_update:
            self._update_tennis_score(decision.point_winner)
        self.last_call = decision.call_type
        self.frame_count += 1
        self.events.append(decision.to_dict())
```

### Tennis Scoring Logic
```python
TENNIS_POINTS = ["0", "15", "30", "40", "AD"]

def _update_tennis_score(self, winner: str):
    loser = "p2" if winner == "p1" else "p1"
    w_pts = self.score["points"][winner]
    l_pts = self.score["points"][loser]

    if w_pts == "40" and l_pts != "40" and l_pts != "AD":
        # Game won
        self._win_game(winner)
    elif w_pts == "40" and l_pts == "40":
        # Deuce → AD
        self.score["points"][winner] = "AD"
    elif w_pts == "AD":
        # AD → Game won
        self._win_game(winner)
    elif l_pts == "AD":
        # Opponent had AD → back to deuce
        self.score["points"][loser] = "40"
    else:
        # Normal progression
        idx = TENNIS_POINTS.index(w_pts)
        self.score["points"][winner] = TENNIS_POINTS[idx + 1]

def _win_game(self, winner: str):
    self.score["points"] = {"p1": "0", "p2": "0"}
    self.score["games"][winner] += 1
    self._toggle_server()
    if self.score["games"][winner] >= 6:
        diff = self.score["games"][winner] - self.score["games"]["p2" if winner == "p1" else "p1"]
        if diff >= 2:
            self._win_set(winner)
```

## Decision Object

Every reasoning cycle produces a decision:

```python
@dataclass
class RefereeDecision:
    call_type: str          # "fault", "out", "in", "let", "ace", "winner", "double_fault", "no_call"
    confidence: float       # 0.0 - 1.0
    reasoning: str          # Chain-of-thought explanation
    announcement: str       # What to say out loud
    score_update: bool      # Does this affect the score?
    point_winner: str       # "p1" or "p2" (if score_update)
    gesture: str            # Robot gesture type
    actions: list           # List of action objects to execute

    def to_dict(self):
        return {
            "call": self.call_type,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "announcement": self.announcement,
            "score_update": self.score_update,
            "point_winner": self.point_winner,
            "gesture": self.gesture,
            "timestamp": time.time(),
        }
```

## Prompt Strategy

### System Prompt
```
You are Sideline, an AI sports referee agent watching a tennis match.

You see one frame at a time. For each frame, you must:
1. Describe what you observe (player positions, ball location, court lines)
2. Determine if a scoring event occurred
3. Apply the correct tennis rule
4. Make the call with a confidence score
5. Call the appropriate tools

Current match state: {game_state_summary}
Last 3 calls: {recent_history}

IMPORTANT:
- Only make a call when you see a clear scoring event
- Say "no_call" if the rally is ongoing with no event
- Use the tools provided to update score, announce, and signal gestures
```

### Multi-Frame Context
```python
def build_messages(self, frame, state):
    messages = [
        {"role": "system", "content": self.system_prompt(state)},
    ]

    # Include last 2-3 frames for rally continuity
    for prev_frame in self.recent_frames[-3:]:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": f"Previous frame ({prev_frame.timestamp}):"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{prev_frame.b64}"}}
            ]
        })
        messages.append({
            "role": "assistant",
            "content": prev_frame.analysis
        })

    # Current frame
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": f"Current frame. Match state: {state.summary()}. What's the call?"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame.b64}"}}
        ]
    })

    return messages
```

---

## Three Action Protocols

### 1. Function Calls (Tool Use via Nebius API)

The VLM model decides which tools to call based on what it sees. This is native OpenAI-compatible tool calling.

```python
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
                    "reason": {"type": "string", "description": "Why the point was awarded (ace, winner, fault, etc.)"}
                },
                "required": ["player", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "announce_call",
            "description": "Announce a referee call out loud",
            "parameters": {
                "type": "object",
                "properties": {
                    "call_type": {"type": "string", "enum": ["fault", "out", "in", "let", "ace", "winner", "double_fault", "no_call"]},
                    "announcement": {"type": "string", "description": "What to say (e.g. 'Fault! Second serve.')"},
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
            "description": "Signal the call with a physical robot gesture",
            "parameters": {
                "type": "object",
                "properties": {
                    "gesture": {"type": "string", "enum": ["point_out", "arm_up", "wave_off", "hold", "signal_fault", "idle"]},
                    "direction": {"type": "string", "enum": ["left", "right", "center"]}
                },
                "required": ["gesture"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "no_call",
            "description": "Rally is ongoing, no scoring event. Call this when nothing notable happened.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Brief note on what's happening (e.g. 'Rally continues, forehand exchange')"}
                },
                "required": ["description"]
            }
        }
    }
]

# Usage with Nebius
response = client.chat.completions.create(
    model=MODEL_VISION,
    messages=messages,
    tools=tools,
    tool_choice="auto",
    max_tokens=500
)

# Process tool calls
for tool_call in response.choices[0].message.tool_calls or []:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    if name == "update_score":
        state.update_score(**args)
    elif name == "announce_call":
        await tts.speak(args["announcement"])
        await broadcast("call", args)
    elif name == "robot_gesture":
        await robot.gesture(**args)
    elif name == "no_call":
        await broadcast("status", args)
```

### 2. MCP — Model Context Protocol

Expose Sideline capabilities as an MCP server. Any MCP client (Claude, ChatGPT, VS Code, Cursor) can connect and use referee tools.

**Why MCP:** Decouples the agent brain from the tools. Swap the robot, swap the rules DB, swap the search provider — agent code stays the same.

```python
# actions/mcp_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sideline-referee")

@mcp.tool()
async def analyze_frame(frame_base64: str, sport: str = "tennis") -> str:
    """Analyze a sports video frame and return the referee's call.

    Args:
        frame_base64: Base64-encoded JPEG image
        sport: Sport being played (tennis, cricket, pickleball)
    """
    decision = await agent.perceive_and_decide(frame_base64, sport)
    return json.dumps(decision.to_dict())

@mcp.tool()
async def get_score() -> str:
    """Get the current match score and game state."""
    return json.dumps(agent.state.to_dict())

@mcp.tool()
async def get_call_history(last_n: int = 10) -> str:
    """Get the last N referee calls with reasoning chains.

    Args:
        last_n: Number of recent calls to return
    """
    return json.dumps(agent.history[-last_n:])

@mcp.tool()
async def lookup_rule(sport: str, situation: str) -> str:
    """Look up the official rule for a game situation using Tavily search.

    Args:
        sport: Sport name (tennis, cricket, pickleball)
        situation: Description (e.g. 'ball hits net on serve')
    """
    from tavily import TavilyClient
    tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    result = tavily.search(f"{sport} official rules: {situation}")
    return json.dumps(result["results"][:3])

@mcp.tool()
async def robot_action(action: str, params: str = "{}") -> str:
    """Send a command to the connected robot.

    Args:
        action: Action type — speak, gesture, or move
        params: JSON string of parameters (e.g. '{"text": "Fault!"}')
    """
    p = json.loads(params)
    await robot_controller.execute(action, **p)
    return f"Executed: {action}({p})"

@mcp.resource("sideline://score")
async def score_resource() -> str:
    """Current match score as a live resource."""
    return json.dumps(agent.state.score)

# MCP server topology:
#
# Agent (MCP Client)
#     │
#     ├──▶ MCP Server: sideline-referee (this file)
#     │    ├── tool: analyze_frame
#     │    ├── tool: get_score
#     │    ├── tool: get_call_history
#     │    ├── tool: lookup_rule (→ Tavily)
#     │    ├── tool: robot_action
#     │    └── resource: sideline://score
#     │
#     ├──▶ MCP Server: tavily-search (optional, separate)
#     │    └── tool: search(query)
#     │
#     └──▶ MCP Server: openrouter (optional, separate)
#          └── tool: generate_commentary(context)

# Run:
# uv add "mcp[cli]"
# uv run python -m actions.mcp_server
if __name__ == "__main__":
    mcp.run(transport="stdio")  # or "sse" for HTTP
```

### 3. A2A — Agent-to-Agent Protocol

Google's open protocol for agents to discover and communicate with each other via JSON-RPC 2.0 over HTTP(S). Each Sideline instance is an agent with an AgentCard.

**Why A2A:** Multiple Sideline agents can cover different camera angles, different sports, or different roles (referee, commentator, scorekeeper) and coordinate decisions.

```python
# actions/a2a_agent.py
# SDK: pip install a2a-sdk
# Spec: https://a2a-protocol.org/latest/specification/

# AgentCard — served at /.well-known/agent.json
AGENT_CARD = {
    "name": "sideline-referee",
    "description": "AI sports referee — watches video, reasons about plays, makes calls",
    "url": "http://localhost:8000",
    "version": "1.0.0",
    "provider": {
        "name": "Sideline",
        "description": "Agentic AI sports referee built at Nebius.Build SF"
    },
    "capabilities": {
        "streaming": True,
        "pushNotifications": False
    },
    "skills": [
        {
            "id": "analyze_play",
            "name": "Analyze Play",
            "description": "Analyze a sports video frame and make a referee call",
            "tags": ["sports", "tennis", "referee", "vision"],
            "inputModes": ["application/json"],
            "outputModes": ["application/json"]
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

# Task lifecycle:
#   submitted → working → completed
#                       → failed
#                       → canceled
#
# JSON-RPC methods:
#   tasks/send          — send a message, create or continue a task
#   tasks/sendSubscribe — same but with SSE streaming
#   tasks/get           — poll task status
#   tasks/cancel        — cancel a running task

# Multi-agent scenarios:
#
# ┌─────────────────┐  A2A  ┌───────────────┐  A2A  ┌─────────────────┐
# │  Camera 1       │◀─────▶│  Coordinator  │◀─────▶│  Camera 2       │
# │  Referee Agent  │       │    Agent      │       │  Referee Agent  │
# └─────────────────┘       └───────┬───────┘       └─────────────────┘
#                                   │ A2A
#                           ┌───────▼───────┐
#                           │  Commentary   │
#                           │    Agent      │
#                           └───────┬───────┘
#                                   │ A2A
#                           ┌───────▼───────┐
#                           │    Robot      │
#                           │    Agent      │
#                           └───────────────┘
#
# Flow:
# 1. Camera agents watch different angles, each produces referee decisions
# 2. Coordinator agent compares decisions, resolves conflicts (majority vote)
# 3. Commentary agent receives final decision, generates play-by-play
# 4. Robot agent receives final decision, executes physical gesture + speech

# A2A endpoint implementation (FastAPI):
from fastapi import FastAPI

app = FastAPI()

@app.get("/.well-known/agent.json")
async def agent_card():
    return AGENT_CARD

@app.post("/a2a")
async def handle_task(request: dict):
    """JSON-RPC 2.0 handler for A2A tasks."""
    method = request.get("method")
    params = request.get("params", {})

    if method == "tasks/send":
        message = params.get("message", {})
        skill = message.get("parts", [{}])[0].get("text", "")

        # Route to appropriate skill
        if "analyze" in skill:
            result = await agent.analyze_current_frame()
        elif "score" in skill:
            result = agent.state.to_dict()
        elif "commentary" in skill:
            result = await agent.generate_commentary()
        else:
            result = {"error": "Unknown skill"}

        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "id": str(uuid4()),
                "status": {"state": "completed"},
                "artifacts": [{"parts": [{"text": json.dumps(result)}]}]
            }
        }
```

---

## How the Three Protocols Work Together

```
Video Frame
    │
    ▼
Nebius VLM (with tool definitions)
    │
    ├── Tool Call: update_score("p1", "ace")     ← Function Calling
    ├── Tool Call: announce_call("ace", "Ace!")   ← Function Calling
    └── Tool Call: robot_gesture("arm_up")        ← Function Calling
         │
         ▼
    Tool Execution Layer
         │
         ├── Direct execution (fast, internal)
         │
         ├── MCP Server call (standardized, swappable)
         │   └── lookup_rule("tennis", "serve speed") → Tavily
         │
         └── A2A message (multi-agent coordination)
             └── tasks/send → Commentary Agent → "Brilliant ace!"
```

**In practice for the hackathon:**
- Tool calling is the primary mechanism (model decides what to do)
- MCP server makes it pluggable (demo: "any MCP client can use our referee")
- A2A shows the multi-agent vision (demo: coordinator + multiple cameras)
