"""One player's camera-to-game loop. The WebRTC worker never calls Streamlit."""

from math import hypot
from threading import RLock
from time import monotonic

import av
import cv2

from game import Game
from gestures import Pinch, capture_square, cell_at, pinch_distance
from rendering import camera_square, draw
from vision import HandDetector
from practice import ExerciseIncomplete, TODO


class CameraGame:
    def __init__(self, detector_factory=HandDetector):
        # WebRTC runs on a worker thread; Streamlit controls run on another.
        self.lock = RLock()
        self.detector_factory = detector_factory
        self.detector = None
        self.game = Game()
        self.photo = None
        self.tiles = []
        self.history = []
        self.error = None
        self.last_frame = None
        self.connected = False
        self.previous_board = list(range(9))
        self.animation_started = 0.0
        self.animation_duration = 0.8
        self.status = "Press START, then show both open hands."
        self.clear_gestures()

    def clear_gestures(self):
        self.pinches = {}
        self.positions = {}
        self.held = None  # (hand identity, board position)
        self.cursor = (0.5, 0.5)
        self.target = None
        self.open_since = None
        self.capture_since = None
        self.capture_rect = None
        self.calibrated = False

    def receive(self, frame: av.VideoFrame) -> av.VideoFrame:
        """The workshop pipeline: image -> landmarks -> gestures -> game -> image."""
        with self.lock:
            now = monotonic()
            camera = camera_square(frame.to_ndarray(format="bgr24"))
            self.connected = True
            if self.last_frame is not None and now - self.last_frame > 0.75:
                self.game.pause(self.last_frame)
                self.clear_gestures()
                self.status = "Video interrupted. Resume when ready."
            self.last_frame = now
            hands = []
            if self.error is None:
                try:
                    if self.detector is None:
                        self.detector = self.detector_factory()
                    hands = self.detector.detect(camera, now)
                    self.advance(camera, hands, now)
                except ExerciseIncomplete as error:
                    # Keep raw camera video available while the worksheet is unfinished.
                    self.error = str(error)
                    self.game.pause(now)
                    self.clear_gestures()
                    self._close_detector()
                except Exception as error:
                    # Keep delivering video so the user can see the error in the UI.
                    self.error = f"Tracking stopped: {error}"
                    self.game.pause(now)
                    self.clear_gestures()
                    self._close_detector()
            output = draw(self, camera, hands, now)
            return av.VideoFrame.from_ndarray(output, format="bgr24")

    def advance(self, camera, hands, now):
        """Purely in-memory interaction step; tests supply synthetic hands here."""
        previous_phase = self.game.phase
        self.game.tick(now)
        if previous_phase != self.game.phase:
            self.clear_gestures()  # Release pinches after countdown before grabbing.
        seen = {hand.identity for hand in hands}
        self.pinches = {
            key: value for key, value in self.pinches.items() if key in seen
        }
        self.positions = {
            key: value for key, value in self.positions.items() if key in seen
        }
        for hand in hands:
            previous = self.positions.get(hand.identity, hand.cursor)
            if hypot(hand.cursor[0] - previous[0], hand.cursor[1] - previous[1]) > 0.3:
                self.pinches[hand.identity] = Pinch()
                self.held = None
            self.positions[hand.identity] = hand.cursor
            pinch = self.pinches.setdefault(hand.identity, Pinch())
            # EXERCISE 8: Connect landmark geometry to this hand's Pinch state.
            # Save the event string in hand.action; pass the current time through.
            hand.action = TODO(8, "connect landmarks to per-hand pinch events")
        if self.photo is None:
            # EXERCISE 9: Dispatch this frame to the photo-capture interaction.
            TODO(9, "route an uncaptured frame to the capture interaction")
        elif self.game.phase == "running":
            # EXERCISE 9: Dispatch running rounds to the tile-drag interaction.
            TODO(9, "route a running frame to the drag interaction")
        elif self.game.phase == "countdown":
            self.status = "Release your pinches. Get ready!"
        elif self.game.phase == "paused":
            self.status = "Paused. Press Resume to continue."
        else:
            self.status = "Solved! Replay this photo or capture a new one."

    def capture(self, camera, hands, now):
        if not self.calibrated:
            # EXERCISE 10a: Calibration needs exactly two hands, both open.
            ready = TODO(10, "recognize the two-open-hands calibration pose")
            if ready:
                if self.open_since is None:
                    self.open_since = now
                self.calibrated = now - self.open_since >= 1.0
            else:
                self.open_since = None
            self.status = "Show both open hands for one second."
            return
        # EXERCISE 10b: Both detected hands must have held pinch states.
        both_held = TODO(10, "recognize two held pinches")
        if not both_held:
            self.capture_since = None
            self.capture_rect = None
            self.status = (
                "Pinch at opposite corners with both hands; hold for 1.5 seconds."
            )
            return
        # EXERCISE 10c: Connect both cursors to your capture geometry function.
        self.capture_rect = TODO(10, "connect hand positions to the capture square")
        if self.capture_rect is None:
            self.capture_since = None
            self.status = "Move your hands farther apart."
            return
        if self.capture_since is None:
            self.capture_since = now
        remaining = max(0, 1.5 - (now - self.capture_since))
        self.status = f"Hold both pinches: {remaining:.1f} seconds."
        if remaining > 0:
            return
        x, y, side = self.capture_rect
        self.photo = cv2.resize(camera[y : y + side, x : x + side], (600, 600)).copy()
        self.tiles = [
            self.photo[row * 200 : (row + 1) * 200, col * 200 : (col + 1) * 200].copy()
            for row in range(3)
            for col in range(3)
        ]
        self.start_round(now)

    def start_round(self, now):
        self.clear_gestures()
        self.previous_board = list(range(9))
        self.animation_started, self.animation_duration = now, 0.8
        self.game.start(now)
        self.status = "Captured! Release your pinches while the puzzle scrambles."

    def drag(self, hands, now):
        self.status = "Open a hand, pinch a tile, move, then release to swap."
        if self.held:
            identity, origin = self.held
            owner = next((hand for hand in hands if hand.identity == identity), None)
            if owner is None or owner.action not in ("hold", "release"):
                self.held = self.target = None
                return
            self.cursor = owner.cursor
            # EXERCISE 11a: Map the owner's cursor to the destination cell.
            self.target = TODO(11, "map the held tile's drop destination")
            if owner.action == "release":
                self.held = None
                self.previous_board = self.game.board.copy()
                # EXERCISE 11b: Only a valid destination may call Game.swap.
                # Save its boolean result; an invalid destination must be False.
                swapped = TODO(11, "commit a valid owner release to the puzzle")
                if swapped:
                    self.animation_started, self.animation_duration = now, 0.18
                    if self.game.phase == "solved":
                        self.history.append(
                            {
                                "Seconds": round(self.game.accumulated, 2),
                                "Swaps": self.game.moves,
                            }
                        )
                        self.history = self.history[-20:]
                self.target = None
            return
        for hand in hands:
            # EXERCISE 11c: On a grab inside the board, store (identity, cell)
            # in self.held, update self.cursor, then return. Ignore other events.
            TODO(11, "connect a grab event to tile ownership")

    def command(self, action):
        """Native Streamlit buttons enter through this thread-safe boundary."""
        with self.lock:
            now = monotonic()
            if action == "pause":
                self.game.pause(now)
                self.clear_gestures()
            elif action == "resume" and self.connected and not self.error:
                self.game.resume(now)
                self.clear_gestures()
            elif (
                action == "replay"
                and self.photo is not None
                and self.game.phase == "solved"
            ):
                self.start_round(now)
            elif action == "new":
                self.game = Game()
                self.photo, self.tiles, self.error = None, [], None
                self.clear_gestures()
                self.status = "Show both open hands to capture a new photo."

    def snapshot(self):
        with self.lock:
            now = monotonic()
            if self.last_frame is not None and now - self.last_frame > 0.75:
                self.game.pause(self.last_frame)
                self.clear_gestures()
                self.connected = False
                self.status = "Waiting for camera frames. Restart the stream if needed."
            return {
                "phase": self.game.phase,
                "seconds": self.game.elapsed(now),
                "moves": self.game.moves,
                "status": self.status,
                "error": self.error,
                "connected": self.connected,
                "history": [row.copy() for row in self.history],
            }

    def _close_detector(self):
        if self.detector is not None:
            self.detector.close()
            self.detector = None

    def close(self):
        """WebRTC calls this when the video track ends; retain the paused puzzle."""
        with self.lock:
            self.game.pause(
                self.last_frame if self.last_frame is not None else monotonic()
            )
            self.clear_gestures()
            self._close_detector()
            self.error = None
            self.connected = False
            self.last_frame = None
            self.status = "Camera stopped. Press START to reconnect."
