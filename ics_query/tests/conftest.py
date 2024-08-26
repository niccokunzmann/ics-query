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
from copy import deepcopy
from pathlib import Path
from typing import Callable, NamedTuple

import pytest

HERE = Path(__file__).parent
IO_DIRECTORY = HERE / "runs"
CALENDARS_DIRECTORY = IO_DIRECTORY / "calendars"


class TestRun(NamedTuple):
    """The result from a test run."""

    exit_code: int
    output: str
    error: str

    @classmethod
    def from_completed_process(
        cls, completed_process: subprocess.CompletedProcess
    ) -> TestRun:
        """Create a new run result."""
        stdout = completed_process.stdout.decode("UTF-8").replace("\r\n", "\n")
        print(stdout)
        return cls(
            completed_process.returncode,
            stdout,
            completed_process.stderr.decode("UTF-8"),
        )


def run_ics_query(*command, cwd=CALENDARS_DIRECTORY) -> TestRun:
    """Run ics-qeury with a command."""
    cmd = ["ics-query", *command]
    print(" ".join(cmd))
    completed_process = subprocess.run(  # noqa: S603, RUF100
        cmd,  # noqa: S603, RUF100
        capture_output=True,
        timeout=3,
        check=False,
        cwd=cwd,
    )
    return TestRun.from_completed_process(completed_process)


class IOTestCase(NamedTuple):
    """An example test case."""

    name: str
    command: list[str]
    location: Path
    expected_output: str

    @classmethod
    def from_path(cls, path: Path) -> IOTestCase:
        """Create a new testcase from the files."""
        expected_output = path.read_text(encoding="UTF-8").replace("\r\n", "\n")
        return cls(path.name, path.stem.split(), path.parent, expected_output)

    def run(self) -> TestRun:
        """Run this test case and return the result."""
        return run_ics_query(*self.command)


io_test_cases = [
    IOTestCase.from_path(test_case_path)
    for test_case_path in IO_DIRECTORY.iterdir()
    if test_case_path.is_file()
]


@pytest.fixture(params=io_test_cases)
def io_testcase(request) -> IOTestCase:
    """Go though all the IO test cases."""
    return deepcopy(request.param)


@pytest.fixture
def run() -> Callable[..., TestRun]:
    """Return a runner function."""
    return run_ics_query


__all__ = ["IOTestCase", "TestRun"]
