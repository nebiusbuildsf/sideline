"""Sideline — FastAPI server with WebSocket for real-time dashboard."""

import asyncio
import json
import os
import sys
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from agent.core import SidelineAgent, add_listener, broadcast
from video.extractor import VideoExtractor

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("sideline")

app = FastAPI(title="Sideline", description="Agentic AI Sports Referee")

# Global agent instance
agent: SidelineAgent = None
ws_clients: list[WebSocket] = []
is_running = False


async def ws_broadcast(event_type: str, data: dict):
    """Broadcast events to all connected WebSocket clients."""
    msg = json.dumps({"type": event_type, "data": data})
    disconnected = []
    for ws in ws_clients:
        try:
            await ws.send_text(msg)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        ws_clients.remove(ws)


# Register the WebSocket broadcaster as a listener
add_listener(ws_broadcast)


@app.on_event("startup")
async def startup():
    global agent
    mock = os.environ.get("SIDELINE_MOCK", "").lower() in ("1", "true", "yes")
    if not os.environ.get("NEBIUS_API_KEY") and not mock:
        logger.warning("No NEBIUS_API_KEY set — running in mock mode")
        mock = True
    agent = SidelineAgent(sport="tennis", mock=mock)
    logger.info(f"Sideline agent ready (mock={mock}, model={agent.model})")


# --- WebSocket ---

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    # Send current state on connect
    await ws.send_text(json.dumps({
        "type": "state",
        "data": agent.state.to_dict(),
    }))
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("action") == "start" and not is_running:
                video = msg.get("video", "")
                asyncio.create_task(run_analysis(video))
    except WebSocketDisconnect:
        ws_clients.remove(ws)


async def run_analysis(video_path: str):
    """Run the agent analysis loop on a video."""
    global is_running
    if is_running:
        return
    is_running = True

    await ws_broadcast("status", {"message": "Starting analysis..."})

    try:
        if video_path and os.path.exists(video_path):
            extractor = VideoExtractor(video_path, fps=1.0)
            frame_count = extractor.get_frame_count()
            await ws_broadcast("status", {"message": f"Analyzing {frame_count} frames..."})

            idx = 0
            async for frame_b64 in extractor.frames():
                idx += 1
                await ws_broadcast("progress", {
                    "frame": idx,
                    "total": frame_count,
                })
                result = await agent.analyze_frame(frame_b64)
                logger.info(f"Frame {idx}: {len(result.get('tool_calls', []))} tool calls")
        else:
            # No video — run mock frames
            for i in range(20):
                await agent.analyze_frame("")
                await asyncio.sleep(1.0)

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await ws_broadcast("error", {"message": str(e)})
    finally:
        is_running = False
        await ws_broadcast("status", {"message": "Analysis complete"})


# --- REST API ---

@app.get("/health")
async def health():
    return {"status": "ok", "agent": agent is not None, "mock": agent.mock if agent else None}


@app.get("/state")
async def get_state():
    return agent.state.to_dict()


@app.get("/score")
async def get_score():
    return agent.state.score_dict()


@app.get("/events")
async def get_events(last_n: int = 20):
    return agent.state.events[-last_n:]


@app.post("/analyze")
async def analyze_frame(file: UploadFile = File(...)):
    """Analyze a single uploaded frame."""
    import base64
    contents = await file.read()
    b64 = base64.b64encode(contents).decode()
    result = await agent.analyze_frame(b64)
    return result


@app.post("/start")
async def start_analysis(video_path: str = ""):
    """Start analysis on a video file."""
    global is_running
    if is_running:
        return {"error": "Already running"}
    asyncio.create_task(run_analysis(video_path))
    return {"status": "started"}


@app.post("/reset")
async def reset():
    """Reset game state."""
    agent.state = __import__("agent.state", fromlist=["GameState"]).GameState(agent.sport)
    await ws_broadcast("state", agent.state.to_dict())
    return {"status": "reset"}


# --- Dashboard ---

app.mount("/static", StaticFiles(directory="dashboard"), name="static")


@app.get("/")
async def dashboard():
    return FileResponse("dashboard/index.html")


# --- A2A Agent Card ---

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "sideline-referee",
        "description": "AI sports referee agent — watches video, reasons about plays, makes calls",
        "url": os.environ.get("SIDELINE_URL", "http://localhost:8000"),
        "version": "1.0.0",
        "provider": {
            "name": "Sideline",
            "description": "Agentic AI sports referee — Nebius.Build SF 2026",
        },
        "capabilities": {"streaming": True, "pushNotifications": False},
        "skills": [
            {
                "id": "analyze_play",
                "name": "Analyze Play",
                "description": "Analyze a sports video frame and make a referee call",
                "tags": ["sports", "tennis", "referee", "vision"],
            },
            {
                "id": "get_score",
                "name": "Get Score",
                "description": "Return current game score and match state",
            },
            {
                "id": "commentary",
                "name": "Generate Commentary",
                "description": "Generate play-by-play commentary for the current action",
            },
        ],
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
