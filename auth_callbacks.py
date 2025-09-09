"""
Authentication Callbacks for USC IR Portal
All the Dash callbacks needed for authentication functionality
"""

from dash import Input, Output, State, callback, ctx, no_update
import dash_bootstrap_components as dbc
from dash import html
from datetime import datetime, timedelta
import re
from auth_system import (
    auth, create_login_form, create_registration_form, 
    create_access_request_form, create_admin_dashboard,
    create_user_profile_page, create_enhanced_navbar
)
from auth_database import db

# ============================================================================
# LOGIN/LOGOUT CALLBACKS
# ============================================================================

@callback(
    [Output('user-session', 'data'),
     Output('login-alerts', 'children'),
     Output('login-email', 'value'),
     Output('login-password', 'value')],
    Input('login-submit-btn', 'n_clicks'),
    [State('login-email', 'value'),
     State('login-password', 'value'),
     State('user-session', 'data')],
    prevent_initial_call=True
)
def handle_login(n_clicks, email, password, current_session):
    """Handle user login"""
    if not n_clicks or not email or not password:
        return no_update, no_update, no_update, no_update
    
    # Validate email format
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        alert = dbc.Alert("Please enter a valid email address", color="danger")
        return no_update, alert, no_update, no_update
    
    # Attempt authentication
    result = db.authenticate_user(email, password)
    
    if result['success']:
        # Store session data
        session_data = {
            'session_token': result['session_token'],
            'user_id': result['user']['id'],
            'email': result['user']['email'],
            'full_name': result['user']['full_name'],
            'access_tier': result['user']['access_tier'],
            'login_time': datetime.now().isoformat()
        }
        
        success_alert = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "Login successful! Redirecting..."
        ], color="success")
        
        return session_data, success_alert, "", ""
    
    else:
        error_alert = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            result['message']
        ], color="danger")
        
        return no_update, error_alert, no_update, ""

@callback(
    Output('user-session', 'data', allow_duplicate=True),
    Input('logout-btn', 'n_clicks'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def handle_logout(n_clicks, session_data):
    """Handle user logout"""
    if n_clicks and session_data:
        # Could add session cleanup here
        return {}
    return no_update

# ============================================================================
# REGISTRATION CALLBACKS
# ============================================================================

@callback(
    [Output('register-alerts', 'children'),
     Output('register-fullname', 'value'),
     Output('register-email', 'value'),
     Output('register-department', 'value'),
     Output('register-password', 'value'),
     Output('register-password-confirm', 'value')],
    Input('register-submit-btn', 'n_clicks'),
    [State('register-fullname', 'value'),
     State('register-email', 'value'),
     State('register-department', 'value'),
     State('register-password', 'value'),
     State('register-password-confirm', 'value')],
    prevent_initial_call=True
)
def handle_registration(n_clicks, fullname, email, department, password, password_confirm):
    """Handle user registration"""
    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    # Validation
    errors = []
    
    if not fullname or len(fullname.strip()) < 2:
        errors.append("Full name is required (minimum 2 characters)")
    
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append("Valid email address is required")
    
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters")
    
    if password != password_confirm:
        errors.append("Passwords do not match")
    
    if errors:
        alert = dbc.Alert([
            html.H5("Please fix the following errors:", className="alert-heading"),
            html.Ul([html.Li(error) for error in errors])
        ], color="danger")
        return alert, no_update, no_update, no_update, no_update, no_update
    
    # Attempt to create user
    result = db.create_user(
        email=email,
        password=password,
        full_name=fullname.strip(),
        department=department.strip() if department else None,
        access_tier=1  # Start with public access
    )
    
    if result['success']:
        if result['auto_approved']:
            alert = dbc.Alert([
                html.H5("Registration Successful!", className="alert-heading"),
                html.P("Your USC account has been automatically approved with factbook access. You can now login."),
                html.Hr(),
                html.P("Click 'Back to Login' to access your account.", className="mb-0")
            ], color="success")
        else:
            alert = dbc.Alert([
                html.H5("Registration Submitted!", className="alert-heading"),
                html.P("Your account has been created and is pending admin approval."),
                html.Hr(),
                html.P("You will receive an email notification once your account is approved.", className="mb-0")
            ], color="info")
        
        # Clear form
        return alert, "", "", "", "", ""
    
    else:
        alert = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            result['message']
        ], color="danger")
        return alert, no_update, no_update, no_update, no_update, no_update

# ============================================================================
# ACCESS REQUEST CALLBACKS
# ============================================================================

