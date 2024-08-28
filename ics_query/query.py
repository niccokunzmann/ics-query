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
"""This is an adaptation of the CalendarQuery."""

from __future__ import annotations

import datetime
import zoneinfo
from typing import TYPE_CHECKING

import x_wr_timezone
from recurring_ical_events import CalendarQuery, Occurrence
from tzlocal import get_localzone

if TYPE_CHECKING:
    from collections.abc import Sequence

    from icalendar import Calendar


class Query(CalendarQuery):
    def __init__(self, calendar: Calendar, timezone: str, components: Sequence[str]):
        """Create a new query."""
        super().__init__(
            x_wr_timezone.to_standard(calendar),
            components=components,
            skip_bad_series=True,
        )
        self.timezone = self.get_timezone(timezone)

    def get_timezone(self, timezone: str) -> datetime.tzinfo | None:
        """Return the local time tz."""
        if timezone == "localtime":
            return get_localzone()
        return zoneinfo.ZoneInfo(timezone) if timezone else None

    def with_timezone(self, dt: datetime.date | datetime.datetime):
        """Add the timezone."""
        if self.timezone is None:
            return dt
        if not isinstance(dt, datetime.datetime):
            return datetime.datetime(
                year=dt.year, month=dt.month, day=dt.day, tzinfo=self.timezone
            )
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.timezone)
        return dt.astimezone(self.timezone)

    def _occurrences_between(
        self,
        start: datetime.date | datetime.datetime,
        end: datetime.date | datetime.datetime,
    ) -> list[Occurrence]:
        """Override to adapt timezones."""
        result = []
        for occurrence in super()._occurrences_between(
            self.with_timezone(start), self.with_timezone(end)
        ):
            occurrence.start = self.with_timezone(occurrence.start)
            occurrence.end = self.with_timezone(occurrence.end)
            result.append(occurrence)
        return result


__all__ = ["Query"]
