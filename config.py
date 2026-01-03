"""
Gap2Growth Configuration Module
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS', 'firebase-credentials.json')
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', '')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN', '')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', '')
    FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID', '')
    FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID', '')
    
    GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    
    DOWNTIME_THRESHOLD_MINUTES = int(os.getenv('DOWNTIME_THRESHOLD_MINUTES', 30))
    SCHEDULER_ENABLED = os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true'
    
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    SCHEDULER_ENABLED = False


config_options = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get the appropriate configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_options.get(env, DevelopmentConfig)
