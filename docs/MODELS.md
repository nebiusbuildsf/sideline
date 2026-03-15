# Sideline — Nebius Model Reference

## API Configuration

All Nebius models use OpenAI-compatible API. One client, swap the model ID.

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ["NEBIUS_API_KEY"]
)
```

### Regional Endpoints
| Region | URL |
|--------|-----|
| Default | `https://api.tokenfactory.nebius.com/v1/` |
| EU North | `https://api.tokenfactory.nebius.com/v1/` |
| EU West | `https://api.tokenfactory.eu-west1.nebius.com/v1/` |
| US Central | `https://api.tokenfactory.us-central1.nebius.com/v1/` |
| Middle East West | `https://api.tokenfactory.me-west1.nebius.com/v1/` |

## Available Models

### Vision Models (frame analysis)

| Model ID | Type | Use For | Tool Calling |
|----------|------|---------|-------------|
| `Qwen/Qwen2-VL-72B-Instruct` | Vision-Language 72B | Frame analysis — our default | Yes |
| `NVIDIA Nemotron Nano 2 VL` | Vision-Language | Document + video understanding | TBD |
| `Cosmos Reason 2` | Video reasoning | Sports CoT — confirm at event | TBD |

### Text Models (commentary, reasoning)

| Model ID | Type | Use For | Speed |
|----------|------|---------|-------|
| `deepseek-ai/DeepSeek-R1-0528` | Reasoning | Deep CoT text analysis | Medium |
| `deepseek-ai/DeepSeek-V3-0324-fast` | Generation | Fast commentary | Fast |
| `meta-llama/Meta-Llama-3.1-70B-Instruct` | General | Fallback, general tasks | Medium |

## Vision API — Frame Analysis

```python
import base64

def encode_frame(frame_path: str) -> str:
    with open(frame_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Analyze a single frame
frame_b64 = encode_frame("frame_001.jpg")

response = client.chat.completions.create(
    model="Qwen/Qwen2-VL-72B-Instruct",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "You are a tennis referee. What is happening in this frame? Is there a scoring event?"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}}
        ]
    }],
    max_tokens=300
)

print(response.choices[0].message.content)
```

## Vision + Tool Calling — Agent Mode

The model analyzes the frame AND decides which tools to call:

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
                    "reason": {"type": "string"}
                },
                "required": ["player", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "announce_call",
            "description": "Announce a referee call",
            "parameters": {
                "type": "object",
                "properties": {
                    "call_type": {"type": "string", "enum": ["fault", "out", "in", "let", "ace", "winner", "double_fault", "no_call"]},
                    "announcement": {"type": "string"},
                    "confidence": {"type": "number"}
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
            "description": "No scoring event — rally continues",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"}
                },
                "required": ["description"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="Qwen/Qwen2-VL-72B-Instruct",
    messages=[
        {"role": "system", "content": REFEREE_PROMPT},
        {"role": "user", "content": [
            {"type": "text", "text": f"Score: 15-30. Server: p1. Analyze this frame:"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}}
        ]}
    ],
    tools=tools,
    tool_choice="auto",
    max_tokens=500
)

# The model returns tool_calls
msg = response.choices[0].message
if msg.tool_calls:
    for tc in msg.tool_calls:
        print(f"Tool: {tc.function.name}")
        print(f"Args: {tc.function.arguments}")
else:
    print(f"Text: {msg.content}")
```

## Text API — Commentary Generation

```python
# After the referee makes a call, generate exciting commentary
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3-0324-fast",
    messages=[
        {"role": "system", "content": "You are an energetic sports commentator. Generate one sentence of commentary."},
        {"role": "user", "content": "The referee just called: Ace by Player 1. Score is now 40-15. Match point."}
    ],
    max_tokens=100
)

commentary = response.choices[0].message.content
# "What a thunderbolt! Player 1 fires an untouchable ace down the T — match point!"
```

## Switching Models at Runtime

```python
# Environment variable controls which model is used
MODEL_VISION = os.environ.get("SIDELINE_VISION_MODEL", "Qwen/Qwen2-VL-72B-Instruct")
MODEL_TEXT = os.environ.get("SIDELINE_TEXT_MODEL", "deepseek-ai/DeepSeek-V3-0324-fast")

# If Cosmos Reason 2 becomes available at the event:
# export SIDELINE_VISION_MODEL="nvidia/Cosmos-Reason2-8B"
# That's it. One line. Everything else works the same.
```

## Budget Estimation

| Action | Cost per call | Calls needed | Total |
|--------|-------------|-------------|-------|
| Vision analysis (72B) | ~$0.01-0.03 | 120 frames (2 min at 1fps) | ~$1.20-3.60 |
| Commentary (fast text) | ~$0.001 | 30 scoring events | ~$0.03 |
| Prompt iteration | ~$0.03 | 50 test calls | ~$1.50 |
| **Per full run** | | | **~$3-5** |
| **Budget ($400)** | | | **80-130 full runs** |

Plenty of budget. Don't hesitate to iterate on prompts.
