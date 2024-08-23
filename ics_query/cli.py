"""The command line interface."""

from __future__ import annotations

import functools
import os  # noqa: TCH003
import sys
import typing as t

import click
import recurring_ical_events
from icalendar.cal import Calendar, Component
from recurring_ical_events import CalendarQuery

from . import parse
from .version import __version__

if t.TYPE_CHECKING:
    from io import FileIO

    from icalendar.cal import Component

    from .parse import DateArgument

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
@click.version_option(__version__)
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
def at(calendar: JoinedCalendars, output: ComponentsResult, date: DateArgument):
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
    """Print only the first occurrence in each calendar."""
    output.add_components(calendar.first())


__all__ = ["main"]
