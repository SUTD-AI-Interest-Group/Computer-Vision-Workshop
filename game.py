"""Pure Python puzzle rules and monotonic stopwatch; no Streamlit dependency."""

from dataclasses import dataclass, field
from math import ceil
from random import Random

SIZE = 3
TILE_COUNT = SIZE * SIZE
COUNTDOWN = 3


@dataclass
class Game:
    """One player's round; methods receive monotonic time in seconds.

    board[position] is the source tile ID, both numbered 0..8. For example,
    [1, 0, 2, 3, 4, 5, 6, 7, 8] needs one swap of positions 0 and 1.
    Passing time in explicitly makes pause/countdown tests deterministic.
    """

    board: list[int] = field(default_factory=lambda: list(range(TILE_COUNT)))
    phase: str = "idle"
    moves: int = 0
    accumulated: float = 0.0
    started_at: float = 0.0
    countdown_end: float = 0.0

    def start(self, now: float, rng: Random | None = None) -> None:
        """Shuffle all nine tiles and start a new three-second countdown."""
        self.board = list(range(TILE_COUNT))
        (rng or Random()).shuffle(self.board)
        if self.board == list(range(TILE_COUNT)):
            self.board[0], self.board[1] = self.board[1], self.board[0]
        self.moves = 0
        self.accumulated = 0.0
        self.phase = "countdown"
        self.countdown_end = now + COUNTDOWN

    def tick(self, now: float) -> None:
        """Advance the countdown without sleeping or blocking Streamlit."""
        if self.phase == "countdown" and now >= self.countdown_end:
            self.started_at = self.countdown_end
            self.phase = "running"

    def remaining(self, now: float) -> int:
        return max(0, ceil(self.countdown_end - now))

    def elapsed(self, now: float) -> float:
        self.tick(now)
        return self.accumulated + (
            max(0.0, now - self.started_at) if self.phase == "running" else 0.0
        )

    def swap(self, first: int, second: int, now: float) -> bool:
        """Swap two positions, returning True only when a move is accepted."""
        self.tick(now)
        if (
            self.phase != "running"
            or type(first) is not int
            or type(second) is not int
            or not 0 <= first < TILE_COUNT
            or not 0 <= second < TILE_COUNT
            or first == second
        ):
            return False
        self.board[first], self.board[second] = self.board[second], self.board[first]
        self.moves += 1
        if self.board == list(range(TILE_COUNT)):
            self.accumulated = self.elapsed(now)
            self.phase = "solved"
        return True

    def pause(self, now: float) -> None:
        if self.phase in ("countdown", "running"):
            self.accumulated = self.elapsed(now)
            self.phase = "paused"

    def resume(self, now: float) -> None:
        if self.phase == "paused":
            self.phase = "countdown"
            self.countdown_end = now + COUNTDOWN
