# nldate

A Python library for DSC 190 Assignment 06: Natural-Language Date Parser.
Requires Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

The public API is `parse(s: str, today: date | None = None) -> date`, available
with `from nldate import parse`. Relative expressions use `today`, or the actual
current date when omitted. The parser has no runtime dependencies.

Supported expressions include:

- Full or abbreviated month names, ordinal days, and day-first named dates.
- ISO dates and numeric month/day/year dates (four-digit years).
- Named dates without a year, using the reference date's year.
- Today, tomorrow, yesterday, day before yesterday, and day after tomorrow.
- Next, last, previous, and this weekdays, including abbreviated weekday names.
- Next/last day, week, month, or year.
- Durations in days, weeks, months, and years, with numeric or English quantities.
- Compound durations, `in …`, `… ago`, and `… before/after/from …` expressions
  with absolute or relative anchors.

Input is case-insensitive and tolerates extra whitespace. Next and last weekdays
are strictly future and past; this weekday means the next occurrence including
today. Years and months are applied together before weeks and days, clamping the
day to the destination month's end. Unsupported expressions and invalid dates
raise `ValueError`. English quantities support units, tens, hundreds, and thousands.

## Development

```bash
uv sync
uv run pytest -v
uv run mypy src/nldate tests
uv run ruff check .
uv run ruff format --check .
```

The human owns all tests and expected behavior. Library code uses strict type
checking; test functions may omit annotations but their bodies are type checked.
Human-authored tests are excluded from automatic formatting checks to preserve
the supplied files.
