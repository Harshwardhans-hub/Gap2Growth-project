"""
Notification Service
"""

from app.utils.database import (
    create_notification,
    get_notifications_by_user,
    get_user_by_id
)
from app.utils.email_sender import send_notification_email, send_report_email, send_email
import os


def get_user_notifications(user_id, limit=20):
    """Get notifications for a specific user"""
    notifications = get_notifications_by_user(user_id)
    return notifications[:limit] if notifications else []


def get_unread_count(user_id):
    """Get count of unread notifications for a user"""
    notifications = get_notifications_by_user(user_id, unread_only=True)
    return len(notifications)


def notify_free_time(user_id, slot_info, send_email_notification=True):
    """Notify user about detected free time"""
    message = f"🕐 Free time detected: {slot_info['duration_minutes']} minutes from {slot_info['start_time']} to {slot_info['end_time']} on {slot_info.get('day', 'today')}"
    
    create_notification(user_id, message)
    
    if send_email_notification and os.getenv('GMAIL_EMAIL'):
        user = get_user_by_id(user_id)
        if user and user.get('email'):
            send_notification_email(
                to_email=user['email'],
                student_name=user.get('name', 'Student'),
                notification_type='free_time',
                details={
                    'message': message,
                    'action': f"You have {slot_info['duration_minutes']} minutes of free time! Check out our recommended activities.",
                    'link': 'http://localhost:5000/student/recommendations'
                }
            )


def notify_class_cancellation(user_id, class_info, recommended_activity=None, send_email_notification=True):
    """Notify user about class cancellation with recommended activity"""
    day = class_info.get('day', 'Today')
    start_time = class_info.get('start_time', '')
    end_time = class_info.get('end_time', '')
    duration = class_info.get('duration_minutes', 0)
    
    message = f"🚨 Class Cancelled! {day} {start_time}-{end_time}. You have {duration} minutes free."
    create_notification(user_id, message)
    
    if recommended_activity:
        activity_msg = f"📚 Suggested: {recommended_activity.get('title')} ({recommended_activity.get('duration_minutes')} min)"
        create_notification(user_id, activity_msg)
    
    if send_email_notification and os.getenv('GMAIL_EMAIL'):
        user = get_user_by_id(user_id)
        if user and user.get('email'):
            _send_cancellation_email_notification(
                user['email'],
                user.get('name', 'Student'),
                class_info,
                recommended_activity
            )


