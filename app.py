"""
Gap2Growth - Adaptive Student Time Utilisation & Learning Continuity Platform
Main Application Entry Point
"""

from flask import Flask, redirect, url_for, session, render_template
from flask_cors import CORS
from config import get_config
from app.utils.database import init_database
from app.utils.firebase_auth import init_firebase
from app.utils.scheduler import init_scheduler

from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.teacher import teacher_bp
from app.routes.student import student_bp
from app.routes.api import api_bp


def create_app():
    """Application factory function to create and configure the Flask app"""
    app = Flask(
        __name__,
        template_folder='app/templates',
        static_folder='app/static'
    )
    
    app.config.from_object(get_config())
    CORS(app, supports_credentials=True)
    
    init_database(app)
    init_firebase(app)
    
    import os
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        init_scheduler(app)
        
        from app.services.realtime_service import start_realtime_detection
        start_realtime_detection()
    else:
        print("⚠ Scheduler and real-time detection disabled in debug mode first load")
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def home():
        if 'user' in session:
            user_role = session['user'].get('role', 'student')
            if user_role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user_role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'Gap2Growth',
            'app_version': '1.0.0'
        }
    
    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
