"""Add options so they can be found by pytest.

See https://stackoverflow.com/a/31526934/1320237
"""

import pytest


def pytest_addoption(parser: pytest.Parser):
    """Add options to pytest."""
    # see https://stackoverflow.com/a/58425144
    parser.addoption(
        "--binary", action="store", default="ics-query", help="the ics-query command"
    )
    print("addoption")
