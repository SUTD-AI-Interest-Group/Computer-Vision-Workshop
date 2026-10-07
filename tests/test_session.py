import unittest
from unittest.mock import patch

import av
import numpy as np

from gestures import Hand
from session import CameraGame
from rendering import camera_square, draw


def hand(identity, x=0.2, y=0.2, closed=False, action="idle"):
    points = [(x, y)] * 21
    points[0], points[5] = (x, y + 0.2), (x, y)
    points[8] = (x, y)
    points[4] = (x + (0.02 if closed else 0.15), y)
    return Hand(identity, points, action)


class FakeDetector:
    closed = False

    def detect(self, image, now):
        return []

    def close(self):
        self.closed = True


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.session = CameraGame(FakeDetector)
        self.camera = np.zeros((600, 600, 3), dtype=np.uint8)

    def start(self):
        s = self.session
        s.photo = self.camera.copy()
        s.tiles = [self.camera[:200, :200].copy() for _ in range(9)]
        s.start_round(0)
        s.game.tick(3)
        s.game.board = [1, 0, 2, 3, 4, 5, 6, 7, 8]
        return s

    def test_capture_full_gesture_sequence(self):
        s = self.session
        for now in (0, 1.1):
            s.advance(
                self.camera, [hand("Left", 0.2, 0.2), hand("Right", 0.8, 0.8)], now
            )
        for now in (1.2, 1.31, 2.9):
            s.advance(
                self.camera,
                [hand("Left", 0.2, 0.2, True), hand("Right", 0.8, 0.8, True)],
                now,
            )
        self.assertIsNotNone(s.photo)
        self.assertEqual(s.photo.shape, (600, 600, 3))
        self.assertEqual(len(s.tiles), 9)
        self.assertEqual(s.game.phase, "countdown")

    def test_capture_loss_resets_hold(self):
        s = self.session
        for now in (0, 1.1):
            s.advance(
                self.camera, [hand("Left", 0.2, 0.2), hand("Right", 0.8, 0.8)], now
            )
        for now in (1.2, 1.31):
            s.advance(
                self.camera,
                [hand("Left", 0.2, 0.2, True), hand("Right", 0.8, 0.8, True)],
                now,
            )
        s.advance(self.camera, [], 2)
        self.assertIsNone(s.capture_since)
        self.assertIsNone(s.photo)

    def test_owner_release_solves_once(self):
        s = self.start()
        s.drag([hand("Left", 0.1, 0.1, action="grab")], 4)
        s.drag(
            [
                hand("Left", 0.5, 0.1, action="hold"),
                hand("Right", 0.9, 0.9, action="release"),
            ],
            4.5,
        )
        self.assertEqual(s.game.moves, 0)
        s.drag([hand("Left", 0.5, 0.1, action="release")], 5)
        self.assertEqual(s.game.phase, "solved")
        self.assertEqual(len(s.history), 1)
        s.drag([hand("Left", 0.5, 0.1, action="release")], 6)
        self.assertEqual(len(s.history), 1)

    def test_loss_and_outside_release_do_not_swap(self):
        s = self.start()
        s.drag([hand("Left", 0.1, 0.1, action="grab")], 4)
        s.drag([], 4.1)
        self.assertIsNone(s.held)
        s.drag([hand("Left", 0.1, 0.1, action="grab")], 5)
        s.drag([hand("Left", 1.1, 0.1, action="release")], 5.1)
        self.assertEqual(s.game.moves, 0)

    def test_receive_frame_and_cleanup(self):
        s = self.session
        output = s.receive(av.VideoFrame.from_ndarray(self.camera, format="bgr24"))
        self.assertEqual((output.width, output.height), (600, 710))
        self.assertIsNone(s.error, s.error)  # Show the unfinished exercise, if any.
        detector = s.detector
        s.close()
        self.assertTrue(detector.closed)
        self.assertIsNone(s.detector)
        self.assertFalse(s.connected)

    def test_stream_stall_pauses_at_last_frame(self):
        s = self.start()
        s.last_frame, s.connected = 5, True
        with patch("session.monotonic", return_value=10):
            state = s.snapshot()
        self.assertEqual(state["phase"], "paused")
        self.assertEqual(state["seconds"], 2)
        self.assertFalse(state["connected"])

    def test_detector_failure_is_visible_without_repeated_retries(self):
        def fail():
            raise RuntimeError("model unavailable")

        s = CameraGame(fail)
        frame = av.VideoFrame.from_ndarray(self.camera, format="bgr24")
        output = s.receive(frame)
        self.assertEqual(output.height, 710)
        self.assertIn("model unavailable", s.error)
        self.assertIsNone(s.detector)
        s.close()
        self.assertIsNone(s.error)

    def test_rendering_does_not_change_camera_pixels(self):
        s = self.start()
        before = self.camera.copy()
        output = draw(s, self.camera, [], 4)
        self.assertTrue(np.array_equal(self.camera, before))
        self.assertEqual(output.shape, (710, 600, 3))

    def test_mirrored_crop(self):
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        image[:, :400] = (255, 0, 0)
        crop = camera_square(image)
        self.assertEqual(tuple(crop[200, 100]), (0, 0, 0))
        self.assertEqual(tuple(crop[200, 500]), (255, 0, 0))

    def test_sessions_are_independent(self):
        self.start()
        other = CameraGame(FakeDetector)
        self.assertIsNone(other.photo)
        self.assertEqual(other.history, [])

    def test_landmarks_drive_a_complete_pinch_swap(self):
        s = self.start()
        s.advance(self.camera, [hand("Left", 0.1, 0.1)], 3.1)
        s.advance(self.camera, [hand("Left", 0.1, 0.1, True)], 3.2)
        s.advance(self.camera, [hand("Left", 0.1, 0.1, True)], 3.31)
        self.assertEqual(s.held, ("Left", 0))
        s.advance(self.camera, [hand("Left", 0.3, 0.1, True)], 3.4)
        s.advance(self.camera, [hand("Left", 0.5, 0.1, True)], 3.5)
        s.advance(self.camera, [hand("Left", 0.5, 0.1)], 3.6)
        self.assertEqual(s.game.phase, "solved")
        self.assertEqual(s.game.moves, 1)
        self.assertEqual(len(s.history), 1)

    def test_replay_and_new_photo_keep_history(self):
        s = self.start()
        s.connected = True
        s.drag([hand("Left", 0.1, 0.1, action="grab")], 4)
        s.drag([hand("Left", 0.5, 0.1, action="release")], 5)
        s.command("replay")
        self.assertEqual(s.game.phase, "countdown")
        self.assertEqual(s.game.moves, 0)
        self.assertIsNotNone(s.photo)
        s.command("new")
        self.assertIsNone(s.photo)
        self.assertEqual(s.game.phase, "idle")
        self.assertEqual(len(s.history), 1)

    def test_stop_reconnect_preserves_pause_until_resume(self):
        s = self.start()
        s.last_frame = 5
        s.close()
        self.assertEqual(s.game.phase, "paused")
        self.assertIsNotNone(s.photo)
        s.command("resume")
        self.assertEqual(s.game.phase, "paused")
        s.connected = True
        s.command("resume")
        self.assertEqual(s.game.phase, "countdown")
