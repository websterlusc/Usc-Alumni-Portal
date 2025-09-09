# components/auth_components.py
"""
Dash components for authentication UI
Handles login/logout buttons, user profile display, and access requests
"""

import dash
from dash import html, dcc, Input, Output, State, callback, clientside_callback
import dash_bootstrap_components as dbc
from datetime import datetime
import requests

# USC Brand Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA',
    'medium_gray': '#E9ECEF',
    'dark_gray': '#495057',
    'text_dark': '#212529'
}

def create_login_button():
    """Create login button component"""
    return dbc.Button(
        [
            html.I(className="fab fa-google me-2"),
            "Sign in with Google"
        ],
        id="login-btn",
        color="light",
        outline=True,
        className="me-2",
        style={
            'borderColor': USC_COLORS['primary_green'],
            'color': USC_COLORS['primary_green']
        }
    )

def create_user_dropdown(user_data):
    """Create user profile dropdown menu"""
    if not user_data:
        return create_login_button()
    
    access_tier_badges = {
        1: {"text": "Public", "color": "secondary"},
        2: {"text": "Employee", "color": "success"},
        3: {"text": "Financial", "color": "warning"}
    }
    
    tier_info = access_tier_badges.get(user_data.get('access_tier', 1), access_tier_badges[1])
    
    profile_img = user_data.get('profile_picture')
    initials = ''.join([name[0].upper() for name in user_data.get('full_name', 'User').split()[:2]])
    
    return dbc.DropdownMenu(
        children=[
            dbc.DropdownMenuItem(
                [
                    html.Div([
                        html.Strong(user_data.get('full_name', 'Unknown User')),
                        html.Br(),
                        html.Small(user_data.get('email', ''), className="text-muted"),
                        html.Br(),
                        dbc.Badge(
                            tier_info["text"],
                            color=tier_info["color"],
                            className="mt-1"
                        )
                    ])
                ],
                header=True,
                className="py-3"
            ),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem(
                [html.I(className="fas fa-user me-2"), "Profile"],
                id="profile-menu-item",
                href="/profile"
            ),
            dbc.DropdownMenuItem(
                [html.I(className="fas fa-key me-2"), "Request Access"],
                id="access-request-menu-item",
                href="/request-access"
            ) if user_data.get('access_tier', 1) < 3 else None,
            dbc.DropdownMenuItem(
                [html.I(className="fas fa-cog me-2"), "Admin Panel"],
                id="admin-menu-item",
                href="/admin"
            ) if user_data.get('role') == 'admin' else None,
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem(
                [html.I(className="fas fa-sign-out-alt me-2"), "Logout"],
                id="logout-menu-item"
            )
        ],
        toggle_id="user-dropdown",
        label=[
            html.Img(
                src=profile_img,
                style={
                    'width': '32px',
                    'height': '32px',
                    'borderRadius': '50%',
                    'marginRight': '8px'
                }
            ) if profile_img else html.Div(
                initials,
                style={
                    'width': '32px',
                    'height': '32px',
                    'borderRadius': '50%',
                    'backgroundColor': USC_COLORS['primary_green'],
                    'color': 'white',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'marginRight': '8px'
                }
            ),
            html.Span(user_data.get('full_name', 'User').split()[0])
        ],
        color="light",
        size="sm",
        direction="down",
        right=True
    )

