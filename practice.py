"""A visible placeholder, not an implementation or fallback to the solution."""

from typing import NoReturn


class ExerciseIncomplete(NotImplementedError):
    pass


def TODO(number: int, task: str) -> NoReturn:
    """Replace each TODO(...) call with your Python code, then remove the call."""
    raise ExerciseIncomplete(f"Exercise {number}: {task}. See WORKSHOP.md.")
