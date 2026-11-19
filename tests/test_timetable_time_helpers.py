"""Offline tests for timetable time parsing and range calculations."""

import sys
import unittest
from datetime import time
from types import ModuleType


# The functions under test are pure helpers, so replace database imports before
# loading the service module. This keeps the suite independent of Supabase.
database_stub = ModuleType("app.utils.database")
for function_name in (
    "get_timetable_by_course",
    "get_users_by_role",
    "get_users_by_course",
    "create_notification",
):
    setattr(database_stub, function_name, lambda *args, **kwargs: [])
sys.modules["app.utils.database"] = database_stub

from app.services.downtime_service import (  # noqa: E402
    calculate_gap_minutes,
    is_time_in_range,
    parse_time,
)


class ParseTimeTests(unittest.TestCase):
    def test_accepts_supported_time_formats(self):
        self.assertEqual(parse_time("09:15"), time(9, 15))
        self.assertEqual(parse_time("09:15:30"), time(9, 15, 30))
        self.assertEqual(parse_time("02:45 PM"), time(14, 45))

    def test_returns_time_objects_unchanged(self):
        value = time(8, 30)
        self.assertIs(parse_time(value), value)

    def test_invalid_or_missing_values_return_none(self):
        self.assertIsNone(parse_time("not-a-time"))
        self.assertIsNone(parse_time(""))
        self.assertIsNone(parse_time(None))


class TimeRangeTests(unittest.TestCase):
    def test_calculates_positive_gap_in_minutes(self):
        self.assertEqual(calculate_gap_minutes(time(9, 0), time(10, 30)), 90)

    def test_reversed_times_return_negative_gap(self):
        self.assertEqual(calculate_gap_minutes(time(10, 0), time(9, 30)), -30)

    def test_range_includes_start_and_excludes_end(self):
        start, end = time(9, 0), time(10, 0)
        self.assertTrue(is_time_in_range(time(9, 0), start, end))
        self.assertTrue(is_time_in_range(time(9, 59), start, end))
        self.assertFalse(is_time_in_range(time(10, 0), start, end))


if __name__ == "__main__":
    unittest.main()
