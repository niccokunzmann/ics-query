# ics-query
Find out what happens when in ICS calendar files - query RFC 5545 files for events, journals, TODOs and more

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
