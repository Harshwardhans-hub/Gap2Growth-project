"""
API Routes
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime
from app.utils.decorators import login_required, admin_required, teacher_or_admin_required
from app.utils.database import (
    get_all_users, get_all_activities, get_timetable_by_course,
    create_activity, get_activity_logs_by_student,
    create_notification, get_notifications_by_user,
    mark_notification_read, mark_all_notifications_read,
    update_timetable_entry
)
from app.services.downtime_service import (
    detect_all_downtime_for_course, 
    get_current_free_slot, 
    get_upcoming_free_slots,
    get_daily_schedule_with_gaps,
    get_weekly_free_time_summary
)
from app.services.recommendation_service import get_recommended_activities, get_personalized_recommendations
from app.services.report_service import get_engagement_stats
from app.services.realtime_service import (
    get_realtime_status,
    trigger_class_cancellation,
    get_current_free_time_for_student,
    get_recommended_activity_for_student
)

api_bp = Blueprint('api', __name__)


@api_bp.route('/health')
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'realtime': get_realtime_status()
    })





@api_bp.route('/user')
@login_required
def get_current_user():
    """Get current user info"""
    return jsonify({'user': session.get('user')})


@api_bp.route('/users')
@admin_required
def get_users():
    """Get all users (admin only)"""
    users = get_all_users()
    return jsonify({'users': users})


@api_bp.route('/activities')
@login_required
def get_activities():
    """Get activities for the user's department"""
    user = session.get('user', {})
    user_course = user.get('course')
    
    if user_course:
        from app.utils.database import get_activities_by_course
        activities = get_activities_by_course(user_course)
    else:
        activities = get_all_activities()
    
    return jsonify({'activities': activities})


@api_bp.route('/activities', methods=['POST'])
@teacher_or_admin_required
def create_new_activity():
    """Create new activity"""
    data = request.get_json()
    
    activity = create_activity(
        title=data.get('title'),
        category=data.get('category', 'Learning'),
        duration_minutes=data.get('duration_minutes', 30),
        difficulty=data.get('difficulty', 'Medium'),
        mode=data.get('mode', 'Solo'),
        course=data.get('course'),
        created_by=session['user'].get('id'),
        description=data.get('description', '')
    )
    
    if activity:
        return jsonify({'success': True, 'activity': activity}), 201
    return jsonify({'success': False, 'error': 'Failed to create activity'}), 400


@api_bp.route('/timetable/<course>')
@login_required
def get_timetable(course):
    """Get timetable for a course"""
    entries = get_timetable_by_course(course)
    return jsonify({'timetable': entries})


@api_bp.route('/free-slots/<course>')
@login_required
def get_free_slots(course):
    """Get detected free time slots"""
    day = request.args.get('day')
    slots = detect_all_downtime_for_course(course, day)
    return jsonify({'free_slots': slots})


@api_bp.route('/current-free-time')
@login_required
def get_current_free_time():
    """Get current free time slot for logged in student"""
    user = session.get('user', {})
    course = user.get('course')
    
    if not course:
        return jsonify({'free_slot': None, 'message': 'No course assigned'})
    
    current_slot = get_current_free_slot(course)
    
    if current_slot:
        recommendations = get_recommended_activities(course, current_slot.get('remaining_minutes', 30))
        return jsonify({
            'free_slot': current_slot,
            'recommendations': recommendations[:5],
            'message': f"You have {current_slot.get('remaining_minutes', 0)} minutes of free time!"
        })
    
    return jsonify({'free_slot': None, 'message': 'No current free time detected'})


@api_bp.route('/upcoming-free-time')
@login_required
def get_upcoming_free_time():
    """Get upcoming free time slots"""
    user = session.get('user', {})
    course = user.get('course')
    limit = request.args.get('limit', 5, type=int)
    
    if not course:
        return jsonify({'slots': [], 'message': 'No course assigned'})
    
    upcoming = get_upcoming_free_slots(course, limit)
    return jsonify({'slots': upcoming})


@api_bp.route('/daily-schedule')
@login_required
def get_daily_schedule():
    """Get daily schedule with classes and gaps"""
    user = session.get('user', {})
    course = user.get('course')
    day = request.args.get('day')
    
    if not course:
        return jsonify({'schedule': [], 'message': 'No course assigned'})
    
    schedule = get_daily_schedule_with_gaps(course, day)
    return jsonify({'schedule': schedule})


@api_bp.route('/weekly-summary')
@login_required
def get_weekly_summary():
    """Get weekly free time summary"""
    user = session.get('user', {})
    course = user.get('course')
    
    if not course:
        return jsonify({'summary': {}, 'message': 'No course assigned'})
    
    summary = get_weekly_free_time_summary(course)
    return jsonify({'summary': summary})


@api_bp.route('/cancel-class/<entry_id>', methods=['POST'])
@teacher_or_admin_required
def cancel_class(entry_id):
    """Cancel a class and trigger real-time notifications"""
    data = request.get_json() or {}
    course = data.get('course')
    
    result = update_timetable_entry(entry_id, {'status': 'cancelled'})
    
    if result:
        if course:
            trigger_class_cancellation(entry_id, course)
        
        return jsonify({
            'success': True, 
            'message': 'Class cancelled. Students have been notified.'
        })
    
    return jsonify({'success': False, 'error': 'Failed to cancel class'}), 400


