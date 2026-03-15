"""Demo: run all referee gestures on the MuJoCo SO-101 arm.

Usage (in Codespace):
    python -m actions.robot.demo                    # browser viewer on port 7860
    python -m actions.robot.demo --gesture fault     # single gesture
    python -m actions.robot.demo --save              # save frames to disk
"""

import os
# Must be set before any mujoco import to avoid GLFW/X11 errors in headless environments
os.environ.setdefault("MUJOCO_GL", "osmesa")

import argparse
import asyncio
import base64
import json
import logging
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from io import BytesIO
from pathlib import Path
from threading import Thread

from actions.robot.gestures import list_gestures, GESTURES
from actions.robot.mujoco_so101 import MuJoCoSO101Adapter

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

# Shared state for the web viewer
_current_frame_b64 = ""
_current_gesture = "ready"

VIEWER_HTML = """<!DOCTYPE html>
<html>
<head>
<title>SO-101 Referee Arm</title>
<style>
  body { margin: 0; background: #1a1a2e; color: #eee; font-family: monospace;
         display: flex; flex-direction: column; align-items: center; padding: 20px; }
  h1 { color: #e94560; margin-bottom: 5px; }
  #gesture { color: #0f3460; background: #e94560; padding: 4px 16px;
             border-radius: 4px; font-size: 1.2em; margin: 10px 0; }
  img { border: 2px solid #333; border-radius: 8px; max-width: 90vw; }
  .controls { display: flex; flex-wrap: wrap; gap: 8px; margin: 15px 0; justify-content: center; }
  button { background: #16213e; color: #eee; border: 1px solid #e94560;
           padding: 8px 16px; border-radius: 4px; cursor: pointer; font-family: monospace; }
  button:hover { background: #e94560; }
</style>
</head>
<body>
<h1>SIDELINE SO-101</h1>
<div id="gesture">ready</div>
<img id="frame" width="640" height="480" />
<div class="controls">
  <button onclick="send('fault')">Fault</button>
  <button onclick="send('out')">Out</button>
  <button onclick="send('in')">In</button>
  <button onclick="send('score_point')">Score Point</button>
  <button onclick="send('second_serve')">2nd Serve</button>
  <button onclick="send('let')">Let</button>
  <button onclick="send('overrule')">Overrule</button>
  <button onclick="send('ready')">Ready</button>
</div>
<script>
function poll() {
  fetch('/frame').then(r => r.json()).then(d => {
    if (d.frame) document.getElementById('frame').src = 'data:image/png;base64,' + d.frame;
    if (d.gesture) document.getElementById('gesture').textContent = d.gesture;
  }).catch(() => {});
  setTimeout(poll, 200);
}
function send(g) {
  fetch('/gesture', {method:'POST', headers:{'Content-Type':'application/json'},
                     body: JSON.stringify({gesture: g})});
}
poll();
</script>
</body>
</html>"""

# Queue for gesture requests from browser
_gesture_queue = asyncio.Queue()


class ViewerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(VIEWER_HTML.encode())
        elif self.path == "/frame":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "frame": _current_frame_b64,
                "gesture": _current_gesture,
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/gesture":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            gesture = body.get("gesture", "ready")
            # Put into the async queue via thread-safe method
            _gesture_queue._loop.call_soon_threadsafe(_gesture_queue.put_nowait, gesture)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Silence HTTP logs


def start_web_server(port: int):
    server = HTTPServer(("0.0.0.0", port), ViewerHandler)
    server.serve_forever()


async def update_frame(robot: MuJoCoSO101Adapter):
    global _current_frame_b64
    frame_bytes = await robot.render_frame()
    if frame_bytes:
        _current_frame_b64 = base64.b64encode(frame_bytes).decode()


async def run_demo(gesture_name: str | None = None, save: bool = False, port: int = 7860):
    global _current_gesture

    robot = MuJoCoSO101Adapter(headless=True)
    await robot.connect()

    # Store event loop ref for thread-safe queue access
    _gesture_queue._loop = asyncio.get_running_loop()

    # Start web server in background thread
    web_thread = Thread(target=start_web_server, args=(port,), daemon=True)
    web_thread.start()
    print(f"\nViewer running at http://localhost:{port}")
    print("Click the buttons to trigger referee gestures.\n")

    if save:
        Path("frames").mkdir(exist_ok=True)

    if gesture_name:
        # Single gesture mode
        gestures_to_run = [gesture_name]
    else:
        gestures_to_run = None  # Interactive mode

    if gestures_to_run:
        for name in gestures_to_run:
            info = GESTURES[name]
            print(f"--- {name}: {info['description']} ---")
            _current_gesture = name
            result = await robot.execute_gesture(name)
            await update_frame(robot)
            if save:
                with open(f"frames/{name}.png", "wb") as f:
                    f.write(base64.b64decode(_current_frame_b64))
                print(f"  Saved: frames/{name}.png")
            print(f"  Result: {result}")
            await asyncio.sleep(1.0)

        await robot.execute_gesture("ready")
        _current_gesture = "ready"
        await update_frame(robot)
        print("\nDone. Viewer still running — press Ctrl+C to exit.")

    # Interactive mode: wait for gestures from browser
    try:
        # Initial frame
        await update_frame(robot)
        while True:
            try:
                gesture = await asyncio.wait_for(_gesture_queue.get(), timeout=0.5)
                print(f"--- {gesture}: {GESTURES[gesture]['description']} ---")
                _current_gesture = gesture
                await robot.execute_gesture(gesture)
                await update_frame(robot)
            except asyncio.TimeoutError:
                pass
    except KeyboardInterrupt:
        pass

    await robot.disconnect()


def main():
    parser = argparse.ArgumentParser(description="SO-101 referee gesture demo")
    parser.add_argument("--gesture", type=str, default=None,
                        choices=list_gestures(),
                        help="Run a single gesture then go interactive")
    parser.add_argument("--save", action="store_true",
                        help="Save rendered frames to frames/ directory")
    parser.add_argument("--port", type=int, default=7860,
                        help="Web viewer port (default: 7860)")
    args = parser.parse_args()
    asyncio.run(run_demo(gesture_name=args.gesture, save=args.save, port=args.port))


if __name__ == "__main__":
    main()
