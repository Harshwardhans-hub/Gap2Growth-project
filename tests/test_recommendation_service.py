"""Offline regression tests for Gap2Growth activity recommendations."""

import random
import sys
import unittest
from types import ModuleType
from unittest.mock import patch


# Supply a dependency-free database module before importing service modules.
database_stub = sys.modules.get("app.utils.database")
if database_stub is None:
    database_stub = ModuleType("app.utils.database")
    sys.modules["app.utils.database"] = database_stub

_DATABASE_FUNCTIONS = (
    "get_activities_by_course",
    "get_activities_by_duration",
    "get_all_activities",
    "get_activity_logs_by_student",
    "get_timetable_by_course",
    "get_users_by_role",
    "get_users_by_course",
    "create_notification",
    "get_all_activity_logs",
    "get_all_users",
)
for _function_name in _DATABASE_FUNCTIONS:
    if not hasattr(database_stub, _function_name):
        setattr(database_stub, _function_name, lambda *args, **kwargs: [])

from app.services import recommendation_service  # noqa: E402


class ActivityScoringTests(unittest.TestCase):
    def test_all_matching_preferences_and_duration_contribute_to_score(self):
        activity = {
            "course": "CSE",
            "category": "Learning",
            "difficulty": "Easy",
            "mode": "Solo",
            "duration_minutes": 45,
        }
        score = recommendation_service.calculate_activity_score(
            activity, "CSE", 60, "Learning", "Easy", "Solo"
        )

        self.assertEqual(score, 95)

    def test_course_neutral_activity_gets_partial_course_score(self):
        score = recommendation_service.calculate_activity_score(
            {"duration_minutes": 0}, "CSE", 30
        )

        self.assertEqual(score, 15)

    def test_duration_component_is_capped(self):
        score = recommendation_service.calculate_activity_score(
            {"course": "CSE", "duration_minutes": 120}, "CSE", 30
        )

        self.assertEqual(score, 50)


class RecommendationSelectionTests(unittest.TestCase):
    def setUp(self):
        self.activities = [
            {"id": "short", "title": "Short", "course": "CSE", "duration_minutes": 20},
            {"id": "long", "title": "Long", "course": "CSE", "duration_minutes": 60},
            {"id": "too-long", "title": "Too long", "course": "CSE", "duration_minutes": 90},
        ]

    def test_filters_out_activities_longer_than_available_time(self):
        with patch.object(
            recommendation_service, "get_activities_by_course", return_value=self.activities
        ), patch.object(random, "shuffle", side_effect=lambda values: None):
            result = recommendation_service.get_recommended_activities("CSE", 60)

        self.assertEqual({item["id"] for item in result}, {"short", "long"})
        self.assertNotIn("too-long", [item["id"] for item in result])

    def test_higher_relevance_scores_come_first(self):
        activities = [
            {"id": "generic", "duration_minutes": 30},
            {"id": "matched", "course": "CSE", "duration_minutes": 30},
        ]
        with patch.object(
            recommendation_service, "get_activities_by_course", return_value=activities
        ), patch.object(random, "shuffle", side_effect=lambda values: None):
            result = recommendation_service.get_recommended_activities("CSE", 30)

        self.assertEqual(result[0]["id"], "matched")
        self.assertGreater(result[0]["relevance_score"], result[1]["relevance_score"])

    def test_empty_activity_source_returns_empty_list(self):
        with patch.object(recommendation_service, "get_activities_by_course", return_value=[]):
            self.assertEqual(recommendation_service.get_recommended_activities("CSE", 30), [])

    def test_quick_suggestions_respect_requested_limit(self):
        with patch.object(
            recommendation_service, "get_recommended_activities",
            return_value=[{"id": 1}, {"id": 2}, {"id": 3}],
        ):
            self.assertEqual(
                recommendation_service.get_quick_activity_suggestions("CSE", 30, limit=2),
                [{"id": 1}, {"id": 2}],
            )

    def test_category_filter_is_case_insensitive_and_respects_max_duration(self):
        activities = [
            {"id": 1, "category": "Learning", "duration_minutes": 20},
            {"id": 2, "category": "learning", "duration_minutes": 40},
            {"id": 3, "category": "Wellness", "duration_minutes": 10},
        ]
        with patch.object(recommendation_service, "get_activities_by_course", return_value=activities):
            result = recommendation_service.get_activities_by_category(
                "LEARNING", course="CSE", max_duration=30
            )

        self.assertEqual([item["id"] for item in result], [1])

    def test_personalized_recommendations_exclude_recently_completed_items(self):
        activities = [
            {"id": 1, "course": "CSE", "category": "Learning", "duration_minutes": 20},
            {"id": 2, "course": "CSE", "category": "Learning", "duration_minutes": 20},
        ]
        logs = [
            {"status": "completed", "activity_id": 1, "activities": {"category": "Learning"}}
        ]
        with patch.object(recommendation_service, "get_activity_logs_by_student", return_value=logs), \
             patch.object(recommendation_service, "get_activities_by_course", return_value=activities), \
             patch.object(random, "shuffle", side_effect=lambda values: None):
            result = recommendation_service.get_personalized_recommendations("student-1", "CSE", 30)

        self.assertEqual([item["id"] for item in result], [2])

    def test_category_lookup_uses_global_activity_source_without_course(self):
        activities = [{"id": 1, "category": "Learning", "duration_minutes": 15}]
        with patch.object(recommendation_service, "get_all_activities", return_value=activities) as lookup:
            result = recommendation_service.get_activities_by_category("Learning")

        lookup.assert_called_once_with()
        self.assertEqual(result, activities)

    def test_group_suggestions_request_group_mode(self):
        expected = [{"id": "group-task"}]
        with patch.object(
            recommendation_service, "get_recommended_activities", return_value=expected
        ) as recommend:
            result = recommendation_service.get_group_activity_suggestions("CSE", 45)

        recommend.assert_called_once_with("CSE", 45, mode="Group")
        self.assertEqual(result, expected)

    def test_categorization_places_unknown_categories_in_learning(self):
        activities = [
            {"id": 1, "category": "Learning"},
            {"id": 2, "category": "Collaboration"},
            {"id": 3, "category": "Creative"},
        ]
        with patch.object(recommendation_service, "get_all_activities", return_value=activities):
            result = recommendation_service.categorize_activities_by_type()

        self.assertEqual(result["Learning"], [activities[0], activities[2]])
        self.assertEqual(result["Collaboration"], [activities[1]])
        self.assertEqual(result["Skill"], [])
        self.assertEqual(result["Wellness"], [])



    def test_personalized_recommendations_fall_back_when_every_item_was_completed(self):
        activities = [
            {"id": 1, "course": "CSE", "category": "Learning", "duration_minutes": 20},
            {"id": 2, "course": "CSE", "category": "Learning", "duration_minutes": 25},
        ]
        logs = [
            {"status": "completed", "activity_id": 1, "activities": {"category": "Learning"}},
            {"status": "completed", "activity_id": 2, "activities": {"category": "Learning"}},
        ]
        with patch.object(recommendation_service, "get_activity_logs_by_student", return_value=logs), \
             patch.object(recommendation_service, "get_activities_by_course", return_value=activities), \
             patch.object(random, "shuffle", side_effect=lambda values: None):
            result = recommendation_service.get_personalized_recommendations("student-2", "CSE", 30)

        self.assertEqual({item["id"] for item in result}, {1, 2})



if __name__ == "__main__":
    unittest.main()
