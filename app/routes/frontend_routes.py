"""
============================================
Gap2Growth - Frontend Routes
============================================
This file contains routes that serve the HTML
pages (frontend) of the application.

These routes use Flask's render_template function
to serve HTML files from the templates folder.
============================================
"""

from flask import Blueprint, render_template, send_from_directory
import os

# Create a Blueprint for frontend routes
# A Blueprint is a way to organize related routes together
frontend_bp = Blueprint('frontend', __name__)


# ========== STATIC FILE SERVING ==========
# These routes serve static files (CSS, JS) during development
# In production, a web server like Nginx handles this

@frontend_bp.route('/static/<path:filename>')
def serve_static(filename):
    """
    Serve static files (CSS, JS, images)
    
    Parameters:
        filename: The path to the static file
        
    Returns:
        The requested static file
    """
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_folder, filename)


# ========== PAGE ROUTES ==========
# These routes render HTML templates

@frontend_bp.route('/')
def index():
    """
    Home page route
    Redirects to the login page for now
    
    Returns:
        Rendered login.html template
    """
    return render_template('login.html')


@frontend_bp.route('/login')
@frontend_bp.route('/login.html')
def login():
    """
    Login page route
    
    This page allows users to:
    - Select their role (Student/Teacher/Admin)
    - Login with email and password
    - Login with Google OAuth
    
    Returns:
        Rendered login.html template
    """
    return render_template('login.html')


@frontend_bp.route('/student')
@frontend_bp.route('/student_dashboard.html')
def student_dashboard():
    """
    Student Dashboard page route
    
    This page shows:
    - Today's schedule with free slots highlighted
    - Recommended activities
    - Progress tracking
    - Recent notifications
    
    Returns:
        Rendered student_dashboard.html template
    """
    return render_template('student_dashboard.html')


@frontend_bp.route('/teacher')
@frontend_bp.route('/teacher_dashboard.html')
def teacher_dashboard():
    """
    Teacher Dashboard page route
    
    This page shows:
    - Today's teaching schedule
    - Class management options
    - Student engagement metrics
    - Activity management
    
    Returns:
        Rendered teacher_dashboard.html template
    """
    return render_template('teacher_dashboard.html')


@frontend_bp.route('/admin')
@frontend_bp.route('/admin_dashboard.html')
def admin_dashboard():
    """
    Admin Dashboard page route
    
    This page shows:
    - System-wide statistics
    - Pending user approvals
    - Department management
    - System activity log
    
    Returns:
        Rendered admin_dashboard.html template
    """
    return render_template('admin_dashboard.html')
