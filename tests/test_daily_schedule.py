"""Offline tests for timetable schedule assembly and weekly summaries."""

import sys
import unittest
from types import ModuleType
from unittest.mock import patch


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


class DailyScheduleTests(unittest.TestCase):
    def test_schedule_includes_free_time_between_classes(self):
        timetable = [
            {"day": "Monday", "status": "scheduled", "start_time": "09:00", "end_time": "10:00", "id": 1},
            {"day": "Monday", "status": "scheduled", "start_time": "10:45", "end_time": "11:30", "id": 2},
        ]
        with patch.object(downtime_service, "get_timetable_by_course", return_value=timetable), \
             patch.object(downtime_service, "_is_slot_current", return_value=False):
            schedule = downtime_service.get_daily_schedule_with_gaps("CSE", "Monday")

        self.assertEqual([entry["type"] for entry in schedule], ["class", "free_time", "class"])
        self.assertEqual(schedule[1]["duration_minutes"], 45)
        self.assertEqual(schedule[1]["start_time"], "10:00")
        self.assertEqual(schedule[1]["end_time"], "10:45")

    def test_schedule_omits_gaps_shorter_than_threshold(self):
        timetable = [
            {"day": "Monday", "status": "scheduled", "start_time": "09:00", "end_time": "10:00", "id": 1},
            {"day": "Monday", "status": "scheduled", "start_time": "10:15", "end_time": "11:00", "id": 2},
        ]
        with patch.object(downtime_service, "get_timetable_by_course", return_value=timetable):
            schedule = downtime_service.get_daily_schedule_with_gaps("CSE", "Monday")

        self.assertEqual([entry["type"] for entry in schedule], ["class", "class"])

    def test_schedule_returns_empty_when_no_timetable_exists(self):
        with patch.object(downtime_service, "get_timetable_by_course", return_value=[]):
            self.assertEqual(downtime_service.get_daily_schedule_with_gaps("CSE", "Monday"), [])


class WeeklySummaryTests(unittest.TestCase):
    def test_summary_contains_all_days_and_aggregated_minutes(self):
        def fake_slots(course, day):
            minutes = {"Monday": 60, "Tuesday": 30}.get(day, 0)
            return [{"duration_minutes": minutes}] if minutes else []

        with patch.object(downtime_service, "detect_all_downtime_for_course", side_effect=fake_slots):
            summary = downtime_service.get_weekly_free_time_summary("CSE")

        self.assertEqual(len(summary), 7)
        self.assertEqual(summary["Monday"]["total_free_minutes"], 60)
        self.assertEqual(summary["Tuesday"]["slot_count"], 1)
        self.assertEqual(summary["Sunday"]["total_free_minutes"], 0)


if __name__ == "__main__":
    unittest.main()
