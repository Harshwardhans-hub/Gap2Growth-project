"""
Student Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app.utils.decorators import student_required, get_current_user
from app.utils.database import (
    get_timetable_by_course, get_activity_logs_by_student,
    create_activity_log, complete_activity_log, get_activity_by_id,
    get_notifications_by_user, mark_notification_read
)
from app.services.downtime_service import (
    detect_all_downtime_for_course, 
    get_upcoming_free_slots,
    get_current_free_slot,
    get_daily_schedule_with_gaps,
    get_weekly_free_time_summary
)
from app.services.recommendation_service import get_recommended_activities, get_personalized_recommendations
from app.services.notification_service import get_user_notifications, get_unread_count

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@student_required
def dashboard():
    """Student dashboard with real-time free time detection"""
    user = get_current_user()
    course = user.get('course', 'General')
    student_id = user.get('id')
    
    timetable = get_timetable_by_course(course)
    
    current_free = get_current_free_slot(course)
    upcoming_slots = get_upcoming_free_slots(course, limit=3)
    all_free_slots = detect_all_downtime_for_course(course)
    
    activity_logs = get_activity_logs_by_student(student_id)
    recent_activities = activity_logs[:5]
    
    notifications = get_user_notifications(student_id, limit=5)
    unread_count = get_unread_count(student_id)
    
    if current_free:
        duration = current_free.get('remaining_minutes', 30)
        recommendations = get_personalized_recommendations(student_id, course, duration)[:4]
        free_time_status = 'active'
    elif upcoming_slots:
        duration = upcoming_slots[0].get('duration_minutes', 30)
        recommendations = get_personalized_recommendations(student_id, course, duration)[:4]
        free_time_status = 'upcoming'
    else:
        recommendations = get_recommended_activities(course, 30)[:4]
        free_time_status = 'none'
    
    completed = [l for l in activity_logs if l.get('status') == 'completed']
    total_minutes = sum(l.get('activities', {}).get('duration_minutes', 0) for l in completed)
    streak_days = calculate_streak(completed)
    
    return render_template('student/dashboard.html',
        user=user,
        timetable=timetable[:5],
        current_free=current_free,
        upcoming_slots=upcoming_slots,
        free_slots=all_free_slots[:3],
        free_time_status=free_time_status,
        recent_activities=recent_activities,
        recommendations=recommendations,
        notifications=notifications,
        unread_count=unread_count,
        streak_days=streak_days,
        stats={
            'completed': len(completed),
            'in_progress': len([l for l in activity_logs if l.get('status') == 'in_progress']),
            'total_hours': round(total_minutes / 60, 1)
        }
    )


def calculate_streak(completed_logs):
    """Calculate consecutive days with completed activities"""
    if not completed_logs:
        return 0
    
    from datetime import datetime, timedelta
    
    dates = set()
    for log in completed_logs:
        end_time = log.get('end_time')
        if end_time:
            try:
                date = datetime.fromisoformat(end_time.replace('Z', '')).date()
                dates.add(date)
            except:
                pass
    
    if not dates:
        return 0
    
    today = datetime.now().date()
    streak = 0
    current_date = today
    
    while current_date in dates:
        streak += 1
        current_date -= timedelta(days=1)
    
    return streak

# Day order for sorting
DAY_ORDER = {
    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
    'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
}


def _sort_entries(entries):
    """Sort timetable entries by day of week then by start time"""
    def sort_key(entry):
        day = entry.get('day', 'Monday')
        day_index = DAY_ORDER.get(day, 7)
        start_time = entry.get('start_time', '00:00:00')
        time_parts = start_time.split(':')
        hour = int(time_parts[0]) if time_parts else 0
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        return (day_index, hour, minute)
    return sorted(entries, key=sort_key)


@student_bp.route('/timetable')
@student_required
def timetable():
    """View timetable with gaps highlighted - sorted by day and time"""
    user = get_current_user()
    course = user.get('course')
    
    entries = get_timetable_by_course(course)
    sorted_entries = _sort_entries(entries)
    
    schedule = get_daily_schedule_with_gaps(course)
    weekly_summary = get_weekly_free_time_summary(course)
    
    return render_template('student/timetable.html', 
        user=user, 
        entries=sorted_entries,
        schedule=schedule,
        weekly_summary=weekly_summary
    )


@student_bp.route('/recommendations')
@student_required
def recommendations():
    """View activity recommendations based on current/upcoming free time"""
    user = get_current_user()
    student_id = user.get('id')
    course = user.get('course', 'General')
    
    duration = request.args.get('duration', type=int)
    category = request.args.get('category')
    
    current_free = get_current_free_slot(course)
    
    if not duration:
        if current_free:
            duration = current_free.get('remaining_minutes', 30)
        else:
            duration = 30
    
    activities = get_personalized_recommendations(student_id, course, duration)
    
    if category:
        activities = [a for a in activities if a.get('category') == category]
    
    return render_template('student/recommendations.html',
        user=user,
        activities=activities,
        duration=duration,
        category=category,
        current_free=current_free
    )


@student_bp.route('/activity/<activity_id>')
@student_required
def view_activity(activity_id):
    """View activity details"""
    user = get_current_user()
    activity = get_activity_by_id(activity_id)
    
    if not activity:
        flash('Activity not found.', 'danger')
        return redirect(url_for('student.recommendations'))
    
    course = user.get('course')
    current_free = get_current_free_slot(course) if course else None
    
    # Check for active log
    activity_logs = get_activity_logs_by_student(user.get('id'))
    active_log = next((log for log in activity_logs 
                      if str(log.get('activity_id')) == str(activity_id) 
                      and log.get('status') == 'in_progress'), None)
    
    can_start = True
    if current_free:
        if activity.get('duration_minutes', 0) > current_free.get('remaining_minutes', 0):
            can_start = False
    
    return render_template('student/activity_detail.html', 
        user=user, 
        activity=activity,
        current_free=current_free,
        can_start=can_start,
        active_log=active_log
    )


@student_bp.route('/activity/<activity_id>/start', methods=['POST'])
@student_required
def start_activity(activity_id):
    """Start an activity - validates free time availability"""
    user = get_current_user()
    course = user.get('course')
    
    # Get the activity details
    activity = get_activity_by_id(activity_id)
    if not activity:
        return jsonify({'success': False, 'error': 'Activity not found'}), 404
    
    activity_duration = activity.get('duration_minutes', 30)
    
    # Check if user is in a free time slot
    current_free = get_current_free_slot(course) if course else None
    
    if not current_free:
        return jsonify({
            'success': False, 
            'error': 'You can only start activities during your free time. No free time detected right now.'
        }), 400
    
    remaining_minutes = current_free.get('remaining_minutes', 0)
    
    # Check if activity duration fits within the free time
    if activity_duration > remaining_minutes:
        return jsonify({
            'success': False, 
            'error': f'This activity takes {activity_duration} minutes but you only have {remaining_minutes} minutes of free time remaining.'
        }), 400
    
    # Check if student already has an in-progress activity
    existing_logs = get_activity_logs_by_student(user.get('id'))
    in_progress = [log for log in existing_logs if log.get('status') == 'in_progress']
    
    if in_progress:
        return jsonify({
            'success': False, 
            'error': 'You already have an activity in progress. Please complete it first.'
        }), 400
    
    log = create_activity_log(
        student_id=user.get('id'),
        activity_id=activity_id,
        start_time=datetime.now().isoformat(),
        status='in_progress'
    )
    
    if log:
        flash('Activity started! Good luck!', 'success')
        return jsonify({
            'success': True, 
            'log_id': log.get('id'),
            'free_time_end': current_free.get('end_time'),
            'remaining_minutes': remaining_minutes
        })
    
    return jsonify({'success': False, 'error': 'Failed to start activity'}), 400


@student_bp.route('/activity/<log_id>/complete', methods=['POST'])
@student_required
def complete_activity(log_id):
    """Complete an activity - only allowed after full duration has elapsed"""
    user = get_current_user()
    
    # Verify the log belongs to this student
    existing_logs = get_activity_logs_by_student(user.get('id'))
    log = next((l for l in existing_logs if str(l.get('id')) == str(log_id)), None)
    
    if not log:
        return jsonify({'success': False, 'error': 'Activity log not found'}), 404
    
    if log.get('status') == 'completed':
        return jsonify({'success': False, 'error': 'Activity already completed'}), 400
    
    # Validate that enough time has elapsed based on activity duration
    activity = log.get('activities', {})
    activity_duration = activity.get('duration_minutes', 0)
    start_time_str = log.get('start_time')
    
    if start_time_str and activity_duration > 0:
        try:
            # Parse start time (handle various ISO formats)
            start_time_str = start_time_str.replace('Z', '+00:00')
            if '.' in start_time_str:
                start_time = datetime.fromisoformat(start_time_str.split('.')[0])
            else:
                start_time = datetime.fromisoformat(start_time_str.split('+')[0])
            
            elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
            
            if elapsed_minutes < activity_duration:
                remaining = int(activity_duration - elapsed_minutes)
                return jsonify({
                    'success': False, 
                    'error': f'Cannot complete yet! You must wait {remaining} more minute(s) to complete this {activity_duration}-minute activity.',
                    'remaining_minutes': remaining
                }), 400
        except Exception as e:
            print(f"Error parsing time: {e}")
            # If we can't parse the time, allow completion (fail-open)
    
    result = complete_activity_log(log_id, datetime.now().isoformat())
    
    if result:
        flash('Activity completed! Great job!', 'success')
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Failed to complete activity'}), 400


@student_bp.route('/activity/<log_id>/end', methods=['POST'])
@student_required
def end_activity(log_id):
    """End/Complete an activity from any page (history, dashboard, etc.) - only allowed after full duration"""
    user = get_current_user()
    
    # Verify the log belongs to this student
    existing_logs = get_activity_logs_by_student(user.get('id'))
    log = next((l for l in existing_logs if str(l.get('id')) == str(log_id)), None)
    
    if not log:
        flash('Activity log not found.', 'danger')
        return redirect(url_for('student.history'))
    
    if log.get('status') == 'completed':
        flash('Activity was already completed.', 'info')
        return redirect(url_for('student.history'))
    
    # Validate that enough time has elapsed based on activity duration
    activity = log.get('activities', {})
    activity_duration = activity.get('duration_minutes', 0)
    start_time_str = log.get('start_time')
    
    if start_time_str and activity_duration > 0:
        try:
            # Parse start time (handle various ISO formats)
            start_time_str = start_time_str.replace('Z', '+00:00')
            if '.' in start_time_str:
                start_time = datetime.fromisoformat(start_time_str.split('.')[0])
            else:
                start_time = datetime.fromisoformat(start_time_str.split('+')[0])
            
            elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
            
            if elapsed_minutes < activity_duration:
                remaining = int(activity_duration - elapsed_minutes)
                flash(f'Cannot complete yet! You must wait {remaining} more minute(s) to complete this {activity_duration}-minute activity.', 'warning')
                return redirect(url_for('student.history'))
        except Exception as e:
            print(f"Error parsing time: {e}")
            # If we can't parse the time, allow completion (fail-open)
    
    result = complete_activity_log(log_id, datetime.now().isoformat())
    
    if result:
        flash('Activity completed! Great job!', 'success')
    else:
        flash('Failed to complete activity.', 'danger')
    
    return redirect(url_for('student.history'))


@student_bp.route('/history')
@student_required
def history():
    """View activity history"""
    user = get_current_user()
    logs = get_activity_logs_by_student(user.get('id'))
    
    return render_template('student/history.html', user=user, logs=logs)


@student_bp.route('/notifications')
@student_required
def notifications():
    """View all notifications"""
    user = get_current_user()
    all_notifications = get_user_notifications(user.get('id'), limit=50)
    
    return render_template('student/notifications.html',
        user=user,
        notifications=all_notifications
    )


@student_bp.route('/notifications/<notification_id>/read', methods=['POST'])
@student_required
def mark_read(notification_id):
    """Mark notification as read"""
    mark_notification_read(notification_id)
    return jsonify({'success': True})


@student_bp.route('/free-time')
@student_required
def free_time():
    """View detected free time slots with real-time status"""
    user = get_current_user()
    course = user.get('course')
    
    current_free = get_current_free_slot(course)
    upcoming = get_upcoming_free_slots(course, 10)
    all_slots = detect_all_downtime_for_course(course)
    weekly = get_weekly_free_time_summary(course)
    
    total_weekly_minutes = sum(
        day_data.get('total_free_minutes', 0) 
        for day_data in weekly.values()
    )
    
    return render_template('student/free_time.html', 
        user=user, 
        current_free=current_free,
        upcoming_slots=upcoming,
        slots=all_slots,
        weekly_summary=weekly,
        total_weekly_minutes=total_weekly_minutes
    )


@student_bp.route('/live-status')
@student_required
def live_status():
    """Get live status for AJAX polling"""
    user = get_current_user()
    course = user.get('course')
    student_id = user.get('id')
    
    current_free = get_current_free_slot(course) if course else None
    upcoming = get_upcoming_free_slots(course, 3) if course else []
    unread = get_unread_count(student_id)
    
    recommendations = []
    if current_free:
        recommendations = get_recommended_activities(
            course, 
            current_free.get('remaining_minutes', 30)
        )[:3]
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'current_free': current_free,
        'upcoming': upcoming,
        'unread_notifications': unread,
        'recommendations': recommendations
    })
