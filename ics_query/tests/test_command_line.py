"""Test the commmand line."""

from ics_query.version import version

from .conftest import IOTestCase


def test_check_program_output(io_testcase: IOTestCase):
    """Run the test case and check the output."""
    result = io_testcase.run()
    print(result.error)
    assert result.output == io_testcase.expected_output


def test_version(run):
    """Check the version is displayed."""
    result = run("--version")
    assert result.exit_code == 0
    assert version in result.output
