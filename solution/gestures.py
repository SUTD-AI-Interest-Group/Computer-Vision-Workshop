"""Workshop core: landmark geometry and pinch events, with no UI dependencies."""

from dataclasses import dataclass
from math import hypot, isfinite

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

    def distance(a, b):
        return hypot(points[a][0] - points[b][0], points[a][1] - points[b][1])

    scale = distance(WRIST, INDEX_BASE)
    return distance(THUMB_TIP, INDEX_TIP) / scale if scale > 0.01 else float("nan")


@dataclass
class Pinch:
    armed: bool = False
    held: bool = False
    since: float | None = None

    def update(self, distance: float, now: float) -> str:
        """Time is monotonic seconds. An open hand must precede every grab."""
        if not isfinite(distance):
            self.armed = self.held = False
            self.since = None
            return "cancel"
        if distance > OPEN_THRESHOLD:
            released = self.held
            self.armed, self.held, self.since = True, False, None
            return "release" if released else "open"
        if self.held:
            return "hold"
        if not self.armed or distance >= CLOSE_THRESHOLD:
            self.since = None
            return "idle"
        if self.since is None:
            self.since = now
        if now - self.since < PINCH_HOLD_SECONDS:
            return "idle"
        self.held, self.armed = True, False
        return "grab"


def cell_at(point: tuple[float, float]) -> int | None:
    x, y = point
    if not (0 <= x < 1 and 0 <= y < 1):
        return None
    return int(y * 3) * 3 + int(x * 3)


def capture_square(a, b, size: int) -> tuple[int, int, int] | None:
    """Centered square inside the two-hand rectangle; minimum 150 pixels."""
    x0, x1 = sorted(max(0, min(size, round(p[0] * size))) for p in (a, b))
    y0, y1 = sorted(max(0, min(size, round(p[1] * size))) for p in (a, b))
    side = min(x1 - x0, y1 - y0)
    if side < 150:
        return None
    return x0 + (x1 - x0 - side) // 2, y0 + (y1 - y0 - side) // 2, side
