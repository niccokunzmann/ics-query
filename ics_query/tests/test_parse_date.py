"""This tests parsing input times and dates."""

import pytest

from ics_query.parse import InvalidTimeFormat, to_time, to_time_and_delta


@pytest.mark.parametrize(
    ("string_argument", "expected_result"),
    [
        # year
        ("2019", (2019,)),
        ("1991", (1991,)),
        # month
        ("2000-11", (2000, 11)),
        ("2001-01", (2001, 1)),
        ("1990-1", (1990, 1)),
        ("201011", (2010, 11)),
        ("199003", (1990, 3)),
        # day
        ("1990-01-01", (1990, 1, 1)),
        ("2001-3-4", (2001, 3, 4)),
        ("19801231", (1980, 12, 31)),
        # hour
        ("1990-01-01 00", (1990, 1, 1, 0)),
        ("1991-12-31T23", (1991, 12, 31, 23)),
        ("2003-1-1T17", (2003, 1, 1, 17)),
        ("20010409T12", (2001, 4, 9, 12)),
        ("2014101018", (2014, 10, 10, 18)),
        # minute
        ("1990-01-01 00:10", (1990, 1, 1, 0, 10)),
        ("1991-12-31T23:11", (1991, 12, 31, 23, 11)),
        ("2003-1-1T17:0", (2003, 1, 1, 17, 0)),
        ("2004-1-1T7:0", (2004, 1, 1, 7, 0)),
        ("20010409T12:59", (2001, 4, 9, 12, 59)),
        ("201410101830", (2014, 10, 10, 18, 30)),
        # second
        ("1990-01-01 00:10:12", (1990, 1, 1, 0, 10, 12)),
        ("1991-12-31T23:11:0", (1991, 12, 31, 23, 11, 0)),
        ("2003-1-1T17:0:11", (2003, 1, 1, 17, 0, 11)),
        ("2004-1-1T7:0:10", (2004, 1, 1, 7, 0, 10)),
        ("20010409T12:59:58", (2001, 4, 9, 12, 59, 58)),
        ("20141010183012", (2014, 10, 10, 18, 30, 12)),
    ],
)
@pytest.mark.parametrize("parser", [to_time_and_delta, to_time])
def test_parse_to_date_argument(string_argument, expected_result, parser):
    """Check that we can properly parse what is accepted."""
    result = parser(string_argument)
    assert result == expected_result


@pytest.mark.parametrize(
    "dt",
    [
        "",
        "  ",
        "132",
        "12345",
    ],
)
@pytest.mark.parametrize("parser", [to_time_and_delta, to_time])
def test_invalid_time_format(dt: str, parser):
    """Check invalid time formats."""
    with pytest.raises(InvalidTimeFormat):
        parser(dt)
