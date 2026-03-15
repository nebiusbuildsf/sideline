# Sideline Agent Design

## Agent Loop

```
while game_running:
    1. OBSERVE  — Extract frame from video
    2. PERCEIVE — Send frame to Nebius VLM with sport-specific prompt
    3. REASON   — Parse CoT: what happened, what rule applies, what's the call
    4. DECIDE   — Classify: rally, fault, let, ace, out, winner, score change
    5. ACT      — Execute actions:
                   a. Update scoreboard
                   b. Announce call (TTS → speaker / robot)
                   c. Log reasoning to dashboard
                   d. Move robot (if applicable)
    6. REMEMBER — Maintain game state (score, set, game, server)
```

## Agent State

```python
{
    "sport": "tennis",
    "score": {"player1": 0, "player2": 0},
    "set_score": {"player1": 0, "player2": 0},
    "game_score": {"player1": 0, "player2": 0},
    "server": "player1",
    "history": [],          # list of all calls
    "current_rally": [],    # frames in current rally
    "last_call": null,
    "frame_count": 0
}
```

## Output Actions

Each reasoning cycle produces an action object:

```python
{
    "call": "fault",                    # or "ace", "out", "in", "let", "winner"
    "confidence": 0.85,
    "reasoning": "Ball landed beyond...",
    "score_update": true,
    "announcement": "Fault! Second serve.",
    "gesture": "arm_raise_right"        # for robot
}
```

## Prompt Strategy

### System Prompt
```
You are Sideline, an AI sports referee agent. You watch tennis matches frame by frame.
For each frame, analyze:
1. What is happening in this frame?
2. What tennis rule applies?
3. What is the correct call?
4. What is the updated score?

Respond in JSON format with: call, confidence, reasoning, score_update, announcement.
```

### Multi-frame Context
Pass last 3-5 frames as context for rally continuity.
Include current score and game state in the prompt.
```

## Interfaces

### Function Calls
- `update_score(player, points)` — Update scoreboard
- `announce(text)` — TTS output
- `move_robot(direction, speed)` — MentorPi movement
- `gesture(type)` — Robot arm signal

### MCP (future)
- Expose referee capabilities as MCP tools
- Other agents can query Sideline for calls

### A2A (future)
- Agent-to-agent communication
- Multiple Sideline agents covering different angles
