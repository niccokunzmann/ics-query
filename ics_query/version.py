# SPDX-FileCopyrightText: 2024 Nicco Kunzmann and Open Web Calendar Contributors <https://open-web-calendar.quelltext.eu/>
#
# SPDX-License-Identifier: GPL-2.0-only

try:
    from ._version import __version__, __version_tuple__, version, version_tuple
except ModuleNotFoundError:
    __version__ = version = "0.0dev0"
    __version_tuple__ = version_tuple = (0, 0, "dev0")
from importlib.metadata import version

cli_version = f"""{__version__}

Components:
"""
modules = ["recurring-ical-events", "icalendar", "pytz", "python-dateutil", "click", "tzdata", "x-wr-timezone"]
modules.sort()
for module in modules:
    cli_version += f"{module}: {version(module)}\n"

__all__ = [
    "__version__",
    "version",
    "__version_tuple__",
    "version_tuple",
    "cli_version"
]
