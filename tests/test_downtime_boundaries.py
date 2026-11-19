"""Boundary tests for minimum free-slot duration and malformed time values."""

import sys
import unittest
from types import ModuleType
from unittest.mock import patch

database_stub = ModuleType("app.utils.database")
for name in (
    "get_timetable_by_course",
    "get_users_by_role",
    "get_users_by_course",
    "create_notification",
):
    setattr(database_stub, name, lambda *args, **kwargs: [])
sys.modules.setdefault("app.utils.database", database_stub)

from app.services import downtime_service  # noqa: E402


class DowntimeBoundaryTests(unittest.TestCase):
    def test_only_gaps_meeting_threshold_are_returned(self):
        timetable = [
            {"day": "Monday", "status": "scheduled", "start_time": "09:00", "end_time": "10:00"},
            {"day": "Monday", "status": "scheduled", "start_time": "10:29", "end_time": "10:45"},
            {"day": "Monday", "status": "scheduled", "start_time": "11:15", "end_time": "12:00"},
        ]
        with patch.object(downtime_service, "DOWNTIME_THRESHOLD", 30), \
             patch.object(downtime_service, "get_timetable_by_course", return_value=timetable), \
             patch.object(downtime_service, "_is_slot_current", return_value=False), \
             patch.object(downtime_service, "_is_slot_upcoming", return_value=True):
            slots = downtime_service.detect_downtime_for_course("CSE", "Monday")

        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0]["start_time"], "10:45")
        self.assertEqual(slots[0]["end_time"], "11:15")
        self.assertEqual(slots[0]["duration_minutes"], 30)

    def test_invalid_time_string_is_ignored_by_parser(self):
        self.assertIsNone(downtime_service.parse_time("not-a-time"))
        self.assertIsNone(downtime_service.parse_time(""))

    def test_time_parser_accepts_supported_formats(self):
        self.assertEqual(downtime_service.parse_time("09:30").strftime("%H:%M"), "09:30")
        self.assertEqual(downtime_service.parse_time("09:30:15").strftime("%H:%M:%S"), "09:30:15")
        self.assertEqual(downtime_service.parse_time("02:15 PM").strftime("%H:%M"), "14:15")


if __name__ == "__main__":
    unittest.main()
