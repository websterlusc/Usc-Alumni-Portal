# auth/google_auth.py
"""
Google OAuth 2.0 Authentication System for USC IR Portal
Handles Google login, user registration, and session management
"""

import os
import secrets
import sqlite3
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
from typing import Optional, Dict, Any
import jwt
from flask import Flask, request, redirect, session, url_for, jsonify


class GoogleOAuthManager:
    """Manages Google OAuth authentication flow"""

    def __init__(self, app: Flask):
        self.app = app
        self.client_id = os.getenv('GOOGLE_CLIENT_ID',
                                   '890006312213-3k7f200g3a94je1j9trfjru716v3kidc.apps.googleusercontent.com')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI', 'http://localhost:8050/auth/google-callback')
        self.scope = 'openid email profile'

        if not self.client_secret:
            raise ValueError("GOOGLE_CLIENT_SECRET environment variable is required")

    def get_auth_url(self, state: str = None) -> str:
        """Generate Google OAuth authorization URL"""
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'select_account',
            'state': state
        }

        return f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        token_url = 'https://oauth2.googleapis.com/token'

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }

        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Token exchange failed: {e}")
            return None

    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google API"""
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(user_info_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Failed to get user info: {e}")
            return None


class UserManager:
    """Manages user database operations"""

    def __init__(self, db_path: str = 'usc_ir.db'):
        self.db_path = db_path

    def get_or_create_user(self, user_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get existing user or create new one from Google user info"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            email = user_info.get('email', '').lower()
            google_id = user_info.get('id')
            full_name = user_info.get('name', '')
            profile_picture = user_info.get('picture', '')

            # Check if user exists
            cursor.execute('SELECT * FROM users WHERE email = ? OR google_id = ?', (email, google_id))
            existing_user = cursor.fetchone()

            if existing_user:
                # Update existing user
                cursor.execute('''
                    UPDATE users 
                    SET full_name = ?, profile_picture = ?, last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (full_name, profile_picture, existing_user['id']))

                user_dict = dict(existing_user)
                user_dict.update({
                    'full_name': full_name,
                    'profile_picture': profile_picture,
                    'last_login': datetime.now().isoformat()
                })
            else:
                # Create new user
                access_tier = 2 if email.endswith('@usc.edu.tt') else 1
                role = 'employee' if email.endswith('@usc.edu.tt') else 'guest'

                cursor.execute('''
                    INSERT INTO users (email, full_name, role, access_tier, google_id, profile_picture, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (email, full_name, role, access_tier, google_id, profile_picture))

                user_id = cursor.lastrowid
                user_dict = {
                    'id': user_id,
                    'email': email,
                    'full_name': full_name,
                    'role': role,
                    'access_tier': access_tier,
                    'google_id': google_id,
                    'profile_picture': profile_picture,
                    'created_at': datetime.now().isoformat(),
                    'last_login': datetime.now().isoformat()
                }

            conn.commit()
            return user_dict

        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            conn.close()


class SessionManager:
    """Manages user sessions and authentication tokens"""

    def __init__(self, db_path: str = 'usc_ir.db', secret_key: str = None):
        self.db_path = db_path
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'usc-ir-development-key')
        self.session_duration = timedelta(hours=8)  # 8-hour sessions

    def create_session(self, user_id: int) -> str:
        """Create a new session token for user"""
        session_token = secrets.token_urlsafe(64)
        expires_at = datetime.now() + self.session_duration

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Clean up expired sessions
            cursor.execute('DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP')

            # Create new session
            cursor.execute('''
                INSERT INTO user_sessions (session_token, user_id, expires_at)
                VALUES (?, ?, ?)
            ''', (session_token, user_id, expires_at))

            conn.commit()
            return session_token

        except sqlite3.Error as e:
            print(f"❌ Session creation failed: {e}")
            return None
        finally:
            conn.close()

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user info"""
        if not session_token:
            return None

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT u.*, s.expires_at
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            ''', (session_token,))

            result = cursor.fetchone()
            return dict(result) if result else None

        except sqlite3.Error as e:
            print(f"❌ Session validation failed: {e}")
            return None
        finally:
            conn.close()

    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session token (logout)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (session_token,))
            conn.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"❌ Session invalidation failed: {e}")
            return False
        finally:
            conn.close()

    def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP')
            conn.commit()
            removed_count = cursor.rowcount
            if removed_count > 0:
                print(f"🧹 Cleaned up {removed_count} expired sessions")

        except sqlite3.Error as e:
            print(f"❌ Session cleanup failed: {e}")
        finally:
            conn.close()


# Authentication decorator for Dash callbacks
def require_auth(access_tier: int = 1):
    """Decorator to require authentication for Dash callbacks"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get session from dcc.Store or other mechanism
            # This would be implemented based on your Dash app structure
            session_token = kwargs.get('session_token')

            session_manager = SessionManager()
            user = session_manager.validate_session(session_token)

            if not user:
                return {"error": "Authentication required"}

            if user.get('access_tier', 1) < access_tier:
                return {"error": "Insufficient access level"}

            kwargs['current_user'] = user
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Database initialization function
def init_database(db_path: str = 'usc_ir.db'):
    """Initialize SQLite database with required tables"""
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'employee',
                access_tier INTEGER DEFAULT 2,
                google_id TEXT,
                profile_picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # Create user sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # Create access requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                requested_tier INTEGER NOT NULL,
                justification TEXT,
                status TEXT DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by INTEGER,
                reviewed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (reviewed_by) REFERENCES users (id)
            )
        ''')

        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions (session_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions (expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_status ON access_requests (status)')

        conn.commit()
        print("✅ Database initialized successfully")
        print(f"📁 Database location: {db_path}")

    except sqlite3.Error as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        conn.close()


# Example usage functions
def init_auth_system(app: Flask) -> tuple:
    """Initialize authentication system and return managers"""
    oauth_manager = GoogleOAuthManager(app)
    user_manager = UserManager()
    session_manager = SessionManager()

    return oauth_manager, user_manager, session_manager


def get_login_url() -> str:
    """Get Google OAuth login URL"""
    oauth_manager = GoogleOAuthManager(None)
    return oauth_manager.get_auth_url()


def handle_oauth_callback(code: str, state: str = None) -> Dict[str, Any]:
    """Handle OAuth callback and return user session info"""
    oauth_manager = GoogleOAuthManager(None)
    user_manager = UserManager()
    session_manager = SessionManager()

    # Exchange code for token
    token_data = oauth_manager.exchange_code_for_token(code)
    if not token_data:
        return {"error": "Failed to exchange authorization code"}

    # Get user info
    user_info = oauth_manager.get_user_info(token_data['access_token'])
    if not user_info:
        return {"error": "Failed to get user information"}

    # Create or update user
    user = user_manager.get_or_create_user(user_info)
    if not user:
        return {"error": "Failed to create user account"}

    # Create session
    session_token = session_manager.create_session(user['id'])
    if not session_token:
        return {"error": "Failed to create session"}

    return {
        "success": True,
        "user": user,
        "session_token": session_token,
        "expires_in": 8 * 3600  # 8 hours in seconds
    }