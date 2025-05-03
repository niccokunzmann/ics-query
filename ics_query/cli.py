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
"""The command line interface."""

from __future__ import annotations

import functools
import os  # noqa: TCH003
import sys
import typing as t
import zoneinfo

import click
from icalendar import Calendar, Component, Timezone
from tzlocal import get_localzone_name

from . import parse
from .query import Query
from .version import __version__, cli_version

if t.TYPE_CHECKING:
    from io import FileIO

    import recurring_ical_events
    from icalendar import Component

    from .parse import Date

print = functools.partial(print, file=sys.stderr)  # noqa: A001

ENV_PREFIX = "ICS_QUERY"
LICENSE = """
ics-query
Copyright (C) 2024 Nicco Kunzmann

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


class ComponentsResult:
    """Output interface for components."""

    def __init__(self, output: FileIO):
        """Create a new result."""
        self._file = output
        self._entered = False

    def write(self, data: bytes | str):
        """Write data to the output."""
        if isinstance(data, str):
            data = data.encode()
        self._file.write(data)

    def __enter__(self):
        """Start adding components."""
        self._entered = True

    def __exit__(self, exc_type, exc_value, traceback):
        """Stop adding components."""
        self._entered = False

    def add_component(self, component: Component) -> None:
        """Return a component."""
        assert self._entered
        self.write(component.to_ical())

    def add_components(self, components: t.Iterable[Component]) -> None:
        """Add all components."""
        for component in components:
            self.add_component(component)


class CalendarResult(ComponentsResult):
    """Wrap the resulting components in a calendar."""

    CALENDAR_START = (
        f"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:ics-query {__version__}\r\n"
    )
    CALENDAR_END = "END:VCALENDAR\r\n"

    def __init__(self, output: FileIO, timezones: list[Timezone]):
        super().__init__(output)
        self.timezones = timezones

    def __enter__(self):
        """Start the calendar."""
        super().__enter__()
        self.write(self.CALENDAR_START)
        for timezone in self.timezones:
            self.write(timezone.to_ical())

    def __exit__(self, exc_type, exc_value, traceback):
        """Stop the calendar."""
        self.write(self.CALENDAR_END)
        super().__exit__(exc_type, exc_value, traceback)


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
        # we claim the as_calendar argument
        wrap_calendar = ctx.params.pop("as_calendar", False)
        if wrap_calendar:
            joined: JoinedCalendars = ctx.params["calendar"]
            return CalendarResult(file, joined.timezones)
        return ComponentsResult(file)


class JoinedCalendars:
    def __init__(
        self, calendars: list[Calendar], timezone: str, components: t.Sequence[str]
    ):
        """Join multiple calendars."""
        self.calendars = calendars
        self.queries = [
            Query(calendar, timezone, components=components) for calendar in calendars
        ]

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

    def all(self) -> t.Generator[Component]:
        """Return the first events of all calendars."""
        for query in self.queries:
            yield from query.all()

    def between(
        self, start: parse.Date, end: parse.DateAndDelta
    ) -> t.Generator[Component]:
        for query in self.queries:
            yield from query.between(start, end)

    @property
    def timezones(self) -> list[Timezone]:
        """Return all the timezones in use."""
        result = []
        tzids = set()
        # add existing timezone components first
        for calendar in self.calendars:
            for timezone in calendar.timezones:
                if timezone.tz_name not in tzids:
                    tzids.add(timezone.tz_name)
                    result.append(timezone)
        # add X-WR-TIMEZONE later to prevent generating if existing
        for calendar in self.calendars:
            tzid = calendar.get("X-WR-TIMEZONE", None)
            if tzid is not None and tzid not in tzids:
                timezone = Timezone.from_tzid(tzid)
                tzids.add(timezone.tz_name)
                tzids.add(tzid)
                result.append(timezone)
        return result


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
        components = ctx.params.get("component", ("VEVENT", "VTODO", "VJOURNAL"))
        timezone = ctx.params.get("tz", "")
        return JoinedCalendars(calendars, timezone, components)


opt_components = click.option(
    "--component",
    "-c",
    multiple=True,
    envvar=ENV_PREFIX + "_COMPONENT",
    help=(
        "Select the components which can be returned. "
        "By default all supported components can be in the result. "
        "Possible values are: VEVENT, VTODO, VJOURNAL. "
    ),
)

opt_timezone = click.option(
    "--tz",
    envvar=ENV_PREFIX + "_TZ",
    help=("Set the timezone. See also --available-timezones"),
)

opt_calendar = click.option(
    "--as-calendar",
    envvar=ENV_PREFIX + "_AS_CALENDAR",
    is_flag=True,
    default=False,
    is_eager=True,
    help="Return a valid calendar, not just the components.",
)


def arg_calendar(func):
    """Decorator for a calendar argument with all used options."""
    arg = click.argument("calendar", type=CalendarQueryInputArgument("rb"))

    @functools.wraps(func)
    def wrapper(*args, component=(), tz="", **kw):  # noqa: ARG001
        """Remove some parameters."""
        return func(*args, **kw)

    return opt_timezone(opt_components(arg(wrapper)))


def arg_output(func):
    """Add the output argument and its parameters."""
    # Option with many values and list as result
    # see https://click.palletsprojects.com/en/latest/options/#multiple-options
    arg = click.argument("output", type=ComponentsResultArgument("wb"), default="-")
    return opt_calendar(arg(func))


def opt_available_timezones(*param_decls: str, **kwargs: t.Any) -> t.Callable:
    """List available timezones.

    This is copied from the --help option.

    Commonly used timezone names are added first.
    """

    def callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:  # noqa: FBT001, ARG001
        if not value or ctx.resilient_parsing:
            return

        click.echo("localtime")  # special local time handle
        click.echo(get_localzone_name())
        click.echo("UTC")
        all_zones = zoneinfo.available_timezones()
        for zone in sorted(all_zones, key=str.lower):
            click.echo(zone)
        ctx.exit()

    if not param_decls:
        param_decls = ("--available-timezones",)

    kwargs.setdefault("is_flag", True)
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("is_eager", True)
    kwargs.setdefault("help", "List all available timezones and exit.")
    kwargs["callback"] = callback
    return click.option(*param_decls, **kwargs)


def opt_license(*param_decls: str, **kwargs: t.Any) -> t.Callable:
    """Show the license

    This is copied from the --help option.
    """

    def callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:  # noqa: FBT001, ARG001
        if not value or ctx.resilient_parsing:
            return
        click.echo(LICENSE)
        ctx.exit()

    if not param_decls:
        param_decls = ("--license",)

    kwargs.setdefault("is_flag", True)
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("is_eager", True)
    kwargs.setdefault("help", "Show the license and exit.")
    kwargs["callback"] = callback
    return click.option(*param_decls, **kwargs)


@click.group()
@click.version_option(cli_version)
@opt_available_timezones()
@opt_license()
def cli():
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
    Calculation
    -----------

    An event can be very long. If you request smaller time spans or a time as
    exact as a second, the event will still occur within this time span if it
    happens during that time.

    Generally, an event occurs within a time span if this applies:

        event.DTSTART <= span.DTEND and span.DTSTART < event.DTEND

    The START is INCLUSIVE, then END is EXCLUSIVE.

    \b
    Timezones
    ---------

    We have several timezones available to choose from.
    While the calendar entries might use their own timezone definitions,
    the timezone parameters of ics-query use the timezone definitions of
    Python's tzdata package.

    You can list all timezones available with this command:

    \b
        ics-query --available-timezones

    By default the local time of the components is assumed.
    In this example, two events happen at 6am, one in Berlin and one in Los Angeles.
    Both are hours apart though.

    \b
        $ ics-query at 2024-08-20 Berlin-Los-Angeles.ics - | grep -E 'DTSTART|SUMMARY'
        SUMMARY:6:00-7:00 Europe/Berlin 20th August
        DTSTART;TZID=Europe/Berlin:20240820T060000
        SUMMARY:6:00-7:00 Amerika/Los Angeles 20th August
        DTSTART;TZID=America/Los_Angeles:20240820T060000

    If you however wish to get all events in a certain timezone, use the --tz parameter.
    In this example, the event that happens at the 19th of August at 21:00 in
    Los Angeles is actually happening on the 20th in local Berlin time.

    \b
        $ ics-query at --tz=Europe/Berlin 2024-08-20 Berlin-Los-Angeles.ics - \\
            | grep -E 'DTSTART|SUMMARY'
        SUMMARY:6:00-7:00 Europe/Berlin 20th August
        DTSTART;TZID=Europe/Berlin:20240820T060000
        SUMMARY:6:00-7:00 Amerika/Los Angeles 20th August
        DTSTART;TZID=Europe/Berlin:20240820T150000
        SUMMARY:21:00-22:00 Amerika/Los Angeles 19th August
        DTSTART;TZID=Europe/Berlin:20240820T060000

    If you wish to get events in your local time, use --tz localtime.
    If you like UTC, use --tz UTC.

    You can also set the environment variable ICS_QUERY_TZ to the timezone instead of
    passing --tz.

    \b
    Components
    ----------

    We support different types of recurring components: VEVENT, VTODO, VJOURNAL.
    You can specify which can be in the result using the --component parameter.

    You can also set the environment variable ICS_QUERY_COMPONENT to the timezone
    instead of passing --component.

    """  # noqa: D301


