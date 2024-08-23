"""Functions for parsing the content."""

from __future__ import annotations

import re
import datetime

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

REGEX_TIMEDELTA = re.compile(
    r"^(?:(?P<days>\d+)d)?"
    r"(?:(?P<hours>\d+)h)?"
    r"(?:(?P<minutes>\d+)m)?"
    r"(?:(?P<seconds>\d+)s)?"
    r"$"
)


def to_time(dt: str) -> tuple[int]:
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


def to_time_and_delta(dt: str) -> tuple[int] | datetime.timedelta:
    """Parse to a absolute time or timedelta."""
    parsed_td = REGEX_TIMEDELTA.match(dt)
    if parsed_td is None:
        return to_time(dt)
    print(parsed_td.groupdict())
    kw = {
        k:int(v)
        for k, v in parsed_td.groupdict().items()
        if v is not None
    }
    return datetime.timedelta(**kw)

__all__ = ["to_time", "DateArgument"]
