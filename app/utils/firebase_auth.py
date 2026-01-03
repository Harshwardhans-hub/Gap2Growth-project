"""
Firebase Authentication Utility Module
"""

import os
import json

try:
    import firebase_admin
    from firebase_admin import credentials, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_admin = None
    credentials = None
    auth = None
    print("⚠ Firebase Admin SDK not installed")


firebase_app = None


def init_firebase(app):
    """Initialize Firebase Admin SDK with the Flask app"""
    global firebase_app
    
    if not FIREBASE_AVAILABLE:
        print("⚠ Firebase Admin SDK not available")
        return False
    
    cred_path = app.config.get('FIREBASE_CREDENTIALS', 'firebase-credentials.json')
    
    if firebase_app:
        return True
    
    try:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_app = firebase_admin.initialize_app(cred)
            print("✓ Firebase initialized successfully from credentials file")
            return True
        else:
            firebase_cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
            if firebase_cred_json:
                cred_dict = json.loads(firebase_cred_json)
                cred = credentials.Certificate(cred_dict)
                firebase_app = firebase_admin.initialize_app(cred)
                print("✓ Firebase initialized successfully from environment variable")
                return True
            else:
                print("⚠ Firebase credentials not found")
                return False
    except Exception as e:
        print(f"✗ Firebase initialization failed: {str(e)}")
        return False


def verify_firebase_token(id_token):
    """Verify a Firebase ID token and extract user information"""
    global firebase_app
    
    if not firebase_app:
        print("Firebase not initialized - cannot verify token")
        return None
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name', decoded_token.get('email', 'User')),
            'email_verified': decoded_token.get('email_verified', False),
            'picture': decoded_token.get('picture'),
            'provider': decoded_token.get('firebase', {}).get('sign_in_provider', 'unknown')
        }
    except auth.ExpiredIdTokenError:
        print("Firebase token expired")
        return None
    except auth.InvalidIdTokenError:
        print("Invalid Firebase token")
        return None
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return None


def get_firebase_user(uid):
    """Get user information from Firebase by UID"""
    global firebase_app
    
    if not firebase_app:
        return None
    
    try:
        user = auth.get_user(uid)
        return {
            'uid': user.uid,
            'email': user.email,
            'name': user.display_name or user.email,
            'email_verified': user.email_verified,
            'picture': user.photo_url,
            'disabled': user.disabled
        }
    except auth.UserNotFoundError:
        print(f"Firebase user not found: {uid}")
        return None
    except Exception as e:
        print(f"Error fetching Firebase user: {str(e)}")
        return None


def create_firebase_user(email, password, display_name=None):
    """Create a new user in Firebase"""
    global firebase_app
    
    if not firebase_app:
        return None
    
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        return {
            'uid': user.uid,
            'email': user.email,
            'name': user.display_name
        }
    except auth.EmailAlreadyExistsError:
        print(f"Email already exists: {email}")
        return None
    except Exception as e:
        print(f"Error creating Firebase user: {str(e)}")
        return None


def delete_firebase_user(uid):
    """Delete a user from Firebase"""
    global firebase_app
    
    if not firebase_app:
        return False
    
    try:
        auth.delete_user(uid)
        return True
    except Exception as e:
        print(f"Error deleting Firebase user: {str(e)}")
        return False


def update_firebase_user_password(uid, new_password):
    """Update a user's password in Firebase"""
    global firebase_app
    
    if not firebase_app:
        return False
    
    try:
        auth.update_user(uid, password=new_password)
        return True
    except Exception as e:
        print(f"Error updating Firebase user password: {str(e)}")
        return False


def is_firebase_initialized():
    """Check if Firebase is properly initialized"""
    global firebase_app
    return firebase_app is not None
