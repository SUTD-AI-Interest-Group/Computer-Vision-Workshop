"""Workshop core: landmark geometry and pinch events, with no UI dependencies."""

from dataclasses import dataclass
from math import hypot, isfinite

from practice import TODO

WRIST, THUMB_TIP, INDEX_BASE, INDEX_TIP = 0, 4, 5, 8
CLOSE_THRESHOLD = 0.45
OPEN_THRESHOLD = 0.55
PINCH_HOLD_SECONDS = 0.1


@dataclass
class Hand:
    identity: str
    points: list[tuple[float, float]]
    action: str = "idle"

    @property
    def cursor(self) -> tuple[float, float]:
        return self.points[INDEX_TIP]


def pinch_distance(points: list[tuple[float, float]]) -> float:
    """Normalize fingertip separation by hand size, rather than using pixels."""

    # EXERCISE 4: Use Euclidean distances and the named landmark constants.
    # Normalize tip separation by wrist-to-index-base distance. If the scale
    # is at most 0.01, return NaN so invalid measurements cancel a grab.
    return TODO(4, "calculate the normalized pinch distance")


@dataclass
class Pinch:
    armed: bool = False
    held: bool = False
    since: float | None = None

    def update(self, distance: float, now: float) -> str:
        """Time is monotonic seconds. An open hand must precede every grab."""
        # EXERCISE 5: Implement the state machine described in WORKSHOP.md.
        # Update armed, held, and since, then return one of:
        # cancel, open, idle, grab, hold, release.
        return TODO(5, "turn pinch measurements into debounced gesture events")


def cell_at(point: tuple[float, float]) -> int | None:
    # EXERCISE 6: Reject coordinates outside [0, 1), then find the row-major
    # cell index in a 3x3 grid. Return None outside the board (do not clamp).
    return TODO(6, "map a normalized fingertip to a puzzle cell")


def capture_square(a, b, size: int) -> tuple[int, int, int] | None:
    """Centered square inside the two-hand rectangle; minimum 150 pixels."""
    # EXERCISE 7: Convert normalized corners to rounded pixel coordinates,
    # clamp to [0, size], and form the largest centered square inside their
    # rectangle. Return (x, y, side), or None when side is less than 150.
    return TODO(7, "calculate the two-hand capture square")
