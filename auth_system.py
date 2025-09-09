"""
Complete Authentication System for USC IR Portal
Integrates with your existing app.py design
"""

import dash
from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import secrets
import hashlib
from typing import Dict, Any, Optional
from auth_database import db

# USC Brand Colors (matching your existing design)
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA',
    'medium_gray': '#E9ECEF',
    'dark_gray': '#495057',
    'text_dark': '#212529',
    'success_green': '#28A745'
}

class AuthenticationManager:
    """Handles all authentication logic"""
    
    def __init__(self):
        self.db = db
    
    def get_user_access_tier(self, session_data: Dict = None) -> int:
        """Get user access tier from session"""
        if not session_data or 'session_token' not in session_data:
            return 1  # Public access
        
        user = self.db.get_user_by_session(session_data['session_token'])
        return user['access_tier'] if user else 1
    
    def get_user_info(self, session_data: Dict = None) -> Optional[Dict]:
        """Get user information from session"""
        if not session_data or 'session_token' not in session_data:
            return None
        
        return self.db.get_user_by_session(session_data['session_token'])
    
    def has_access(self, required_tier: int, session_data: Dict = None) -> bool:
        """Check if user has required access tier"""
        user_tier = self.get_user_access_tier(session_data)
        return user_tier >= required_tier

# Initialize auth manager
auth = AuthenticationManager()

