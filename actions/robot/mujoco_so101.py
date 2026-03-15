"""MuJoCo SO-101 robot adapter.

Loads the official SO-101 MJCF model and runs gestures in MuJoCo simulation.
Can run headless (offscreen) or with the interactive viewer.
"""

import asyncio
import logging
import os
from pathlib import Path

# Force offscreen rendering before importing mujoco (avoids GLFW/X11 errors)
if "MUJOCO_GL" not in os.environ:
    os.environ["MUJOCO_GL"] = "osmesa"

import numpy as np

import mujoco

from actions.robot.base import RobotAdapter
from actions.robot.gestures import get_gesture, JOINT_NAMES

logger = logging.getLogger("sideline.robot.mujoco")

SCENE_XML = Path(__file__).resolve().parent.parent.parent / "simulation" / "so101" / "scene.xml"


class MuJoCoSO101Adapter(RobotAdapter):
    """Controls a simulated SO-101 arm in MuJoCo."""

    def __init__(self, headless: bool = False, scene_path: str | None = None):
        self.scene_path = Path(scene_path) if scene_path else SCENE_XML
        self.headless = headless
        self.model = None
        self.data = None
        self.viewer_handle = None
        self._renderer = None
        self._cam_id = -1
        self._step_dt = 0.002  # MuJoCo default timestep

    async def connect(self) -> None:
        if not self.scene_path.exists():
            raise FileNotFoundError(f"Scene not found: {self.scene_path}")

        self.model = mujoco.MjModel.from_xml_path(str(self.scene_path))
        self.data = mujoco.MjData(self.model)
        mujoco.mj_forward(self.model, self.data)

        if not self.headless:
            from mujoco import viewer as mj_viewer
            self.viewer_handle = mj_viewer.launch_passive(self.model, self.data)

        # Pre-create renderer and camera for offscreen rendering
        self._renderer = mujoco.Renderer(self.model, width=480, height=360)
        self._cam_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_CAMERA, "referee_cam")

        logger.info(f"MuJoCo SO-101 loaded: {self.scene_path} (headless={self.headless})")
        logger.info(f"  Actuators: {[self.model.actuator(i).name for i in range(self.model.nu)]}")

    async def execute_gesture(self, gesture_name: str) -> dict:
        gesture = get_gesture(gesture_name)
        target_joints = gesture["joints"]
        duration = gesture["duration"]

        logger.info(f"Executing gesture: {gesture_name} — {gesture['description']}")

        # Interpolate from current position to target over duration
        start_joints = list(self.data.ctrl[:6])
        steps = int(duration / self._step_dt)

        for step in range(steps):
            t = step / max(steps - 1, 1)
            # Smooth interpolation (ease in-out)
            t = t * t * (3 - 2 * t)
            for i in range(6):
                self.data.ctrl[i] = start_joints[i] + t * (target_joints[i] - start_joints[i])

            mujoco.mj_step(self.model, self.data)

            if self.viewer_handle is not None:
                self.viewer_handle.sync()

            # Yield every ~20ms to keep things responsive
            if step % 10 == 0:
                await asyncio.sleep(0)

        return {"gesture": gesture_name, "status": "ok", "adapter": "mujoco"}

    async def set_joints(self, joint_values: list[float]) -> None:
        for i, v in enumerate(joint_values[:6]):
            self.data.ctrl[i] = v
        # Step a few times to let the arm move
        for _ in range(100):
            mujoco.mj_step(self.model, self.data)
        if self.viewer_handle is not None:
            self.viewer_handle.sync()

    async def get_joints(self) -> list[float]:
        return [float(self.data.qpos[i]) for i in range(min(6, self.model.nq))]

    async def disconnect(self) -> None:
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None
        if self.viewer_handle is not None:
            self.viewer_handle.close()
            self.viewer_handle = None
        self.model = None
        self.data = None
        logger.info("MuJoCo SO-101 disconnected")

    async def render_frame(self) -> bytes | None:
        """Render a frame as PNG bytes (for streaming to dashboard)."""
        if self._renderer is None:
            return None

        try:
            if self._cam_id >= 0:
                self._renderer.update_scene(self.data, camera=self._cam_id)
            else:
                self._renderer.update_scene(self.data)
            pixels = self._renderer.render()
        except Exception as e:
            logger.error(f"Render error: {e}")
            return None

        from io import BytesIO
        from PIL import Image
        img = Image.fromarray(pixels)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=70)
        return buf.getvalue()