@callback(
    [Output('request-alerts', 'children'),
     Output('request-tier', 'value'),
     Output('request-justification', 'value'),
     Output('request-supervisor', 'value')],
    Input('request-submit-btn', 'n_clicks'),
    [State('request-tier', 'value'),
     State('request-justification', 'value'),
     State('request-supervisor', 'value'),
     State('user-session', 'data')],
    prevent_initial_call=True
)
def handle_access_request(n_clicks, requested_tier, justification, supervisor_email, session_data):
    """Handle access tier upgrade request"""
    if not n_clicks or not session_data:
        return no_update, no_update, no_update, no_update
    
    # Validation
    errors = []
    
    if not requested_tier:
        errors.append("Please select an access level")
    
    if not justification or len(justification.strip()) < 20:
        errors.append("Business justification is required (minimum 20 characters)")
    
    if requested_tier >= 3 and (not supervisor_email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', supervisor_email)):
        errors.append("Supervisor email is required for Tier 3+ access")
    
    if errors:
        alert = dbc.Alert([
            html.H5("Please fix the following errors:", className="alert-heading"),
            html.Ul([html.Li(error) for error in errors])
        ], color="danger")
        return alert, no_update, no_update, no_update
    
    # Submit request
    result = db.request_access_upgrade(
        user_id=session_data['user_id'],
        requested_tier=requested_tier,
        justification=justification.strip(),
        business_need=supervisor_email if supervisor_email else None
    )
    
    if result['success']:
        alert = dbc.Alert([
            html.H5("Request Submitted!", className="alert-heading"),
            html.P("Your access request has been submitted for admin review."),
            html.Hr(),
            html.P(f"Request ID: {result['request_id']}", className="mb-0")
        ], color="success")
        
        # Clear form
        return alert, None, "", ""
    
    else:
        alert = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            result['message']
        ], color="danger")
        return alert, no_update, no_update, no_update

# ============================================================================
# ADMIN DASHBOARD CALLBACKS
# ============================================================================

@callback(
    [Output('pending-requests-count', 'children'),
     Output('total-users-count', 'children'),
     Output('active-sessions-count', 'children'),
     Output('tier3-users-count', 'children')],
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def update_admin_stats(pathname, session_data):
    """Update admin dashboard statistics"""
    if pathname != '/admin' or not session_data:
        return no_update, no_update, no_update, no_update
    
    # Check if user is admin
    user_info = auth.get_user_info(session_data)
    if not user_info or user_info['access_tier'] < 4:
        return no_update, no_update, no_update, no_update
    
    # Get statistics (would implement in database)
    pending_requests = len(db.get_pending_requests())
    
    # Placeholder stats - implement proper queries
    total_users = "156"
    active_sessions = "23"
    tier3_users = "12"
    
    return str(pending_requests), total_users, active_sessions, tier3_users

@callback(
    Output('admin-tab-content', 'children'),
    Input('admin-tabs', 'active_tab'),
    State('user-session', 'data')
)
def render_admin_tab_content(active_tab, session_data):
    """Render content for admin dashboard tabs"""
    if not session_data:
        return html.Div("Please login to access admin features.")
    
    user_info = auth.get_user_info(session_data)
    if not user_info or user_info['access_tier'] < 4:
        return html.Div("Admin access required.")
    
    if active_tab == "requests-tab":
        return create_requests_management_panel()
    elif active_tab == "users-tab":
        return create_users_management_panel()
    elif active_tab == "logs-tab":
        return create_logs_panel()
    elif active_tab == "settings-tab":
        return create_settings_panel()
    
    return html.Div("Select a tab to view content.")

def create_requests_management_panel():
    """Create admin panel for managing access requests"""
    pending_requests = db.get_pending_requests()
    
    if not pending_requests:
        return dbc.Alert("No pending requests", color="info")
    
    request_cards = []
    for req in pending_requests:
        card = dbc.Card([
            dbc.CardHeader([
                html.H5(f"{req['full_name']} ({req['email']})", className="mb-0"),
                dbc.Badge(f"Tier {req['current_tier']} → {req['requested_tier']}", 
                         color="info", className="float-end")
            ]),
            dbc.CardBody([
                html.P([html.Strong("Justification: "), req['justification']]),
                html.P([html.Strong("Requested: "), req['requested_at']]),
                dbc.ButtonGroup([
                    dbc.Button("Approve", color="success", size="sm", 
                              id=f"approve-{req['id']}"),
                    dbc.Button("Deny", color="danger", size="sm", 
                              id=f"deny-{req['id']}"),
                    dbc.Button("Details", color="info", size="sm",
                              id=f"details-{req['id']}")
                ])
            ])
        ], className="mb-3")
        request_cards.append(card)
    
    return html.Div(request_cards)

def create_users_management_panel():
    """Create admin panel for managing users"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5("User Management"),
                html.P("Manage user accounts, access levels, and permissions.")
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Button("Add New User", color="primary", className="mb-3"),
                html.Div("User management table would go here...")
            ])
        ])
    ])

def create_logs_panel():
    """Create admin panel for viewing system logs"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5("System Audit Logs"),
                html.P("View system activity and security events.")
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.Div("Audit log table would go here...")
            ])
        ])
    ])

