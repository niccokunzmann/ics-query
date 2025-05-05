"""We make sure that the result can be processed by another icalendar application.

See https://github.com/niccokunzmann/ics-query/issues/40
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ics_query import __version__

if TYPE_CHECKING:
    from icalendar import Calendar, Timezone

    from ics_query.tests.conftest import ExampleRun


@pytest.fixture()
def calendar(run) -> ExampleRun:
    """Return a calendar that is wrapped around the event."""
    return run("first", "--as-calendar", "one-event-without-timezone.ics").calendar


def test_result_is_wrapped_in_a_calendar(calendar: Calendar):
    """Add the calendar component around the event."""
    assert calendar.name == "VCALENDAR"


def test_the_product_id_is_that_of_ics_query(calendar):
    """The product id is set with version."""
    assert calendar["PRODID"] == f"ics-query {__version__}"


def test_the_version_is_set(calendar):
    """Version is required."""
    assert calendar["VERSION"] == "2.0"


def test_no_timezone_is_included(calendar):
    """We do not have timezones in this file, so there should be none."""
    assert calendar.timezones == []


@pytest.mark.parametrize(
    "file",
    [
        "one-event.ics",  # one timezone
        "multiple-calendars.ics",  # same timezone twice
    ],
)
def test_calendar_adds_timezones_automatically(run, file):
    """Return a calendar that is wrapped around the event."""
    calendar = run("first", "--as-calendar", file).calendar
    assert len(calendar.timezones) == 1
    tz: Timezone = calendar.timezones[0]
    assert tz.tz_name == "Europe/Berlin"


def test_x_wr_timezone_is_added(run):
    """X-WR-TIMEZONE requires adding the timezone component manually."""
    calendar = run(
        "first", "--as-calendar", "x-wr-timezone-rdate-hackerpublicradio.ics"
    ).calendar
    assert len(calendar.timezones) == 1
    tz: Timezone = calendar.timezones[0]
    assert tz.tz_name == "Europe/London"
