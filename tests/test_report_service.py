"""Offline tests for Gap2Growth engagement report aggregation."""

import sys
import unittest
from types import ModuleType
from unittest.mock import patch


database_stub = sys.modules.get("app.utils.database")
if database_stub is None:
    database_stub = ModuleType("app.utils.database")
    sys.modules["app.utils.database"] = database_stub

for _name in (
    "get_all_activity_logs",
    "get_activity_logs_by_student",
    "get_all_users",
    "get_users_by_role",
    "get_all_activities",
    "get_activities_by_course",
    "get_activities_by_duration",
    "get_activity_logs_by_student",
    "get_timetable_by_course",
    "get_users_by_course",
    "create_notification",
):
    if not hasattr(database_stub, _name):
        setattr(database_stub, _name, lambda *args, **kwargs: [])

from app.services import report_service  # noqa: E402


class EngagementStatsTests(unittest.TestCase):
    def test_aggregates_completed_activity_minutes_and_top_titles(self):
        logs = [
            {"status": "completed", "activities": {"title": "Python", "duration_minutes": 45}},
            {"status": "completed", "activities": {"title": "Python", "duration_minutes": 30}},
            {"status": "completed", "activities": {"title": "DBMS", "duration_minutes": 60}},
            {"status": "started", "activities": {"title": "Networking", "duration_minutes": 90}},
        ]
        with patch.object(report_service, "get_all_activity_logs", return_value=logs):
            result = report_service.get_engagement_stats(days=14)

        self.assertEqual(result["total_completed"], 3)
        self.assertEqual(result["total_minutes"], 135)
        self.assertEqual(result["total_hours"], 2.2)
        self.assertEqual(result["top_activities"], [("Python", 2), ("DBMS", 1)])
        self.assertEqual(result["period_days"], 14)

    def test_student_scope_uses_student_activity_logs(self):
        logs = [
            {"status": "completed", "activities": {"title": "Algorithms", "duration_minutes": 30}}
        ]
        with patch.object(report_service, "get_activity_logs_by_student", return_value=logs) as scoped, \
             patch.object(report_service, "get_all_activity_logs") as global_logs:
            result = report_service.get_engagement_stats(student_id="student-7", days=30)

        scoped.assert_called_once_with("student-7")
        global_logs.assert_not_called()
        self.assertEqual(result["total_completed"], 1)
        self.assertEqual(result["total_hours"], 0.5)

    def test_empty_activity_history_has_zero_totals(self):
        with patch.object(report_service, "get_all_activity_logs", return_value=[]):
            result = report_service.get_engagement_stats()

        self.assertEqual(result["total_completed"], 0)
        self.assertEqual(result["total_minutes"], 0)
        self.assertEqual(result["total_hours"], 0.0)
        self.assertEqual(result["top_activities"], [])


if __name__ == "__main__":
    unittest.main()
