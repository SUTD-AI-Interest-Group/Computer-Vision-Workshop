"""MediaPipe lives here. One detector per camera session; no Streamlit calls."""

from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gestures import Hand

MODEL_PATH = Path(__file__).parent / "models" / "hand_landmarker.task"


class HandDetector:
    def __init__(self):
        if not MODEL_PATH.is_file():
            raise FileNotFoundError(
                "Missing models/hand_landmarker.task; see README.md."
            )
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.model = vision.HandLandmarker.create_from_options(options)
        self.last_timestamp = -1

    def detect(self, bgr_image: np.ndarray, now: float) -> list[Hand]:
        """Input is already mirrored and square; landmarks share its coordinates."""
        rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp = max(self.last_timestamp + 1, int(now * 1000))
        self.last_timestamp = timestamp
        result = self.model.detect_for_video(image, timestamp)
        labels = [items[0].category_name for items in result.handedness]
        hands = []
        for label, scores, landmarks in zip(
            labels, result.handedness, result.hand_landmarks
        ):
            # Array order can change. Reject ambiguous identities rather than
            # allowing another hand to inherit a held tile.
            if labels.count(label) != 1 or scores[0].score < 0.6:
                continue
            hands.append(Hand(label, [(p.x, p.y) for p in landmarks]))
        return hands

    def close(self):
        self.model.close()
