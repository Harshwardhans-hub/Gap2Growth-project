"""Offline regression tests for timetable gap and cancellation detection."""

import sys
import unittest
from types import ModuleType
from unittest.mock import patch


# The service imports database functions at module load time. Stub only those
# imports so tests can run without Supabase credentials or network access.
database_stub = ModuleType("app.utils.database")
for function_name in (
    "get_timetable_by_course",
    "get_users_by_role",
    "get_users_by_course",
    "create_notification",
):
    setattr(database_stub, function_name, lambda *args, **kwargs: [])
sys.modules.setdefault("app.utils.database", database_stub)

from app.services import downtime_service  # noqa: E402


class DowntimeDetectionTests(unittest.TestCase):
    def test_no_timetable_returns_no_gap_slots(self):
        with patch.object(downtime_service, "get_timetable_by_course", return_value=[]):
            self.assertEqual(downtime_service.detect_downtime_for_course("CSE", "Monday"), [])

    def test_detects_gap_between_scheduled_classes_on_requested_day(self):
        timetable = [
            {"day": "Monday", "status": "scheduled", "start_time": "09:00", "end_time": "10:00"},
            {"day": "Monday", "status": "scheduled", "start_time": "10:45", "end_time": "11:30"},
            {"day": "Tuesday", "status": "scheduled", "start_time": "12:00", "end_time": "13:00"},
            {"day": "Monday", "status": "cancelled", "start_time": "12:00", "end_time": "13:00"},
        ]
        with patch.object(downtime_service, "get_timetable_by_course", return_value=timetable), \
             patch.object(downtime_service, "_is_slot_current", return_value=False), \
             patch.object(downtime_service, "_is_slot_upcoming", return_value=True):
            slots = downtime_service.detect_downtime_for_course("CSE", "Monday")

        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0]["start_time"], "10:00")
        self.assertEqual(slots[0]["end_time"], "10:45")
        self.assertEqual(slots[0]["duration_minutes"], 45)
        self.assertEqual(slots[0]["reason"], "timetable_gap")

    def test_detects_cancelled_classes_above_minimum_duration(self):
        timetable = [
            {"day": "Monday", "status": "cancelled", "start_time": "14:00", "end_time": "15:00"},
            {"day": "Monday", "status": "cancelled", "start_time": "15:00", "end_time": "15:20"},
            {"day": "Tuesday", "status": "cancelled", "start_time": "16:00", "end_time": "17:00"},
        ]
        with patch.object(downtime_service, "get_timetable_by_course", return_value=timetable), \
             patch.object(downtime_service, "_is_slot_current", return_value=False), \
             patch.object(downtime_service, "_is_slot_upcoming", return_value=True):
            slots = downtime_service.detect_cancelled_class_slots("CSE", "Monday")

        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0]["duration_minutes"], 60)
        self.assertEqual(slots[0]["reason"], "class_cancelled")

    def test_combined_slots_are_sorted_by_start_time(self):
        with patch.object(downtime_service, "detect_downtime_for_course", return_value=[
            {"start_time": "11:00", "duration_minutes": 30}
        ]), patch.object(downtime_service, "detect_cancelled_class_slots", return_value=[
            {"start_time": "09:00", "duration_minutes": 60}
        ]):
            slots = downtime_service.detect_all_downtime_for_course("CSE", "Monday")

        self.assertEqual([slot["start_time"] for slot in slots], ["09:00", "11:00"])

    def test_daily_schedule_inserts_free_time_between_classes(self):
        timetable = [
            {"id": 1, "day": "Monday", "status": "scheduled", "start_time": "09:00", "end_time": "10:00"},
            {"id": 2, "day": "Monday", "status": "scheduled", "start_time": "11:00", "end_time": "12:00"},
            {"id": 3, "day": "Tuesday", "status": "scheduled", "start_time": "13:00", "end_time": "14:00"},
        ]
        with patch.object(downtime_service, "get_timetable_by_course", return_value=timetable), \
             patch.object(downtime_service, "_is_slot_current", return_value=False):
            schedule = downtime_service.get_daily_schedule_with_gaps("CSE", "Monday")

        self.assertEqual([item["type"] for item in schedule], ["class", "free_time", "class"])
        self.assertEqual(schedule[1]["start_time"], "10:00")
        self.assertEqual(schedule[1]["end_time"], "11:00")
        self.assertEqual(schedule[1]["duration_minutes"], 60)

    def test_daily_schedule_without_matching_day_is_empty(self):
        timetable = [
            {"day": "Tuesday", "status": "scheduled", "start_time": "09:00", "end_time": "10:00"}
        ]
        with patch.object(downtime_service, "get_timetable_by_course", return_value=timetable):
            self.assertEqual(downtime_service.get_daily_schedule_with_gaps("CSE", "Monday"), [])


if __name__ == "__main__":
    unittest.main()
