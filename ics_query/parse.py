"""Functions for parsing the content."""

from __future__ import annotations

import re

DateArgument = tuple[int]


class InvalidTimeFormat(ValueError):
    """The value provided does not yield a precise time."""


REGEX_TIME = re.compile(
    r"^(?P<year>\d\d\d\d)"
    r"(?P<month>-\d?\d|\d\d)?"
    r"(?P<day>-\d?\d|\d\d)?"
    r"(?P<hour>[ T]\d?\d|\d\d)?"
    r"(?P<minute>:\d?\d|\d\d)?"
    r"(?P<second>:\d?\d|\d\d)?"
    r"$"
)


def to_time(dt: str) -> DateArgument:
    """Parse the time and date."""
    parsed_dt = REGEX_TIME.match(dt)
    if parsed_dt is None:
        raise InvalidTimeFormat(dt)

    def group(group_name: str) -> tuple[int]:
        """Return a group's value."""
        result = parsed_dt.group(group_name)
        while result and result[0] not in "0123456789":
            result = result[1:]
        if result is None:
            return ()
        return (int(result),)

    return (
        group("year")
        + group("month")
        + group("day")
        + group("hour")
        + group("minute")
        + group("second")
    )


__all__ = ["to_time", "DateArgument"]
