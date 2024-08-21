"""Configure the tests."""

from __future__ import annotations

import subprocess
from copy import deepcopy
from pathlib import Path
from typing import NamedTuple

import pytest

HERE = Path(__file__).parent
IO_DIRECTORY = HERE / "io"


class TestRun(NamedTuple):
    """The result from a test run."""

    exit_code: int
    output: str

    @classmethod
    def from_completed_process(cls, completed_process: subprocess.CompletedProcess) -> TestRun:
        """Create a new run result."""
        return cls(completed_process.returncode, completed_process.stdout)


class IOTestCase:
    """An example test case."""

    name: str
    command: list[str]
    cwd: Path
    expected_output: str

    @classmethod
    def from_path(cls, path: Path) -> IOTestCase:
        """Create a new testcase from the files."""
        return cls(
            path.name, path.stem.split(), path.parent, path.read_text(encoding="UTF-8")
        )

    def run(self) -> TestRun:
        """Run this test case and return the result."""
        completed_process = subprocess.run(
            ["ics-query", *self.command],  # noqa: S603, S607
            stdout=subprocess.PIPE,
            timeout=3,
            check=False,
            cwd=io_testcase.cwd,
        )
        return TestRun.from_completed_process(completed_process)


io_test_cases = [
    IOTestCase.from_path(test_case_path)
    for test_case_path in IO_DIRECTORY.iterdir()
    if test_case_path.is_file()
]


@pytest.fixture(params=io_test_cases)
def io_testcase(request) -> IOTestCase:
    """Go though all the IO test cases."""
    return deepcopy(request.param)


__all__ = ["IOTestCase", "TestRun"]
