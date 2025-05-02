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
"""Test the commmand line."""

from tzlocal import get_localzone_name

from ics_query.version import version

from .conftest import IOTestCase


def test_check_program_output(io_testcase: IOTestCase):
    """Run the test case and check the output."""
    result = io_testcase.run()
    print(result.error)
    assert result.exit_code == 0, "The process must not exist with an error."
    assert result.output == io_testcase.expected_output


def test_version(run):
    """Check the version is displayed."""
    result = run("--version")
    assert result.exit_code == 0
    assert version in result.output


def test_license(run):
    """Check the version is displayed."""
    result = run("--license")
    assert result.exit_code == 0
    assert "Copyright (C) 2024 Nicco Kunzmann" in result.output
    assert "GNU General Public License" in result.output


def test_timezones(run):
    """Check the available timezones."""
    result = run("--available-timezones")
    tz = result.output.split()
    assert result.exit_code == 0
    assert tz.index("Zulu") > tz.index("Pacific/Nauru")
    assert tz.index("Pacific/Nauru") > tz.index("UTC")
    assert tz.index("UTC") > tz.index("localtime")


def test_special_timezones(run):
    """Make sure we show special timezones first."""
    result = run("--available-timezones")
    tz = result.output.split()
    assert result.exit_code == 0
    assert tz[0] == "localtime"
    assert tz[1] == get_localzone_name()
    assert tz[2] == "UTC"


def test_localtime_is_not_in_the_result_string(run):
    """We do not want 'localtime' to turn up as the result tz name."""
    result = run("first", "--tz", "localtime", "one-event-without-timezone.ics")
    assert (
        f"DTSTART;TZID={get_localzone_name()}:201903" in result.output
        or "TZID=" not in result.output
    )
    assert (
        f"DTEND;TZID={get_localzone_name()}:201903" in result.output
        or "TZID=" not in result.output
    )
