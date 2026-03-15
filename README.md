# Sideline

An agentic AI that watches sports, reasons about every play, and acts through any physical form.

**Track:** Edge Inference & Agents — Nebius.Build SF Hackathon, March 15 2026

## What It Does

Sideline watches a tennis match through video, reasons about what's happening using chain-of-thought, and takes actions: calling faults, tracking score, announcing plays through a robot, and displaying live reasoning on a dashboard.

## Architecture

```
Video Feed
    │
    ▼
Frame Extraction (1-2 fps)
    │
    ▼
Nebius VLM (Qwen2-VL-72B / Cosmos Reason 2 / Nemotron)
    │
    ▼
Reasoning Agent (CoT: what happened → what's the rule → what's the call)
    │
    ├──▶ Dashboard (video + reasoning panel + scoreboard)
    ├──▶ Voice (TTS — announces the call)
    └──▶ MentorPi Robot (speaks, moves, gestures)
```

## Team

| Name | Role |
|------|------|
| Ravinder Jilkapally | Demo UI + agent pipeline |
| Vivek Gopal Ramaswamy | Robotics + architecture |
| Kruthik Hulisandra | Domain rules + agent logic |
| Visshwa Balasubramanian | Backend engine + robot control |

## Tech Stack

- **Inference:** Nebius Token Factory (OpenAI-compatible API)
- **Backend:** Python + FastAPI
- **Frontend:** Vanilla HTML/JS dashboard
- **Robot:** HiWonder MentorPi (ROS2, camera, speaker, mecanum wheels)
- **Video:** Pre-recorded tennis clip (2 min)

## Quick Start

```bash
uv init
uv add openai fastapi uvicorn
export NEBIUS_API_KEY="your-key"
python server.py
```
