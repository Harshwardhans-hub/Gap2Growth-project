"""
Downtime Detection Service
Real-time free time slot detection and analysis
"""

from datetime import datetime, timedelta, time
from app.utils.database import (
    get_timetable_by_course, 
    get_users_by_role,
    get_users_by_course,
    create_notification
)
import os


DOWNTIME_THRESHOLD = int(os.getenv('DOWNTIME_THRESHOLD_MINUTES', 30))


def parse_time(time_str):
    """Convert time string to datetime.time object"""
    if isinstance(time_str, time):
        return time_str
    
    if not time_str:
        return None
    
    for fmt in ['%H:%M:%S', '%H:%M', '%I:%M %p']:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    return None


def get_day_name():
    """Get current day name"""
    return datetime.now().strftime('%A')


def get_current_time():
    """Get current time"""
    return datetime.now().time()


def calculate_gap_minutes(start_time, end_time):
    """
    Calculate minutes between start_time (earlier) and end_time (later).
    Returns positive minutes if start < end.
    """
    today = datetime.today().date()
    end_datetime = datetime.combine(today, end_time)
    start_datetime = datetime.combine(today, start_time)
    
    if end_datetime < start_datetime:
        return (start_datetime - end_datetime).total_seconds() / 60 * -1
        
    gap = end_datetime - start_datetime
    return gap.total_seconds() / 60


def is_time_in_range(check_time, start_time, end_time):
    """Check if a time falls within a range"""
    return start_time <= check_time < end_time


def detect_downtime_for_course(course, day=None):
    """Detect free time slots for a specific course on a given day"""
    if day is None:
        day = get_day_name()
    
    timetable = get_timetable_by_course(course)
    
    if not timetable:
        return []
    
    day_entries = [
        entry for entry in timetable 
        if entry.get('day', '').lower() == day.lower() 
        and entry.get('status', 'scheduled').lower() == 'scheduled'
    ]
    
    if not day_entries:
        return []
    
    day_entries.sort(key=lambda x: parse_time(x.get('start_time', '00:00')) or time(0, 0))
    
    free_slots = []
    
    for i in range(len(day_entries) - 1):
        current_class = day_entries[i]
        next_class = day_entries[i + 1]
        
        current_end = parse_time(current_class.get('end_time'))
        next_start = parse_time(next_class.get('start_time'))
        
        if current_end and next_start:
            gap_minutes = calculate_gap_minutes(current_end, next_start)
            
            if gap_minutes >= DOWNTIME_THRESHOLD:
                free_slots.append({
                    'course': course,
                    'day': day,
                    'start_time': current_end.strftime('%H:%M'),
                    'end_time': next_start.strftime('%H:%M'),
                    'duration_minutes': int(gap_minutes),
                    'reason': 'timetable_gap',
                    'is_current': _is_slot_current(current_end, next_start),
                    'is_upcoming': _is_slot_upcoming(current_end)
                })
    
    return free_slots


def detect_cancelled_class_slots(course, day=None):
    """Detect free time from cancelled classes"""
    if day is None:
        day = get_day_name()
    
    timetable = get_timetable_by_course(course)
    
    if not timetable:
        return []
    
    cancelled_entries = [
        entry for entry in timetable 
        if entry.get('day', '').lower() == day.lower() 
        and entry.get('status', '').lower() == 'cancelled'
    ]
    
    free_slots = []
    
    for entry in cancelled_entries:
        start_time = parse_time(entry.get('start_time'))
        end_time = parse_time(entry.get('end_time'))
        
        if start_time and end_time:
            duration = calculate_gap_minutes(start_time, end_time)
            
            if duration >= DOWNTIME_THRESHOLD:
                free_slots.append({
                    'course': course,
                    'day': day,
                    'start_time': start_time.strftime('%H:%M'),
                    'end_time': end_time.strftime('%H:%M'),
                    'duration_minutes': int(duration),
                    'reason': 'class_cancelled',
                    'is_current': _is_slot_current(start_time, end_time),
                    'is_upcoming': _is_slot_upcoming(start_time)
                })
    
    return free_slots


def _is_slot_current(start_time, end_time):
    """Check if a slot is currently active"""
    current = get_current_time()
    return is_time_in_range(current, start_time, end_time)


def _is_slot_upcoming(start_time):
    """Check if a slot is upcoming (starts in the future)"""
    current = get_current_time()
    return start_time > current


def detect_all_downtime_for_course(course, day=None):
    """Detect all free time slots (gaps + cancellations) for a course"""
    gap_slots = detect_downtime_for_course(course, day)
    cancelled_slots = detect_cancelled_class_slots(course, day)
    
    all_slots = gap_slots + cancelled_slots
    all_slots.sort(key=lambda x: x.get('start_time', '00:00'))
    
    return all_slots


