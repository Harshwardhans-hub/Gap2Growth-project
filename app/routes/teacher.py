"""
Teacher Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import teacher_required, get_current_user, get_current_user_id
from app.utils.database import (
    get_timetable_by_teacher, create_timetable_entry, update_timetable_entry,
    delete_timetable_entry, cancel_class,
    get_all_activities, get_activities_by_course, create_activity, update_activity, delete_activity,
    get_users_by_course
)
from app.services.realtime_service import trigger_class_cancellation

teacher_bp = Blueprint('teacher', __name__)


# Day order for sorting (Monday = 0, Sunday = 6)
DAY_ORDER = {
    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
    'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
}


def _get_today():
    """Get current day name"""
    from datetime import datetime
    return datetime.now().strftime('%A')


def _sort_timetable_entries(entries):
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


@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    """Teacher dashboard with real statistics"""
    user = get_current_user()
    user_course = user.get('course')
    timetable = get_timetable_by_teacher(user.get('id'))
    
    sorted_timetable = _sort_timetable_entries(timetable)
    
    activities = get_activities_by_course(user_course) if user_course else get_all_activities()
    students = get_users_by_course(user.get('course')) if user.get('course') else []
    students = [s for s in students if s.get('role') == 'student']
    
    from app.utils.database import get_all_activity_logs
    all_logs = get_all_activity_logs()
    
    course_activity_ids = {a.get('id') for a in activities}
    course_completions = [
        log for log in all_logs 
        if log.get('status') == 'completed' 
        and log.get('activity_id') in course_activity_ids
    ]
    
    today_classes = [
        e for e in sorted_timetable 
        if e.get('day', '').lower() == _get_today().lower()
    ]
    
    return render_template('teacher/dashboard.html',
        user=user,
        timetable=sorted_timetable,
        today_classes=today_classes,
        activities=activities,
        students=students,
        completions_count=len(course_completions)
    )


@teacher_bp.route('/timetable')
@teacher_required
def timetable():
    """Timetable management page - sorted by day and time"""
    user = get_current_user()
    entries = get_timetable_by_teacher(user.get('id'))
    
    sorted_entries = _sort_timetable_entries(entries)
    
    return render_template('teacher/timetable.html', user=user, entries=sorted_entries)


@teacher_bp.route('/timetable/add', methods=['GET', 'POST'])
@teacher_required
def add_timetable():
    """Add timetable entry"""
    user = get_current_user()
    
    if request.method == 'POST':
        entry = create_timetable_entry(
            teacher_id=user.get('id'),
            course=request.form.get('course', user.get('course')),
            day=request.form.get('day'),
            start_time=request.form.get('start_time'),
            end_time=request.form.get('end_time'),
            status='scheduled'
        )
        
        if entry:
            flash('Timetable entry added!', 'success')
            return redirect(url_for('teacher.timetable'))
        flash('Failed to add entry.', 'danger')
    
    return render_template('teacher/timetable_form.html', user=user, entry=None)


@teacher_bp.route('/timetable/<entry_id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_timetable(entry_id):
    """Edit timetable entry"""
    user = get_current_user()
    
    if request.method == 'POST':
        update_data = {
            'day': request.form.get('day'),
            'start_time': request.form.get('start_time'),
            'end_time': request.form.get('end_time'),
            'status': request.form.get('status', 'scheduled')
        }
        
        if update_timetable_entry(entry_id, update_data):
            flash('Entry updated!', 'success')
            return redirect(url_for('teacher.timetable'))
        flash('Update failed.', 'danger')
    
    return render_template('teacher/timetable_form.html', user=user, entry={'id': entry_id})


@teacher_bp.route('/timetable/<entry_id>/cancel', methods=['POST'])
@teacher_required
def cancel_timetable(entry_id):
    """Cancel a class - triggers real-time notifications to students"""
    user = get_current_user()
    teacher_course = user.get('course')
    
    from app.utils.database import get_timetable_by_teacher
    entries = get_timetable_by_teacher(user.get('id'))
    entry = next((e for e in entries if str(e.get('id')) == str(entry_id)), None)
    
    course = entry.get('course') if entry else teacher_course
    
    print(f"\n📋 CANCEL CLASS REQUEST:")
    print(f"   Entry ID: {entry_id}")
    print(f"   Course: {course}")
    print(f"   Teacher: {user.get('name')}")
    
    if cancel_class(entry_id):
        print(f"   ✓ Class marked as cancelled in database")
        
        if course:
            trigger_class_cancellation(entry_id, course)
        else:
            print(f"   ⚠ No course found - notifications not sent!")
        
        flash('Class cancelled! Students have been notified.', 'success')
    else:
        print(f"   ✗ Failed to cancel class in database")
        flash('Failed to cancel class.', 'danger')
    
    return redirect(url_for('teacher.timetable'))


@teacher_bp.route('/timetable/<entry_id>/reschedule', methods=['POST'])
@teacher_required
def reschedule_timetable(entry_id):
    """Reschedule a class to a new time"""
    user = get_current_user()
    
    new_start = request.form.get('new_start_time')
    new_end = request.form.get('new_end_time')
    
    if new_start and new_end:
        update_data = {
            'start_time': new_start,
            'end_time': new_end,
            'status': 'rescheduled'
        }
        
        if update_timetable_entry(entry_id, update_data):
            flash('Class rescheduled! Students will be notified.', 'success')
        else:
            flash('Failed to reschedule class.', 'danger')
    else:
        flash('Please provide new start and end times.', 'warning')
    
    return redirect(url_for('teacher.timetable'))


@teacher_bp.route('/timetable/<entry_id>/delete', methods=['POST'])
@teacher_required
def delete_timetable(entry_id):
    """Delete timetable entry"""
    if delete_timetable_entry(entry_id):
        flash('Entry deleted!', 'success')
    else:
        flash('Delete failed.', 'danger')
    return redirect(url_for('teacher.timetable'))


@teacher_bp.route('/activities')
@teacher_required
def activities_list():
    """Activity management page - filtered by teacher's department"""
    user = get_current_user()
    user_course = user.get('course')
    activities = get_activities_by_course(user_course) if user_course else get_all_activities()
    return render_template('teacher/activities.html', user=user, activities=activities)


