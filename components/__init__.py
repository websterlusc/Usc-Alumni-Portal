# components/__init__.py
"""
UI Components for USC Institutional Research Portal
Provides Dash components for authentication and user interface
"""

from .auth_components import (
    create_login_button,
    create_user_dropdown,
    create_access_request_modal,
    create_logout_confirmation_modal,
    create_auth_status_store,
    create_auth_interval,
    create_access_denied_alert,
    register_auth_callbacks,
    get_user_navbar_content,
    require_auth_wrapper,
    create_session_timeout_warning
)

__all__ = [
    'create_login_button',
    'create_user_dropdown', 
    'create_access_request_modal',
    'create_logout_confirmation_modal',
    'create_auth_status_store',
    'create_auth_interval',
    'create_access_denied_alert',
    'register_auth_callbacks',
    'get_user_navbar_content',
    'require_auth_wrapper',
    'create_session_timeout_warning'
]