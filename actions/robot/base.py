"""Base robot interface. All robot adapters implement this."""

from abc import ABC, abstractmethod


class RobotAdapter(ABC):
    """Abstract interface for controlling a robot arm."""

    @abstractmethod
    async def connect(self) -> None:
        """Initialize connection to the robot."""

    @abstractmethod
    async def execute_gesture(self, gesture_name: str) -> dict:
        """Execute a named referee gesture. Returns status dict."""

    @abstractmethod
    async def set_joints(self, joint_values: list[float]) -> None:
        """Set joint positions directly (radians)."""

    @abstractmethod
    async def get_joints(self) -> list[float]:
        """Get current joint positions."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up connection."""
