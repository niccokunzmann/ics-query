# ics-query

<!-- Change description also in pyproject.toml -->
Find out what happens in ICS calendar files - query and filter RFC 5545 compatible `.ics` files for events, journals, TODOs and more.

## Installation

You can install this package from the [PyPI](https://pypi.org/project/ics-query/).

```shell
pip install ics-query
```

## `ics-query at` - occurrences at certain times

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

## `ics-query at` - time ranges


## `ics-query --output=count` - count occurrences


## `ics-query --output=ics` - use ics as output (default)


## `ics-query --select-index` - reduce output size

Examples: `0,2,4` `0-10`

## `ics-query all` - the whole calendar

## `ics-query between` - time ranges

```shell
ics-query between dt dt
ics-query between dt duration
```

## `ics-query --select-component` - filter for components


## `ics-query --select-uid` - filter by uid


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

## New Release

To release new versions,

1. edit the Changelog Section
2. create a commit and push it
3. wait for [GitHub Actions](https://github.com/niccokunzmann/ics-query/actions) to finish the build
4. create a tag and push it

    ```shell
    git tag v0.1.0a
    ```

5. Notify the issues about their release

## Changelog

- v0.1.0a

  - Update Python version compatibility
  - Add development documentation

- v0.0.1a

  - first version
