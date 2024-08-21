"""Functions for parsing the content."""

from __future__ import annotations

DateArgument = tuple[int]


def to_time(dt: str) -> DateArgument:
    """Parse the time and date."""
    return tuple(map(int, dt.split("-")))


__all__ = ["to_time", "DateArgument"]
