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
