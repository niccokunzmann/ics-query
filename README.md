# ics-query

<!-- Change description also in pyproject.toml -->
Find out what happens in ICS calendar files - query and filter RFC 5545 compatible `.ics` files for events, journals, TODOs and more.

## Installation

You can install this package from the [PyPI](https://pypi.org/project/ics-query/).

```shell
pip install ics-query
```

## Usage

See how to use `ics-query`.

### Examples

You can easily get a calendar from the web and see what is on.
In this example, we show which German National Holidays happen in August 2024:

```shell
$ wget -qO- 'https://www.calendarlabs.com/ical-calendar/ics/46/Germany_Holidays.ics' | ./ics-query at 2024-08 - -
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

We can concatenate calendars and pipe them into `ics-query`.
In the example below, we get all events that happen right now in two calendars.

```shell
$ cat calendar1.ics calendar2.ics | ics-query at `date +%Y%m%d%H%M%S` - -
BEGIN:VEVENT
...
```

### Events at Certain Times

You can query which events happen at certain times:

```shell
ics-query at <date-time> calendar.ics -
```

`<date-time>` can be built up: It can be a year, a month, a day, an hour, a minute or a second.

Please see the command documentation for more help:

```shell
ics-query at --help
ics-query --help
```

### Events within a Time Span

You can query which events happen between certain times:

```shell
ics-query between <start> <end> calendar.ics -
ics-query between <start> <duration> calendar.ics -
```

Please see the command documentation for more help:

```shell
ics-query between --help
ics-query --help
```

### Time Span Examples

This example returns the events within the next week:

```shell
ics-query between `date +%Y%m%d` +7d calendar.ics -
```

This example saves the events from the 1st of May 2024 to the 10th of June in
events.ics:

```shell
ics-query between 2024-5-1 2024-6-10 calendar.ics events.ics
```

In this example, you can check what is happening on New Years Eve 2025 around
midnight:

```shell
ics-query between 2025-12-31T21:00 +6h calendar.ics events.ics
```

### Filtering Components

We support different component types: VEVENT, VJOURNAL and VTODO.
By default, we include all types in the result.

You can specify which components you would like to get using the
`--component` or `-c` parameter.

```shell
-c VEVENT   # only events
-c VTODO    # only TODOs
-c VJOURNAL # only journal entries
-c VEVENT -v VTODO # only events and journal entries
```

This example returns the first event of a calendar.

```shell
ics-query first -c VEVENT calendar.ics -
```

## Vision

This section shows where we would like to get to.

### `ics-query at` - occurrences at certain times

You can get all **events** that happen at a certain **day**.

```shell
ics-query --components VEVENT at 2029-12-24 calendar.ics
```

You can get all **events** that happen **today**.

```shell
ics-query --components VEVENT at `date +%Y-%m-%d` calendar.ics
```

You can get all **TODO**s that happen at in certain **month**.

```shell
ics-query --components VTODO at 2029-12-24 calendar.ics
```

### `ics-query --select-index` - reduce output size

Examples: `0,2,4` `0-10`

### `ics-query all` - the whole calendar

### `ics-query --select-uid` - filter by uid

## How to edit an event

To edit a component like an event, you can append it to the calendar and increase the sequence number.

Example:

1. get the first event `--select-index=0` TODO: recurring-ical-events: set recurrence-id, sequence number
2. change the summary
3. increase sequence number
4. add the event to the end of the calendar file
5. show that the occurrence has changed

## Piping calendars

```shell
cat calendar.ics | ics-query --output=count --filter-component=VEVENT all > calendar-event-count.int
```

## Notifications

Examples:

- There are x todos in the next hour
- There are x events today
- Please write a journal entry!

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

This section should set you up for development.

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

To release new versions,

1. edit the Changelog Section
2. create a commit and push it
3. wait for [GitHub Actions](https://github.com/niccokunzmann/ics-query/actions) to finish the build
4. create a tag and push it

    ```shell
    git tag v0.1.0a
    git push origin v0.1.0a
    ```

5. Notify the issues about their release

## Changelog

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
