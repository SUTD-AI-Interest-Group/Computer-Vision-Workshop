"""MediaPipe API-contract checks; no webcam or model inference is needed."""

from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from vision import HandDetector, vision


def result(labels, scores=None):
    scores = scores or [0.9] * len(labels)
    return SimpleNamespace(
        handedness=[
            [SimpleNamespace(category_name=label, score=score)]
            for label, score in zip(labels, scores)
        ],
        hand_landmarks=[
            [SimpleNamespace(x=index / 20, y=0.25) for index in range(21)]
            for _ in labels
        ],
    )


class VisionTests(unittest.TestCase):
    def detector(self, output):
        model = MagicMock()
        model.detect_for_video.return_value = output
        with patch(
            "vision.vision.HandLandmarker.create_from_options", return_value=model
        ) as create:
            detector = HandDetector()
        return detector, model, create

    def test_video_model_configuration_and_cleanup(self):
        detector, model, create = self.detector(result([]))
        options = create.call_args.args[0]
        self.assertEqual(options.running_mode, vision.RunningMode.VIDEO)
        self.assertEqual(options.num_hands, 2)
        self.assertEqual(options.min_hand_detection_confidence, 0.6)
        self.assertEqual(options.min_hand_presence_confidence, 0.6)
        self.assertEqual(options.min_tracking_confidence, 0.6)
        self.assertTrue(
            options.base_options.model_asset_path.endswith("hand_landmarker.task")
        )
        detector.close()
        model.close.assert_called_once()

    def test_rgb_and_strictly_increasing_milliseconds(self):
        detector, model, _ = self.detector(result([]))
        frame = np.full((2, 2, 3), (10, 20, 30), dtype=np.uint8)
        for now in (1.0, 1.0, 0.9, 1.1):
            self.assertEqual(detector.detect(frame, now), [])
        calls = model.detect_for_video.call_args_list
        self.assertEqual([call.args[1] for call in calls], [1000, 1001, 1002, 1100])
        self.assertEqual(tuple(calls[0].args[0].numpy_view()[0, 0]), (30, 20, 10))
        self.assertEqual(tuple(frame[0, 0]), (10, 20, 30))
        detector.close()

    def test_identity_order_ambiguity_and_confidence(self):
        detector, model, _ = self.detector(result(["Right", "Left"]))
        frame = np.zeros((2, 2, 3), dtype=np.uint8)
        hands = detector.detect(frame, 1)
        self.assertEqual([hand.identity for hand in hands], ["Right", "Left"])
        self.assertEqual(hands[0].cursor, (0.4, 0.25))
        self.assertEqual(len(hands[0].points), 21)
        model.detect_for_video.return_value = result(["Left", "Left"])
        self.assertEqual(detector.detect(frame, 2), [])
        model.detect_for_video.return_value = result(["Left", "Right"], [0.59, 0.9])
        self.assertEqual([h.identity for h in detector.detect(frame, 3)], ["Right"])
        detector.close()
