"""Mock robot adapter for testing without hardware or simulation."""

import logging

from actions.robot.base import RobotAdapter
from actions.robot.gestures import get_gesture, JOINT_NAMES

logger = logging.getLogger("sideline.robot.mock")


class MockRobotAdapter(RobotAdapter):

    def __init__(self):
        self.joints = [0.0] * 6
        self.connected = False

    async def connect(self) -> None:
        self.connected = True
        logger.info("Mock robot connected")

    async def execute_gesture(self, gesture_name: str) -> dict:
        gesture = get_gesture(gesture_name)
        self.joints = list(gesture["joints"])
        logger.info(f"Mock gesture: {gesture_name} — {gesture['description']}")
        return {"gesture": gesture_name, "status": "ok", "adapter": "mock"}

    async def set_joints(self, joint_values: list[float]) -> None:
        self.joints = list(joint_values[:6])
        joint_str = ", ".join(f"{n}={v:.2f}" for n, v in zip(JOINT_NAMES, self.joints))
        logger.info(f"Mock joints: {joint_str}")

    async def get_joints(self) -> list[float]:
        return list(self.joints)

    async def disconnect(self) -> None:
        self.connected = False
        logger.info("Mock robot disconnected")
