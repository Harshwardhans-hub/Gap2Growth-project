"""
Activity Recommendation Service
"""

from app.utils.database import (
    get_activities_by_course,
    get_activities_by_duration,
    get_all_activities,
    get_activity_logs_by_student
)


def get_recommended_activities(course, duration_minutes, category=None, difficulty=None, mode=None):
    """Get recommended activities based on course, available time and preferences"""
    all_activities = get_activities_by_course(course) if course else get_all_activities()
    
    if not all_activities:
        return []
    
    suitable_activities = [
        activity for activity in all_activities
        if activity.get('duration_minutes', 0) <= duration_minutes
    ]
    
    if not suitable_activities:
        return []
    
    scored_activities = []
    
    for activity in suitable_activities:
        score = calculate_activity_score(
            activity, 
            course, 
            duration_minutes, 
            category, 
            difficulty, 
            mode
        )
        scored_activities.append({
            **activity,
            'relevance_score': score
        })
    
    import random
    random.shuffle(scored_activities)
    scored_activities.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return scored_activities


def calculate_activity_score(activity, course, duration_minutes, category=None, difficulty=None, mode=None):
    """Calculate relevance score for an activity"""
    score = 0
    
    activity_course = activity.get('course', '')
    if activity_course and activity_course.lower() == course.lower():
        score += 30
    elif not activity_course:
        score += 15
    
    if category and activity.get('category', '').lower() == category.lower():
        score += 20
    
    if difficulty and activity.get('difficulty', '').lower() == difficulty.lower():
        score += 15
    
    if mode and activity.get('mode', '').lower() == mode.lower():
        score += 15
    
    activity_duration = activity.get('duration_minutes', 0)
    if activity_duration > 0 and duration_minutes > 0:
        efficiency = activity_duration / duration_minutes
        efficiency_score = int(efficiency * 20)
        score += min(efficiency_score, 20)
    
    return score


def get_quick_activity_suggestions(course, duration_minutes, limit=3):
    """Get quick activity suggestions for immediate use"""
    recommendations = get_recommended_activities(course, duration_minutes)
    return recommendations[:limit]


def get_activities_by_category(category, course=None, max_duration=None):
    """Get activities filtered by category and course"""
    if course:
        all_activities = get_activities_by_course(course)
    else:
        all_activities = get_all_activities()
    
    filtered = [
        activity for activity in all_activities
        if activity.get('category', '').lower() == category.lower()
    ]
    
    if max_duration:
        filtered = [
            activity for activity in filtered
            if activity.get('duration_minutes', 0) <= max_duration
        ]
    
    return filtered


def get_personalized_recommendations(student_id, course, duration_minutes):
    """Get personalized activity recommendations based on student history"""
    activity_logs = get_activity_logs_by_student(student_id)
    
    completed_activities = [
        log for log in activity_logs 
        if log.get('status') == 'completed'
    ]
    
    category_counts = {}
    for log in completed_activities:
        activity = log.get('activities', {})
        category = activity.get('category', 'Learning')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    preferred_category = None
    if category_counts:
        preferred_category = max(category_counts, key=category_counts.get)
    
    recommendations = get_recommended_activities(
        course, 
        duration_minutes, 
        category=preferred_category
    )
    
    completed_ids = [log.get('activity_id') for log in completed_activities[-10:]]
    
    filtered_recommendations = [
        rec for rec in recommendations
        if rec.get('id') not in completed_ids
    ]
    
    return filtered_recommendations if filtered_recommendations else recommendations


def get_group_activity_suggestions(course, duration_minutes, participant_count=2):
    """Get activity suggestions suitable for group collaboration"""
    recommendations = get_recommended_activities(
        course, 
        duration_minutes, 
        mode='Group'
    )
    
    return recommendations


def categorize_activities_by_type():
    """Get all activities organized by category"""
    all_activities = get_all_activities()
    
    categorized = {
        'Learning': [],
        'Skill': [],
        'Wellness': [],
        'Collaboration': []
    }
    
    for activity in all_activities:
        category = activity.get('category', 'Learning')
        if category in categorized:
            categorized[category].append(activity)
        else:
            categorized['Learning'].append(activity)
    
    return categorized
