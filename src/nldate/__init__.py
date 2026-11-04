"""Parse English date expressions using only the Python standard library."""

import calendar
import re
from datetime import date, timedelta

__all__ = ["parse"]

_MONTHS = {
    name.lower(): index
    for index in range(1, 13)
    for name in (calendar.month_name[index], calendar.month_abbr[index])
}
_MONTHS["sept"] = 9
_WEEKDAYS = {
    name.lower(): index
    for index in range(7)
    for name in (calendar.day_name[index], calendar.day_abbr[index])
}
_SMALL = dict(
    zip(
        "zero one two three four five six seven eight nine ten eleven twelve "
        "thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(),
        range(20),
        strict=True,
    )
)
_TENS = dict(
    zip(
        "twenty thirty forty fifty sixty seventy eighty ninety".split(),
        range(20, 100, 10),
        strict=True,
    )
)


def _number(text: str) -> int:
    if text.isdecimal():
        return int(text)
    if text in {"a", "an"}:
        return 1
    text = text.replace("-", " ")
    units = "|".join(word for word, value in _SMALL.items() if 0 < value < 10)
    small = "|".join(word for word, value in _SMALL.items() if value > 0)
    tens = "|".join(_TENS)
    under_hundred = rf"(?:(?:{small})|(?:{tens})(?: (?:{units}))?)"
    under_thousand = (
        rf"(?:(?:{units}) hundred(?: (?:and )?{under_hundred})?|{under_hundred})"
    )
    number = (
        rf"(?:zero|{under_thousand}"
        rf"(?: thousand(?: (?:and )?{under_thousand})?)?)"
    )
    if re.fullmatch(number, text) is None:
        raise ValueError(f"Invalid number: {text!r}")
    total = current = 0
    for word in text.split():
        if word in _SMALL:
            current += _SMALL[word]
        elif word in _TENS:
            current += _TENS[word]
        elif word == "hundred" and current:
            current *= 100
        elif word == "thousand" and current:
            total += current * 1000
            current = 0
        elif word != "and":
            raise ValueError(f"Invalid number: {text!r}")
    return total + current


def _shift(anchor: date, duration: str, direction: int) -> date:
    """Apply calendar years/months first, then weeks/days; clamp short months."""
    months = days = 0
    remaining = duration
    pattern = r"(.+?)\s+(years?|months?|weeks?|days?)\b"
    while remaining:
        match = re.match(pattern, remaining)
        if match is None:
            raise ValueError(f"Invalid duration: {duration!r}")
        amount = _number(match[1])
        unit = match[2].rstrip("s")
        if unit in {"year", "month"}:
            months += amount * (12 if unit == "year" else 1)
        else:
            days += amount * (7 if unit == "week" else 1)
        remaining = remaining[match.end() :].lstrip()
        has_comma = remaining.startswith(",")
        if has_comma:
            remaining = remaining[1:].lstrip()
        if remaining.startswith("and "):
            remaining = remaining[4:]
            if not remaining:
                raise ValueError(f"Invalid duration: {duration!r}")
        if has_comma and not remaining:
            raise ValueError(f"Invalid duration: {duration!r}")
    month_index = anchor.year * 12 + anchor.month - 1 + direction * months
    year, month = divmod(month_index, 12)
    month += 1
    day = min(anchor.day, calendar.monthrange(year, month)[1])
    return date(year, month, day) + timedelta(days=direction * days)


def _parse(text: str, today: date) -> date:
    offsets = {
        "today": 0,
        "now": 0,
        "tomorrow": 1,
        "yesterday": -1,
        "day after tomorrow": 2,
        "day before yesterday": -2,
    }
    if text in offsets:
        return today + timedelta(days=offsets[text])

    match = re.fullmatch(r"(.+?)\s+(before|after|from)\s+(.+)", text)
    if match:
        anchor = _parse(match[3], today)
        return _shift(anchor, match[1], -1 if match[2] == "before" else 1)
    if text.startswith("in "):
        return _shift(today, text[3:], 1)
    match = re.fullmatch(r"(.+?)\s+(ago|hence|from now)", text)
    if match:
        return _shift(today, match[1], -1 if match[2] == "ago" else 1)

    match = re.fullmatch(r"(?:(next|last|previous|this)\s+)?([a-z]+)", text)
    if match:
        modifier, name = match.groups()
        if name in _WEEKDAYS:
            delta = (_WEEKDAYS[name] - today.weekday()) % 7
            if modifier in {"last", "previous"}:
                delta = delta - 7 if delta else -7
            elif modifier != "this" and delta == 0:
                delta = 7
            return today + timedelta(days=delta)
        if modifier and name in {"day", "week", "month", "year"}:
            direction = -1 if modifier in {"last", "previous"} else 1
            return (
                today if modifier == "this" else _shift(today, f"1 {name}", direction)
            )

    # Ordinal suffixes and punctuation do not affect absolute calendar dates.
    text = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", r"\1", text)
    text = " ".join(text.replace(",", " ").replace(".", "").split())
    match = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
    if match:
        return date(int(match[1]), int(match[2]), int(match[3]))
    match = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
    if match:
        return date(int(match[3]), int(match[1]), int(match[2]))
    match = re.fullmatch(r"([a-z]+) (\d{1,2})(?: (\d{4}))?", text)
    if match and match[1] in _MONTHS:
        return date(
            int(match[3]) if match[3] else today.year, _MONTHS[match[1]], int(match[2])
        )
    match = re.fullmatch(r"(?:the )?(\d{1,2})(?: of)? ([a-z]+)(?: (\d{4}))?", text)
    if match and match[2] in _MONTHS:
        return date(
            int(match[3]) if match[3] else today.year, _MONTHS[match[2]], int(match[1])
        )
    raise ValueError(f"Unrecognized date expression: {text!r}")


def parse(s: str, today: date | None = None) -> date:
    """Parse an English date expression relative to ``today`` (default: today).

    Accept named and numeric dates, weekdays, and compound relative durations.
    Numeric dates use month/day/year unless the year comes first. Missing years
    use today's year. Next/last weekdays are strictly future/past; ``this`` uses
    the next occurrence including today. Calendar arithmetic clamps the day to
    the destination month's end, applying years/months before weeks/days.

    Raise ValueError for unrecognized expressions or dates outside date's range.
    """
    text = " ".join(s.lower().split())
    if not text:
        raise ValueError("Date expression must not be empty")
    try:
        return _parse(text, today if today is not None else date.today())
    except (OverflowError, RecursionError) as exc:
        raise ValueError(f"Date expression outside supported range: {s!r}") from exc
