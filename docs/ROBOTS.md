# Sideline — Physical Embodiment

## Embodiment Tiers

The same agent brain outputs to any physical form. Each tier adds capability.

```
Sideline Agent
    │
    ├──▶ Tier 0: Dashboard (always works)
    │    └── Video + reasoning panel + scoreboard + voice
    │
    ├──▶ Tier 1: MentorPi Tank Bot
    │    └── Camera + speaker + movement + depth sensing
    │
    ├──▶ Tier 2: SO-101 Robotic Arm
    │    └── 6-DOF gestures: point out, signal fault, wave off
    │
    └──▶ Tier 3: Unitree G1 Humanoid
         └── Full referee: walk, gesture, speak, head track
```

---

## Tier 1: MentorPi (HiWonder)

**Status:** Confirmed — teammate's robot at the event

### Specs
- **Chassis:** Tracked with mecanum wheels (omnidirectional)
- **Camera:** Pi Camera module (visible in green PCB)
- **Depth Camera:** Stereo depth with point cloud support
- **Lidar:** 360° scanning for navigation
- **Speaker:** Built-in speaker grille for TTS output
- **IMU:** Inertial measurement for orientation
- **Compute:** Onboard SBC (Raspberry Pi or Jetson Nano)
- **Connectivity:** WiFi, USB

### Software Stack
- **ROS2** — full ROS2 integration for control
- **OpenCV** — image processing pipeline
- **MediaPipe** — hand tracking, pose detection
- **YOLOv5** — object detection
- **SLAM** — slam_toolbox + RTAB-VSLAM for mapping
- **Docker** — containerized deployment

### What We Use It For
1. **Watch:** Camera streams frames to Nebius VLM
2. **Speak:** TTS plays referee calls through speaker
3. **Move:** Drive toward action on the court
4. **Sense:** Lidar + depth for spatial awareness

### Control Interface — ROSA (NASA JPL)

The MentorPi is built on **ROSA** (Robot Operating System Agent) from NASA JPL — an AI agent that translates natural language into ROS commands. This means Sideline's agent brain can control the robot through natural language, not just raw ROS topics.

**Repo:** https://github.com/nasa-jpl/rosa

```python
# ROSA: Natural language → ROS2 commands
from rosa import ROSA

llm = get_nebius_llm()  # Use Nebius Token Factory as the LLM
robot = ROSA(ros_version=2, llm=llm)

# Natural language robot control
robot.invoke("Move forward 0.5 meters")
robot.invoke("Turn left 90 degrees")
robot.invoke("List all active topics")
robot.invoke("What sensors are publishing data?")
```

**How it fits Sideline:**
```python
# Agent makes a call → ROSA translates to robot actions
async def execute_on_robot(decision: RefereeDecision):
    if decision.call_type == "fault":
        robot.invoke("Say 'Fault! Second serve' through the speaker")
        robot.invoke("Raise the arm to signal fault")
    elif decision.call_type == "out":
        robot.invoke("Say 'Out!' through the speaker")
        robot.invoke("Point the arm to the right to signal out")
    elif decision.call_type == "ace":
        robot.invoke("Say 'Ace! Beautiful serve!' through the speaker")
        robot.invoke("Move forward 0.2 meters in celebration")
```

**Why ROSA matters for the pitch:**
- NASA JPL technology powering our sports referee
- Natural language control — no hardcoded joint angles
- LLM-agnostic — we plug in Nebius Token Factory as the brain
- Works with both ROS1 and ROS2

### Raw ROS2 Control (Fallback)
```python
# Direct ROS2 topic publishing if ROSA isn't needed
import rclpy
from geometry_msgs.msg import Twist

# Move forward
twist = Twist()
twist.linear.x = 0.2  # m/s forward
publisher.publish(twist)

# Stop
twist = Twist()
publisher.publish(twist)
```

### Docs
- Full documentation: https://docs.hiwonder.com/projects/MentorPi/en/latest/
- ROSA: https://github.com/nasa-jpl/rosa
- Capabilities: autonomous navigation, obstacle avoidance, line following, color tracking, multi-robot coordination

---

## Tier 2: SO-101 Robotic Arm (LeRobot / HuggingFace)

**Status:** Available at event (LeRobot workshop)

### Specs
- **DOF:** 6-axis (base pan, shoulder lift, elbow flex, wrist flex, wrist roll, gripper)
- **Motors:** 6x STS3215 Feetech servo motors
- **Gear Ratios:**
  | Joint | Motor | Gear Ratio |
  |-------|:-----:|:----------:|
  | Base / Shoulder Pan | 1 | 1/191 |
  | Shoulder Lift | 2 | 1/345 |
  | Elbow Flex | 3 | 1/191 |
  | Wrist Flex | 4 | 1/147 |
  | Wrist Roll | 5 | 1/147 |
  | Gripper | 6 | 1/147 |
