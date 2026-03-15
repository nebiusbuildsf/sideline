"""Demo: run all referee gestures on the MuJoCo SO-101 arm.

Usage (in Codespace):
    python -m actions.robot.demo
    python -m actions.robot.demo --headless
    python -m actions.robot.demo --gesture fault
"""

import argparse
import asyncio
import sys

from actions.robot.gestures import list_gestures, GESTURES
from actions.robot.mujoco_so101 import MuJoCoSO101Adapter


async def run_demo(gesture_name: str | None = None, headless: bool = False):
    robot = MuJoCoSO101Adapter(headless=headless)
    await robot.connect()

    gestures = [gesture_name] if gesture_name else list_gestures()

    for name in gestures:
        info = GESTURES[name]
        print(f"\n--- {name}: {info['description']} ---")
        result = await robot.execute_gesture(name)
        print(f"  Result: {result}")

        # Hold the pose briefly so you can see it
        await asyncio.sleep(1.5)

    # Return to ready
    if gesture_name != "ready":
        print("\n--- Returning to ready ---")
        await robot.execute_gesture("ready")

    if not headless:
        print("\nViewer open. Close the window to exit.")
        # Keep alive while viewer is open
        while robot.viewer_handle is not None and robot.viewer_handle.is_running():
            await asyncio.sleep(0.1)

    await robot.disconnect()


def main():
    parser = argparse.ArgumentParser(description="SO-101 referee gesture demo")
    parser.add_argument("--headless", action="store_true", help="Run without viewer")
    parser.add_argument("--gesture", type=str, default=None,
                        choices=list_gestures(),
                        help="Run a single gesture (default: all)")
    args = parser.parse_args()
    asyncio.run(run_demo(gesture_name=args.gesture, headless=args.headless))


if __name__ == "__main__":
    main()
