"""
Admin Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.utils.decorators import admin_required, get_current_user
from app.utils.database import (
    get_all_users, create_user, update_user, delete_user,
    get_all_activities, get_all_activity_logs
)
from app.services.report_service import generate_report_pdf, get_engagement_stats

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    users = get_all_users()
    activities = get_all_activities()
    stats = get_engagement_stats(days=30)
    
    role_counts = {
        'admin': len([u for u in users if u.get('role') == 'admin']),
        'teacher': len([u for u in users if u.get('role') == 'teacher']),
        'student': len([u for u in users if u.get('role') == 'student'])
    }
    
    return render_template('admin/dashboard.html',
        user=get_current_user(),
        users=users,
        activities=activities,
        stats=stats,
        role_counts=role_counts
    )


@admin_bp.route('/users')
@admin_required
def users_list():
    """List all users"""
    all_users = get_all_users()
    users = [u for u in all_users if u.get('role').lower() != 'admin']
    return render_template('admin/users.html', user=get_current_user(), users=users)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user_page():
    """Create a new user"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        course = request.form.get('course') if role != 'admin' else None
        
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('admin/user_form.html', user=get_current_user(), edit_user=None)
        
        if role == 'admin':
            flash('Cannot create admin users.', 'danger')
            return render_template('admin/user_form.html', user=get_current_user(), edit_user=None)
        
        from app.utils.firebase_auth import create_firebase_user
        firebase_user = create_firebase_user(email, password, name)
        
        if firebase_user:
            new_user = create_user(
                firebase_uid=firebase_user['uid'],
                name=name,
                role=role,
                email=email,
                course=course
            )
            
            if new_user:
                flash(f'User {name} created successfully! They can now login with email: {email}', 'success')
                return redirect(url_for('admin.users_list'))
            else:
                flash('User created in Firebase but failed to save to database.', 'warning')
        else:
            flash('Failed to create user. Email may already be registered.', 'danger')
    
    return render_template('admin/user_form.html', user=get_current_user(), edit_user=None)


@admin_bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user_page(user_id):
    """Edit an existing user"""
    from app.utils.database import get_user_by_id
    edit_user = get_user_by_id(user_id)
    
    if not edit_user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users_list'))
    
    # Protect Admin Account
    if edit_user.get('role', '').lower() == 'admin' or edit_user.get('email') == 'admin@gmail.com':
        flash('System administrator details cannot be modified.', 'warning')
        return redirect(url_for('admin.users_list'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        
        if new_password and len(new_password) >= 6:
            from app.utils.firebase_auth import update_firebase_user_password
            firebase_uid = edit_user.get('firebase_uid')
            if firebase_uid:
                if update_firebase_user_password(firebase_uid, new_password):
                    flash('Password updated successfully!', 'success')
                else:
                    flash('Failed to update password in Firebase.', 'warning')
        elif new_password and len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('admin/user_form.html', user=get_current_user(), edit_user=edit_user)
        
        update_data = {
            'name': request.form.get('name'),
            'role': request.form.get('role'),
            'course': request.form.get('course') if request.form.get('role') != 'admin' else None
        }
        
        if update_user(user_id, update_data):
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.users_list'))
        else:
            flash('Failed to update user.', 'danger')
    
    return render_template('admin/user_form.html', user=get_current_user(), edit_user=edit_user)


@admin_bp.route('/users/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user_action(user_id):
    """Delete a user"""
    from app.utils.database import get_user_by_id
    target_user = get_user_by_id(user_id)
    
    if not target_user:
        flash('User not found.', 'warning')
        return redirect(url_for('admin.users_list'))
        
    if target_user.get('role', '').lower() == 'admin' or target_user.get('email') == 'admin@gmail.com':
        flash('Cannot delete the system administrator.', 'danger')
        return redirect(url_for('admin.users_list'))
        
    if delete_user(user_id):
        flash('User deleted successfully!', 'success')
    else:
        flash('Failed to delete user.', 'danger')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/activities')
@admin_required
def activities_list():
    """List all activities"""
    activities = get_all_activities()
    return render_template('admin/activities.html', user=get_current_user(), activities=activities)


@admin_bp.route('/reports')
@admin_required
def reports():
    """Reports and analytics page"""
    stats = get_engagement_stats(days=30)
    return render_template('admin/reports.html', user=get_current_user(), stats=stats)


@admin_bp.route('/reports/download/<report_type>')
@admin_required
def download_report(report_type):
    """Download PDF report"""
    from flask import Response
    
    content, file_type = generate_report_pdf(report_type.title())
    
    if file_type == 'pdf':
        return Response(
            content,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=gap2growth_{report_type}_report.pdf'}
        )
    else:
        return Response(
            content,
            mimetype='text/html',
            headers={'Content-Disposition': f'attachment; filename=gap2growth_{report_type}_report.html'}
        )
