"""Test the commmand line."""
from .conftest import IOTestCase


def test_check_program_output(io_testcase:IOTestCase):
    """Run the test case and check the output."""
    result = io_testcase.run()
    assert result.output == io_testcase.expected_output
