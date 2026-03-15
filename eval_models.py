"""Model evaluation harness — compare VLMs on the same tennis frames."""

import base64
import json
import os
import sys
import time

from openai import OpenAI

from agent.tools import TOOLS
from agent.prompts import TENNIS_SYSTEM, TENNIS_FRAME

# Models to evaluate
MODELS = [
    "Qwen/Qwen2.5-VL-72B-Instruct",
    # Uncomment as they become available on Nebius:
    # "nvidia/Nemotron-Nano-2-VL",
    # "nvidia/Cosmos-Reason2-8B",
]

client = OpenAI(
    base_url=os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"),
    api_key=os.environ["NEBIUS_API_KEY"],
)


def encode_frame(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def extract_frames_from_video(video_path: str, count: int = 5) -> list[str]:
    """Extract evenly spaced frames from a video."""
    import cv2
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = [int(i * total / count) for i in range(count)]
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frames.append(base64.b64encode(buf).decode())
    cap.release()
    return frames


def eval_model(model: str, frame_b64: str, frame_idx: int) -> dict:
    """Run a single model on a single frame, return results + timing."""
    state = "0-0 (Games: 0-0, Sets: 0-0) Server: Player 1"
    system = TENNIS_SYSTEM.format(state=state, history="[]")
    user_text = TENNIS_FRAME.format(state=state)

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": [
            {"type": "text", "text": user_text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}},
        ]},
    ]

    # Try with tool calling first
    t0 = time.time()
    try:
        # Try with tools first, fall back to no-tools if unsupported
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                max_tokens=500,
            )
        except Exception as tool_err:
            if "tool" in str(tool_err).lower():
                # Model doesn't support tools — call without them
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=500,
                )
        latency = time.time() - t0
        msg = response.choices[0].message

        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {"raw": tc.function.arguments}
                tool_calls.append({"name": tc.function.name, "args": args})

        # If no tool calls, try fallback parsing from text
        if not tool_calls and msg.content:
            from agent.parsing import parse_tool_calls_from_text
            tool_calls = parse_tool_calls_from_text(msg.content)

        return {
            "model": model,
            "frame": frame_idx,
            "latency_s": round(latency, 2),
            "content": msg.content or "",
            "tool_calls": tool_calls,
            "tool_call_source": "native" if msg.tool_calls else ("fallback" if tool_calls else "none"),
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            },
            "error": None,
        }
    except Exception as e:
        latency = time.time() - t0
        return {
            "model": model,
            "frame": frame_idx,
            "latency_s": round(latency, 2),
            "content": "",
            "tool_calls": [],
            "tool_call_source": "error",
            "usage": {},
            "error": str(e),
        }


def run_eval(frame_source: str, num_frames: int = 3):
    """Run evaluation across all models and frames."""
    # Load frames
    if frame_source.endswith((".mp4", ".avi", ".mov", ".mkv")):
        print(f"Extracting {num_frames} frames from {frame_source}...")
        frames = extract_frames_from_video(frame_source, num_frames)
    else:
        print(f"Using single image: {frame_source}")
        frames = [encode_frame(frame_source)]

    print(f"\nEvaluating {len(MODELS)} model(s) on {len(frames)} frame(s)\n")
    print("=" * 80)

    results = []
    for model in MODELS:
        print(f"\n--- {model} ---")
        model_latencies = []
        for i, frame_b64 in enumerate(frames):
            print(f"  Frame {i+1}/{len(frames)}...", end=" ", flush=True)
            result = eval_model(model, frame_b64, i)
            results.append(result)
            model_latencies.append(result["latency_s"])

            if result["error"]:
                print(f"ERROR: {result['error']}")
            else:
                tc_summary = ", ".join(
                    f"{tc['name']}({tc['args'].get('call_type', tc['args'].get('description', '')[:30])})"
                    for tc in result["tool_calls"]
                ) or "no tool calls"
                print(f"{result['latency_s']}s | {result['tool_call_source']} | {tc_summary}")

        if model_latencies:
            avg = sum(model_latencies) / len(model_latencies)
            print(f"  Avg latency: {avg:.2f}s")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for model in MODELS:
        model_results = [r for r in results if r["model"] == model]
        errors = sum(1 for r in model_results if r["error"])
        native_tc = sum(1 for r in model_results if r["tool_call_source"] == "native")
        fallback_tc = sum(1 for r in model_results if r["tool_call_source"] == "fallback")
        no_tc = sum(1 for r in model_results if r["tool_call_source"] == "none")
        avg_latency = sum(r["latency_s"] for r in model_results) / len(model_results) if model_results else 0
        total_tokens = sum(r["usage"].get("prompt_tokens", 0) + r["usage"].get("completion_tokens", 0) for r in model_results)

        print(f"\n{model}:")
        print(f"  Frames: {len(model_results)} | Errors: {errors}")
        print(f"  Tool calls: {native_tc} native, {fallback_tc} fallback, {no_tc} none")
        print(f"  Avg latency: {avg_latency:.2f}s")
        print(f"  Total tokens: {total_tokens}")

    # Save raw results
    out_path = "eval_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nRaw results saved to {out_path}")


if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "assets/videoplayback.mp4"
    n_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    run_eval(source, n_frames)
