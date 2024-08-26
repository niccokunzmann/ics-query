# ics-query
# Copyright (C) 2024 Nicco Kunzmann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Functions for parsing the content."""

from __future__ import annotations

import datetime
import re
from typing import Union

Date = tuple[int]
DateAndDelta = Union[Date, datetime.timedelta]


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
    r"^\+?(?:(?P<days>\d+)d)?"
    r"(?:(?P<hours>\d+)h)?"
    r"(?:(?P<minutes>\d+)m)?"
    r"(?:(?P<seconds>\d+)s)?"
    r"$"
)


def to_time(dt: str) -> Date:
    """Parse the time and date."""
    parsed_dt = REGEX_TIME.match(dt)
    if parsed_dt is None:
        raise InvalidTimeFormat(dt)

    def group(group_name: str) -> Date:
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


def to_time_and_delta(dt: str) -> DateAndDelta:
    """Parse to a absolute time or timedelta."""
    parsed_td = REGEX_TIMEDELTA.match(dt)
    if parsed_td is None:
        return to_time(dt)
    kw = {k: int(v) for k, v in parsed_td.groupdict().items() if v is not None}
    if not kw:
        raise InvalidTimeFormat(dt)
    return datetime.timedelta(**kw)


__all__ = ["to_time", "Date", "to_time_and_delta", "DateAndDelta"]
