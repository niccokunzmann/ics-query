# ics-query

[![GitHub Actions CI](https://github.com/niccokunzmann/ics-query/actions/workflows/tests.yml/badge.svg)][GitHub Actions]
[![PyPI Version](https://badge.fury.io/py/ics-query.svg)][PyPI]
[![PyPI Downloads](https://img.shields.io/pypi/dm/ics-query.svg)][PyPI]
[![Support on Open Collective](https://img.shields.io/opencollective/all/open-web-calendar?label=support%20on%20open%20collective)][Open Collective]
[![Fund Issues with Polar](https://img.shields.io/github/issues/niccokunzmann/ics-query?logo=github&label=issues%20seek%20funding&color=%230062ff)][Polar]

<!-- Change description also in pyproject.toml -->
Find out what happens in ICS calendar files - query and filter RFC 5545 compatible `.ics` files for events, journals, TODOs and more.

## Installation

You can install this package from the [PyPI].

```shell
pip install ics-query
```

For **Windows**, you can download `ics-query.exe` from our [Releases].

## Support

- Support using [GitHub Sponsors]
- Fund specific issues using [Polar]
- Support using [Open Collective]
- Support using [thanks.dev]

We accept donations to sustain our work, once or regular.
Consider donating money to open-source as everyone benefits.

## Supported Features

This library is based on

- [recurring-ical-events]
- [icalendar]
- [x-wr-timezone]

[recurring-ical-events]: https://pypi.org/project/recurring-ical-events/
[icalendar]: https://pypi.org/project/icalendar/
[x-wr-timezone]: https://pypi.org/project/x-wr-timezone/

For a list of supported features and RFC compatibility,
please refer to their documentation, too.

## Usage

`ics-query` is a command line tool that aims to make icalendar occurance calculations
accessible and easy.
This section walks you though the different functionalities.

```shell
ics-query --help
```

### Examples

You can get a calendar from the web and see what is on.
In this example, we show which German National Holidays happening in August 2024:

```shell
$ wget -qO- 'https://www.calendarlabs.com/ical-calendar/ics/46/Germany_Holidays.ics' | ics-query at 2024-08 - -
BEGIN:VEVENT
SUMMARY:Assumption Day (BY\, SL)
DTSTART;VALUE=DATE:20240815
DTEND;VALUE=DATE:20240815
DTSTAMP:20231013T092513Z
UID:65290cf9326601697189113@calendarlabs.com
SEQUENCE:0
DESCRIPTION:Visit https://calendarlabs.com/holidays/us/the-assumption-of-m
 ary.php to know more about Assumption Day (BY\, SL). \n\n Like us on Faceb
 ook: http://fb.com/calendarlabs to get updates
LOCATION:Germany
STATUS:CONFIRMED
TRANSP:TRANSPARENT
END:VEVENT
```

In the following example, we query a calendar file and print the result.

```shell
$ ics-query at 2019-03-04 one-event.ics -
BEGIN:VEVENT
SUMMARY:test1
DTSTART;TZID=Europe/Berlin:20190304T080000
DTEND;TZID=Europe/Berlin:20190304T083000
DTSTAMP:20190303T111937
UID:UYDQSG9TH4DE0WM3QFL2J
CREATED:20190303T111937
LAST-MODIFIED:20190303T111937
END:VEVENT
```

#### Concatenating Calendars

We can concatenate calendars and pipe them into `ics-query`.
In the example below, we get all events that happen right now in two calendars.

```shell
$ cat calendar1.ics calendar2.ics | ics-query at `date +%Y%m%d%H%M%S` - -
BEGIN:VEVENT
...
```

#### Piping calendars

You can pipe one or more calendars into the input.

```shell
cat calendar.ics | ics-query first -
```

#### Valid ICS files

The resulting events are missing the timezone and the calendar information by default.
This information can be added using the `--as-calendar` parameter.
The result is a valid `.ics` file that can be processed further by other commands and programs.

In the example below, we use the calendar command to inspect the event for human readability.

```shell
$ ics-query at --as-calendar 2014-05-03 x-wr-timezone-rdate-hackerpublicradio.ics event.ics
$ icalendar event.ics
    Organizer: 
    Attendees:

    Summary    : HPR Community News
    Starts     : Sat May  3 20:00:00 2014
    End        : Sat May  3 22:00:00 2014
    Duration   : 2:00:00
    Location   : mumble.openspeak.cc port: 64747
    Comment    : 
    Description:
     This is from http://www.hackerpublicradio.org/eps/hpr1286/iCalendar_Hacking_shownotes.html
```

### Events at Certain Times

You can query which events happen at certain times:

```shell
ics-query at TIME calendar.ics -
```

The format of TIME:

| TIME | description |
| ------- | ----------- |
| `2019`    | the whole year 2019 |
| `2019-08` | August 2019 |
| `2019-08-12` | 12th of August 2019 |
| `2019-08-12T17` | 17:00-18:00 at the 12th of August 2019 |
| `2019-08-12T17:20` | 17:20-17:21 at the 12th of August 2019 |
| `2019-08-12T17:20:00` | 17:20 at the 12th of August 2019 |


Please see the command documentation for more help:

```shell
ics-query at --help
ics-query --help
```

You can get all **events** that happen at a certain **day**.

```shell
ics-query at --components VEVENT 2029-12-24 calendar.ics
```

You can get all **events** that happen **today**.

```shell
ics-query at --components VEVENT `date +%Y-%m-%d` calendar.ics
```

You can get all **TODO**s that happen in a certain **month**.

```shell
ics-query at --components VTODO 2029-12-24 calendar.ics
```

### Events within a Time Span

You can query which events happen between certain times:

```shell
ics-query between START END calendar.ics -
ics-query between START DURATION calendar.ics -
```

Please see the command documentation for more help:

```shell
ics-query between --help
ics-query --help
```

The format of START and END with examples:

| START or END | Description |
| ------- | ----------- |
| `2019`    | the whole year 2019 |
| `2019-08` | August 2019 |
| `2019-08-12` | 12th of August 2019 |
| `2019-08-12T17` | 17:00-18:00 at the 12th of August 2019 |
| `2019-08-12T17:20` | 17:20-17:21 at the 12th of August 2019 |
| `2019-08-12T17:20:00` | 17:20 at the 12th of August 2019 |

Instead of an absolute time, you can specify a duration after the START.
The `+` is optional.

| DURATION | Description |
| ------- | ----------- |
| `+1d`   | one more day |
| `+1h`   | one more hour |
| `+1m`   | one more minute |
| `+1s`   | one more second |
| `+3600s`   | one more hour or 3600 seconds |
| `+5d10h`   | five more days and 10 more hours |

### Time Span Examples

This example returns the occurrences within the **next week**:

```shell
ics-query between `date +%Y%m%d` +7d calendar.ics -
```

This example saves the **events** from the **1st of May 2024 to the 10th of June** in
events.ics:

```shell
ics-query between --component VEVENT 2024-5-1 2024-6-10 calendar.ics events.ics
```

In this example, you can check what is happening on **New Years Eve 2025** around
midnight:

```shell
ics-query between 2025-12-31T21:00 +6h calendar.ics events.ics
```

### `ics-query all` - the whole calendar

You can get everything that is happening in a calendar but that can be a lot!

```shell
ics-query all calendar.ics
```

### Filtering Components

We support different component types: `VEVENT`, `VJOURNAL` and `VTODO`.
By default, we include all types in the result.

You can specify which components you would like to get using the
`--component` or `-c` parameter.

```shell
-c VEVENT   # only events
-c VTODO    # only TODOs
-c VJOURNAL # only journal entries
-c VEVENT -c VTODO # only events and journal entries
```

This example returns the first event of a calendar.

```shell
ics-query first -c VEVENT calendar.ics -
```

This option is also available as `ICS_QUERY_COMPONENT` variable.

```shell
export ICS_QUERY_COMPONENT=VEVENT
# from now on, you will get only events
ics-query first calendar.ics
```

Please see the command documentation for more help:

```shell
ics-query --help
```


### Timezones

You can set the timezone of the query, otherwise the event's local timezone is used and you
might miss events in your own timezone.

The first event at New Year 2000 in the **event's local time**:

```shell
ics-query at 2000-01-01 calendar.ics
```

The first event at New Year 2000 in **your local time**:

```shell
ics-query at --tz=localtime 2000-01-01 calendar.ics
```

The first event at New Year 2000 in **UTC**:

```shell
ics-query at --tz=UTC 2000-01-01 calendar.ics
```

The first event at New Year 2000 in **Berlin time**:

```shell
ics-query at --tz=Europe/Berlin 2000-01-01 calendar.ics
```

You can also use the `ICS_QUERY_TZ` variable.

```shell
export ICS_QUERY_TZ=localtime
# from now on, we use your local time
ics-query at 2000-01-01 calendar.ics
```

For all avaiable timezones see:

```shell
ics-query --available-timezones
```

Please see the command documentation for more help:

```shell
ics-query --help
```

## Version Fixing

If you use this library in your code, you may want to make sure that
updates can be received but they do not break your code.
The version numbers are handeled this way: `a.b.c` example: `0.1.12`

- `c` is changed for each minor bug fix.
- `b` is changed whenever new features are added.
- `a` is changed when the interface or major assumptions change that may break your code.

So, I recommend to version-fix this library to stay with the same `a`
while `b` and `c` can change.

## Development

This section should set you up for developing `ics-query`.

To create new commits, you should install [pre-commit](https://pre-commit.com/).
Then run:

```shell
pre-commit install
```

### Testing

This project's development is driven by tests.
Tests assure a consistent interface and less knowledge lost over time.
If you like to change the code, tests help that nothing breaks in the future.
They are required in that sense.
Example code and ics files can be transferred into tests and speed up fixing bugs.

You can view the tests in the [test folder](https://github.com/niccokunzmann/ics-query/tree/main/ics_query/tests)
If you have a calendar ICS file for which this library does not
generate the desired output, you can add it to the ``test/calendars``
folder and write tests for what you expect.
If you like, [open an issue](https://github.com/niccokunzmann/ics-query/issues) first, e.g. to discuss the changes and
how to go about it.

To run the tests, we use `tox`.
`tox` tests all different Python versions which we want to  be compatible to.

```shell
pip3 install tox
```

To run all the tests:

```shell
tox
```

To run the tests in a specific Python version:

```shell
tox -e py39
```

We use ``ruff`` to format the code.
Run this to format the code and show problems:

```shell
tox -e ruff
```

### New Release

Renovate updates the dependencies automatically on the `main` branch.
New commits on `main` are automatically published with an increased
PATCH version number.

To release a new version with a new MINOR or MAJOR version number change,
follow these steps:

1. edit the Changelog Section
2. create a commit and push it
3. wait for [GitHub Actions] to finish the build
4. create a tag and push it

    ```shell
    git tag v0.1.0
    git push origin v0.1.0
    ```

5. Notify the issues about their release

## Changelog

We automatically release the versions that only update dependencies.
If the version you installed does not show up here, only the dependencies
have been updated.

- v0.4.33

  - Add `--as-calendar` parameter.

- v0.4.32

  - Update dependencies.
  - Include recurrence ID in events to identify the occurrence in a series.
  - Update help message in command line.

- v0.4.1

  - Automatic release with patch level version number increased
  - Increase patch version instead of minor version for automatic releases

- v0.3.4

  - Update dependencies
  - Start automatic release of dependencies increasing the version number

- v0.3.3b

  - Update dependencies

- v0.3.2b

  - Fix that `--tz localtime` would use `localtime` as timezone name instead of the local timezone name.
  - Fix tests on Windows
  - Add Windows .exe build artifact

- v0.3.1b

  - Add `--license` option

- v0.3.0b

  - Add `--tz` timezone parameter
  - Add `ics-query all` to get all occurrences

- v0.2.1a

  - Add `--component` to filter component types VEVENT, VJOURNAL and VTODO

- v0.2.0a

  - Add `ics-query first <calendar> <output>` for earliest occurrences
  - Add `ics-query between <span_start> <span_stop> <calendar> <output>` to query time ranges

- v0.1.1a

  - Add `--version`
  - Add `ics-query at <date> <calendar> <output>`
  - Add support for multiple calendars in one input

- v0.1.0a

  - Update Python version compatibility
  - Add development documentation

- v0.0.1a

  - first version

## Related Work

- [icalBuddy](https://hasseg.org/icalBuddy/)
- [Blog Post](https://opencollective.com/open-web-calendar/updates/calendar-calculation-on-the-command-line-ics-query)
- [#icsquery on mastodon](https://toot.wales/tags/icsquery)

## Vision

This section shows where we would like to get to.

### `ics-query --select-index` - reduce output size

Examples: `0,2,4` `0-10`


### `ics-query --select-uid` - filter by uid

### How to edit an event

To edit a component like an event, you can append it to the calendar and increase the sequence number.

Example:

1. get the event `--select-index=0`
2. change the summary
3. increase sequence number
4. add the event to the end of the calendar file
5. show that the occurrence has changed


### Notifications

Examples:

- There are x todos in the next hour
- There are x events today
- Please write a journal entry!

[PyPI]: https://pypi.org/project/ics-query/
[GitHub Actions]: https://github.com/niccokunzmann/ics-query/actions
[Open Collective]: https://opencollective.com/open-web-calendar/
[Polar]: https://polar.sh/niccokunzmann/ics-query
[GitHub Sponsors]: https://github.com/sponsors/niccokunzmann
[thanks.dev]: https://thanks.dev
[Releases]: https://github.com/niccokunzmann/ics-query/releases