def create_login_form():
    """Create login form component"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Login to USC IR Portal", className="mb-0 text-center",
                   style={'color': USC_COLORS['primary_green']})
        ], style={'background': USC_COLORS['light_gray']}),
        dbc.CardBody([
            dbc.Form([
                dbc.Row([
                    dbc.Label("Email Address", className="fw-bold"),
                    dbc.Input(
                        id="login-email",
                        type="email",
                        placeholder="your.email@usc.edu.tt",
                        className="mb-3"
                    )
                ]),
                dbc.Row([
                    dbc.Label("Password", className="fw-bold"),
                    dbc.Input(
                        id="login-password",
                        type="password",
                        placeholder="Enter your password",
                        className="mb-3"
                    )
                ]),
                html.Div(id="login-alerts", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Login",
                            id="login-submit-btn",
                            color="success",
                            size="lg",
                            className="w-100",
                            style={'background-color': USC_COLORS['primary_green']}
                        )
                    ], width=12)
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.P("Don't have an account?", className="text-center mb-2"),
                        dbc.Button(
                            "Register New Account",
                            id="show-register-btn",
                            color="outline-primary",
                            size="sm",
                            className="w-100"
                        )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        html.P("Forgot your password?", className="text-center mb-2 mt-2"),
                        dbc.Button(
                            "Reset Password",
                            id="show-reset-btn",
                            color="outline-secondary",
                            size="sm",
                            className="w-100"
                        )
                    ])
                ])
            ])
        ])
    ], style={'max-width': '400px', 'margin': '0 auto'})

def create_registration_form():
    """Create user registration form"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Register for USC IR Portal", className="mb-0 text-center",
                   style={'color': USC_COLORS['primary_green']})
        ], style={'background': USC_COLORS['light_gray']}),
        dbc.CardBody([
            dbc.Form([
                dbc.Row([
                    dbc.Label("Full Name *", className="fw-bold"),
                    dbc.Input(
                        id="register-fullname",
                        type="text",
                        placeholder="Enter your full name",
                        className="mb-3"
                    )
                ]),
                dbc.Row([
                    dbc.Label("Email Address *", className="fw-bold"),
                    dbc.Input(
                        id="register-email",
                        type="email",
                        placeholder="your.email@usc.edu.tt",
                        className="mb-3"
                    ),
                    dbc.FormText("USC employees (@usc.edu.tt) get automatic factbook access")
                ]),
                dbc.Row([
                    dbc.Label("Department", className="fw-bold"),
                    dbc.Input(
                        id="register-department",
                        type="text",
                        placeholder="Your department/unit",
                        className="mb-3"
                    )
                ]),
                dbc.Row([
                    dbc.Label("Password *", className="fw-bold"),
                    dbc.Input(
                        id="register-password",
                        type="password",
                        placeholder="Create a strong password",
                        className="mb-3"
                    )
                ]),
                dbc.Row([
                    dbc.Label("Confirm Password *", className="fw-bold"),
                    dbc.Input(
                        id="register-password-confirm",
                        type="password",
                        placeholder="Confirm your password",
                        className="mb-3"
                    )
                ]),
                html.Div(id="register-alerts", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Create Account",
                            id="register-submit-btn",
                            color="success",
                            size="lg",
                            className="w-100",
                            style={'background-color': USC_COLORS['primary_green']}
                        )
                    ], width=12)
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.P("Already have an account?", className="text-center mb-2"),
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

def create_access_request_form():
    """Create access tier upgrade request form"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Request Higher Access", className="mb-0 text-center",
                   style={'color': USC_COLORS['primary_green']})
        ], style={'background': USC_COLORS['light_gray']}),
        dbc.CardBody([
            dbc.Alert([
                html.H5("Access Tier Information", className="alert-heading"),
                html.P([
                    html.Strong("Tier 2 (Factbook): "), "Student data, HR analytics, enrollment trends",
                    html.Br(),
                    html.Strong("Tier 3 (Financial): "), "Budget data, revenue reports, financial analytics",
                    html.Br(),
                    html.Strong("Tier 4 (Admin): "), "User management, system administration"
                ])
            ], color="info"),
            dbc.Form([
                dbc.Row([
                    dbc.Label("Requested Access Level", className="fw-bold"),
                    dcc.Dropdown(
                        id="request-tier",
                        options=[
                            {'label': 'Tier 2 - Factbook Access', 'value': 2},
                            {'label': 'Tier 3 - Financial Access', 'value': 3},
                            {'label': 'Tier 4 - Admin Access', 'value': 4}
                        ],
                        placeholder="Select access level",
                        className="mb-3"
                    )
                ]),
                dbc.Row([
                    dbc.Label("Business Justification *", className="fw-bold"),
                    dbc.Textarea(
                        id="request-justification",
                        placeholder="Explain why you need this access level and how it relates to your role...",
                        rows=4,
                        className="mb-3"
                    )
                ]),
                dbc.Row([
                    dbc.Label("Supervisor Email (for Tier 3+)", className="fw-bold"),
                    dbc.Input(
                        id="request-supervisor",
                        type="email",
                        placeholder="supervisor@usc.edu.tt",
                        className="mb-3"
                    )
                ]),
                html.Div(id="request-alerts", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Submit Request",
                            id="request-submit-btn",
                            color="success",
                            size="lg",
                            className="w-100",
                            style={'background-color': USC_COLORS['primary_green']}
                        )
                    ], width=12)
                ])
            ])
        ])
    ], style={'max-width': '500px', 'margin': '0 auto'})

def create_admin_dashboard():
    """Create admin control panel"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Admin Dashboard", style={'color': USC_COLORS['primary_green']}),
                html.P("Manage users, approve access requests, and control system settings.")
            ])
        ]),
        
        # Quick Stats Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(id="pending-requests-count", className="text-center"),
                        html.P("Pending Requests", className="text-center text-muted")
                    ])
                ], color="warning", outline=True)
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(id="total-users-count", className="text-center"),
                        html.P("Total Users", className="text-center text-muted")
                    ])
                ], color="info", outline=True)
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(id="active-sessions-count", className="text-center"),
                        html.P("Active Sessions", className="text-center text-muted")
                    ])
                ], color="success", outline=True)
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(id="tier3-users-count", className="text-center"),
                        html.P("Financial Access", className="text-center text-muted")
                    ])
                ], color="primary", outline=True)
            ], width=3)
        ], className="mb-4"),
        
        # Tab interface for different admin functions
        dbc.Tabs([
            dbc.Tab(label="Access Requests", tab_id="requests-tab"),
            dbc.Tab(label="User Management", tab_id="users-tab"),
            dbc.Tab(label="System Logs", tab_id="logs-tab"),
            dbc.Tab(label="Settings", tab_id="settings-tab")
        ], id="admin-tabs", active_tab="requests-tab"),
        
        html.Div(id="admin-tab-content", className="mt-4")
    ])

