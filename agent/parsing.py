"""Fallback parser — extract tool calls from raw text when tool_calls is empty."""

import json
import re
import logging

logger = logging.getLogger("sideline")

VALID_TOOLS = {"update_score", "announce_call", "robot_gesture", "no_call"}

# Call types that award a point
SCORING_CALLS = {"ace", "winner", "double_fault", "out"}


def parse_tool_calls_from_text(text: str) -> list[dict]:
    """Extract tool calls from model text output.

    The Qwen2.5-VL model on Nebius returns structured text like:
        no_call
        Reasoning: ...

    Or for scoring events:
        announce_call
        call_type: ace
        announcement: Ace by Player 1!
        ...
    """
    calls = []
    text_stripped = text.strip()
    first_line = text_stripped.split("\n")[0].strip().lower()

    # Strategy 1: Model starts response with a tool name
    if first_line in VALID_TOOLS or first_line.replace(" ", "_") in VALID_TOOLS:
        tool_name = first_line.replace(" ", "_")
        if tool_name == "no_call":
            # Extract reasoning after the tool name
            reasoning = _extract_after(text_stripped, first_line)
            calls.append({"name": "no_call", "args": {
                "description": reasoning[:200] if reasoning else "Rally continues",
            }})
            return calls
        elif tool_name == "announce_call":
            return _parse_announce_block(text_stripped)
        elif tool_name == "update_score":
            return _parse_score_block(text_stripped)

    # Strategy 2: Look for JSON blocks
    json_blocks = _extract_json_blocks(text)
    for block in json_blocks:
        parsed = _try_parse_tool_block(block)
        if parsed:
            return parsed

    # Strategy 3: Detect call types from natural language
    return _detect_from_language(text_stripped)


def _extract_after(text: str, prefix: str) -> str:
    """Get text after the first line (the tool name)."""
    lines = text.split("\n", 1)
    if len(lines) > 1:
        result = lines[1].strip()
        # Remove markdown bold markers and "Reasoning:" prefix
        result = re.sub(r'^\*{0,2}Reasoning:?\*{0,2}\s*', '', result, flags=re.IGNORECASE)
        return result
    return ""


def _parse_announce_block(text: str) -> list[dict]:
    """Parse an announce_call block from structured text."""
    lines = text.split("\n")
    call_type = "no_call"
    announcement = ""
    confidence = 0.8
    player = None

    for line in lines[1:]:  # skip first line (tool name)
        line = line.strip().lstrip("*").rstrip("*").strip()
        lower = line.lower()
        if lower.startswith("call_type:"):
            call_type = line.split(":", 1)[1].strip().lower()
        elif lower.startswith("announcement:"):
            announcement = line.split(":", 1)[1].strip()
        elif lower.startswith("confidence:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif lower.startswith("player:"):
            player = line.split(":", 1)[1].strip().lower()

    if not announcement:
        announcement = _extract_after(text, lines[0])[:100]

    calls = [{"name": "announce_call", "args": {
        "call_type": call_type,
        "announcement": announcement or f"{call_type} called",
        "confidence": confidence,
    }}]

    # If it's a scoring call, add update_score
    if call_type in SCORING_CALLS:
        if not player:
            player = "p1"  # default
        calls.append({"name": "update_score", "args": {
            "player": player,
            "reason": call_type,
        }})

    return calls


def _parse_score_block(text: str) -> list[dict]:
    """Parse an update_score block from structured text."""
    lines = text.split("\n")
    player = "p1"
    reason = ""

    for line in lines[1:]:
        line = line.strip()
        lower = line.lower()
        if lower.startswith("player:"):
            player = line.split(":", 1)[1].strip().lower()
        elif lower.startswith("reason:"):
            reason = line.split(":", 1)[1].strip()

    return [{"name": "update_score", "args": {
        "player": player,
        "reason": reason or "point",
    }}]


def _extract_json_blocks(text: str) -> list[str]:
    """Find all JSON-like blocks in text."""
    blocks = []
    code_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)```', text)
    blocks.extend(code_blocks)

    brace_depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '{':
            if brace_depth == 0:
                start = i
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
            if brace_depth == 0 and start is not None:
                blocks.append(text[start:i+1])
                start = None

    return blocks


def _try_parse_tool_block(block: str) -> list[dict] | None:
    """Try to parse a JSON block as one or more tool calls."""
    try:
        data = json.loads(block)
    except json.JSONDecodeError:
        return None

    results = []

    if isinstance(data, dict):
        name = data.get("name") or data.get("function", {}).get("name")
        args = data.get("arguments") or data.get("args") or data.get("parameters")
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                return None
        if name in VALID_TOOLS and isinstance(args, dict):
            results.append({"name": name, "args": args})

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                name = item.get("name") or item.get("function", {}).get("name")
                args = item.get("arguments") or item.get("args") or item.get("parameters")
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        continue
                if name in VALID_TOOLS and isinstance(args, dict):
                    results.append({"name": name, "args": args})

    return results if results else None


def _detect_from_language(text: str) -> list[dict]:
    """Last resort: detect call type from natural language."""
    lower = text.lower()
    first_line = lower.split("\n")[0].strip()

    # Check if model explicitly says no_call / no call / no scoring
    if any(phrase in first_line for phrase in ["no_call", "no call", "no scoring", "rally continues", "ongoing"]):
        return [{"name": "no_call", "args": {
            "description": text[:200],
        }}]

    # Look for explicit scoring keywords
    if "ace" in first_line and "scoring" not in first_line:
        player = "p2" if "player 2" in lower or "receiver" in lower else "p1"
        return [
            {"name": "announce_call", "args": {"call_type": "ace", "announcement": text[:100], "confidence": 0.6}},
            {"name": "update_score", "args": {"player": player, "reason": "ace"}},
        ]

    if "double fault" in lower:
        server = "p1"  # default server
        loser_is_scorer_opponent = "p2" if server == "p1" else "p1"
        return [
            {"name": "announce_call", "args": {"call_type": "double_fault", "announcement": text[:100], "confidence": 0.6}},
            {"name": "update_score", "args": {"player": loser_is_scorer_opponent, "reason": "double_fault"}},
        ]

    if "fault" in first_line:
        return [{"name": "announce_call", "args": {"call_type": "fault", "announcement": text[:100], "confidence": 0.6}}]

    if "out" in first_line and "about" not in first_line:
        return [{"name": "announce_call", "args": {"call_type": "out", "announcement": text[:100], "confidence": 0.6}}]

    if "winner" in first_line:
        player = "p2" if "player 2" in lower else "p1"
        return [
            {"name": "announce_call", "args": {"call_type": "winner", "announcement": text[:100], "confidence": 0.6}},
            {"name": "update_score", "args": {"player": player, "reason": "winner"}},
        ]

    # Default: no call
    return [{"name": "no_call", "args": {"description": text[:200]}}]
