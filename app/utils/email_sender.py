"""
Email Utility Module
Handles all email communications with dynamic URL support
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os


def get_app_url():
    """Get the application URL from environment or default to localhost"""
    return os.getenv('APP_URL', 'http://localhost:5000').rstrip('/')


def send_email(to_email, subject, body, html_body=None, attachment=None, attachment_name=None):
    """Send an email using Gmail SMTP"""
    gmail_email = os.getenv('GMAIL_EMAIL')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    if not gmail_email or not gmail_password:
        print("Email credentials not configured - skipping email")
        return False
    
    if not to_email:
        print("No recipient email provided")
        return False
    
    try:
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"Gap2Growth <{gmail_email}>"
        message['To'] = to_email
        
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)
        
        if html_body:
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)
        
        if attachment and attachment_name:
            attachment_part = MIMEApplication(attachment, Name=attachment_name)
            attachment_part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
            message.attach(attachment_part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_email, gmail_password)
            server.sendmail(gmail_email, to_email, message.as_string())
        
        print(f"✓ Email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("✗ SMTP authentication failed. Check your Gmail App Password.")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error sending email: {str(e)}")
        return False


def send_notification_email(to_email, student_name, notification_type, details):
    """Send a formatted notification email to a student"""
    app_url = get_app_url()
    
    subject_templates = {
        'free_time': '⏰ Gap2Growth: Free Time Detected!',
        'activity': '📚 Gap2Growth: New Activity Recommendation',
        'collaboration': '👥 Gap2Growth: Collaboration Invitation',
        'reminder': '🔔 Gap2Growth: Activity Reminder',
        'class_cancelled': '📢 Gap2Growth: Class Cancelled - Free Time Available!',
        'weekly_report': '📊 Gap2Growth: Your Weekly Progress Report'
    }
    
    subject = subject_templates.get(notification_type, '🎯 Gap2Growth Notification')
    
    # Ensure the link uses the correct base URL
    link = details.get('link', f'{app_url}/student/dashboard')
    if link.startswith('/'):
        link = f'{app_url}{link}'
    elif not link.startswith('http'):
        link = f'{app_url}/{link}'
    
    body = f"""
Hello {student_name},

{details.get('message', 'You have a new notification from Gap2Growth.')}

{details.get('action', '')}

Visit your dashboard: {link}

Best regards,
Gap2Growth Team

---
This is an automated message from Gap2Growth - Adaptive Student Time Utilisation Platform
    """
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; padding: 20px; margin: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .content p {{ color: #374151; line-height: 1.7; margin: 0 0 16px 0; }}
        .greeting {{ font-size: 18px; }}
        .highlight {{ background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-left: 4px solid #2563eb; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .highlight p {{ margin: 0; color: #1e40af; font-weight: 500; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white !important; padding: 14px 32px; text-decoration: none; border-radius: 8px; margin-top: 20px; font-weight: 600; }}
        .button:hover {{ background: #1d4ed8; }}
        .footer {{ background: #f8fafc; padding: 24px; text-align: center; color: #64748b; font-size: 13px; border-top: 1px solid #e2e8f0; }}
        .footer p {{ margin: 4px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Gap2Growth</h1>
            <p>Adaptive Student Time Utilisation Platform</p>
        </div>
        <div class="content">
            <p class="greeting">Hello <strong>{student_name}</strong>,</p>
            <div class="highlight">
                <p>{details.get('message', 'You have a new notification.')}</p>
            </div>
            <p>{details.get('action', 'Check your dashboard for more details.')}</p>
            <a href="{link}" class="button">View Details</a>
        </div>
        <div class="footer">
            <p><strong>Gap2Growth</strong></p>
            <p>Transforming downtime into growth opportunities</p>
            <p style="margin-top: 12px; font-size: 11px;">© 2024 Gap2Growth - All rights reserved</p>
        </div>
    </div>
</body>
</html>
    """
    
    return send_email(to_email, subject, body, html_body)


def send_class_cancelled_email(to_email, student_name, class_details):
    """Send a specific email when a class is cancelled"""
    app_url = get_app_url()
    
    details = {
        'message': f"Your class on <strong>{class_details.get('day', 'today')}</strong> from <strong>{class_details.get('start_time', '')} - {class_details.get('end_time', '')}</strong> has been cancelled.",
        'action': f"This gives you approximately {class_details.get('duration', 60)} minutes of free time. Why not use it productively with a recommended activity?",
        'link': f'{app_url}/student/recommendations?duration={class_details.get("duration", 60)}'
    }
    
    return send_notification_email(to_email, student_name, 'class_cancelled', details)


def send_free_time_alert_email(to_email, student_name, free_time_details):
    """Send an alert when free time is detected"""
    app_url = get_app_url()
    
    details = {
        'message': f"You have <strong>{free_time_details.get('duration', 30)} minutes</strong> of free time coming up from {free_time_details.get('start_time', '')} to {free_time_details.get('end_time', '')}!",
        'action': "Check out our personalized activity recommendations to make the most of your downtime.",
        'link': f'{app_url}/student/recommendations?duration={free_time_details.get("duration", 30)}'
    }
    
    return send_notification_email(to_email, student_name, 'free_time', details)


def send_report_email(to_email, recipient_name, report_type, pdf_content):
    """Send a PDF report via email"""
    app_url = get_app_url()
    subject = f"📊 Gap2Growth: Your {report_type.title()} Report"
    
    body = f"""
Hello {recipient_name},

Please find attached your {report_type} engagement report from Gap2Growth.

This report includes:
• Total productive time utilized
• Most frequently completed activities  
• Engagement summary and trends
• Activity completion statistics

Keep up the great work on your learning journey!

View your dashboard: {app_url}/student/dashboard

Best regards,
Gap2Growth Team
    """
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .content ul {{ color: #374151; line-height: 2; }}
        .button {{ display: inline-block; background: #2563eb; color: white !important; padding: 12px 28px; text-decoration: none; border-radius: 8px; margin-top: 16px; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #64748b; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Your {report_type.title()} Report</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{recipient_name}</strong>,</p>
            <p>Please find attached your {report_type} engagement report. This report includes:</p>
            <ul>
                <li>Total productive time utilized</li>
                <li>Most frequently completed activities</li>
                <li>Engagement summary and trends</li>
                <li>Activity completion statistics</li>
            </ul>
            <p>Keep up the great work on your learning journey!</p>
            <a href="{app_url}/student/history" class="button">View Activity History</a>
        </div>
        <div class="footer">
            <p>© 2024 Gap2Growth - Transforming downtime into growth</p>
        </div>
    </div>
</body>
</html>
    """
    
    filename = f"gap2growth_{report_type}_report.pdf"
    
    return send_email(to_email, subject, body, html_body, attachment=pdf_content, attachment_name=filename)


def send_daily_reminder_email(to_email, student_name, stats):
    """Send a daily reminder with activity stats"""
    app_url = get_app_url()
    
    details = {
        'message': f"You've completed <strong>{stats.get('completed_today', 0)} activities</strong> today! Your current streak is <strong>{stats.get('streak', 0)} days</strong>.",
        'action': f"Total productive time this week: {stats.get('weekly_hours', 0)} hours. Keep the momentum going!",
        'link': f'{app_url}/student/dashboard'
    }
    
    return send_notification_email(to_email, student_name, 'reminder', details)