def create_requests_tab():
    """Create pending requests management tab"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H4("Pending Access Requests"),
                html.Div(id="requests-table")
            ])
        ])
    ])

def create_users_tab():
    """Create user management tab"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H4("User Management"),
                dbc.Button("Add New User", id="add-user-btn", color="primary", className="mb-3"),
                html.Div(id="users-table")
            ])
        ])
    ])

def create_user_profile_page(user_info: Dict):
    """Create user profile management page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("My Profile", style={'color': USC_COLORS['primary_green']}),
                html.Hr()
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Account Information"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.P([html.Strong("Name: "), user_info.get('full_name', 'N/A')]),
                                html.P([html.Strong("Email: "), user_info.get('email', 'N/A')]),
                                html.P([html.Strong("Access Level: "), f"Tier {user_info.get('access_tier', 1)}"]),
                                html.P([html.Strong("Member Since: "), "January 2025"]),  # Could be from DB
                            ])
                        ])
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Access Permissions"),
                    dbc.CardBody([
                        create_access_level_display(user_info.get('access_tier', 1))
                    ])
                ])
            ], width=6)
        ], className="mb-4"),
        
        # Access upgrade section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Request Higher Access"),
                    dbc.CardBody([
                        html.P("Need access to additional data or features?"),
                        dbc.Button(
                            "Request Access Upgrade",
                            id="request-upgrade-btn",
                            color="primary",
                            style={'background-color': USC_COLORS['primary_green']}
                        )
                    ])
                ])
            ])
        ])
    ])

def create_access_level_display(tier: int):
    """Create visual display of access level"""
    access_levels = [
        {"tier": 1, "name": "Public", "desc": "Basic institutional information", "color": "secondary"},
        {"tier": 2, "name": "Factbook", "desc": "Student data and analytics", "color": "info"},
        {"tier": 3, "name": "Financial", "desc": "Budget and financial reports", "color": "warning"},
        {"tier": 4, "name": "Admin", "desc": "System administration", "color": "danger"}
    ]
    
    elements = []
    for level in access_levels:
        if level["tier"] <= tier:
            # User has this access
            badge_color = level["color"]
            icon = "fas fa-check-circle text-success"
        else:
            # User doesn't have this access
            badge_color = "light"
            icon = "fas fa-times-circle text-muted"
        
        elements.append(
            dbc.Row([
                dbc.Col([
                    html.I(className=icon), " ",
                    dbc.Badge(f"Tier {level['tier']}", color=badge_color, className="me-2"),
                    html.Strong(level["name"]), " - ", level["desc"]
                ], className="mb-2")
            ])
        )
    
    return elements

# Authentication Helper Functions
def require_auth(min_tier: int = 1):
    """Decorator to require authentication for callbacks"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get session data from callback context
            session_data = kwargs.get('session_data', {})
            
            if not auth.has_access(min_tier, session_data):
                return create_access_denied_page(min_tier)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def create_access_denied_page(required_tier: int):
    """Create access denied page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H4("Access Denied", className="alert-heading"),
                    html.P(f"You need Tier {required_tier} access to view this page."),
                    html.Hr(),
                    html.P("Contact your administrator to request higher access.")
                ], color="danger", className="text-center"),
                dbc.Button("Return Home", href="/", color="primary", className="d-block mx-auto")
            ])
        ])
    ], className="mt-5")

def create_enhanced_navbar(user_info: Dict = None):
    """Create enhanced navbar with authentication"""
    access_tier = user_info.get('access_tier', 1) if user_info else 1
    
    # Build navigation items based on access tier
    nav_items = []
    
    # Public items (Tier 1+)
    nav_items.extend([
        dbc.NavItem(dbc.NavLink("Home", href="/", style={'color': USC_COLORS['accent_yellow']})),
        dbc.NavItem(dbc.NavLink("About USC", href="/about-usc", style={'color': USC_COLORS['accent_yellow']})),
        dbc.NavItem(dbc.NavLink("Vision & Mission", href="/vision-mission", style={'color': USC_COLORS['accent_yellow']})),
        dbc.NavItem(dbc.NavLink("Governance", href="/governance", style={'color': USC_COLORS['accent_yellow']}))
    ])
    
    # Factbook items (Tier 2+)
    if access_tier >= 2:
        factbook_dropdown = dbc.DropdownMenu([
            dbc.DropdownMenuItem("Factbook Home", href="/factbook"),
            dbc.DropdownMenuItem("Enrollment Data", href="/enrollment"),
            dbc.DropdownMenuItem("Graduation Stats", href="/graduation"),
            dbc.DropdownMenuItem("HR Analytics", href="/hr-data"),
            dbc.DropdownMenuItem("Student Employment", href="/student-employment")
        ], label="Factbook", nav=True, style={'color': USC_COLORS['accent_yellow']})
        nav_items.append(factbook_dropdown)
    
    # Financial items (Tier 3+)
    if access_tier >= 3:
        financial_dropdown = dbc.DropdownMenu([
            dbc.DropdownMenuItem("Financial Dashboard", href="/financial"),
            dbc.DropdownMenuItem("Budget Analysis", href="/budget"),
            dbc.DropdownMenuItem("Revenue Reports", href="/revenue"),
            dbc.DropdownMenuItem("Endowment Funds", href="/endowments")
        ], label="Financial", nav=True, style={'color': USC_COLORS['accent_yellow']})
        nav_items.append(financial_dropdown)
    
    # Admin items (Tier 4+)
    if access_tier >= 4:
        nav_items.append(
            dbc.NavItem(dbc.NavLink("Admin", href="/admin", style={'color': USC_COLORS['accent_yellow']}))
        )
    
    # User menu
    if user_info:
        user_menu = dbc.DropdownMenu([
            dbc.DropdownMenuItem([
                html.I(className="fas fa-user me-2"),
                "My Profile"
            ], href="/profile"),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-cog me-2"),
                "Settings"
            ], href="/settings"),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-sign-out-alt me-2"),
                "Logout"
            ], id="logout-btn")
        ], label=[
            html.I(className="fas fa-user-circle me-2"),
            user_info.get('full_name', 'User')
        ], nav=True, style={'color': USC_COLORS['accent_yellow']})
        nav_items.append(user_menu)
    else:
        nav_items.append(
            dbc.NavItem(dbc.Button("Login", id="login-btn", color="outline-light", size="sm"))
        )
    
    return dbc.Navbar([
        dbc.Row([
            dbc.Col([
                dbc.NavbarBrand([
                    html.Img(src="/assets/usc-logo.png", height="40px", className="me-2"),
                    "USC Institutional Research"
                ], href="/", style={'color': USC_COLORS['accent_yellow'], 'font-weight': 'bold'})
            ], width="auto"),
            dbc.Col([
                dbc.Nav(nav_items, navbar=True, className="ms-auto")
            ])
        ], className="w-100 align-items-center")
    ], color=USC_COLORS['primary_green'], dark=True, className="mb-0", style={'min-height': '70px'})

# Export the authentication system components
__all__ = [
    'auth', 'AuthenticationManager', 'create_login_form', 'create_registration_form',
    'create_access_request_form', 'create_admin_dashboard', 'create_user_profile_page',
    'create_enhanced_navbar', 'require_auth', 'create_access_denied_page'
]
                    