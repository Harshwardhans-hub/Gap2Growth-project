"""
Role-Based Access Control Decorators
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify


def login_required(f):
    """Decorator to require user login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        user_role = session['user'].get('role', '')
        if user_role != 'admin':
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Admin access required'}), 403
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    """Decorator to require teacher role for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        user_role = session['user'].get('role', '')
        if user_role not in ['teacher', 'admin']:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Teacher access required'}), 403
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator to require student role for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        user_role = session['user'].get('role', '')
        if user_role not in ['student', 'teacher', 'admin']:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Student access required'}), 403
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def teacher_or_admin_required(f):
    """Decorator to require teacher or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        user_role = session['user'].get('role', '')
        if user_role not in ['teacher', 'admin']:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Teacher or Admin access required'}), 403
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get the currently logged in user from session"""
    return session.get('user', None)


def get_current_user_id():
    """Get the current user's database ID"""
    user = get_current_user()
    return user.get('id') if user else None


def get_current_user_role():
    """Get the current user's role"""
    user = get_current_user()
    return user.get('role') if user else None


def get_current_user_course():
    """Get the current user's course"""
    user = get_current_user()
    return user.get('course') if user else None
