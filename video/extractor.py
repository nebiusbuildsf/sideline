"""Frame extraction from video files."""

import base64
import cv2
import asyncio
from pathlib import Path


class VideoExtractor:
    def __init__(self, video_path: str, fps: float = 1.0):
        self.video_path = video_path
        self.target_fps = fps
        self.cap = None

    async def frames(self):
        """Yield base64-encoded JPEG frames at target FPS."""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video: {self.video_path}")

        video_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        skip = max(1, int(video_fps / self.target_fps))
        frame_idx = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            if frame_idx % skip == 0:
                _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                b64 = base64.b64encode(buf).decode()
                yield b64
                await asyncio.sleep(0)  # yield control

            frame_idx += 1

        self.cap.release()

    def get_frame_count(self) -> int:
        cap = cv2.VideoCapture(self.video_path)
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        cap.release()
        return int(count / max(1, fps / self.target_fps))

    @staticmethod
    def encode_image(image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
