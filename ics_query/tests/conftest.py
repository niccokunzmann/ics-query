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
"""Configure the tests."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, NamedTuple

import pytest
from icalendar import Calendar

HERE = Path(__file__).parent
IO_DIRECTORY = HERE / "runs"
CALENDARS_DIRECTORY = IO_DIRECTORY / "calendars"


class ExampleRun(NamedTuple):
    """The result from a test run."""

    exit_code: int
    output: str
    error: str

    @classmethod
    def from_completed_process(
        cls, completed_process: subprocess.CompletedProcess
    ) -> ExampleRun:
        """Create a new run result."""
        stdout = completed_process.stdout.decode("UTF-8").replace("\r\n", "\n")
        print(stdout)
        return cls(
            completed_process.returncode,
            stdout,
            completed_process.stderr.decode("UTF-8"),
        )

    @property
    def calendar(self) -> Calendar:
        """Return the output as a calendar."""
        return Calendar.from_ical(self.output)


def get_binary_path(request: pytest.FixtureRequest) -> str:
    """Return the path to the ics-query command."""
    command: str = request.config.getoption("--binary")
    if command == "ics-query":
        # The default command can be found on the command line
        return command
    # we must set the path to be absolute
    return Path(command).absolute()


def run_ics_query(*command, cwd=CALENDARS_DIRECTORY, binary: str) -> ExampleRun:
    """Run ics-qeury with a command.

    - cwd is the working directory
    - binary is the path to the command
    """
    cmd = [binary, *command]
    print(" ".join(map(str, cmd)))
    completed_process = subprocess.run(  # noqa: S603, RUF100
        cmd,  # noqa: S603, RUF100
        capture_output=True,
        timeout=10,
        check=False,
        cwd=cwd,
    )
    if completed_process.stderr:
        print(completed_process.stderr.decode())
    return ExampleRun.from_completed_process(completed_process)


class IOTestCase(NamedTuple):
    """An example test case."""

    name: str
    command: list[str]
    location: Path
    expected_output: str
    binary: str

    @classmethod
    def from_path(cls, path: Path, binary: str) -> IOTestCase:
        """Create a new testcase from the files."""
        expected_output = path.read_text(encoding="UTF-8").replace("\r\n", "\n")
        return cls(path.name, path.stem.split(), path.parent, expected_output, binary)

    def run(self) -> ExampleRun:
        """Run this test case and return the result."""
        return run_ics_query(*self.command, binary=self.binary)


io_test_case_paths = [
    test_case_path
    for test_case_path in IO_DIRECTORY.iterdir()
    if test_case_path.is_file() and test_case_path.suffix == ".run"
]


@pytest.fixture(params=io_test_case_paths)
def io_testcase(request: pytest.FixtureRequest) -> IOTestCase:
    """Go though all the IO test cases."""
    path: Path = request.param
    binary = get_binary_path(request)
    return IOTestCase.from_path(path, binary)


@pytest.fixture()
def run(request: pytest.FixtureRequest) -> Callable[..., ExampleRun]:
    """Return a runner function."""

    def run(*args, **kw):
        kw["binary"] = get_binary_path(request)
        return run_ics_query(*args, **kw)

    return run


__all__ = ["IOTestCase", "ExampleRun"]