pass_datetime = click.make_pass_decorator(parse.to_time)


@cli.command()
@click.argument("date", type=parse.to_time)
@arg_calendar
@arg_output
def at(calendar: JoinedCalendars, output: ComponentsResult, date: Date):
    """Print occurrences at a certain date or time.

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
    with output:
        output.add_components(calendar.at(date))


@cli.command()
@arg_calendar
@arg_output
def first(calendar: JoinedCalendars, output: ComponentsResult):
    """Print only the first occurrence.

    This prints the first occurrence in each calendar that is given.

    \b
    This example prints the first event in calendar.ics:
    \b
        ics-query first --component VEVENT calendar.ics -

    """  # noqa: D301
    with output:
        output.add_components(calendar.first())


@cli.command()
@arg_calendar
@arg_output
def all(calendar: JoinedCalendars, output: ComponentsResult):  # noqa: A001
    """Print all occurrences in a calendar.

    The result is ordered by the start of the occurrences.
    If you have multiple calendars, the result will contain
    the occurrences of the first calendar before those of the second calendar
    and so on.

    \b
    This example prints all events in calendar.ics:
    \b
        ics-query all --component VEVENT calendar.ics -

    Note that calendars can create hundreds of occurrences and especially
    contain endless repetitions. Use this with care as the output is
    potentially enourmous. You can mitigate this by closing the OUTPUT
    when you have enough e.g. with a head command.
    """  # noqa: D301
    with output:
        output.add_components(calendar.all())


@cli.command()
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
    """Print occurrences between a START and an END.

    The start is inclusive, the end is exclusive.

    This example returns the events within the next week:

    \b
        ics-query between --component VEVENT `date +%Y%m%d` +7d calendar.ics -

    This example saves the events from the 1st of May 2024 to the 10th of June in
    events.ics:

    \b
        ics-query between --component VEVENT 2024-5-1 2024-6-10 calendar.ics events.ics

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
    with output:
        output.add_components(calendar.between(start, end))


def main():
    """Run the program."""
    cli(auto_envvar_prefix=ENV_PREFIX)


__all__ = ["main", "ENV_PREFIX", "cli"]
