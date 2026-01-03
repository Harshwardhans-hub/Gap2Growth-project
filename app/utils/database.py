"""
Database Utility Module
"""

from supabase import create_client, Client
from flask import current_app, g


supabase_client = None


def init_database(app):
    """Initialize database connection with the Flask app"""
    global supabase_client
    
    supabase_url = app.config.get('SUPABASE_URL')
    supabase_key = app.config.get('SUPABASE_KEY')
    
    if supabase_url and supabase_key and supabase_url.startswith('https://'):
        try:
            supabase_client = create_client(supabase_url, supabase_key)
            print("✓ Database connection initialized successfully")
        except Exception as e:
            print(f"✗ Database connection failed: {str(e)}")
            supabase_client = None
    else:
        print("✗ Database credentials not configured")


def get_db() -> Client:
    """Get the database client instance"""
    global supabase_client
    return supabase_client


def is_database_connected():
    """Check if database is connected"""
    return supabase_client is not None


def create_user(firebase_uid, name, role, email, course=None):
    """Create a new user in the database"""
    db = get_db()
    if not db:
        print("Error: Database not connected")
        return None
    
    user_data = {
        'firebase_uid': firebase_uid,
        'name': name,
        'role': role,
        'email': email,
        'course': course
    }
    
    try:
        result = db.table('users').insert(user_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return None


def get_user_by_firebase_uid(firebase_uid):
    """Get user by Firebase UID"""
    db = get_db()
    if not db:
        return None
    
    try:
        result = db.table('users').select('*').eq('firebase_uid', firebase_uid).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error fetching user: {str(e)}")
        return None


def get_user_by_id(user_id):
    """Get user by database ID"""
    db = get_db()
    if not db:
        return None
    
    try:
        result = db.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error fetching user: {str(e)}")
        return None


def get_all_users():
    """Get all users from the database"""
    db = get_db()
    if not db:
        return []
    
    try:
        result = db.table('users').select('*').order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return []


def get_users_by_role(role):
    """Get all users with a specific role"""
    db = get_db()
    if not db:
        return []
    
    try:
        result = db.table('users').select('*').eq('role', role).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching users by role: {str(e)}")
        return []


def get_users_by_course(course):
    """Get all users enrolled in a specific course (case-insensitive)"""
    db = get_db()
    if not db:
        return []
    
    try:
        result = db.table('users').select('*').execute()
        users = result.data if result.data else []
        
        if not course:
            return []
            
        return [
            u for u in users 
            if u.get('course') and u.get('course').lower() == course.lower()
        ]
    except Exception as e:
        print(f"Error fetching users by course: {str(e)}")
        return []


def update_user(user_id, update_data):
    """Update user information"""
    db = get_db()
    if not db:
        return None
    
    try:
        result = db.table('users').update(update_data).eq('id', user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        return None


def delete_user(user_id):
    """Delete a user from the database"""
    db = get_db()
    if not db:
        return False
    
    try:
        db.table('users').delete().eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return False


def create_timetable_entry(teacher_id, course, day, start_time, end_time, status='scheduled'):
    """Create a new timetable entry"""
    db = get_db()
    if not db:
        return None
    
    entry_data = {
        'teacher_id': teacher_id,
        'course': course,
        'day': day,
        'start_time': start_time,
        'end_time': end_time,
        'status': status
    }
    
    try:
        result = db.table('timetables').insert(entry_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating timetable entry: {str(e)}")
        return None


def get_timetable_by_course(course):
    """Get timetable for a specific course (Department)"""
    db = get_db()
    if not db:
        return []
    
    try:
        print(f"DEBUG: Fetching timetable for course: '{course}'")
        
        users = get_users_by_course(course)
        instructors = [u for u in users if u.get('role') in ['teacher', 'admin']]
        instructor_ids = [u.get('id') for u in instructors]
        
        print(f"DEBUG: Found {len(instructors)} instructors for {course}: {[u.get('name') for u in instructors]}")
        
        if not instructor_ids:
            print("DEBUG: No instructors found - falling back to direct course match")
            result = db.table('timetables').select('*').order('day').order('start_time').execute()
            all_entries = result.data if result.data else []
            return [e for e in all_entries if e.get('course') and e.get('course').lower() == course.lower()]

        result = db.table('timetables').select('*').in_('teacher_id', instructor_ids).order('day').order('start_time').execute()
        entries = result.data if result.data else []
        print(f"DEBUG: Found {len(entries)} timetable entries linked to these instructors")
        return entries
        
    except Exception as e:
        print(f"Error fetching timetable: {str(e)}")
        return []


def get_timetable_by_teacher(teacher_id):
    """Get timetable entries created by a specific teacher"""
    db = get_db()
    if not db:
        return []
    
    try:
        result = db.table('timetables').select('*').eq('teacher_id', teacher_id).order('day').order('start_time').execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching timetable: {str(e)}")
        return []


def update_timetable_entry(entry_id, update_data):
    """Update a timetable entry"""
    db = get_db()
    if not db:
        return None
    
    try:
        result = db.table('timetables').update(update_data).eq('id', entry_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error updating timetable: {str(e)}")
        return None


def delete_timetable_entry(entry_id):
    """Delete a timetable entry"""
    db = get_db()
    if not db:
        return False
    
    try:
        db.table('timetables').delete().eq('id', entry_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting timetable entry: {str(e)}")
        return False


def cancel_class(entry_id):
    """Mark a class as cancelled"""
    return update_timetable_entry(entry_id, {'status': 'cancelled'})


def reschedule_class(entry_id, new_start_time, new_end_time):
    """Reschedule a class to a new time"""
    return update_timetable_entry(entry_id, {
        'start_time': new_start_time,
        'end_time': new_end_time,
        'status': 'rescheduled'
    })


def create_activity(title, category, duration_minutes, difficulty, mode, course, created_by, description=''):
    """Create a new activity in the repository"""
    db = get_db()
    if not db:
        print("DEBUG create_activity: Database not connected!")
        return None
    
    # Build activity data (note: activities table doesn't have 'description' column)
    activity_data = {
        'title': title,
        'category': category,
        'duration_minutes': duration_minutes,
        'difficulty': difficulty,
        'mode': mode
    }
    
    # Only add course if it's not None/empty
    if course:
        activity_data['course'] = course
    
    # Add created_by if provided
    if created_by:
        activity_data['created_by'] = created_by
    
    print(f"DEBUG create_activity: Attempting to create activity with data: {activity_data}")
    
    try:
        result = db.table('activities').insert(activity_data).execute()
        print(f"DEBUG create_activity: Success! Created activity: {result.data}")
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"DEBUG create_activity: ERROR - {str(e)}")
        print(f"DEBUG create_activity: Full exception details: {type(e).__name__}")
        return None


def get_all_activities():
    """Get all activities from the repository"""
    db = get_db()
    if not db:
        return []
    
    try:
        result = db.table('activities').select('*').order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching activities: {str(e)}")
        return []


def get_activities_by_course(course):
    """Get activities for a specific course (department) plus universal activities"""
    db = get_db()
    if not db:
        return []
    
    try:
        dept_result = db.table('activities').select('*').eq('course', course).execute()
        dept_activities = dept_result.data if dept_result.data else []
        
        universal_result = db.table('activities').select('*').is_('course', 'null').execute()
        universal_activities = universal_result.data if universal_result.data else []
        
        general_result = db.table('activities').select('*').eq('course', 'General').execute()
        general_activities = general_result.data if general_result.data else []
        
        all_activities = dept_activities + universal_activities + general_activities
        
        seen_ids = set()
        unique_activities = []
        for activity in all_activities:
            if activity['id'] not in seen_ids:
                seen_ids.add(activity['id'])
                unique_activities.append(activity)
        
        return unique_activities
    except Exception as e:
        print(f"Error fetching activities by course: {str(e)}")
        return []


def get_activities_by_duration(max_duration):
    """Get activities that fit within a time limit"""
    db = get_db()
    if not db:
        return []
    
    try:
        result = db.table('activities').select('*').lte('duration_minutes', max_duration).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching activities: {str(e)}")
        return []


def get_activity_by_id(activity_id):
    """Get a specific activity by ID"""
    db = get_db()
    if not db:
        return None
    
    try:
        result = db.table('activities').select('*').eq('id', activity_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error fetching activity: {str(e)}")
        return None


def update_activity(activity_id, update_data):
    """Update an activity"""
    db = get_db()
    if not db:
        return None
    
    try:
        result = db.table('activities').update(update_data).eq('id', activity_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error updating activity: {str(e)}")
        return None


def delete_activity(activity_id):
    """Delete an activity from the repository"""
    db = get_db()
    if not db:
        return False
    
    try:
        db.table('activities').delete().eq('id', activity_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting activity: {str(e)}")
        return False


def create_activity_log(student_id, activity_id, start_time, status='in_progress'):
    """Create a new activity log entry"""
    db = get_db()
    if not db:
        return None
    
    log_data = {
        'student_id': student_id,
        'activity_id': activity_id,
        'start_time': start_time,
        'status': status
    }
    
    try:
        result = db.table('activity_logs').insert(log_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating activity log: {str(e)}")
        return None


def complete_activity_log(log_id, end_time):
    """Mark an activity log as completed"""
    db = get_db()
    if not db:
        return None
    
    try:
        result = db.table('activity_logs').update({
            'end_time': end_time,
            'status': 'completed'
        }).eq('id', log_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error completing activity log: {str(e)}")
        return None


def get_activity_logs_by_student(student_id):
    """Get all activity logs for a student"""
    db = get_db()
    if not db:
        return []
    
    try:
        result = db.table('activity_logs').select('*, activities(*)').eq('student_id', student_id).order('start_time', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching activity logs: {str(e)}")
        return []


def get_all_activity_logs():
    """Get all activity logs"""
    db = get_db()
    if not db:
        return []
    
    try:
        result = db.table('activity_logs').select('*, activities(*), users(*)').order('start_time', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching activity logs: {str(e)}")
        return []


def create_notification(user_id, message):
    """Create a new notification"""
    db = get_db()
    if not db:
        return None
    
    notification_data = {
        'user_id': user_id,
        'message': message,
        'is_read': False
    }
    
    try:
        result = db.table('notifications').insert(notification_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating notification: {str(e)}")
        return None


def get_notifications_by_user(user_id, unread_only=False):
    """Get notifications for a user"""
    db = get_db()
    if not db:
        return []
    
    try:
        query = db.table('notifications').select('*').eq('user_id', user_id)
        if unread_only:
            query = query.eq('is_read', False)
        result = query.order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching notifications: {str(e)}")
        return []


def mark_notification_read(notification_id):
    """Mark a notification as read"""
    db = get_db()
    if not db:
        return False
    
    try:
        db.table('notifications').update({'is_read': True}).eq('id', notification_id).execute()
        return True
    except Exception as e:
        print(f"Error marking notification as read: {str(e)}")
        return False


def mark_all_notifications_read(user_id):
    """Mark all notifications as read for a user"""
    db = get_db()
    if not db:
        return False
    
    try:
        db.table('notifications').update({'is_read': True}).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error marking notifications as read: {str(e)}")
        return False
