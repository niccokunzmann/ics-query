"""This tests parsing input times and dates."""

from datetime import timedelta

import pytest

from ics_query.parse import to_time_and_delta


@pytest.mark.parametrize(
    ("string_argument", "expected_result"),
    [
        ("10d", timedelta(days=10)),
        ("10d10h", timedelta(days=10, hours=10)),
        ("1d2h12m33s", timedelta(days=1, hours=2, minutes=12, seconds=33)),
        ("3600s", timedelta(seconds=3600)),
        ("10m", timedelta(minutes=10)),
        ("23h", timedelta(hours=23)),
    ],
)
@pytest.mark.parametrize("plus", ["", "+"])
def test_parse_to_date_argument(string_argument, expected_result, plus):
    """Check that we can properly parse what is accepted."""
    result = to_time_and_delta(plus + string_argument)
    assert result == expected_result
