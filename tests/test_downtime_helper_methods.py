"""Offline tests for current and upcoming timetable gap helpers."""

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


class DowntimeHelperMethodTests(unittest.TestCase):
    def test_current_slot_adds_remaining_minutes(self):
        slot = {
            "is_current": True,
            "start_time": "09:00",
            "end_time": "10:00",
            "duration_minutes": 60,
        }
        with patch.object(downtime_service, "get_day_name", return_value="Monday"), \
             patch.object(downtime_service, "detect_all_downtime_for_course", return_value=[slot]), \
             patch.object(downtime_service, "_calculate_remaining_time", return_value=17):
            result = downtime_service.get_current_free_slot("CSE")

        self.assertEqual(result["remaining_minutes"], 17)
        self.assertEqual(result["end_time"], "10:00")

    def test_current_slot_returns_none_when_no_active_slot(self):
        with patch.object(downtime_service, "get_day_name", return_value="Monday"), \
             patch.object(downtime_service, "detect_all_downtime_for_course", return_value=[]):
            self.assertIsNone(downtime_service.get_current_free_slot("CSE"))

    def test_upcoming_slots_get_start_offsets_and_limit(self):
        slots = [
            {"is_upcoming": True, "start_time": "11:00"},
            {"is_upcoming": True, "start_time": "13:00"},
            {"is_upcoming": False, "start_time": "08:00"},
        ]
        with patch.object(downtime_service, "get_day_name", return_value="Monday"), \
             patch.object(downtime_service, "detect_all_downtime_for_course", return_value=slots), \
             patch.object(downtime_service, "_calculate_time_until", side_effect=[30, 150]):
            result = downtime_service.get_upcoming_free_slots("CSE", limit=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["starts_in_minutes"], 30)


if __name__ == "__main__":
    unittest.main()
