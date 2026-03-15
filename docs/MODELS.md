# Nebius Model Options

## Available on Nebius

| Model | Type | API | Best For |
|-------|------|-----|----------|
| `Qwen/Qwen2-VL-72B-Instruct` | Vision-Language | Token Factory (OpenAI-compatible) | Image analysis, scene understanding |
| `NVIDIA Nemotron Nano 2 VL` | Vision-Language | Nebius AI Studio | Document + video understanding |
| `Cosmos Reason 2` | Video reasoning | TBD — confirm at event | Sports video CoT reasoning |
| `deepseek-ai/DeepSeek-R1-0528` | Text reasoning | Token Factory | CoT text reasoning |
| `deepseek-ai/DeepSeek-V3-0324-fast` | Text | Token Factory | Fast text generation |
| `meta-llama/Meta-Llama-3.1-70B-Instruct` | Text | Token Factory | General purpose |

## Recommended Setup

### Primary: Vision model for frame analysis
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ["NEBIUS_API_KEY"]
)

response = client.chat.completions.create(
    model="Qwen/Qwen2-VL-72B-Instruct",  # swap model ID as needed
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": REFEREE_PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}}
        ]
    }],
    max_tokens=500
)
```

### Secondary: Text model for commentary generation
```python
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3-0324-fast",
    messages=[{
        "role": "system",
        "content": "You are a sports commentator. Given the referee's analysis, generate exciting commentary."
    }, {
        "role": "user",
        "content": f"Call: {call}. Score: {score}. Generate a one-line commentary."
    }]
)
```

## Switching Models

All Nebius models use the same OpenAI-compatible API. To switch:
1. Change the `model` parameter
2. Everything else stays the same

```python
MODEL = os.environ.get("SIDELINE_MODEL", "Qwen/Qwen2-VL-72B-Instruct")
```
