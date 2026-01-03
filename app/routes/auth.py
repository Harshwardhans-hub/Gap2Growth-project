"""
Authentication Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.utils.firebase_auth import verify_firebase_token, is_firebase_initialized
from app.utils.database import get_user_by_firebase_uid, create_user, get_all_users

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login():
    """Render the login page with Firebase config"""
    if 'user' in session:
        return redirect_by_role(session['user'].get('role'))
    
    config = {
        'FIREBASE_API_KEY': current_app.config.get('FIREBASE_API_KEY', ''),
        'FIREBASE_AUTH_DOMAIN': current_app.config.get('FIREBASE_AUTH_DOMAIN', ''),
        'FIREBASE_PROJECT_ID': current_app.config.get('FIREBASE_PROJECT_ID', ''),
        'FIREBASE_STORAGE_BUCKET': current_app.config.get('FIREBASE_STORAGE_BUCKET', ''),
        'FIREBASE_MESSAGING_SENDER_ID': current_app.config.get('FIREBASE_MESSAGING_SENDER_ID', ''),
        'FIREBASE_APP_ID': current_app.config.get('FIREBASE_APP_ID', '')
    }
    return render_template('auth/login.html', config=config)


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify Firebase token and create session"""
    data = request.get_json()
    id_token = data.get('idToken')
    requested_role = data.get('role', 'student')
    
    print(f"\n🔐 TOKEN VERIFICATION REQUEST:")
    print(f"   Role: {requested_role}")
    print(f"   Token received: {'Yes' if id_token else 'No'}")
    
    if not id_token:
        print("   ✗ No token provided!")
        return jsonify({'success': False, 'error': 'No token provided'}), 400
    
    if not is_firebase_initialized():
        print("   ✗ Firebase not initialized!")
        return jsonify({'success': False, 'error': 'Authentication service unavailable'}), 503
    
    firebase_user = verify_firebase_token(id_token)
    
    if not firebase_user:
        print("   ✗ Token verification failed - check Firebase credentials")
        return jsonify({'success': False, 'error': 'Invalid or expired token. Please try again.'}), 401
    
    print(f"   ✓ Token verified for: {firebase_user.get('email')}")
    
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@gmail.com')
    is_admin = firebase_user['email'].lower() == admin_email.lower()
    
    db_user = get_user_by_firebase_uid(firebase_user['uid'])
    
    if db_user:
        user_actual_role = db_user['role']
        
        if is_admin:
            if requested_role != 'admin':
                return jsonify({
                    'success': False, 
                    'error': 'Please use the Admin tab to login'
                }), 403
        else:
            if user_actual_role != requested_role:
                role_name = user_actual_role.title()
                return jsonify({
                    'success': False, 
                    'error': f'This account is registered as {role_name}. Please use the {role_name} tab to login.'
                }), 403
        
        session['user'] = {
            'id': db_user['id'],
            'firebase_uid': db_user['firebase_uid'],
            'name': db_user['name'],
            'email': db_user['email'],
            'role': user_actual_role,
            'course': db_user.get('course')
        }
        return jsonify({
            'success': True,
            'user': session['user'],
            'redirect': get_redirect_url(user_actual_role)
        })
    else:
        if requested_role == 'admin' and not is_admin:
            return jsonify({'success': False, 'error': 'Admin access denied'}), 403
        
        if is_admin:
            new_user = create_user(
                firebase_uid=firebase_user['uid'],
                name='Administrator',
                role='admin',
                email=firebase_user['email'],
                course=None
            )
            if new_user:
                session['user'] = {
                    'id': new_user['id'],
                    'firebase_uid': new_user['firebase_uid'],
                    'name': new_user['name'],
                    'email': new_user['email'],
                    'role': 'admin',
                    'course': None
                }
                return jsonify({
                    'success': True,
                    'user': session['user'],
                    'redirect': get_redirect_url('admin')
                })
        
        session['pending_user'] = {
            'firebase_uid': firebase_user['uid'],
            'email': firebase_user['email'],
            'name': firebase_user['name'],
            'requested_role': requested_role
        }
        return jsonify({
            'success': True,
            'needsRegistration': True,
            'redirect': url_for('auth.complete_registration')
        })


@auth_bp.route('/complete-registration', methods=['GET', 'POST'])
def complete_registration():
    """Complete user registration with role selection"""
    if 'pending_user' not in session:
        return redirect(url_for('auth.login'))
    
    pending = session['pending_user']
    role = pending.get('requested_role', 'student')
    
    if role == 'admin':
        flash('Invalid role selection.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        course = request.form.get('course')
        name = request.form.get('name', pending['name'])
        
        new_user = create_user(
            firebase_uid=pending['firebase_uid'],
            name=name,
            role=role,
            email=pending['email'],
            course=course
        )
        
        if new_user:
            session.pop('pending_user', None)
            session['user'] = {
                'id': new_user['id'],
                'firebase_uid': new_user['firebase_uid'],
                'name': new_user['name'],
                'email': new_user['email'],
                'role': new_user['role'],
                'course': new_user.get('course')
            }
            flash('Registration complete! Welcome to Gap2Growth.', 'success')
            return redirect(get_redirect_url(role))
        else:
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('auth/register.html', pending_user=pending, role=role)



@auth_bp.route('/logout')
def logout():
    """Log out the current user"""
    session.clear()
    return redirect(url_for('auth.login'))


def get_redirect_url(role):
    """Get redirect URL based on user role"""
    if role == 'admin':
        return url_for('admin.dashboard')
    elif role == 'teacher':
        return url_for('teacher.dashboard')
    else:
        return url_for('student.dashboard')


def redirect_by_role(role):
    """Redirect to appropriate dashboard"""
    return redirect(get_redirect_url(role))
