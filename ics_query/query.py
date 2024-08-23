"""This is an adaptation of the CalendarQuery."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Sequence

import x_wr_timezone
import zoneinfo
from recurring_ical_events import CalendarQuery, Occurrence

if TYPE_CHECKING:
    from icalendar import Calendar


class Query(CalendarQuery):
    def __init__(self, calendar: Calendar, timezone: str, components: Sequence[str]):
        """Create a new query."""
        super().__init__(
            x_wr_timezone.to_standard(calendar),
            components=components,
            skip_bad_series=True,
        )
        self.timezone = zoneinfo.ZoneInfo(timezone) if timezone else None

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
