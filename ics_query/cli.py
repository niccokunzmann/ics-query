"""The command line interface."""

from __future__ import annotations

import functools
import os  # noqa: TCH003
import sys
import typing as t

import click
import recurring_ical_events
from icalendar.cal import Calendar, Component

from . import parse
from .version import cli_version

if t.TYPE_CHECKING:
    from io import FileIO

    from icalendar.cal import Component

    from .parse import Date

print = functools.partial(print, file=sys.stderr)  # noqa: A001


class ComponentsResult:
    """Output interface for components."""

    def __init__(self, output: FileIO):
        """Create a new result."""
        self._file = output

    def add_component(self, component: Component):
        """Return a component."""
        self._file.write(component.to_ical())

    def add_components(self, components: t.Iterable[Component]):
        """Add all components."""
        for component in components:
            self.add_component(component)


class ComponentsResultArgument(click.File):
    """Argument for the result."""

    def convert(
        self,
        value: str | os.PathLike[str] | t.IO[t.Any],
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> ComponentsResult:
        """Return a ComponentsResult."""
        file = super().convert(value, param, ctx)
        return ComponentsResult(file)


class JoinedCalendars:
    def __init__(self, calendars: list[Calendar]):
        """Join multiple calendars."""
        self.queries = [recurring_ical_events.of(calendar) for calendar in calendars]

    def at(self, dt: tuple[int]) -> t.Generator[Component]:
        """Return the components."""
        for query in self.queries:
            yield from query.at(dt)

    def first(self) -> t.Generator[Component]:
        """Return the first events of all calendars."""
        for query in self.queries:
            for component in query.all():
                yield component
                break

    def between(
        self, start: parse.Date, end: parse.DateAndDelta
    ) -> t.Generator[Component]:
        for query in self.queries:
            yield from query.between(start, end)


class CalendarQueryInputArgument(click.File):
    """Argument for the result."""

    def convert(
        self,
        value: str | os.PathLike[str] | t.IO[t.Any],
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> recurring_ical_events.CalendarQuery:
        """Return a CalendarQuery."""
        file = super().convert(value, param, ctx)
        calendars = Calendar.from_ical(file.read(), multiple=True)
        return JoinedCalendars(calendars)


arg_calendar = click.argument("calendar", type=CalendarQueryInputArgument("rb"))
arg_output = click.argument("output", type=ComponentsResultArgument("wb"))


@click.group()
@click.version_option(cli_version)
def main():
    """Find out what happens in ICS calendar files.

    ics-query can query and filter RFC 5545 compatible .ics files.
    Components are events, journal entries and TODOs.

    \b
    Common Parameters
    -----------------

    Common parameters are described below.

    CALENDAR

    The CALENDAR is a readable file with one or more ICS calendars in it.
    If CALENDAR is "-", then the standard input is used.

    OUTPUT

    This is the OUTPUT file for the result.
    It is usually a path to a file that can be written to.
    If OUTPUT is "-", then the standard output is used.

    \b
    Notes on Calculation
    --------------------

    An event can be very long. If you request smaller time spans or a time as
    exact as a second, the event will still occur within this time span if it
    happens during that time.

    Generally, an event occurs within a time span if this applies:

        event.DTSTART <= span.DTEND and span.DTSTART < event.DTEND

    The START is INCLUSIVE, then END is EXCLUSIVE.

    \b
    Notes on Timezones
    ------------------
    """  # noqa: D301


pass_datetime = click.make_pass_decorator(parse.to_time)


@main.command()
@click.argument("date", type=parse.to_time)
@arg_calendar
@arg_output
def at(calendar: JoinedCalendars, output: ComponentsResult, date: Date):
    """Occurrences at a certain dates.

    YEAR

        All occurrences in this year.

    \b
        Formats:
    \b
            YYYY
    \b
        Examples:
    \b
            ics-query at 2024       # all occurrences in year 2024
            ics-query at `date +%Y` # all occurrences in this year

    MONTH

        All occurrences in this month.

    \b
        Formats:
    \b
            YYYY-MM
            YYYY-M
            YYYYMM
    \b
        Examples:
    \b
            ics-query at 2019-10      # October 2019
            ics-query at 1990-01      # January 1990
            ics-query at 1990-1       # January 1990
            ics-query at 199001       # January 1990
            ics-query at `date +%Y%m` # this month

    DAY

        All occurrences in one day.

    \b
        Formats:
    \b
            YYYY-MM-DD
            YYYY-M-D
            YYYYMMDD
    \b
        Examples:
    \b
            ics-query at 1990-01-01     # 1st January 1990
            ics-query at 1990-1-1       # 1st January 1990
            ics-query at 19900101       # 1st January 1990
            ics-query at `date +%Y%m%d` # today

    HOUR

        All occurrences within one hour.

    \b
        Formats:
    \b
            YYYY-MM-DD HH
            YYYY-MM-DDTHH
            YYYY-M-DTH
            YYYYMMDDTHH
            YYYYMMDDHH
    \b
        Examples:
    \b
            ics-query at 1990-01-01 00    # 1st January 1990, 12am - 1am
            ics-query at 1990-01-01T00    # 1st January 1990, 12am - 1am
            ics-query at 1990-1-1T17      # 1st January 1990, 17:00 - 18:00
            ics-query at 19900101T23      # 1st January 1990, 23:00 - midnight
            ics-query at 1990010123       # 1st January 1990, 23:00 - midnight
            ics-query at `date +%Y%m%d%H` # this hour

    MINUTE

        All occurrences within one minute.

    \b
        Formats:
    \b
            YYYY-MM-DD HH:MM
            YYYY-MM-DDTHH:MM
            YYYY-M-DTH:M
            YYYYMMDDTHHMM
            YYYYMMDDHHMM
    \b
        Examples:
    \b
            ics-query at 1990-01-01 10:10   # 1st January 1990, 10:10am - 10:11am
            ics-query at 1990-01-01T10:10   # 1st January 1990, 10:10am - 10:11am
            ics-query at 1990-1-1T7:2       # 1st January 1990, 07:02 - 07:03
            ics-query at 19900101T2359      # 1st January 1990, 23:59 - midnight
            ics-query at 199001012359       # 1st January 1990, 23:59 - midnight
            ics-query at `date +%Y%m%d%H%M` # this minute

    SECOND

        All occurrences at a precise time.

    \b
        Formats:
    \b
            YYYY-MM-DD HH:MM:SS
            YYYY-MM-DDTHH:MM:SS
            YYYY-M-DTH:M:S
            YYYYMMDDTHHMMSS
            YYYYMMDDHHMMSS
    \b
        Examples:
    \b
            ics-query at 1990-01-01 10:10:00  # 1st January 1990, 10:10am
            ics-query at 1990-01-01T10:10:00  # 1st January 1990, 10:10am
            ics-query at 1990-1-1T7:2:30      # 1st January 1990, 07:02:30
            ics-query at 19901231T235959      # 31st December 1990, 23:59:59
            ics-query at 19900101235959       # 1st January 1990, 23:59:59
            ics-query at `date +%Y%m%d%H%M%S` # now
    """  # noqa: D301
    output.add_components(calendar.at(date))


@main.command()
@arg_calendar
@arg_output
def first(calendar: JoinedCalendars, output: ComponentsResult):
    """Print only the first occurrence in each calendar.

    \b
    This example prints the first event in calendar.ics:
    \b
        ics-query first calendar.ics -

    """  # noqa: D301
    output.add_components(calendar.first())


@main.command()
@click.argument("start", type=parse.to_time)
@click.argument("end", type=parse.to_time_and_delta)
@arg_calendar
@arg_output
def between(
    start: parse.Date,
    end: parse.DateAndDelta,
    calendar: JoinedCalendars,
    output: ComponentsResult,
):
    """Print all occurrences between the START and the END.

    The start is inclusive, the end is exclusive.

    This example returns the events within the next week:

    \b
        ics-query between `date +%Y%m%d` +7d calendar.ics -

    This example saves the events from the 1st of May 2024 to the 10th of June in
    events.ics:

    \b
        ics-query between 2024-5-1 2024-6-10 calendar.ics events.ics

    In this example, you can check what is happening on New Years Eve 2025 around
    midnight:

    \b
        ics-query between 2025-12-31T21:00 +6h calendar.ics events.ics

    \b
    Absolute Time
    -------------

    START must be specified as an absolute time.
    END can be absolute or relative to START, see Relative Time below.

    Each of the formats specify the earliest time e.g. the start of a day.
    Thus, if START == END, there are 0 seconds in between and the result is
    only what happens during that time or starts exactly at that time.

    YEAR

        Specifiy the start of the year.

    \b
        Formats:
    \b
            YYYY
    \b
        Examples:
    \b
            2024       # start of 2024
            `date +%Y` # this year

    MONTH

        The start of the month.

    \b
        Formats:
    \b
            YYYY-MM
            YYYY-M
            YYYYMM
    \b
        Examples:
    \b
            2019-10      # October 2019
            1990-01      # January 1990
            1990-1       # January 1990
            199001       # January 1990
            `date +%Y%m` # this month

    DAY

        The start of the day

    \b
        Formats:
    \b
            YYYY-MM-DD
            YYYY-M-D
            YYYYMMDD
    \b
        Examples:
    \b
            1990-01-01     # 1st January 1990
            1990-1-1       # 1st January 1990
            19900101       # 1st January 1990
            `date +%Y%m%d` # today

    HOUR

        The start of the hour.

    \b
        Formats:
    \b
            YYYY-MM-DD HH
            YYYY-MM-DDTHH
            YYYY-M-DTH
            YYYYMMDDTHH
            YYYYMMDDHH
    \b
        Examples:
    \b
            1990-01-01 01    # 1st January 1990, 1am
            1990-01-01T01    # 1st January 1990, 1am
            1990-1-1T17      # 1st January 1990, 17:00
            19900101T23      # 1st January 1990, 23:00
            1990010123       # 1st January 1990, 23:00
            `date +%Y%m%d%H` # this hour

    MINUTE

        The start of a minute.

    \b
        Formats:
    \b
            YYYY-MM-DD HH:MM
            YYYY-MM-DDTHH:MM
            YYYY-M-DTH:M
            YYYYMMDDTHHMM
            YYYYMMDDHHMM
    \b
        Examples:
    \b
            1990-01-01 10:10   # 1st January 1990, 10:10am
            1990-01-01T10:10   # 1st January 1990, 10:10am
            1990-1-1T7:2       # 1st January 1990, 07:02
            19900101T2359      # 1st January 1990, 23:59
            199001012359       # 1st January 1990, 23:59
            `date +%Y%m%d%H%M` # this minute

    SECOND

        A precise time. RFC 5545 calendars are specified to the second.
        This is the most precise format to specify times.

    \b
        Formats:
    \b
            YYYY-MM-DD HH:MM:SS
            YYYY-MM-DDTHH:MM:SS
            YYYY-M-DTH:M:S
            YYYYMMDDTHHMMSS
            YYYYMMDDHHMMSS
    \b
        Examples:
    \b
            1990-01-01 10:10:00  # 1st January 1990, 10:10am
            1990-01-01T10:10:00  # 1st January 1990, 10:10am
            1990-1-1T7:2:30      # 1st January 1990, 07:02:30
            19901231T235959      # 31st December 1990, 23:59:59
            19900101235959       # 1st January 1990, 23:59:59
            `date +%Y%m%d%H%M%S` # now
    \b
    Relative Time
    -------------

    The END argument can be a time range.
    The + at the beginning is optional but makes for a better reading.

    \b
    Examples:
    \b
    Add 10 days to START: +10d
    Add 24 hours to START: +1d or +24h
    Add 3 hours to START: +3h
    Add 30 minutes to START: +30m
    Add 1000 seconds to START: +1000s
    \b
    You can also combine the ranges:
    Add 1 day and 12 hours to START: +1d12h
    Add 3 hours and 15 minutes to START: +3h15m

    """  # noqa: D301
    output.add_components(calendar.between(start, end))


__all__ = ["main"]