def _send_cancellation_email_notification(email, name, class_info, activity=None):
    """Send detailed cancellation email"""
    day = class_info.get('day', 'Today')
    start_time = class_info.get('start_time', '')
    end_time = class_info.get('end_time', '')
    duration = class_info.get('duration_minutes', 0)
    
    subject = f"🚨 Gap2Growth: Class Cancelled - {day} {start_time}"
    
    activity_html = ""
    if activity:
        activity_html = f"""
        <div style="background: #ecfdf5; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; border-radius: 8px;">
            <h3 style="margin: 0 0 12px 0; color: #059669;">📚 Recommended Activity for Your Free Time</h3>
            <h4 style="margin: 0 0 8px 0; font-size: 20px; color: #1e293b;">{activity.get('title', 'Activity')}</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0;"><strong>Duration:</strong> {activity.get('duration_minutes', 30)} minutes</td>
                    <td style="padding: 8px 0;"><strong>Category:</strong> {activity.get('category', 'Learning')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><strong>Difficulty:</strong> {activity.get('difficulty', 'Medium')}</td>
                    <td style="padding: 8px 0;"><strong>Mode:</strong> {activity.get('mode', 'Solo')}</td>
                </tr>
            </table>
            <a href="http://localhost:5000/student/activity/{activity.get('id')}" 
               style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin-top: 12px; font-weight: 600;">
               Start This Activity
            </a>
        </div>
        """
    
    body = f"Your class on {day} from {start_time} to {end_time} has been cancelled. You now have {duration} minutes of free time."
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9; padding: 20px; margin: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 20px 0; }}
        .info-box {{ background: #f8fafc; border-radius: 12px; padding: 20px; text-align: center; }}
        .info-box .label {{ font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }}
        .info-box .value {{ font-size: 24px; font-weight: 700; color: #1e293b; margin-top: 8px; }}
        .free-time-banner {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; border-radius: 12px; text-align: center; margin: 20px 0; }}
        .free-time-banner .big {{ font-size: 56px; font-weight: 700; line-height: 1; }}
        .free-time-banner .label {{ margin-top: 8px; opacity: 0.9; }}
        .cta-button {{ display: inline-block; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 16px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; }}
        .footer {{ background: #f8fafc; padding: 24px; text-align: center; color: #64748b; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Class Cancelled</h1>
            <p>Your scheduled class has been cancelled by the teacher</p>
        </div>
        <div class="content">
            <p style="font-size: 16px;">Hello <strong>{name}</strong>,</p>
            
            <div class="info-grid">
                <div class="info-box">
                    <div class="label">Day</div>
                    <div class="value">{day}</div>
                </div>
                <div class="info-box">
                    <div class="label">Time Slot</div>
                    <div class="value">{start_time} - {end_time}</div>
                </div>
            </div>
            
            <div class="free-time-banner">
                <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.9;">You Now Have</div>
                <div class="big">{duration}</div>
                <div class="label">minutes of productive time available</div>
            </div>
            
            {activity_html}
            
            <p style="color: #475569; line-height: 1.6;">Don't let this unexpected free time go to waste! Use Gap2Growth to find activities that match your available time and boost your productivity.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5000/student/recommendations?duration={duration}" class="cta-button">
                    Browse All Activities
                </a>
            </div>
        </div>
        <div class="footer">
            <p style="margin: 0;">Gap2Growth - Adaptive Student Time Utilisation Platform</p>
            <p style="margin: 8px 0 0 0;">Transforming downtime into growth opportunities 🚀</p>
        </div>
    </div>
</body>
</html>
    """
    
    try:
        send_email(email, subject, body, html_body)
        print(f"📧 Cancellation email sent to {email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def notify_activity_recommendation(user_id, activity_info, send_email_notification=False):
    """Notify user about a recommended activity"""
    message = f"📚 Recommended: {activity_info.get('title', 'New Activity')} ({activity_info.get('duration_minutes', 30)} min)"
    
    create_notification(user_id, message)
    
    if send_email_notification and os.getenv('GMAIL_EMAIL'):
        user = get_user_by_id(user_id)
        if user and user.get('email'):
            send_notification_email(
                to_email=user['email'],
                student_name=user.get('name', 'Student'),
                notification_type='activity',
                details={
                    'message': f"We recommend: {activity_info.get('title')}",
                    'action': f"Category: {activity_info.get('category')} | Duration: {activity_info.get('duration_minutes')} minutes | Difficulty: {activity_info.get('difficulty')}",
                    'link': f"http://localhost:5000/student/activity/{activity_info.get('id')}"
                }
            )


def notify_collaboration_invite(user_id, inviter_name, activity_title, send_email_notification=True):
    """Notify user about a collaboration invitation"""
    message = f"👥 {inviter_name} invited you to collaborate on: {activity_title}"
    
    create_notification(user_id, message)
    
    if send_email_notification and os.getenv('GMAIL_EMAIL'):
        user = get_user_by_id(user_id)
        if user and user.get('email'):
            send_notification_email(
                to_email=user['email'],
                student_name=user.get('name', 'Student'),
                notification_type='collaboration',
                details={
                    'message': message,
                    'action': 'Join your classmate for a collaborative learning session!',
                    'link': 'http://localhost:5000/student/recommendations?mode=Group'
                }
            )


def notify_activity_completed(user_id, activity_title, duration_minutes):
    """Notify user about completed activity"""
    message = f"✅ Great job completing: {activity_title}! You spent {duration_minutes} productive minutes."
    create_notification(user_id, message)


def notify_daily_reminder(user_id, message_text=None):
    """Send a daily reminder to the user"""
    message = message_text or "🔔 Don't forget to check for free time slots and available activities today!"
    create_notification(user_id, message)


def notify_weekly_report(user_id, stats):
    """Notify user about their weekly report"""
    message = f"📊 Your weekly report is ready! You completed {stats.get('total_completed', 0)} activities for {stats.get('total_hours', 0)} hours of productive time."
    create_notification(user_id, message)


def send_batch_notifications(user_ids, message, notification_type='general'):
    """Send the same notification to multiple users"""
    for user_id in user_ids:
        create_notification(user_id, message)


def send_urgent_email_alert(user_id, subject, message, action_url=None):
    """Send an urgent email alert to a user"""
    user = get_user_by_id(user_id)
    if not user or not user.get('email'):
        return False
    
    if not os.getenv('GMAIL_EMAIL'):
        return False
    
    return send_notification_email(
        to_email=user['email'],
        student_name=user.get('name', 'Student'),
        notification_type='urgent',
        details={
            'message': message,
            'action': 'Take action now!',
            'link': action_url or 'http://localhost:5000/student/dashboard'
        }
    )
