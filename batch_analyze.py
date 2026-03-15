"""Batch analyze a video and cache results to JSON."""

import asyncio
import json
import os
import sys
import time

# Ensure we can import from the project
sys.path.insert(0, os.path.dirname(__file__))

from agent.core import SidelineAgent
from video.extractor import VideoExtractor


async def batch_analyze(video_path: str, output_path: str, fps: float = 0.5):
    agent = SidelineAgent(sport="tennis", mock=False)
    extractor = VideoExtractor(video_path, fps=fps)
    frame_count = extractor.get_frame_count()

    print(f"Analyzing {video_path}: {frame_count} frames at {fps} fps")
    print(f"Model: {agent.model}")

    results = []
    idx = 0
    async for frame_b64 in extractor.frames():
        idx += 1
        timestamp = round(idx / fps, 1)
        print(f"  Frame {idx}/{frame_count} ({timestamp}s)...", end=" ", flush=True)

        t0 = time.time()
        result = await agent.analyze_frame(frame_b64)
        latency = round(time.time() - t0, 2)

        result["timestamp"] = timestamp
        result["latency_s"] = latency

        # Don't store base64 in cache
        if "frame_b64" in result:
            del result["frame_b64"]

        calls = [tc["name"] for tc in result.get("tool_calls", [])]
        print(f"{latency}s | {calls}")

        results.append(result)

    # Save cache
    cache = {
        "video": os.path.basename(video_path),
        "model": agent.model,
        "fps": fps,
        "total_frames": len(results),
        "analyzed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "frames": results,
    }

    with open(output_path, "w") as f:
        json.dump(cache, f, indent=2)

    print(f"\nSaved {len(results)} frames to {output_path}")
    print(f"Stats: {agent.stats}")


if __name__ == "__main__":
    video = sys.argv[1] if len(sys.argv) > 1 else "video/clips/tennis_demo.mp4"
    output = sys.argv[2] if len(sys.argv) > 2 else "video/clips/tennis_demo_cache.json"
    fps = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5

    asyncio.run(batch_analyze(video, output, fps))