@api_bp.route('/recommendations')
@login_required
def get_recommendations():
    """Get activity recommendations"""
    user = session.get('user', {})
    course = request.args.get('course', user.get('course', 'General'))
    duration = request.args.get('duration', 30, type=int)
    
    activities = get_recommended_activities(course, duration)
    return jsonify({'recommendations': activities[:10]})


@api_bp.route('/smart-recommendations')
@login_required
def get_smart_recommendations():
    """Get smart recommendations based on current free time"""
    user = session.get('user', {})
    course = user.get('course')
    student_id = user.get('id')
    
    if not course:
        return jsonify({'recommendations': [], 'context': 'no_course'})
    
    current_slot = get_current_free_slot(course)
    
    if current_slot:
        duration = current_slot.get('remaining_minutes', 30)
        context = 'current_free_time'
    else:
        upcoming = get_upcoming_free_slots(course, 1)
        if upcoming:
            duration = upcoming[0].get('duration_minutes', 30)
            context = 'upcoming_free_time'
        else:
            duration = 30
            context = 'default'
    
    recommendations = get_personalized_recommendations(student_id, course, duration)
    
    return jsonify({
        'recommendations': recommendations[:10],
        'context': context,
        'available_minutes': duration,
        'current_slot': current_slot
    })


@api_bp.route('/activity-logs')
@login_required
def get_activity_logs():
    """Get activity logs for current user"""
    user = session.get('user', {})
    logs = get_activity_logs_by_student(user.get('id'))
    return jsonify({'logs': logs})


@api_bp.route('/notifications')
@login_required
def get_notifications():
    """Get notifications for current user"""
    user = session.get('user', {})
    unread_only = request.args.get('unread', 'false').lower() == 'true'
    notifications = get_notifications_by_user(user.get('id'), unread_only)
    return jsonify({'notifications': notifications[:20]})


@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read"""
    user = session.get('user', {})
    mark_all_notifications_read(user.get('id'))
    return jsonify({'success': True})


@api_bp.route('/stats')
@login_required
def get_stats():
    """Get engagement statistics"""
    user = session.get('user', {})
    days = request.args.get('days', 7, type=int)
    
    if user.get('role') == 'admin':
        stats = get_engagement_stats(days=days)
    else:
        stats = get_engagement_stats(student_id=user.get('id'), days=days)
    
    return jsonify({'stats': stats})


@api_bp.route('/realtime-status')
@login_required
def realtime_status():
    """Get real-time detection system status"""
    status = get_realtime_status()
    return jsonify({'status': status})


@api_bp.route('/poll-updates')
@login_required
def poll_updates():
    """Poll for real-time updates (for clients that don't support WebSocket)"""
    user = session.get('user', {})
    student_id = user.get('id')
    course = user.get('course')
    
    if not course:
        return jsonify({'updates': [], 'free_time': None})
    
    current_free = get_current_free_slot(course)
    upcoming = get_upcoming_free_slots(course, 3)
    notifications = get_notifications_by_user(student_id, unread_only=True)
    
    recommendations = []
    if current_free:
        recommendations = get_recommended_activities(course, current_free.get('remaining_minutes', 30))[:3]
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'current_free_time': current_free,
        'upcoming_slots': upcoming,
        'unread_notifications': len(notifications),
        'latest_notifications': notifications[:5],
        'recommendations': recommendations
    })


@api_bp.route('/seed-demo-data', methods=['POST'])
@admin_required
def seed_demo_data():
    """Seed demo activities and timetable (admin only)"""
    from app.utils.demo_data import DEMO_ACTIVITIES, DEMO_TIMETABLE
    from app.utils.database import create_activity, create_timetable_entry
    
    created_activities = 0
    created_timetable = 0
    errors = []
    
    for activity_data in DEMO_ACTIVITIES:
        try:
            result = create_activity(
                title=activity_data['title'],
                category=activity_data.get('category', 'Learning'),
                duration_minutes=activity_data.get('duration_minutes', 30),
                difficulty=activity_data.get('difficulty', 'Medium'),
                mode=activity_data.get('mode', 'Solo'),
                course=activity_data.get('course'),
                description=activity_data.get('description', ''),
                created_by=session['user'].get('id')
            )
            if result:
                created_activities += 1
        except Exception as e:
            errors.append(f"Activity '{activity_data['title']}': {str(e)}")
    
    teacher_course = session['user'].get('course', 'Computer Science')
    for entry_data in DEMO_TIMETABLE:
        if entry_data.get('course') == teacher_course or not entry_data.get('course'):
            try:
                result = create_timetable_entry(
                    day=entry_data['day'],
                    start_time=entry_data['start_time'],
                    end_time=entry_data['end_time'],
                    course=teacher_course,
                    status=entry_data.get('status', 'scheduled'),
                    teacher_id=session['user'].get('id')
                )
                if result:
                    created_timetable += 1
            except Exception as e:
                errors.append(f"Timetable {entry_data['day']} {entry_data['start_time']}: {str(e)}")
    
    return jsonify({
        'success': True,
        'message': 'Demo data seeded successfully',
        'created_activities': created_activities,
        'created_timetable': created_timetable,
        'errors': errors if errors else None
    })
