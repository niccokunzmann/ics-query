"""The command line interface."""

from __future__ import annotations

import functools
import os  # noqa: TCH003
import sys
import typing as t

import click
import recurring_ical_events
from icalendar import Calendar
from recurring_ical_events import CalendarQuery

from . import parse

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
        calendar = Calendar.from_ical(file.read())
        return recurring_ical_events.of(calendar)


arg_calendar = click.argument("calendar", type=CalendarQueryInputArgument("rb"))
arg_output = click.argument("output", type=ComponentsResultArgument("wb"))


@click.group()
def main():
    """Simple program that greets NAME for a total of COUNT times."""
    # sys.stdout = sys.stderr  # remove accidential print impact


pass_datetime = click.make_pass_decorator(parse.to_time)


@main.command()
@click.argument("date", type=parse.to_time)
@arg_calendar
@arg_output
def at(calendar: CalendarQuery, output: ComponentsResult, date: DateArgument):
    """Get the components at a certain time."""
    for event in calendar.at(date):
        print("debug")
        output.add_component(event)


__all__ = ["main"]
