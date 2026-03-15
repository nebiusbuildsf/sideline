"""Sideline Agent — the core agentic pipeline."""

import json
import os
import base64
import asyncio
import logging

from openai import OpenAI

from agent.state import GameState
from agent.prompts import get_system_prompt, get_frame_prompt
from agent.tools import TOOLS

logger = logging.getLogger("sideline")

# Callbacks for broadcasting events to dashboard/robot
_listeners: list = []


def add_listener(fn):
    _listeners.append(fn)


async def broadcast(event_type: str, data: dict):
    for fn in _listeners:
        try:
            await fn(event_type, data)
        except Exception as e:
            logger.error(f"Listener error: {e}")


class SidelineAgent:
    def __init__(
        self,
        sport: str = "tennis",
        model: str = None,
        mock: bool = False,
    ):
        self.sport = sport
        self.mock = mock
        self.state = GameState(sport)
        self.model = model or os.environ.get(
            "SIDELINE_VISION_MODEL", "Qwen/Qwen2-VL-72B-Instruct"
        )
        self.client = None if mock else OpenAI(
            base_url=os.environ.get(
                "NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"
            ),
            api_key=os.environ.get("NEBIUS_API_KEY", "mock"),
        )
        self.recent_frames = []

    async def analyze_frame(self, frame_b64: str) -> dict:
        """Analyze a single frame and execute tool calls."""
        self.state.frame_count += 1

        if self.mock:
            return await self._mock_analyze(frame_b64)

        # Build messages with context
        history = json.dumps(self.state.events[-5:]) if self.state.events else "[]"
        system = get_system_prompt(self.sport, self.state.summary(), history)
        user_text = get_frame_prompt(self.sport, self.state.summary())

        messages = [
            {"role": "system", "content": system},
        ]

        # Add last 2 frames for rally context
        for prev in self.recent_frames[-2:]:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Previous frame:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{prev['b64'][:100]}..."}},
                ],
            })
            if prev.get("analysis"):
                messages.append({"role": "assistant", "content": prev["analysis"]})

        # Current frame
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}},
            ],
        })

        # Call Nebius VLM with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=500,
        )

        msg = response.choices[0].message
        result = {
            "frame": self.state.frame_count,
            "content": msg.content or "",
            "tool_calls": [],
            "score": self.state.score_dict(),
        }

        # Execute tool calls
        if msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                result["tool_calls"].append({"name": name, "args": args})
                await self._execute_tool(name, args)

        # Update score in result after tool execution
        result["score"] = self.state.score_dict()

        # Store for context
        self.recent_frames.append({
            "b64": frame_b64[:200],  # don't store full image in memory
            "analysis": msg.content or json.dumps(result["tool_calls"]),
        })
        if len(self.recent_frames) > 5:
            self.recent_frames.pop(0)

        # Broadcast to dashboard
        await broadcast("analysis", result)

        return result

    async def _execute_tool(self, name: str, args: dict):
        """Execute a tool call from the model."""
        if name == "update_score":
            self.state.update_score(args["player"], args.get("reason", ""))
            await broadcast("score", {
                "player": args["player"],
                "reason": args.get("reason", ""),
                "score": self.state.score_dict(),
            })

        elif name == "announce_call":
            self.state.add_event({
                "type": "call",
                "call_type": args["call_type"],
                "announcement": args["announcement"],
                "confidence": args.get("confidence", 0.5),
            })
            await broadcast("call", args)

        elif name == "robot_gesture":
            await broadcast("gesture", args)

        elif name == "no_call":
            await broadcast("status", {"description": args.get("description", "")})

    async def _mock_analyze(self, frame_b64: str) -> dict:
        """Mock analysis for development without API."""
        import random
        await asyncio.sleep(0.5)  # simulate latency

        frame_num = self.state.frame_count
        calls = []

        # Every 5th frame, simulate a scoring event
        if frame_num % 5 == 0:
            call_type = random.choice(["ace", "winner", "fault", "out"])
            winner = random.choice(["p1", "p2"])
            announcement = {
                "ace": f"Ace by {self.state.players[winner]}!",
                "winner": f"Winner! Point to {self.state.players[winner]}",
                "fault": "Fault!",
                "out": "Out!",
            }[call_type]

            calls.append({"name": "announce_call", "args": {
                "call_type": call_type,
                "announcement": announcement,
                "confidence": round(random.uniform(0.7, 0.95), 2),
            }})
            await self._execute_tool("announce_call", calls[0]["args"])

            if call_type in ("ace", "winner", "out"):
                score_args = {"player": winner, "reason": call_type}
                calls.append({"name": "update_score", "args": score_args})
                await self._execute_tool("update_score", score_args)

            gesture = {"ace": "arm_up", "winner": "arm_up", "fault": "signal_fault", "out": "point_out"}
            gesture_args = {"gesture": gesture[call_type], "direction": "center"}
            calls.append({"name": "robot_gesture", "args": gesture_args})
            await self._execute_tool("robot_gesture", gesture_args)
        else:
            desc = random.choice([
                "Rally continues, baseline exchange",
                "Player preparing to serve",
                "Net approach, volley exchange",
                "Deep forehand rally",
            ])
            calls.append({"name": "no_call", "args": {"description": desc}})
            await self._execute_tool("no_call", calls[0]["args"])

        result = {
            "frame": frame_num,
            "content": f"[Mock] Frame {frame_num} analyzed",
            "tool_calls": calls,
            "score": self.state.score_dict(),
        }
        await broadcast("analysis", result)
        return result
