"""Referee gesture definitions mapped to SO-101 joint configurations.

Joint order: [shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper]
All values in radians. Ranges from the SO-101 MJCF model:
  shoulder_pan:  [-1.92, 1.92]
  shoulder_lift: [-1.75, 1.75]
  elbow_flex:    [-1.69, 1.69]
  wrist_flex:    [-1.66, 1.66]
  wrist_roll:    [-2.74, 2.84]
  gripper:       [-0.17, 1.75]
"""

import math

JOINT_NAMES = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]

# Each gesture is a dict with joint targets and a duration (seconds)
GESTURES: dict[str, dict] = {
    "ready": {
        "description": "Neutral position — arms at sides",
        "joints": [0.0, 0.0, 0.0, 0.0, 0.0, 0.5],
        "duration": 1.0,
    },
    "fault": {
        "description": "Right arm straight up — fault call",
        "joints": [0.0, -1.5, -0.3, 0.0, 0.0, 1.5],
        "duration": 1.5,
    },
    "out": {
        "description": "Point toward sideline — ball out",
        "joints": [1.2, -0.8, -0.5, 0.0, 0.0, 1.5],
        "duration": 1.2,
    },
    "in": {
        "description": "Point down at court — ball in",
        "joints": [0.0, 0.8, 0.5, 0.3, 0.0, 1.5],
        "duration": 1.0,
    },
    "score_point": {
        "description": "Arm raise — point scored",
        "joints": [-0.5, -1.5, -0.2, -0.3, 0.0, 1.5],
        "duration": 1.5,
    },
    "second_serve": {
        "description": "Two fingers up — second serve",
        "joints": [0.0, -1.2, -0.5, -0.5, 0.0, 0.3],
        "duration": 1.2,
    },
    "let": {
        "description": "Wave motion — let, replay point",
        "joints": [0.0, -1.0, -0.3, 0.0, 1.5, 1.0],
        "duration": 1.5,
    },
    "overrule": {
        "description": "Cross arms — overrule previous call",
        "joints": [0.3, -0.5, -1.2, -1.0, 0.0, 1.5],
        "duration": 1.5,
    },
}


def get_gesture(name: str) -> dict:
    """Get gesture config by name. Returns 'ready' if not found."""
    return GESTURES.get(name, GESTURES["ready"])


def list_gestures() -> list[str]:
    """List all available gesture names."""
    return list(GESTURES.keys())