def get_current_free_slot(course):
    """Get the free slot that is active right now"""
    today = get_day_name()
    all_slots = detect_all_downtime_for_course(course, today)
    
    for slot in all_slots:
        if slot.get('is_current'):
            remaining = _calculate_remaining_time(slot.get('end_time'))
            slot['remaining_minutes'] = remaining
            return slot
    
    return None


def _calculate_remaining_time(end_time_str):
    """Calculate remaining minutes until end time"""
    end_time = parse_time(end_time_str)
    if not end_time:
        return 0
    
    current = get_current_time()
    today = datetime.today().date()
    
    current_dt = datetime.combine(today, current)
    end_dt = datetime.combine(today, end_time)
    
    delta = end_dt - current_dt
    return max(0, int(delta.total_seconds() / 60))


def get_upcoming_free_slots(course, limit=5):
    """Get upcoming free slots for a course"""
    today = get_day_name()
    all_slots = detect_all_downtime_for_course(course, today)
    
    upcoming = [slot for slot in all_slots if slot.get('is_upcoming')]
    
    for slot in upcoming:
        slot['starts_in_minutes'] = _calculate_time_until(slot.get('start_time'))
    
    return upcoming[:limit]


def _calculate_time_until(start_time_str):
    """Calculate minutes until start time"""
    start_time = parse_time(start_time_str)
    if not start_time:
        return 0
    
    current = get_current_time()
    today = datetime.today().date()
    
    current_dt = datetime.combine(today, current)
    start_dt = datetime.combine(today, start_time)
    
    delta = start_dt - current_dt
    return max(0, int(delta.total_seconds() / 60))


def detect_all_student_downtime():
    """Detect downtime for all students across all courses"""
    all_results = []
    
    students = get_users_by_role('student')
    
    if not students:
        return all_results
    
    courses = set(student.get('course') for student in students if student.get('course'))
    
    for course in courses:
        free_slots = detect_all_downtime_for_course(course)
        
        if free_slots:
            course_students = [s for s in students if s.get('course') == course]
            
            for slot in free_slots:
                for student in course_students:
                    result = {
                        'student_id': student.get('id'),
                        'student_name': student.get('name'),
                        'student_email': student.get('email'),
                        **slot
                    }
                    all_results.append(result)
                    
                    if slot.get('is_current'):
                        message = f"⏰ Free time NOW: {slot['remaining_minutes']} minutes remaining until {slot['end_time']}"
                    else:
                        message = f"📅 Upcoming free time: {slot['duration_minutes']} minutes from {slot['start_time']} to {slot['end_time']}"
                    
                    create_notification(student.get('id'), message)
    
    return all_results


def get_weekly_free_time_summary(course):
    """Get a summary of free time slots for the entire week"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    summary = {}
    
    for day in days:
        slots = detect_all_downtime_for_course(course, day)
        total_minutes = sum(s.get('duration_minutes', 0) for s in slots)
        summary[day] = {
            'slots': slots,
            'total_free_minutes': total_minutes,
            'slot_count': len(slots)
        }
    
    return summary


def get_daily_schedule_with_gaps(course, day=None):
    """Get full daily schedule including classes and gaps"""
    if day is None:
        day = get_day_name()
    
    timetable = get_timetable_by_course(course)
    
    if not timetable:
        return []
    
    day_entries = [
        entry for entry in timetable 
        if entry.get('day', '').lower() == day.lower()
    ]
    
    day_entries.sort(key=lambda x: parse_time(x.get('start_time', '00:00')) or time(0, 0))
    
    schedule = []
    
    for i, entry in enumerate(day_entries):
        schedule.append({
            'type': 'class',
            'start_time': entry.get('start_time'),
            'end_time': entry.get('end_time'),
            'status': entry.get('status'),
            'id': entry.get('id')
        })
        
        if i < len(day_entries) - 1:
            current_end = parse_time(entry.get('end_time'))
            next_start = parse_time(day_entries[i + 1].get('start_time'))
            
            if current_end and next_start:
                gap = calculate_gap_minutes(current_end, next_start)
                
                if gap >= DOWNTIME_THRESHOLD:
                    schedule.append({
                        'type': 'free_time',
                        'start_time': current_end.strftime('%H:%M'),
                        'end_time': next_start.strftime('%H:%M'),
                        'duration_minutes': int(gap),
                        'is_current': _is_slot_current(current_end, next_start)
                    })
    
    return schedule
