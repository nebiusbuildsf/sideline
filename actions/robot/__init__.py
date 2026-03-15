"""Robot adapter factory."""

from actions.robot.base import RobotAdapter
from actions.robot.mock import MockRobotAdapter


def create_robot(adapter: str = "mock", **kwargs) -> RobotAdapter:
    """Create a robot adapter by name.

    Args:
        adapter: "mock" or "mujoco"
        **kwargs: passed to adapter constructor
    """
    if adapter == "mock":
        return MockRobotAdapter()
    elif adapter == "mujoco":
        from actions.robot.mujoco_so101 import MuJoCoSO101Adapter
        return MuJoCoSO101Adapter(**kwargs)
    else:
        raise ValueError(f"Unknown robot adapter: {adapter}")