@teacher_bp.route('/activities/add', methods=['GET', 'POST'])
@teacher_required
def add_activity():
    """Add new activity - automatically assigned to teacher's department"""
    user = get_current_user()
    user_course = user.get('course')
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        duration = request.form.get('duration', 30)
        difficulty = request.form.get('difficulty', 'Medium')
        mode = request.form.get('mode', 'Solo')
        description = request.form.get('description', '')
        
        # Validate required fields
        if not title or not title.strip():
            flash('Activity title is required.', 'danger')
            return render_template('teacher/activity_form.html', user=user, activity=None)
        
        if not category:
            flash('Category is required.', 'danger')
            return render_template('teacher/activity_form.html', user=user, activity=None)
        
        try:
            duration_int = int(duration)
        except (ValueError, TypeError):
            duration_int = 30
        
        # Create the activity
        activity = create_activity(
            title=title.strip(),
            category=category,
            duration_minutes=duration_int,
            difficulty=difficulty,
            mode=mode,
            course=user_course,  # May be None for general activities
            created_by=user.get('id'),
            description=description
        )
        
        if activity:
            course_msg = user_course if user_course else 'General'
            flash(f'Activity "{title}" created successfully for {course_msg}!', 'success')
            return redirect(url_for('teacher.activities_list'))
        else:
            flash('Failed to create activity. Please check your database connection.', 'danger')
    
    return render_template('teacher/activity_form.html', user=user, activity=None)


@teacher_bp.route('/activities/<activity_id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_activity(activity_id):
    """Edit activity"""
    user = get_current_user()
    
    if request.method == 'POST':
        update_data = {
            'title': request.form.get('title'),
            'category': request.form.get('category'),
            'duration_minutes': int(request.form.get('duration', 30)),
            'difficulty': request.form.get('difficulty'),
            'mode': request.form.get('mode'),
            'description': request.form.get('description', '')
        }
        
        if update_activity(activity_id, update_data):
            flash('Activity updated!', 'success')
            return redirect(url_for('teacher.activities_list'))
        flash('Update failed.', 'danger')
    
    from app.utils.database import get_activity_by_id
    activity = get_activity_by_id(activity_id)
    return render_template('teacher/activity_form.html', user=user, activity=activity)


@teacher_bp.route('/activities/<activity_id>/delete', methods=['POST'])
@teacher_required
def delete_activity_action(activity_id):
    """Delete activity"""
    if delete_activity(activity_id):
        flash('Activity deleted!', 'success')
    else:
        flash('Delete failed.', 'danger')
    return redirect(url_for('teacher.activities_list'))


@teacher_bp.route('/students')
@teacher_required
def students_list():
    """View students in course"""
    user = get_current_user()
    students = get_users_by_course(user.get('course')) if user.get('course') else []
    students = [s for s in students if s.get('role') == 'student']
    return render_template('teacher/students.html', user=user, students=students)