def create_settings_panel():
    """Create admin panel for system settings"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5("System Settings"),
                html.P("Configure system-wide settings and preferences.")
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Form([
                    dbc.Row([
                        dbc.Label("Session Timeout (hours)", width=4),
                        dbc.Col([
                            dbc.Input(type="number", value=8, min=1, max=24)
                        ], width=8)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Max Login Attempts", width=4),
                        dbc.Col([
                            dbc.Input(type="number", value=5, min=3, max=10)
                        ], width=8)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Auto-approve USC emails", width=4),
                        dbc.Col([
                            dbc.Switch(value=True)
                        ], width=8)
                    ], className="mb-3"),
                    dbc.Button("Save Settings", color="primary")
                ])
            ], width=6)
        ])
    ])

# ============================================================================
# FORM SWITCHING CALLBACKS
# ============================================================================

@callback(
    Output('auth-form-container', 'children'),
    [Input('show-login-btn', 'n_clicks'),
     Input('show-register-btn', 'n_clicks'),
     Input('show-reset-btn', 'n_clicks'),
     Input('request-upgrade-btn', 'n_clicks')],
    prevent_initial_call=True
)
def switch_auth_forms(login_clicks, register_clicks, reset_clicks, upgrade_clicks):
    """Switch between different authentication forms"""
    if ctx.triggered_id == 'show-register-btn':
        return create_registration_form()
    elif ctx.triggered_id == 'show-reset-btn':
        return create_password_reset_form()
    elif ctx.triggered_id == 'request-upgrade-btn':
        return create_access_request_form()
    else:
        return create_login_form()

def create_password_reset_form():
    """Create password reset form"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Reset Password", className="mb-0 text-center",
                   style={'color': '#1B5E20'})
        ], style={'background': '#F8F9FA'}),
        dbc.CardBody([
            dbc.Form([
                dbc.Row([
                    dbc.Label("Email Address", className="fw-bold"),
                    dbc.Input(
                        id="reset-email",
                        type="email",
                        placeholder="your.email@usc.edu.tt",
                        className="mb-3"
                    )
                ]),
                html.Div(id="reset-alerts", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Send Reset Link",
                            id="reset-submit-btn",
                            color="success",
                            size="lg",
                            className="w-100",
                            style={'background-color': '#1B5E20'}
                        )
                    ], width=12)
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.P("Remember your password?", className="text-center mb-2"),
                        dbc.Button(
                            "Back to Login",
                            id="show-login-btn",
                            color="outline-primary",
                            size="sm",
                            className="w-100"
                        )
                    ])
                ])
            ])
        ])
    ], style={'max-width': '400px', 'margin': '0 auto'})

# ============================================================================
# PAGE ROUTING WITH AUTHENTICATION
# ============================================================================

@callback(
    Output('auth-form-container', 'children', allow_duplicate=True),
    Input('url', 'pathname'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def show_auth_form_when_needed(pathname, session_data):
    """Show authentication form when user needs to login"""
    
    # Define which pages require authentication
    protected_routes = {
        '/factbook': 2,
        '/enrollment': 2,
        '/graduation': 2,
        '/hr-data': 2,
        '/student-employment': 2,
        '/financial': 3,
        '/budget': 3,
        '/revenue': 3,
        '/endowments': 3,
        '/admin': 4,
        '/profile': 2
    }
    
    required_tier = protected_routes.get(pathname, 1)
    
    if required_tier > 1:
        user_tier = auth.get_user_access_tier(session_data)
        if user_tier < required_tier:
            return create_login_form()
    
    return no_update

# Export all the callback functions
__all__ = [
    'handle_login', 'handle_logout', 'handle_registration', 
    'handle_access_request', 'update_admin_stats', 'render_admin_tab_content',
    'switch_auth_forms', 'show_auth_form_when_needed'
]
                