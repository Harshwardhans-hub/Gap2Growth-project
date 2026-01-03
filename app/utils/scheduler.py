"""
Scheduler Utility Module
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from datetime import datetime
import os


scheduler = None


def init_scheduler(app):
    """Initialize the APScheduler with the Flask app"""
    global scheduler
    
    if app.config.get('SCHEDULER_ENABLED', True):
        scheduler = BackgroundScheduler()
        scheduler.start()
        
        atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler else None)
        setup_default_jobs()
        
        print("✓ Background scheduler started successfully")
    else:
        print("⚠ Scheduler disabled")


def setup_default_jobs():
    """Setup default scheduled jobs"""
    global scheduler
    
    if not scheduler:
        return
    
    scheduler.add_job(
        func=run_realtime_detection_cycle,
        trigger=IntervalTrigger(minutes=1),
        id='realtime_detection',
        name='Real-time Free Time Detection',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=run_downtime_scan,
        trigger=IntervalTrigger(minutes=15),
        id='downtime_scan',
        name='Downtime Detection Scan',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=run_activity_completion_check,
        trigger=IntervalTrigger(minutes=1),
        id='activity_check',
        name='Activity Completion Check',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=send_upcoming_free_time_alerts,
        trigger=IntervalTrigger(minutes=5),
        id='upcoming_alerts',
        name='Upcoming Free Time Alerts',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=send_daily_reminders,
        trigger=CronTrigger(hour=8, minute=0),
        id='daily_reminder',
        name='Daily Reminder',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=generate_weekly_reports,
        trigger=CronTrigger(day_of_week='sun', hour=18, minute=0),
        id='weekly_report',
        name='Weekly Report Generation',
        replace_existing=True
    )
    
    print(f"  → Scheduled {len(scheduler.get_jobs())} background jobs")


def run_realtime_detection_cycle():
    """Run real-time detection for current free time slots"""
    try:
        from app.services.downtime_service import get_current_free_slot
        from app.utils.database import get_users_by_role, create_notification
        from app.services.recommendation_service import get_recommended_activities
        
        students = get_users_by_role('student')
        
        for student in students:
            course = student.get('course')
            if not course:
                continue
            
            current_slot = get_current_free_slot(course)
            
            if current_slot and current_slot.get('remaining_minutes', 0) > 5:
                recommendations = get_recommended_activities(
                    course, 
                    current_slot.get('remaining_minutes', 30)
                )[:2]
                
    except Exception as e:
        print(f"[{datetime.now()}] Realtime detection error: {e}")


def send_upcoming_free_time_alerts():
    """Send alerts (including emails) for free time slots starting soon"""
    try:
        from app.services.downtime_service import get_upcoming_free_slots
        from app.utils.database import get_users_by_role, create_notification
        from app.services.recommendation_service import get_recommended_activities
        from app.utils.email_sender import send_email
        
        students = get_users_by_role('student')
        email_enabled = bool(os.getenv('GMAIL_EMAIL'))
        
        for student in students:
            course = student.get('course')
            if not course:
                continue
            
            upcoming = get_upcoming_free_slots(course, 1)
            
            if upcoming:
                slot = upcoming[0]
                starts_in = slot.get('starts_in_minutes', 0)
                
                if 5 <= starts_in <= 10:
                    duration = slot.get('duration_minutes', 30)
                    message = f"⏰ Free time in {starts_in} min! {duration} minutes available from {slot.get('start_time')}"
                    create_notification(student.get('id'), message)
                    
                    if email_enabled and student.get('email'):
                        recommendations = get_recommended_activities(course, duration)[:1]
                        activity = recommendations[0] if recommendations else None
                        
                        _send_upcoming_free_time_email(
                            student.get('email'),
                            student.get('name', 'Student'),
                            slot,
                            activity
                        )
                    
    except Exception as e:
        print(f"[{datetime.now()}] Upcoming alert error: {e}")


def _send_upcoming_free_time_email(email, name, slot, activity=None):
    """Send email about upcoming free time"""
    from app.utils.email_sender import send_email
    
    duration = slot.get('duration_minutes', 30)
    starts_in = slot.get('starts_in_minutes', 0)
    start_time = slot.get('start_time', '')
    end_time = slot.get('end_time', '')
    
    subject = f"⏰ Gap2Growth: Free time in {starts_in} minutes!"
    
    activity_section = ""
    if activity:
        activity_section = f"""
        <div style="background: #f0fdf4; padding: 20px; border-radius: 12px; margin: 20px 0;">
            <h3 style="margin: 0 0 12px 0; color: #059669;">📚 Suggested Activity</h3>
            <p style="font-size: 18px; font-weight: 600; margin: 0 0 8px 0;">{activity.get('title')}</p>
            <p style="margin: 0; color: #64748b;">
                {activity.get('duration_minutes')} min • {activity.get('category')} • {activity.get('difficulty')}
            </p>
        </div>
        """
    
    body = f"You have {duration} minutes of free time starting in {starts_in} minutes!"
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f1f5f9; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .time-box {{ background: #fef3c7; border-radius: 12px; padding: 24px; text-align: center; margin: 20px 0; }}
        .time-box .big {{ font-size: 48px; font-weight: 700; color: #92400e; }}
        .button {{ display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #64748b; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ Free Time Alert!</h1>
            <p style="margin: 0; opacity: 0.9;">Get ready - your free time is coming up!</p>
        </div>
        <div class="content">
            <p>Hello <strong>{name}</strong>,</p>
            
            <div class="time-box">
                <div style="font-size: 14px; color: #78716c; text-transform: uppercase;">Starting In</div>
                <div class="big">{starts_in}</div>
                <div style="color: #78716c;">minutes</div>
            </div>
            
            <p style="text-align: center; color: #475569;">
                <strong>{duration} minutes</strong> available from <strong>{start_time}</strong> to <strong>{end_time}</strong>
            </p>
            
            {activity_section}
            
            <div style="text-align: center; margin: 24px 0;">
                <a href="http://localhost:5000/student/recommendations?duration={duration}" class="button">View Recommendations</a>
            </div>
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
        print(f"📧 Upcoming free time email sent to {email}")
    except Exception as e:
        print(f"Email error: {e}")


def run_downtime_scan():
    """Scan all courses for downtime and notify students"""
    print(f"[{datetime.now()}] Running downtime scan...")
    
    try:
        from app.services.downtime_service import detect_all_student_downtime
        results = detect_all_student_downtime()
        print(f"[{datetime.now()}] Downtime scan complete. Found {len(results)} free slots.")
    except Exception as e:
        print(f"[{datetime.now()}] Downtime scan error: {e}")


def send_daily_reminders():
    """Send daily reminders to all students (including email)"""
    print(f"[{datetime.now()}] Sending daily reminders...")
    
    try:
        from app.utils.database import get_users_by_role
        from app.services.notification_service import notify_daily_reminder
        from app.services.downtime_service import detect_all_downtime_for_course
        from app.utils.email_sender import send_email
        
        students = get_users_by_role('student')
        email_enabled = bool(os.getenv('GMAIL_EMAIL'))
        
        for student in students:
            course = student.get('course')
            
            if course:
                slots = detect_all_downtime_for_course(course)
                if slots:
                    total_minutes = sum(s.get('duration_minutes', 0) for s in slots)
                    message = f"📅 Today you have {len(slots)} free time slots totaling {total_minutes} minutes. Make the most of them!"
                else:
                    message = "🔔 Good morning! Check your timetable for today's opportunities."
            else:
                message = "🔔 Don't forget to check for free time slots and available activities today!"
            
            notify_daily_reminder(student.get('id'), message)
            
            if email_enabled and student.get('email'):
                _send_daily_summary_email(
                    student.get('email'),
                    student.get('name', 'Student'),
                    slots if course else [],
                    total_minutes if course and slots else 0
                )
        
        print(f"[{datetime.now()}] Daily reminders sent to {len(students)} students.")
    except Exception as e:
        print(f"[{datetime.now()}] Daily reminder error: {e}")


def _send_daily_summary_email(email, name, slots, total_minutes):
    """Send daily summary email"""
    from app.utils.email_sender import send_email
    from datetime import datetime
    
    today = datetime.now().strftime('%A, %B %d')
    slot_count = len(slots)
    
    subject = f"☀️ Gap2Growth: Your schedule for {today}"
    
    slots_html = ""
    if slots:
        slots_list = ""
        for slot in slots[:5]:
            slots_list += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{slot.get('start_time')} - {slot.get('end_time')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">{slot.get('duration_minutes')} min</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{slot.get('reason', 'gap').replace('_', ' ').title()}</td>
            </tr>
            """
        
        slots_html = f"""
        <h3 style="color: #1e293b; margin: 24px 0 16px 0;">📋 Today's Free Time Slots</h3>
        <table style="width: 100%; border-collapse: collapse; background: #f8fafc; border-radius: 8px; overflow: hidden;">
            <thead>
                <tr style="background: #e2e8f0;">
                    <th style="padding: 12px; text-align: left;">Time</th>
                    <th style="padding: 12px; text-align: left;">Duration</th>
                    <th style="padding: 12px; text-align: left;">Type</th>
                </tr>
            </thead>
            <tbody>
                {slots_list}
            </tbody>
        </table>
        """
    
    body = f"Good morning! You have {slot_count} free time slots today totaling {total_minutes} minutes."
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f1f5f9; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .stats {{ display: flex; gap: 16px; margin: 20px 0; }}
        .stat {{ flex: 1; background: #f8fafc; padding: 20px; border-radius: 12px; text-align: center; }}
        .stat .value {{ font-size: 32px; font-weight: 700; color: #2563eb; }}
        .stat .label {{ color: #64748b; font-size: 13px; }}
        .button {{ display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #64748b; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>☀️ Good Morning!</h1>
            <p style="margin: 0; opacity: 0.9;">{today}</p>
        </div>
        <div class="content">
            <p style="font-size: 16px;">Hello <strong>{name}</strong>,</p>
            <p>Here's your daily productivity summary from Gap2Growth.</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="value">{slot_count}</div>
                    <div class="label">Free Slots Today</div>
                </div>
                <div class="stat">
                    <div class="value">{total_minutes}</div>
                    <div class="label">Total Minutes</div>
                </div>
            </div>
            
            {slots_html}
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5000/student/dashboard" class="button">View Dashboard</a>
            </div>
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
    except Exception as e:
        print(f"Daily email error: {e}")


def generate_weekly_reports():
    """Generate and send weekly reports for all students"""
    print(f"[{datetime.now()}] Generating weekly reports...")
    
    try:
        from app.utils.database import get_users_by_role
        from app.services.report_service import generate_report_pdf, get_engagement_stats
        from app.services.notification_service import notify_weekly_report
        from app.utils.email_sender import send_report_email
        
        students = get_users_by_role('student')
        email_enabled = bool(os.getenv('GMAIL_EMAIL'))
        
        for student in students:
            stats = get_engagement_stats(student.get('id'), days=7)
            notify_weekly_report(student.get('id'), stats)
            
            if email_enabled and student.get('email'):
                pdf_content, file_type = generate_report_pdf('Weekly', student.get('id'))
                if file_type == 'pdf':
                    send_report_email(
                        student['email'],
                        student.get('name', 'Student'),
                        'weekly',
                        pdf_content
                    )
        
        print(f"[{datetime.now()}] Weekly reports generated for {len(students)} students.")
    except Exception as e:
        print(f"[{datetime.now()}] Weekly report error: {e}")


def add_job(func, trigger, job_id, **kwargs):
    """Add a custom job to the scheduler"""
    global scheduler
    
    if scheduler:
        scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        return True
    return False


def remove_job(job_id):
    """Remove a job from the scheduler"""
    global scheduler
    
    if scheduler:
        try:
            scheduler.remove_job(job_id)
            return True
        except Exception:
            return False
    return False


def get_scheduled_jobs():
    """Get list of all scheduled jobs"""
    global scheduler
    
    if scheduler:
        jobs = scheduler.get_jobs()
        return [
            {
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time) if job.next_run_time else None
            }
            for job in jobs
        ]
    return []


def pause_scheduler():
    """Pause all scheduled jobs"""
    global scheduler
    if scheduler:
        scheduler.pause()


def resume_scheduler():
    """Resume all scheduled jobs"""
    global scheduler
    if scheduler:
        scheduler.resume()


def run_activity_completion_check():
    """Check for and complete expired activities"""
    try:
        from app.services.activity_monitor import auto_complete_expired_activities
        auto_complete_expired_activities()
    except Exception as e:
        print(f"[{datetime.now()}] Activity check error: {e}")

def run_job_now(job_id):
    """Immediately run a specific job"""
    global scheduler
    
    if scheduler:
        job = scheduler.get_job(job_id)
        if job:
            job.func()
            return True
    return False
