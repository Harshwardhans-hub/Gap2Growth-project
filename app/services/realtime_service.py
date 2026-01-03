"""
Real-Time Detection Service
Handles real-time class cancellation detection, free time detection, and auto-assignment
"""

from datetime import datetime, timedelta, time
from flask import current_app
import threading
import time as time_module

from app.utils.database import (
    get_timetable_by_course,
    get_users_by_role,
    get_users_by_course,
    create_notification,
    get_all_activities,
    create_activity_log,
    get_activity_logs_by_student,
    update_timetable_entry,
    get_user_by_id
)
from app.utils.email_sender import send_email


class RealTimeDetector:
    """Real-time detection engine for class cancellations and free time"""
    
    def __init__(self):
        self.active_sessions = {}
        self.last_timetable_state = {}
        self.detection_running = False
        self.detection_thread = None
    
    def start_detection(self):
        """Start the real-time detection loop"""
        if self.detection_running:
            return
        
        self.detection_running = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        print("✓ Real-time detection started")
    
    def stop_detection(self):
        """Stop the real-time detection loop"""
        self.detection_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=5)
        print("✓ Real-time detection stopped")
    
    def _detection_loop(self):
        """Main detection loop - runs every 30 seconds"""
        while self.detection_running:
            try:
                self._check_for_cancellations()
                self._detect_current_free_time()
            except Exception as e:
                print(f"Detection loop error: {e}")
            time_module.sleep(30)
    
    def _check_for_cancellations(self):
        """Check for newly cancelled classes"""
        students = get_users_by_role('student')
        courses = set(s.get('course') for s in students if s.get('course'))
        
        for course in courses:
            current_timetable = get_timetable_by_course(course)
            previous_state = self.last_timetable_state.get(course, [])
            
            for entry in current_timetable:
                entry_id = entry.get('id')
                current_status = entry.get('status')
                
                prev_entry = next((e for e in previous_state if e.get('id') == entry_id), None)
                
                if prev_entry and prev_entry.get('status') == 'scheduled' and current_status == 'cancelled':
                    self._handle_class_cancellation(course, entry)
            
            self.last_timetable_state[course] = current_timetable
    
    def _handle_class_cancellation(self, course, cancelled_entry):
        """Handle a newly detected class cancellation - sends notifications AND emails"""
        print(f"🔔 Processing class cancellation for course: {course}")
        
        students = get_users_by_course(course)
        students = [s for s in students if s.get('role') == 'student']
        
        print(f"   Found {len(students)} students to notify")
        
        if not students:
            print(f"   ⚠ No students found for course: {course}")
            return
        
        start_time = cancelled_entry.get('start_time', '')
        end_time = cancelled_entry.get('end_time', '')
        day = cancelled_entry.get('day', '')
        
        duration = self._calculate_duration(start_time, end_time)
        print(f"   Class: {day} {start_time}-{end_time} (Duration: {duration} min)")
        
        for student in students:
            student_id = student.get('id')
            student_name = student.get('name', 'Student')
            student_email = student.get('email')
            
            message = f"🚨 Class Cancelled! {day} {start_time}-{end_time}. You now have {duration} minutes of free time."
            notification_result = create_notification(student_id, message)
            
            if notification_result:
                print(f"   ✓ Notification created for {student_name} (ID: {student_id})")
            else:
                print(f"   ✗ Failed to create notification for {student_name} (ID: {student_id})")
            
            recommended_activity = self._auto_assign_activity(student_id, course, duration)
            
            if student_email:
                self._send_cancellation_email(
                    student_email,
                    student_name,
                    day,
                    start_time,
                    end_time,
                    duration,
                    recommended_activity
                )
    
    def _send_cancellation_email(self, email, name, day, start_time, end_time, duration, activity):
        """Send email notification about class cancellation with dynamic URL"""
        import os
        app_url = os.getenv('APP_URL', 'http://localhost:5000').rstrip('/')
        
        subject = f"🚨 Gap2Growth: Class Cancelled - {day} {start_time}"
        
        activity_section = ""
        if activity:
            activity_section = f"""
            <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; border-radius: 4px;">
                <h3 style="margin: 0 0 10px 0; color: #059669;">📚 Recommended Activity</h3>
                <p style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">{activity.get('title', 'Activity')}</p>
                <p style="margin: 0; color: #666;">
                    <strong>Duration:</strong> {activity.get('duration_minutes', 30)} minutes |
                    <strong>Category:</strong> {activity.get('category', 'Learning')}
                </p>
            </div>
            """
        
        body = f"Your class on {day} from {start_time} to {end_time} has been cancelled. You now have {duration} minutes of free time!"
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; padding: 20px; margin: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .content {{ padding: 30px; }}
        .alert-box {{ background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .alert-box h2 {{ margin: 0 0 10px 0; color: #dc2626; }}
        .time-info {{ display: flex; justify-content: space-between; background: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .time-block {{ text-align: center; }}
        .time-block .label {{ font-size: 12px; color: #64748b; text-transform: uppercase; }}
        .time-block .value {{ font-size: 24px; font-weight: 700; color: #1e293b; }}
        .free-time {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
        .free-time h3 {{ margin: 0 0 5px 0; font-size: 14px; text-transform: uppercase; opacity: 0.9; }}
        .free-time .big {{ font-size: 48px; font-weight: 700; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 25px; margin-top: 20px; font-weight: 600; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Class Cancelled</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{name}</strong>,</p>
            
            <div class="alert-box">
                <h2>Your class has been cancelled</h2>
                <p>The scheduled class has been cancelled by your teacher.</p>
            </div>
            
            <div class="time-info">
                <div class="time-block">
                    <div class="label">Day</div>
                    <div class="value">{day}</div>
                </div>
                <div class="time-block">
                    <div class="label">Original Time</div>
                    <div class="value">{start_time} - {end_time}</div>
                </div>
            </div>
            
            <div class="free-time">
                <h3>You Now Have</h3>
                <div class="big">{duration}</div>
                <div>minutes of free time!</div>
            </div>
            
            {activity_section}
            
            <p>Don't let this time go to waste! Use Gap2Growth to find productive activities that fit your schedule.</p>
            
            <center>
                <a href="{app_url}/student/recommendations?duration={duration}" class="button">
                    Find Activities Now
                </a>
            </center>
        </div>
        <div class="footer">
            <p>Gap2Growth - Transforming downtime into growth opportunities</p>
        </div>
    </div>
</body>
</html>
        """
        
        try:
            send_email(email, subject, body, html_body)
            print(f"📧 Cancellation email sent to {email}")
        except Exception as e:
            print(f"Email send error: {e}")
    
    def _detect_current_free_time(self):
        """Detect if current time falls within a free slot"""
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime('%A')
        
        students = get_users_by_role('student')
        
        for student in students:
            course = student.get('course')
            if not course:
                continue
            
            student_id = student.get('id')
            session_key = f"{student_id}_{current_day}"
            
            if session_key in self.active_sessions:
                continue
            
            free_slot = self._get_current_free_slot(course, current_day, current_time)
            
            if free_slot:
                self.active_sessions[session_key] = {
                    'start': free_slot['start_time'],
                    'end': free_slot['end_time'],
                    'notified': True
                }
                
                message = f"⏰ Free time now: {free_slot['duration_minutes']} minutes until {free_slot['end_time']}. Recommended activities available!"
                create_notification(student_id, message)
                
                self._auto_assign_activity(student_id, course, free_slot['duration_minutes'])
    
    def _get_current_free_slot(self, course, day, current_time):
        """Check if current time is within a free slot"""
        timetable = get_timetable_by_course(course)
        
        if not timetable:
            return None
        
        day_entries = [
            e for e in timetable 
            if e.get('day', '').lower() == day.lower() 
            and e.get('status') == 'scheduled'
        ]
        
        day_entries.sort(key=lambda x: self._parse_time(x.get('start_time', '00:00')))
        
        for i in range(len(day_entries) - 1):
            current_end = self._parse_time(day_entries[i].get('end_time'))
            next_start = self._parse_time(day_entries[i + 1].get('start_time'))
            
            if current_end and next_start and current_end <= current_time < next_start:
                duration = self._calculate_duration(
                    current_end.strftime('%H:%M'),
                    next_start.strftime('%H:%M')
                )
                
                if duration >= 30:
                    return {
                        'start_time': current_end.strftime('%H:%M'),
                        'end_time': next_start.strftime('%H:%M'),
                        'duration_minutes': duration,
                        'reason': 'timetable_gap'
                    }
        
        cancelled = [
            e for e in timetable 
            if e.get('day', '').lower() == day.lower() 
            and e.get('status') == 'cancelled'
        ]
        
        for entry in cancelled:
            start = self._parse_time(entry.get('start_time'))
            end = self._parse_time(entry.get('end_time'))
            
            if start and end and start <= current_time < end:
                duration = self._calculate_duration(
                    entry.get('start_time'),
                    entry.get('end_time')
                )
                return {
                    'start_time': entry.get('start_time'),
                    'end_time': entry.get('end_time'),
                    'duration_minutes': duration,
                    'reason': 'class_cancelled'
                }
        
        return None
    
    def _auto_assign_activity(self, student_id, course, duration_minutes):
        """Automatically suggest and assign a DEPARTMENT-SPECIFIC activity"""
        from app.utils.database import get_activities_by_course
        
        activities = get_activities_by_course(course) if course else get_all_activities()
        
        suitable = [
            a for a in activities 
            if a.get('duration_minutes', 0) <= duration_minutes
        ]
        
        if not suitable:
            return None
        
        student_logs = get_activity_logs_by_student(student_id)
        completed_ids = {log.get('activity_id') for log in student_logs if log.get('status') == 'completed'}
        
        scored = []
        for activity in suitable:
            score = 0
            
            if activity.get('course') == course:
                score += 50
            elif not activity.get('course') or activity.get('course') == 'General':
                score += 20
            
            if activity.get('id') not in completed_ids:
                score += 30
            
            efficiency = activity.get('duration_minutes', 0) / duration_minutes
            score += int(efficiency * 25)
            
            if activity.get('category') == 'Learning':
                score += 15
            elif activity.get('category') == 'Skill':
                score += 10
            
            scored.append({'activity': activity, 'score': score})
        
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        if scored:
            best = scored[0]['activity']
            
            try:
                log = create_activity_log(student_id, best.get('id'), 'suggested')
                print(f"✓ Auto-assigned activity '{best.get('title')}' to student {student_id}")
            except Exception as e:
                print(f"Auto-assign log error: {e}")
            
            message = f"🎯 Auto-Suggested: {best.get('title')} ({best.get('duration_minutes')} min) - Perfect for your free time!"
            create_notification(student_id, message)
            
            return best
        
        return None
    
    def _parse_time(self, time_str):
        """Parse time string to time object"""
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
    
    def _calculate_duration(self, start_str, end_str):
        """Calculate duration in minutes between two time strings"""
        start = self._parse_time(start_str)
        end = self._parse_time(end_str)
        
        if not start or not end:
            return 0
        
        today = datetime.today().date()
        start_dt = datetime.combine(today, start)
        end_dt = datetime.combine(today, end)
        
        delta = end_dt - start_dt
        return int(delta.total_seconds() / 60)


detector = RealTimeDetector()


def start_realtime_detection():
    """Start the real-time detection service"""
    detector.start_detection()


def stop_realtime_detection():
    """Stop the real-time detection service"""
    detector.stop_detection()


def trigger_class_cancellation(entry_id, course):
    """Manually trigger class cancellation handling with logging"""
    from app.utils.database import get_timetable_by_course
    
    print(f"\n{'='*50}")
    print(f"🚨 CLASS CANCELLATION TRIGGERED")
    print(f"   Entry ID: {entry_id}")
    print(f"   Course: {course}")
    print(f"{'='*50}")
    
    if not course:
        print("   ⚠ ERROR: No course provided!")
        return False
    
    timetable = get_timetable_by_course(course)
    print(f"   Timetable entries found: {len(timetable)}")
    
    entry = next((e for e in timetable if str(e.get('id')) == str(entry_id)), None)
    
    if entry:
        print(f"   ✓ Found entry: {entry.get('day')} {entry.get('start_time')}-{entry.get('end_time')}")
        detector._handle_class_cancellation(course, entry)
        print(f"{'='*50}\n")
        return True
    else:
        print(f"   ✗ Entry not found with ID: {entry_id}")
        print(f"   Available IDs: {[e.get('id') for e in timetable[:5]]}...")
        print(f"{'='*50}\n")
    return False


def get_realtime_status():
    """Get current real-time detection status"""
    return {
        'running': detector.detection_running,
        'active_sessions': len(detector.active_sessions),
        'monitored_courses': len(detector.last_timetable_state)
    }


def get_current_free_time_for_student(student_id, course):
    """Get current free time slot for a specific student"""
    now = datetime.now()
    current_time = now.time()
    current_day = now.strftime('%A')
    
    return detector._get_current_free_slot(course, current_day, current_time)


def get_recommended_activity_for_student(student_id, course, duration):
    """Get recommended activity for a student based on available time"""
    return detector._auto_assign_activity(student_id, course, duration)


def send_activity_reminder_email(student_id, activity, free_slot):
    """Send email reminding student to do activity during free time"""
    from app.utils.database import get_user_by_id
    
    student = get_user_by_id(student_id)
    if not student or not student.get('email'):
        return False
    
    email = student.get('email')
    name = student.get('name', 'Student')
    
    subject = f"⏰ Gap2Growth: {free_slot.get('duration_minutes')} minutes free - Try {activity.get('title')}"
    
    body = f"You have {free_slot.get('duration_minutes')} minutes of free time from {free_slot.get('start_time')} to {free_slot.get('end_time')}. We recommend: {activity.get('title')}"
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .activity-card {{ background: #f8fafc; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .button {{ display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ Free Time Alert!</h1>
            <p style="margin: 0; opacity: 0.9;">You have {free_slot.get('duration_minutes')} minutes available</p>
        </div>
        <div class="content">
            <p>Hello <strong>{name}</strong>,</p>
            <p>You have free time from <strong>{free_slot.get('start_time')}</strong> to <strong>{free_slot.get('end_time')}</strong>.</p>
            
            <div class="activity-card">
                <h3 style="margin: 0 0 10px 0;">📚 Recommended Activity</h3>
                <h2 style="margin: 0 0 10px 0; color: #1e293b;">{activity.get('title')}</h2>
                <p style="margin: 0; color: #64748b;">
                    ⏱️ {activity.get('duration_minutes')} minutes | 
                    📂 {activity.get('category')}
                </p>
            </div>
            
            <center>
                <a href="http://localhost:5000/student/activity/{activity.get('id')}" class="button">Start Activity</a>
            </center>
        </div>
        <div class="footer">
            <p>Gap2Growth - Transforming downtime into growth opportunities</p>
        </div>
    </div>
</body>
</html>
    """
    
    try:
        send_email(email, subject, body, html_body)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