def create_access_request_modal():
    """Create modal for requesting access tier upgrades"""
    return dbc.Modal(
        [
            dbc.ModalHeader("Request Access Upgrade"),
            dbc.ModalBody([
                html.P("Request higher access level to view additional institutional data."),
                dbc.Form([
                    dbc.Row([
                        dbc.Label("Current Access Level:", html_for="current-tier", width=4),
                        dbc.Col([
                            dbc.Input(
                                id="current-tier-display",
                                type="text",
                                disabled=True,
                                value="Employee (Factbook Access)"
                            )
                        ], width=8)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Requested Access Level:", html_for="requested-tier", width=4),
                        dbc.Col([
                            dbc.Select(
                                id="requested-tier-select",
                                options=[
                                    {"label": "Financial Access (Admin Approval Required)", "value": 3}
                                ],
                                value=3
                            )
                        ], width=8)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Label("Justification:", html_for="justification", width=4),
                        dbc.Col([
                            dbc.Textarea(
                                id="access-justification",
                                placeholder="Please explain why you need access to financial data...",
                                rows=4,
                                required=True
                            )
                        ], width=8)
                    ], className="mb-3")
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "Cancel",
                    id="cancel-access-request",
                    color="secondary",
                    className="me-2"
                ),
                dbc.Button(
                    "Submit Request",
                    id="submit-access-request",
                    color="primary",
                    style={'backgroundColor': USC_COLORS['primary_green'], 'borderColor': USC_COLORS['primary_green']}
                )
            ])
        ],
        id="access-request-modal",
        is_open=False,
        centered=True
    )

def create_auth_status_store():
    """Create dcc.Store component for authentication status"""
    return dcc.Store(
        id='auth-status-store',
        storage_type='session',
        data={
            'authenticated': False,
            'user': None,
            'access_tier': 1,
            'last_check': None
        }
    )

def create_auth_interval():
    """Create interval component for periodic auth status checks"""
    return dcc.Interval(
        id='auth-check-interval',
        interval=60*1000,  # Check every minute
        n_intervals=0
    )

def create_logout_confirmation_modal():
    """Create confirmation modal for logout"""
    return dbc.Modal(
        [
            dbc.ModalHeader("Confirm Logout"),
            dbc.ModalBody([
                html.P("Are you sure you want to sign out?"),
                html.Small("You will need to sign in again to access protected content.", className="text-muted")
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "Cancel",
                    id="cancel-logout",
                    color="secondary",
                    className="me-2"
                ),
                dbc.Button(
                    "Sign Out",
                    id="confirm-logout",
                    color="danger"
                )
            ])
        ],
        id="logout-confirmation-modal",
        is_open=False,
        centered=True
    )

def create_access_denied_alert(required_tier=2):
    """Create access denied alert component"""
    tier_names = {1: "Public", 2: "Employee", 3: "Financial"}
    
    return dbc.Alert(
        [
            html.H4("Access Restricted", className="alert-heading"),
            html.P(f"This page requires {tier_names.get(required_tier, 'Higher')} access level."),
            html.Hr(),
            html.P([
                "To request access, please ",
                html.A("contact the Institutional Research office", href="/contact"),
                " or ",
                html.A("submit an access request", href="#", id="request-access-link"),
                "."
            ], className="mb-0")
        ],
        color="warning",
        className="mb-4"
    )

