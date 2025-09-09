# auth/__init__.py
"""
Authentication module for USC Institutional Research Portal
Provides Google OAuth integration and user management
"""

from .google_auth import (
    GoogleOAuthManager,
    UserManager, 
    SessionManager,
    init_database,
    init_auth_system,
    get_login_url,
    handle_oauth_callback,
    require_auth
)

from .auth_routes import register_auth_routes, get_current_user

__all__ = [
    'GoogleOAuthManager',
    'UserManager',
    'SessionManager', 
    'init_database',
    'init_auth_system',
    'get_login_url',
    'handle_oauth_callback',
    'require_auth',
    'register_auth_routes',
    'get_current_user'
]