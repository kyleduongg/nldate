
from datetime import date

from nldate import parse


# Test 1: Standard date
def test_standard_date():
    assert parse("December 1, 2025") == date(2025, 12, 1)


# Test 2: Abbreviated month
def test_abbreviated_month():
    assert parse("Dec 1, 2025") == date(2025, 12, 1)


# Test 3: ISO date format
def test_iso_date():
    assert parse("2025-12-01") == date(2025, 12, 1)


# Test 4: Numeric date format
def test_numeric_date():
    assert parse("12/01/2025") == date(2025, 12, 1)


# Test 5: Ordinal date and leap year
def test_leap_year():
    assert parse("February 29th, 2024") == date(2024, 2, 29)


# Test 6: Today
def test_today():
    assert parse("today", today=date(2025, 12, 1)) == date(2025, 12, 1)


# Test 7: Tomorrow across a year boundary
def test_tomorrow():
    assert parse("tomorrow", today=date(2025, 12, 31)) == date(2026, 1, 1)


# Test 8: Yesterday across a year boundary
def test_yesterday():
    assert parse("yesterday", today=date(2025, 1, 1)) == date(2024, 12, 31)


# Test 9: Next weekday
def test_next_tuesday():
    assert parse("next Tuesday", today=date(2025, 12, 3)) == date(2025, 12, 9)


# Test 10: Previous weekday
def test_last_friday():
    assert parse("last Friday", today=date(2025, 12, 3)) == date(2025, 11, 28)


# Test 11: Days in the future
def test_in_three_days():
    assert parse("in 3 days", today=date(2025, 12, 1)) == date(2025, 12, 4)


# Test 12: Weeks in the past
def test_three_weeks_ago():
    assert parse("3 weeks ago", today=date(2025, 12, 1)) == date(2025, 11, 10)


# Test 13: Days before a specific date
def test_days_before():
    assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)


# Test 14: Compound years and months
def test_compound_date():
    assert parse(
        "1 year and 2 months after yesterday",
        today=date(2025, 3, 15),
    ) == date(2026, 5, 14)


# Test 15: Written numbers and relative dates
def test_two_weeks_from_tomorrow():
    assert parse(
        "two weeks from tomorrow",
        today=date(2025, 1, 10),
    ) == date(2025, 1, 25)
