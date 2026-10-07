import unittest
from gestures import Pinch, capture_square, cell_at, pinch_distance


class GestureTests(unittest.TestCase):
    def test_rearm_debounce_and_hysteresis(self):
        pinch = Pinch()
        self.assertEqual(pinch.update(0.2, 0), "idle")
        self.assertEqual(pinch.update(0.7, 1), "open")
        self.assertEqual(pinch.update(0.2, 2), "idle")
        self.assertEqual(pinch.update(0.2, 2.05), "idle")
        self.assertEqual(pinch.update(0.2, 2.11), "grab")
        self.assertEqual(pinch.update(0.5, 2.2), "hold")
        self.assertEqual(pinch.update(0.6, 2.3), "release")

    def test_invalid_measurement_cancels(self):
        pinch = Pinch(armed=False, held=True)
        self.assertEqual(pinch.update(float("nan"), 0), "cancel")
        self.assertFalse(pinch.held)
        self.assertEqual(pinch.update(0.1, 1), "idle")

    def test_normalized_geometry(self):
        points = [(0.0, 0.0)] * 21
        points[5], points[8] = (0.2, 0), (0.08, 0)
        self.assertAlmostEqual(pinch_distance(points), 0.4)
        self.assertEqual(cell_at((0.5, 0.5)), 4)
        self.assertIsNone(cell_at((1.0, 0.5)))
        self.assertIsNone(cell_at((-0.1, 0)))
        self.assertEqual(capture_square((0.1, 0.1), (0.9, 0.5), 600), (180, 60, 240))
        self.assertIsNone(capture_square((0.1, 0.1), (0.2, 0.2), 600))