- **Control:** Leader-follower teleoperation OR programmatic
- **Interface:** USB serial via Waveshare controller board

### Software Stack
- **LeRobot SDK:** `pip install -e ".[feetech]"`
- **Calibration:** `lerobot-calibrate`
- **Port discovery:** `lerobot-find-port`
- **Motor setup:** `lerobot-setup-motors`

### Setup Commands
```bash
# Install LeRobot with Feetech support
pip install -e ".[feetech]"

# Find USB ports
lerobot-find-port

# Setup motor IDs (one-time)
lerobot-setup-motors \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodemXXX

# Calibrate
lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodemXXX
```

### Referee Gestures (Mapped to Joint Positions)
```python
GESTURES = {
    "signal_out": {
        "description": "Point arm outward — ball is out",
        "shoulder_lift": 45,
        "elbow_flex": 0,
        "wrist_roll": 0,
    },
    "signal_fault": {
        "description": "Raise arm up — fault",
        "shoulder_lift": 90,
        "elbow_flex": 0,
        "wrist_roll": 0,
    },
    "signal_safe": {
        "description": "Flat palm down — ball is in / safe",
        "shoulder_lift": 30,
        "elbow_flex": 90,
        "wrist_flex": -45,
    },
    "signal_point": {
        "description": "Point to player who won the point",
        "shoulder_lift": 60,
        "elbow_flex": 30,
        "wrist_roll": 0,  # 0=center, +45=right, -45=left
    },
    "idle": {
        "description": "Arm at rest",
        "shoulder_lift": 0,
        "elbow_flex": 0,
        "wrist_roll": 0,
    }
}
```

### Docs
- Assembly: https://github.com/TheRobotStudio/SO-ARM100
- LeRobot: https://huggingface.co/docs/lerobot/en/so101

---

## Tier 3: Unitree G1 Humanoid

**Status:** Request access at 9 AM — shared fleet of 8-10 units, subject to safety review

### Specs
- Full body humanoid robot
- Walking, gesturing, head tracking
- Camera arrays for perception
- Speakers for voice output
- SDK for joint control

### What We'd Use It For
- Walk along the sideline
- Full referee gestures (both arms, head turn)
- Voice calls through onboard speakers
- Head tracking to follow the ball

### Access Requirements
- Safety review by event organizers
- Operator must be present
- Limited time slots shared across teams
- Apply early — this is competitive

---

## Robot Interface (Shared Abstraction)

All robots implement the same interface so the agent doesn't care which one is connected:

```python
# actions/robot/base.py
from abc import ABC, abstractmethod

class RobotController(ABC):
    @abstractmethod
    async def speak(self, text: str) -> None:
        """Announce a call through the robot's speaker."""
        pass

    @abstractmethod
    async def gesture(self, gesture_type: str, **kwargs) -> None:
        """Signal a call with a physical gesture."""
        pass

    @abstractmethod
    async def move(self, direction: str, speed: float) -> None:
        """Move the robot in a direction."""
        pass

    @abstractmethod
    async def idle(self) -> None:
        """Return to idle position."""
        pass

# Implementations:
# - MockRobotController  — prints to console (development)
# - MentorPiController   — ROS2 topics
# - SO101Controller      — LeRobot/Feetech serial
# - UnitreeG1Controller  — Unitree SDK
```

---

## NVIDIA Osmo — Orchestration Layer

**What:** Open-source, cloud-native orchestrator for physical AI workflows. Manages the full pipeline: synthetic data generation → training → RL → hardware-in-the-loop testing.

**URL:** https://developer.nvidia.com/osmo

**How it fits Sideline (future / pitch narrative):**
- Define referee training workflows in YAML (no code)
- Orchestrate: generate synthetic sports data → train VLM → RL fine-tune on scoring accuracy → test on robot
- Deploy across Nebius cloud, Jetson edge, or ARM devices
- Dataset versioning for model auditing (was this call correct? retrain)

**For the hackathon:** Mention in pitch as "where this goes next" — Osmo for training referee models at scale. Don't try to implement it in 6 hours.

```yaml
# Future: osmo_workflow.yaml
name: sideline-referee-training
stages:
  - name: generate-data
    type: isaac-sim
    config:
      scene: tennis-court
      cameras: 3
      episodes: 10000

  - name: train-vlm
    type: pytorch
    config:
      model: qwen2-vl-72b
      dataset: generated-data
      epochs: 5

  - name: evaluate
    type: hardware-in-loop
    config:
      robot: mentorpi
      test-clips: 50
```

---

## Fallback Strategy

If robot integration hits a wall:
1. Dashboard + voice (TTS through laptop speaker) is a complete demo
2. Robot is the cherry on top, not the cake
3. Pre-record a robot clip as backup if live demo is flaky
