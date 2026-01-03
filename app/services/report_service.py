"""
Report Service
"""

from datetime import datetime, timedelta
from jinja2 import Template
from app.utils.database import (
    get_all_activity_logs,
    get_activity_logs_by_student,
    get_all_users,
    get_users_by_role,
    get_all_activities
)

WEASYPRINT_AVAILABLE = False
HTML = None
CSS = None

try:
    import sys
    print(f"  Python: {sys.executable}")
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
    print("✓ WeasyPrint loaded - PDF generation enabled")
except ImportError as e:
    print(f"⚠ WeasyPrint not installed - PDF generation disabled (HTML fallback)")
    print(f"  ImportError: {e}")
except OSError as e:
    print(f"⚠ WeasyPrint GTK libraries not found - PDF generation disabled (HTML fallback)")
    print(f"  OSError: {e}")
except Exception as e:
    print(f"⚠ WeasyPrint initialization failed - PDF generation disabled (HTML fallback)")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error: {e}")


def get_engagement_stats(student_id=None, days=7):
    """Get engagement statistics for reporting"""
    if student_id:
        logs = get_activity_logs_by_student(student_id)
    else:
        logs = get_all_activity_logs()
    
    cutoff = datetime.now() - timedelta(days=days)
    
    completed = [l for l in logs if l.get('status') == 'completed']
    total_minutes = sum(
        l.get('activities', {}).get('duration_minutes', 0) 
        for l in completed
    )
    
    activity_counts = {}
    for log in completed:
        title = log.get('activities', {}).get('title', 'Unknown')
        activity_counts[title] = activity_counts.get(title, 0) + 1
    
    top_activities = sorted(
        activity_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:5]
    
    return {
        'total_completed': len(completed),
        'total_minutes': total_minutes,
        'total_hours': round(total_minutes / 60, 1),
        'top_activities': top_activities,
        'period_days': days
    }


REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
        .header { text-align: center; border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { color: #667eea; margin: 0; }
        .header p { color: #888; margin: 5px 0; }
        .stats-grid { display: flex; justify-content: space-around; margin: 30px 0; }
        .stat-box { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; min-width: 120px; }
        .stat-value { font-size: 32px; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; font-size: 14px; }
        .section { margin: 30px 0; }
        .section h2 { color: #333; border-left: 4px solid #667eea; padding-left: 15px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #667eea; color: white; }
        tr:nth-child(even) { background: #f8f9fa; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #888; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Gap2Growth Report</h1>
        <p>{{ report_type }} Engagement Summary</p>
        <p>Generated: {{ generated_at }}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-value">{{ stats.total_completed }}</div>
            <div class="stat-label">Activities Completed</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{{ stats.total_hours }}h</div>
            <div class="stat-label">Productive Time</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{{ stats.period_days }}</div>
            <div class="stat-label">Days Analyzed</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Top Activities</h2>
        <table>
            <tr><th>Activity</th><th>Completions</th></tr>
            {% for activity, count in stats.top_activities %}
            <tr><td>{{ activity }}</td><td>{{ count }}</td></tr>
            {% endfor %}
        </table>
    </div>
    
    <div class="footer">
        <p>Gap2Growth - Adaptive Student Time Utilisation Platform</p>
    </div>
</body>
</html>
"""


def generate_report_html(report_type='Weekly', student_id=None):
    """Generate report as HTML"""
    days = 7 if report_type == 'Weekly' else 30
    stats = get_engagement_stats(student_id, days)
    
    template = Template(REPORT_TEMPLATE)
    html = template.render(
        report_type=report_type,
        stats=stats,
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M')
    )
    return html


def generate_report_pdf(report_type='Weekly', student_id=None):
    """Generate PDF report"""
    html_content = generate_report_html(report_type, student_id)
    
    if not WEASYPRINT_AVAILABLE:
        return html_content.encode('utf-8'), 'html'
    
    try:
        pdf = HTML(string=html_content).write_pdf()
        return pdf, 'pdf'
    except Exception as e:
        print(f"PDF generation error: {e}")
        return html_content.encode('utf-8'), 'html'


def generate_weekly_reports():
    """Generate weekly reports for all students"""
    students = get_users_by_role('student')
    for student in students:
        try:
            generate_report_pdf('Weekly', student.get('id'))
        except Exception as e:
            print(f"Report generation failed for {student.get('id')}: {e}")
