"""MediaPipe lives here. One detector per camera session; no Streamlit calls."""

from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gestures import Hand
from practice import TODO

MODEL_PATH = Path(__file__).parent / "models" / "hand_landmarker.task"


class HandDetector:
    def __init__(self):
        if not MODEL_PATH.is_file():
            raise FileNotFoundError(
                "Missing models/hand_landmarker.task; see README.md."
            )
        # EXERCISE 1: Configure a two-hand VIDEO-mode landmarker using MODEL_PATH.
        # Use 0.6 for detection, presence, and tracking confidence. Store the
        # created HandLandmarker in self.model. Imports are already provided.
        TODO(1, "create the MediaPipe hand landmarker")
        self.last_timestamp = -1

    def detect(self, bgr_image: np.ndarray, now: float) -> list[Hand]:
        """Input is already mirrored and square; landmarks share its coordinates."""
        # EXERCISE 2: Convert BGR to RGB, wrap it in mp.Image, and call the
        # VIDEO inference method. Convert now (seconds) to milliseconds, keeping
        # timestamps strictly increasing even when two frames share a timestamp.
        # Update self.last_timestamp and assign the inference output to result.
        result = TODO(2, "prepare the frame and run video inference")
        # EXERCISE 3: Return a list of Hand(identity, points) objects.
        # Pair handedness with landmarks; keep normalized (x, y) coordinates.
        # Use Left/Right labels, not array positions, as identity. Reject labels
        # that occur more than once and classifications with score below 0.6.
        return TODO(3, "translate MediaPipe results into stable Hand objects")

    def close(self):
        self.model.close()
