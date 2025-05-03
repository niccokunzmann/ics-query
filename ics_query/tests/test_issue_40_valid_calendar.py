"""We make sure that the result can be processed by another icalendar application.

See https://github.com/niccokunzmann/ics-query/issues/40
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from icalendar import Calendar

from ics_query import __version__

if TYPE_CHECKING:
    from ics_query.tests.conftest import ExampleRun


@pytest.fixture()
def calendar(run) -> ExampleRun:
    """Return a calendar that is wrapped around the event."""
    result = run("first", "--as-calendar", "one-event-without-timezone.ics")
    return Calendar.from_ical(result.output)


def test_result_is_wrapped_in_a_calendar(calendar: Calendar):
    """Add the calendar component around the event."""
    assert calendar.name == "VCALENDAR"


def test_the_product_id_is_that_of_ics_query(calendar):
    """The product id is set with version."""
    assert calendar["PRODID"] == f"ics-query {__version__}"


def test_the_version_is_set(calendar):
    """Version is required."""
    assert calendar["VERSION"] == "2.0"
