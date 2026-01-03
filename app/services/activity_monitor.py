"""
Activity Monitor Service
Handles auto-completion of expired activities
"""

from datetime import datetime, timedelta
from app.utils.database import get_db

def auto_complete_expired_activities():
    """
    Check for 'in_progress' activities that have exceeded their duration 
    and mark them as completed.
    """
    db = get_db()
    if not db:
        print("Database not connected for activity monitoring")
        return

    try:
        # Fetch all in_progress activities with their associated activity details
        # We need to join with activities table to get duration_minutes
        result = db.table('activity_logs').select('*, activities(*)').eq('status', 'in_progress').execute()
        active_logs = result.data if result.data else []
        
        count = 0
        now = datetime.now()
        
        for log in active_logs:
            activity = log.get('activities')
            if not activity:
                continue
                
            start_time_str = log.get('start_time')
            if not start_time_str:
                continue
                
            # Parse start time (handle ISO format)
            try:
                # Handle simplified ISO format or full format
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            except ValueError:
                # Fallback for simple string if needed, though ISO is standard
                continue
            
            duration_minutes = activity.get('duration_minutes', 0)
            
            # Calculate expected end time
            expected_end_time = start_time + timedelta(minutes=duration_minutes)
            
            # If current time is past expected end time (plus a small buffer maybe, but user wants strict)
            if now > expected_end_time:
                # Complete the activity
                # Use strict expected end time as completion time to respect the duration
                # OR use 'now' if we want to show when it was actually processed?
                # Usually 'expected_end_time' is cleaner for stats, but 'now' might be more honest about when system caught it.
                # Given user wants "automatically finish after the time gets up", using expected end time seems correct for "productive time" accounting.
                # However, let's use the actual expected finish time so the duration matches perfectly.
                
                db.table('activity_logs').update({
                    'status': 'completed',
                    'end_time': expected_end_time.isoformat()
                }).eq('id', log.get('id')).execute()
                
                count += 1
                
        if count > 0:
            print(f"[{now}] Auto-completed {count} expired activities")
            
    except Exception as e:
        print(f"Error in auto_complete_expired_activities: {str(e)}")