# Callback functions for authentication components
def register_auth_callbacks(app):
    """Register callbacks for authentication components"""
    
    @callback(
        Output('auth-status-store', 'data'),
        Input('auth-check-interval', 'n_intervals'),
        State('auth-status-store', 'data'),
        prevent_initial_call=False
    )
    def update_auth_status(n_intervals, current_status):
        """Periodically check authentication status"""
        try:
            # Make request to auth status endpoint
            response = requests.get('/auth/status', timeout=5)
            
            if response.status_code == 200:
                auth_data = response.json()
                auth_data['last_check'] = datetime.now().isoformat()
                return auth_data
            else:
                return {
                    'authenticated': False,
                    'user': None,
                    'access_tier': 1,
                    'last_check': datetime.now().isoformat()
                }
                
        except requests.RequestException:
            # If request fails, keep current status but update timestamp
            if current_status:
                current_status['last_check'] = datetime.now().isoformat()
                return current_status
            
            return {
                'authenticated': False,
                'user': None,
                'access_tier': 1,
                'last_check': datetime.now().isoformat()
            }
    
    @callback(
        Output('logout-confirmation-modal', 'is_open'),
        Input('logout-menu-item', 'n_clicks'),
        Input('cancel-logout', 'n_clicks'),
        State('logout-confirmation-modal', 'is_open'),
        prevent_initial_call=True
    )
    def toggle_logout_modal(logout_clicks, cancel_clicks, is_open):
        """Toggle logout confirmation modal"""
        if logout_clicks or cancel_clicks:
            return not is_open
        return is_open
    
    @callback(
        Output('access-request-modal', 'is_open'),
        Input('access-request-menu-item', 'n_clicks'),
        Input('request-access-link', 'n_clicks'),
        Input('cancel-access-request', 'n_clicks'),
        Input('submit-access-request', 'n_clicks'),
        State('access-request-modal', 'is_open'),
        prevent_initial_call=True
    )
    def toggle_access_request_modal(menu_clicks, link_clicks, cancel_clicks, submit_clicks, is_open):
        """Toggle access request modal"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id in ['access-request-menu-item', 'request-access-link']:
            return True
        elif button_id in ['cancel-access-request', 'submit-access-request']:
            return False
        
        return is_open
    
    @callback(
        Output('access-request-feedback', 'children'),
        Input('submit-access-request', 'n_clicks'),
        State('requested-tier-select', 'value'),
        State('access-justification', 'value'),
        prevent_initial_call=True
    )
    def handle_access_request(n_clicks, requested_tier, justification):
        """Handle access request submission"""
        if not n_clicks:
            return ""
        
        try:
            # Submit access request
            response = requests.post('/auth/request-access', json={
                'requested_tier': requested_tier,
                'justification': justification
            }, timeout=5)
            
            if response.status_code == 200:
                return dbc.Alert(
                    [
                        html.I(className="fas fa-check-circle me-2"),
                        "Access request submitted successfully! You will be notified when it's reviewed."
                    ],
                    color="success",
                    className="mt-3"
                )
            else:
                error_data = response.json()
                return dbc.Alert(
                    [
                        html.I(className="fas fa-exclamation-circle me-2"),
                        f"Error: {error_data.get('error', 'Request failed')}"
                    ],
                    color="danger",
                    className="mt-3"
                )
                
        except requests.RequestException:
            return dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Unable to submit request. Please try again later."
                ],
                color="warning",
                className="mt-3"
            )
    
    # Client-side callback for logout
    clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks > 0) {
                // Submit logout form
                fetch('/auth/logout', {
                    method: 'POST',
                    credentials: 'include'
                }).then(response => {
                    window.location.href = '/?logout=success';
                }).catch(error => {
                    console.error('Logout error:', error);
                    window.location.href = '/?logout=error';
                });
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('confirm-logout', 'id'),
        Input('confirm-logout', 'n_clicks'),
        prevent_initial_call=True
    )
    
    # Client-side callback for login
    clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks > 0) {
                window.location.href = '/auth/login';
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('login-btn', 'id'),
        Input('login-btn', 'n_clicks'),
        prevent_initial_call=True
    )

def get_user_navbar_content(auth_status):
    """Get navbar content based on authentication status"""
    if not auth_status or not auth_status.get('authenticated'):
        return create_login_button()
    
    return create_user_dropdown(auth_status.get('user'))

def require_auth_wrapper(component, required_tier=2, auth_status=None):
    """Wrap component with authentication check"""
    if not auth_status or not auth_status.get('authenticated'):
        return html.Div([
            create_access_denied_alert(required_tier),
            html.P([
                "Please ",
                html.A("sign in", href="/auth/login", className="btn btn-primary btn-sm"),
                " to access this content."
            ])
        ])
    
    user_tier = auth_status.get('access_tier', 1)
    if user_tier < required_tier:
        return create_access_denied_alert(required_tier)
    
    return component

# Additional utility components
def create_loading_spinner():
    """Create loading spinner for auth operations"""
    return dbc.Spinner(
        html.Div(id="auth-loading-content"),
        size="sm",
        color="primary",
        type="border"
    )

def create_auth_feedback():
    """Create container for authentication feedback messages"""
    return html.Div(id="auth-feedback", className="mt-3")

def create_session_timeout_warning():
    """Create session timeout warning component"""
    return dbc.Toast(
        [
            html.P([
                html.I(className="fas fa-clock me-2"),
                "Your session will expire in 5 minutes. ",
                html.A("Click here to extend", href="#", id="extend-session-link")
            ])
        ],
        id="session-timeout-toast",
        header="Session Expiring Soon",
        is_open=False,
        dismissable=True,
        icon="warning",
        duration=10000,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350, "z-index": 9999}
    )