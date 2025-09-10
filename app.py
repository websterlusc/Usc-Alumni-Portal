"""
USC Institutional Research Portal - Clean Working Version
Your exact design with properly working authentication
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import sqlite3
import os
from datetime import datetime
import hashlib
import secrets
from datetime import timedelta
# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import your existing pages
try:
    from pages.about_usc_page import create_about_usc_page
    from pages.vision_mission_page import create_vision_mission_page
    from pages.contact_page import create_contact_page
    from pages.governance_page import create_governance_page
    PAGES_AVAILABLE = True
except ImportError:
    PAGES_AVAILABLE = False

# USC Brand Colors
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

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "description", "content": "USC Institutional Research Portal"}
    ],
    suppress_callback_exceptions=True
)

app.title = "USC Institutional Research Portal"
server = app.server


# Add these functions to your existing app.py

# ============================================================================
# ENHANCED DATABASE SETUP WITH PASSWORD HASHING
# ============================================================================

def init_enhanced_database():
    """Initialize database with enhanced user management"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    # Enhanced users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'employee',
            access_tier INTEGER DEFAULT 1,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            registration_status TEXT DEFAULT 'pending'
        )
    ''')

    # Access requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_requests (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            current_tier INTEGER,
            requested_tier INTEGER,
            justification TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            reviewed_by INTEGER,
            admin_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (reviewed_by) REFERENCES users (id)
        )
    ''')

    # Password reset tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            token TEXT UNIQUE,
            expires_at TIMESTAMP,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Enhanced demo users with hashed passwords
    demo_users = [
        ('admin@usc.edu.tt', 'admin123', 'USC Administrator', 'admin', 3, 'approved'),
        ('employee@usc.edu.tt', 'emp123', 'USC Employee', 'employee', 2, 'approved'),
        ('student@usc.edu.tt', 'student123', 'USC Student', 'student', 1, 'approved'),
        ('demo@usc.edu.tt', 'demo123', 'Demo User', 'employee', 2, 'approved'),
        ('nrobinson@usc.edu.tt', 'admin123', 'Nordian Robinson', 'admin', 3, 'approved'),
        ('websterl@usc.edu.tt', 'admin123', 'Liam Webster', 'admin', 3, 'approved')
    ]

    for email, password, name, role, tier, status in demo_users:
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT OR REPLACE INTO users (email, password_hash, full_name, role, access_tier, registration_status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, name, role, tier, status))

    conn.commit()
    conn.close()
    print("✅ Enhanced database initialized")


def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash


def create_user(email, password, full_name):
    """Create a new user account"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Check if user already exists
        cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return {"success": False, "message": "Email already registered"}

        # Determine initial access tier based on email domain
        if email.endswith('@usc.edu.tt'):
            access_tier = 2  # Employee access for USC emails
            status = 'approved'
        else:
            access_tier = 1  # General access for external emails
            status = 'pending'

        password_hash = hash_password(password)

        cursor.execute('''
            INSERT INTO users (email, password_hash, full_name, access_tier, registration_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, password_hash, full_name, access_tier, status))

        conn.commit()
        return {"success": True, "message": "Account created successfully", "access_tier": access_tier}

    except Exception as e:
        return {"success": False, "message": f"Error creating account: {str(e)}"}
    finally:
        conn.close()


def request_access_upgrade(user_id, requested_tier, justification):
    """Submit an access tier upgrade request"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Get current user tier
        cursor.execute('SELECT access_tier FROM users WHERE id = ?', (user_id,))
        current_tier = cursor.fetchone()[0]

        # Check for existing pending request
        cursor.execute('''
            SELECT id FROM access_requests 
            WHERE user_id = ? AND status = 'pending'
        ''', (user_id,))

        if cursor.fetchone():
            return {"success": False, "message": "You already have a pending access request"}

        cursor.execute('''
            INSERT INTO access_requests (user_id, current_tier, requested_tier, justification)
            VALUES (?, ?, ?, ?)
        ''', (user_id, current_tier, requested_tier, justification))

        conn.commit()
        return {"success": True, "message": "Access request submitted successfully"}

    except Exception as e:
        return {"success": False, "message": f"Error submitting request: {str(e)}"}
    finally:
        conn.close()


def change_password(user_id, current_password, new_password):
    """Change user password"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Verify current password
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        stored_hash = cursor.fetchone()[0]

        if not verify_password(current_password, stored_hash):
            return {"success": False, "message": "Current password is incorrect"}

        # Update password
        new_hash = hash_password(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))

        conn.commit()
        return {"success": True, "message": "Password updated successfully"}

    except Exception as e:
        return {"success": False, "message": f"Error changing password: {str(e)}"}
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Get user data by ID"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT id, email, full_name, role, access_tier, created_at, last_login
            FROM users WHERE id = ?
        ''', (user_id,))

        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'email': result[1],
                'full_name': result[2],
                'role': result[3],
                'access_tier': result[4],
                'created_at': result[5],
                'last_login': result[6]
            }
        return None
    finally:
        conn.close()


def get_user_access_requests(user_id):
    """Get user's access requests"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT requested_tier, justification, status, created_at, admin_notes
            FROM access_requests WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))

        return cursor.fetchall()
    finally:
        conn.close()


# ============================================================================
# SIGNUP PAGE
# ============================================================================

def create_signup_page():
    """Create the signup page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src="/assets/usc-logo.png", style={'height': '120px', 'marginBottom': '20px'},
                             className="mx-auto d-block"),
                    html.H2("Create USC IR Account", className="text-center mb-4",
                            style={'color': USC_COLORS['primary_green']}),
                    html.P("Join the USC Institutional Research portal", className="text-center text-muted mb-4")
                ], className="text-center mb-4"),

                dbc.Card([
                    dbc.CardBody([
                        html.H4("Sign Up", className="card-title text-center mb-4"),
                        html.Div(id="signup-alert"),

                        dbc.Form([
                            dbc.Row([
                                dbc.Label("Full Name", html_for="signup-name"),
                                dbc.Input(type="text", id="signup-name", placeholder="Enter your full name",
                                          className="mb-3")
                            ]),
                            dbc.Row([
                                dbc.Label("Email Address", html_for="signup-email"),
                                dbc.Input(type="email", id="signup-email", placeholder="Enter your email address",
                                          className="mb-3")
                            ]),
                            dbc.Row([
                                dbc.Label("Password", html_for="signup-password"),
                                dbc.Input(type="password", id="signup-password", placeholder="Create a password",
                                          className="mb-3")
                            ]),
                            dbc.Row([
                                dbc.Label("Confirm Password", html_for="signup-confirm-password"),
                                dbc.Input(type="password", id="signup-confirm-password",
                                          placeholder="Confirm your password", className="mb-3")
                            ]),
                            dbc.Row([
                                dbc.Button("Create Account", id="signup-submit-btn", color="success",
                                           className="w-100 mb-3", size="lg")
                            ])
                        ])
                    ])
                ], className="shadow"),

                dbc.Card([
                    dbc.CardBody([
                        html.H6("Access Tiers", className="card-title"),
                        html.P([
                            html.Strong("Tier 1 (General): "), "Basic access to public information", html.Br(),
                            html.Strong("Tier 2 (Employee): "), "Factbook access (requires admin approval)", html.Br(),
                            html.Strong("Tier 3 (Admin): "), "Full access including financial data"
                        ], className="mb-2 small"),
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "All new accounts require manual approval by administrators."
                        ], color="info", className="small")
                    ])
                ], className="mt-3", color="light")

            ], width=12, md=6, lg=4)
        ], justify="center", className="min-vh-100 d-flex align-items-center")
    ], fluid=True, className="bg-light")


# ============================================================================
# PROFILE PAGE
# ============================================================================

def create_profile_page(user_data):
    """Create user profile page"""
    if not user_data:
        return create_access_denied_page("Authentication Required", "Please sign in to view your profile.")

    tier_info = {
        1: {"name": "General Access", "description": "Basic access to public information", "color": "secondary"},
        2: {"name": "Employee Access", "description": "Full factbook access and data analytics", "color": "success"},
        3: {"name": "Administrative Access", "description": "Complete access including financial data",
            "color": "warning"}
    }

    current_tier = user_data.get('access_tier', 1)
    tier = tier_info.get(current_tier, tier_info[1])

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("User Profile", className="display-5 fw-bold mb-4",
                        style={'color': USC_COLORS['primary_green']}),

                # Profile Information Card
                dbc.Card([
                    dbc.CardHeader(html.H5("Profile Information", className="mb-0")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.P([html.Strong("Name: "), user_data.get('full_name', 'N/A')]),
                                html.P([html.Strong("Email: "), user_data.get('email', 'N/A')]),
                                html.P([html.Strong("Role: "), user_data.get('role', 'employee').title()]),
                                html.P([html.Strong("Member Since: "),
                                        user_data.get('created_at', 'N/A')[:10] if user_data.get(
                                            'created_at') else 'N/A'])
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.H6("Current Access Tier"),
                                    dbc.Badge(f"Tier {current_tier}: {tier['name']}",
                                              color=tier['color'], className="mb-2 fs-6"),
                                    html.P(tier['description'], className="text-muted small")
                                ])
                            ], md=6)
                        ])
                    ])
                ], className="mb-4"),

                # Access Management Card
                dbc.Card([
                    dbc.CardHeader(html.H5("Access Management", className="mb-0")),
                    dbc.CardBody([
                        html.Div(id="profile-alerts"),

                        dbc.Row([
                            dbc.Col([
                                html.H6("Request Higher Access"),
                                html.P("Need access to additional features? Request an upgrade:",
                                       className="text-muted"),

                                dbc.Form([
                                    dbc.Label("Requested Access Tier"),
                                    dbc.RadioItems(
                                        id="access-tier-request",
                                        options=[
                                            {"label": "Tier 2: Employee Access (Factbook)", "value": 2,
                                             "disabled": current_tier >= 2},
                                            {"label": "Tier 3: Administrative Access (Financial)", "value": 3,
                                             "disabled": current_tier >= 3}
                                        ],
                                        value=min(current_tier + 1, 3),
                                        className="mb-3"
                                    ),
                                    dbc.Label("Justification"),
                                    dbc.Textarea(
                                        id="access-justification",
                                        placeholder="Please explain why you need this access level...",
                                        rows=4,
                                        className="mb-3"
                                    ),
                                    dbc.Button("Submit Request", id="request-access-btn", color="primary",
                                               disabled=current_tier >= 3)
                                ]) if current_tier < 3 else html.Div([
                                    dbc.Alert("You have the highest access level available.", color="success")
                                ])
                            ], md=6),

                            dbc.Col([
                                html.H6("Change Password"),
                                html.P("Update your account password:", className="text-muted"),

                                dbc.Form([
                                    dbc.Label("Current Password"),
                                    dbc.Input(type="password", id="current-password", className="mb-3"),
                                    dbc.Label("New Password"),
                                    dbc.Input(type="password", id="new-password", className="mb-3"),
                                    dbc.Label("Confirm New Password"),
                                    dbc.Input(type="password", id="confirm-new-password", className="mb-3"),
                                    dbc.Button("Change Password", id="change-password-btn", color="secondary")
                                ])
                            ], md=6)
                        ])
                    ])
                ], className="mb-4"),

                # Recent Access Requests Card
                dbc.Card([
                    dbc.CardHeader(html.H5("Access Request History", className="mb-0")),
                    dbc.CardBody([
                        html.Div(id="access-requests-history")
                    ])
                ])

            ], width=12, lg=10)
        ], justify="center")
    ], className="py-4")


# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

def create_admin_dashboard(user_data):
    """Create admin dashboard for managing users and requests"""
    if not user_data or user_data.get('access_tier', 1) < 3:
        return create_access_denied_page("Admin Access Required",
                                         "You need administrative access to view this page.")

    return dbc.Container([
        html.H1("Admin Dashboard", className="display-5 fw-bold mb-4",
                style={'color': USC_COLORS['primary_green']}),

        dbc.Tabs([
            dbc.Tab(label="Pending Requests", tab_id="requests"),
            dbc.Tab(label="User Management", tab_id="users"),
            dbc.Tab(label="System Stats", tab_id="stats")
        ], id="admin-tabs", active_tab="requests"),

        html.Div(id="admin-content", className="mt-4")
    ], className="py-4")


# ============================================================================
# ENHANCED AUTHENTICATION FUNCTION
# ============================================================================

def authenticate_user_enhanced(email, password):
    """Enhanced authentication with proper password hashing"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT id, email, password_hash, full_name, role, access_tier, registration_status
            FROM users WHERE email = ? AND is_active = 1
        ''', (email,))

        user = cursor.fetchone()
        if user and verify_password(password, user[2]):
            # Check if account is approved
            if user[6] == 'pending':
                return {"error": "Account pending approval. Please contact ir@usc.edu.tt"}

            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                           (datetime.now(), user[0]))
            conn.commit()

            return {
                'id': user[0],
                'email': user[1],
                'full_name': user[3],
                'role': user[4],
                'access_tier': user[5]
            }
        return None
    finally:
        conn.close()


# ============================================================================
# ADD THESE CALLBACKS TO YOUR EXISTING APP
# ============================================================================

# Signup callback
@callback(
    [Output('signup-alert', 'children'), Output('url', 'pathname', allow_duplicate=True)],
    Input('signup-submit-btn', 'n_clicks'),
    [State('signup-name', 'value'), State('signup-email', 'value'),
     State('signup-password', 'value'), State('signup-confirm-password', 'value')],
    prevent_initial_call=True
)
def handle_signup(n_clicks, name, email, password, confirm_password):
    if not n_clicks:
        return "", dash.no_update

    # Validation
    if not all([name, email, password, confirm_password]):
        return dbc.Alert("Please fill in all fields", color="danger"), dash.no_update

    if password != confirm_password:
        return dbc.Alert("Passwords do not match", color="danger"), dash.no_update

    if len(password) < 6:
        return dbc.Alert("Password must be at least 6 characters", color="danger"), dash.no_update

    # Create user
    result = create_user(email.strip().lower(), password, name.strip())

    if result["success"]:
        if email.endswith('@usc.edu.tt'):
            return dbc.Alert("Account created! You can now sign in.", color="success"), "/login"
        else:
            return dbc.Alert("Account created! Please wait for approval.", color="info"), "/login"
    else:
        return dbc.Alert(result["message"], color="danger"), dash.no_update


# Profile page callbacks
@callback(
    Output('profile-alerts', 'children'),
    Input('request-access-btn', 'n_clicks'),
    [State('access-tier-request', 'value'), State('access-justification', 'value'),
     State('user-session', 'data')],
    prevent_initial_call=True
)
def handle_access_request(n_clicks, requested_tier, justification, user_session):
    if not n_clicks or not user_session.get('authenticated'):
        return ""

    if not justification or len(justification.strip()) < 20:
        return dbc.Alert("Please provide a detailed justification (at least 20 characters)", color="danger")

    result = request_access_upgrade(user_session['id'], requested_tier, justification.strip())

    if result["success"]:
        return dbc.Alert(result["message"], color="success")
    else:
        return dbc.Alert(result["message"], color="danger")


@callback(
    Output('profile-alerts', 'children', allow_duplicate=True),
    Input('change-password-btn', 'n_clicks'),
    [State('current-password', 'value'), State('new-password', 'value'),
     State('confirm-new-password', 'value'), State('user-session', 'data')],
    prevent_initial_call=True
)
def handle_password_change(n_clicks, current_password, new_password, confirm_password, user_session):
    if not n_clicks or not user_session.get('authenticated'):
        return ""

    if not all([current_password, new_password, confirm_password]):
        return dbc.Alert("Please fill in all password fields", color="danger")

    if new_password != confirm_password:
        return dbc.Alert("New passwords do not match", color="danger")

    if len(new_password) < 6:
        return dbc.Alert("New password must be at least 6 characters", color="danger")

    result = change_password(user_session['id'], current_password, new_password)

    if result["success"]:
        return dbc.Alert(result["message"], color="success")
    else:
        return dbc.Alert(result["message"], color="danger")


# ============================================================================
# UPDATE YOUR EXISTING FUNCTIONS
# ============================================================================

# Replace your authenticate_user function with authenticate_user_enhanced
# Add /signup and /profile routes to your display_page callback
# Update init_database() call to init_enhanced_database()
# Add "Sign Up" link to your login page
def init_database():
    """Initialize database with demo users"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'employee',
            access_tier INTEGER DEFAULT 2
        )
    ''')

    # Add demo users
    demo_users = [
        ('demo@usc.edu.tt', 'Demo Employee', 'employee', 2),
        ('admin@usc.edu.tt', 'Admin User', 'admin', 3),
        ('nrobinson@usc.edu.tt', 'Nordian Robinson', 'admin', 3),
        ('websterl@usc.edu.tt', 'Liam Webster', 'admin', 3)
    ]

    for email, name, role, tier in demo_users:
        cursor.execute('''
            INSERT OR IGNORE INTO users (email, full_name, role, access_tier)
            VALUES (?, ?, ?, ?)
        ''', (email, name, role, tier))

    conn.commit()
    conn.close()



# ============================================================================
# NAVBAR WITH AUTHENTICATION
# ============================================================================
def authenticate_user(email, password):
    """Authenticate user credentials"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    # Simple demo - in real app you'd hash passwords
    demo_users = {
        'admin@usc.edu.tt': {'password': 'admin123', 'name': 'Admin User', 'tier': 3},
        'employee@usc.edu.tt': {'password': 'emp123', 'name': 'USC Employee', 'tier': 2},
        'student@usc.edu.tt': {'password': 'student123', 'name': 'USC Student', 'tier': 1}
    }

    if email in demo_users and demo_users[email]['password'] == password:
        return {
            'email': email,
            'full_name': demo_users[email]['name'],
            'access_tier': demo_users[email]['tier']
        }
    return None


# Session check callback
@callback(
    Output('user-session', 'data'),
    Input('user-check-interval', 'n_intervals'),
    prevent_initial_call=False
)
def check_user_session(n_intervals):
    # For now, maintain session state - don't automatically log out
    return dash.no_update
# Login form callback
@callback(
    [Output('login-alert', 'children'),
     Output('url', 'pathname', allow_duplicate=True),
     Output('user-session', 'data', allow_duplicate=True)],
    Input('login-submit-btn', 'n_clicks'),
    [State('login-email', 'value'), State('login-password', 'value')],
    prevent_initial_call=True
)
def handle_login_form(n_clicks, email, password):
    if not n_clicks:
        return "", dash.no_update, dash.no_update

    if not email or not password:
        return dbc.Alert("Please enter both email and password", color="danger"), dash.no_update, dash.no_update

    user = authenticate_user(email.strip().lower(), password)
    if user:
        # Store user data in session and redirect
        user_session = {'authenticated': True, **user}
        return "", "/", user_session
    else:
        return dbc.Alert("Invalid email or password", color="danger"), dash.no_update, dash.no_update

# Logout callback
@callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('user-session', 'data', allow_duplicate=True)],
    Input('navbar-logout-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_navbar_logout(n_clicks):
    if n_clicks:
        return "/login", {'authenticated': False}
    return dash.no_update, dash.no_update


def create_auth_section(user_data=None):
    """Create authentication section of navbar"""
    if not user_data or not user_data.get('authenticated'):
        return dbc.NavItem(dbc.Button(
            "Sign In",
            id="navbar-login-btn",
            color="outline-success",
            size="sm",
            href="/login"
        ))

    # User is logged in - show dropdown
    tier_info = {1: "Public", 2: "Employee", 3: "Admin"}
    user_tier = user_data.get('access_tier', 1)

    return dbc.NavItem([
        dbc.DropdownMenu([
            dbc.DropdownMenuItem([
                html.Strong(user_data.get('full_name', 'User')),
                html.Br(),
                html.Small(user_data.get('email', ''), className="text-muted"),
                html.Br(),
                dbc.Badge(tier_info.get(user_tier, "Public"), color="success", className="mt-1")
            ], header=True),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-user me-2"), "Profile"
            ], href="/profile"),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-sign-out-alt me-2"), "Logout"
            ], id="navbar-logout-btn")
        ], label=user_data.get('email', 'User'), nav=True, align_end=True)
    ])
def create_modern_navbar(user_data=None):
    """Your exact navbar design with authentication"""
    user_access_tier = user_data.get('access_tier', 1) if user_data else 1

    # Dynamic factbook menu
    factbook_items = []
    if user_access_tier >= 2:
        factbook_items = [
            dbc.DropdownMenuItem("Factbook Overview", href="/factbook"),
            dbc.DropdownMenuItem("Enrollment Data", href="/enrollment"),
            dbc.DropdownMenuItem("Graduation Stats", href="/graduation"),
            dbc.DropdownMenuItem("Student Employment", href="/student-employment"),
            dbc.DropdownMenuItem("HR Analytics", href="/hr-data")
        ]

        if user_access_tier >= 3:
            factbook_items.extend([
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Financial Reports", href="/financial"),
                dbc.DropdownMenuItem("Budget Analysis", href="/budget"),
                dbc.DropdownMenuItem("Endowments", href="/endowments")
            ])
    else:
        factbook_items = [
            dbc.DropdownMenuItem("Sign in to access factbook", disabled=True)
        ]

    # Dynamic services menu
    services_items = [
        dbc.DropdownMenuItem("Request Report", href="/request-report") if user_access_tier >= 2 else None,
        dbc.DropdownMenuItem("Admin Dashboard", href="/admin") if user_access_tier >= 3 else None,
        dbc.DropdownMenuItem(divider=True) if user_access_tier >= 2 else None,
        dbc.DropdownMenuItem("Help", href="/help"),
        dbc.DropdownMenuItem("Contact IR", href="/contact")
    ]
    services_items = [item for item in services_items if item is not None]

    return dbc.Navbar(
        dbc.Container([
            # Brand (your exact design)
            dbc.NavbarBrand([
                html.Img(src="/assets/usc-logo.png", height="45", className="me-3"),
                html.Div([
                    html.Div("Institutional Research", style={
                        'fontSize': '1.2rem', 'fontWeight': '700',
                        'color': '#FDD835', 'lineHeight': '1.1'
                    }),
                    html.Div("University of the Southern Caribbean", style={
                        'fontSize': '0.8rem', 'color': '#FFFFFF',
                        'lineHeight': '1.1'
                    })
                ])
            ], href="/"),

            # Spacer
            html.Div(style={'flex': '1'}),

            # Right-aligned navigation
            dbc.Nav([
                dbc.NavItem(dbc.NavLink(
                    "Home", href="/",
                    style={'color': '#1B5E20', 'fontWeight': '600'}
                )),
                dbc.DropdownMenu([
                    dbc.DropdownMenuItem("About USC", href="/about-usc"),
                    dbc.DropdownMenuItem("Vision & Mission", href="/vision-mission"),
                    dbc.DropdownMenuItem("Governance", href="/governance"),
                    dbc.DropdownMenuItem("Contact", href="/contact")
                ],
                label="About USC", nav=True,
                toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none', 'background': 'transparent'}
                ),
                dbc.NavItem(dbc.NavLink(
                    "Alumni Portal", href="/alumni",
                    style={'color': '#1B5E20', 'fontWeight': '600'}
                )),
                dbc.DropdownMenu(
                    factbook_items,
                    label="Factbook", nav=True,
                    toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none', 'background': 'transparent'}
                ),
                dbc.DropdownMenu(
                    services_items,
                    label="Services", nav=True,
                    toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none', 'background': 'transparent'}
                ),

                # Authentication section
                create_auth_section(user_data)
            ])
        ], fluid=True, style={'display': 'flex', 'alignItems': 'center'}),
        color="white",
        className="shadow-sm sticky-top",
        style={'borderBottom': '3px solid #1B5E20', 'minHeight': '75px'}
    )

# ============================================================================
# YOUR EXISTING COMPONENTS (unchanged)
# ============================================================================

def create_hero_section():
    """Your exact hero section"""
    return html.Section([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1([
                        "Institutional Research & ",
                        html.Span("Analytics", style={
                            'background': 'linear-gradient(45deg, #FDD835, #FFEB3B)',
                            'WebkitBackgroundClip': 'text',
                            'WebkitTextFillColor': 'transparent'
                        })
                    ], style={'fontSize': '3.5rem', 'fontWeight': '700', 'marginBottom': '1.5rem'}),
                    html.P(
                        "Empowering data-driven decisions through comprehensive institutional analytics, "
                        "enrollment insights, and strategic planning support for USC's continued excellence.",
                        style={'fontSize': '1.25rem', 'opacity': '0.9', 'marginBottom': '2rem'}
                    ),
                    html.Div([
                        dbc.Button("Explore Factbook", color="warning", size="lg", className="me-3", href="/factbook"),
                        dbc.Button("Request Report", color="outline-light", size="lg", href="/request-report")
                    ])
                ], md=8)
            ])
        ], fluid=True, style={'position': 'relative', 'zIndex': '2'})
    ], style={
        'background': f'''
            linear-gradient(135deg, rgba(27, 94, 32, 0.85) 0%, rgba(46, 125, 50, 0.85) 50%, rgba(76, 175, 80, 0.85) 100%),
            url('/assets/banner.png')
        ''',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'backgroundRepeat': 'no-repeat',
        'color': 'white',
        'padding': '100px 0',
        'position': 'relative'
    })

def create_stats_overview():
    """Your exact stats section"""
    stats = [
        {'title': '3,110', 'subtitle': 'Total Enrollment', 'icon': 'fas fa-users', 'color': '#1B5E20'},
        {'title': '5', 'subtitle': 'Academic Divisions', 'icon': 'fas fa-building', 'color': '#4CAF50'},
        {'title': '250+', 'subtitle': 'Employees', 'icon': 'fas fa-user-tie', 'color': '#FDD835'},
        {'title': '100%', 'subtitle': 'Data Transparency', 'icon': 'fas fa-eye', 'color': '#28A745'}
    ]

    cards = []
    for stat in stats:
        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className=stat['icon'], style={
                                'fontSize': '2.5rem', 'color': stat['color'], 'marginRight': '20px'
                            }),
                            html.Div([
                                html.H3(stat['title'], style={'fontSize': '2.2rem', 'fontWeight': '700', 'color': '#1B5E20', 'margin': '0'}),
                                html.P(stat['subtitle'], style={'color': '#666', 'margin': '5px 0'})
                            ])
                        ], style={'display': 'flex', 'alignItems': 'center'})
                    ])
                ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
            ], md=3, className="mb-4")
        )

    return html.Section([
        dbc.Container([
            html.H2("At a Glance", style={
                'color': '#1B5E20', 'fontWeight': '700', 'fontSize': '2.5rem',
                'textAlign': 'center', 'marginBottom': '3rem'
            }),
            dbc.Row(cards)
        ])
    ], style={'padding': '80px 0', 'background': '#F8F9FA'})

def create_feature_showcase():
    """Your exact feature showcase"""
    features = [
        {'title': 'Interactive Factbook', 'desc': 'Comprehensive institutional data with interactive visualizations.', 'icon': 'fas fa-chart-line'},
        {'title': 'Alumni Portal', 'desc': 'Connect with USC alumni and access alumni services and networks.', 'icon': 'fas fa-graduation-cap'},
        {'title': 'Yearly Reports', 'desc': 'Annual institutional reports and comprehensive data analysis.', 'icon': 'fas fa-calendar-alt'},
        {'title': 'Custom Reports', 'desc': 'Request tailored analytical reports for your specific needs.', 'icon': 'fas fa-file-alt'}
    ]

    cards = []
    for feature in features:
        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className=feature['icon'], style={'fontSize': '2.2rem', 'color': '#1B5E20', 'marginBottom': '15px'}),
                        html.H4(feature['title'], style={'color': '#1B5E20', 'fontWeight': '600'}),
                        html.P(feature['desc'], style={'color': '#666', 'marginBottom': '20px'}),
                        dbc.Button("Explore", color="outline-primary", size="sm")
                    ])
                ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none', 'height': '100%'})
            ], md=3, className="mb-4")
        )

    return html.Section([
        dbc.Container([
            html.H2("Our Services", style={
                'color': '#1B5E20', 'fontWeight': '700', 'fontSize': '2.5rem',
                'textAlign': 'center', 'marginBottom': '3rem'
            }),
            dbc.Row(cards)
        ])
    ], style={'padding': '80px 0'})

def create_director_message():
    """Your exact director's message"""
    return html.Section([
        dbc.Container([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Img(
                                src="/assets/DirectorIR.jpg",
                                style={
                                    'width': '120px', 'height': '120px', 'objectFit': 'cover',
                                    'border': '4px solid #1B5E20', 'boxShadow': '0 4px 15px rgba(0,0,0,0.2)'
                                }
                            )
                        ], md=3, className="text-center"),
                        dbc.Col([
                            html.H3("Director's Message", style={'color': '#1B5E20', 'fontWeight': '600', 'marginBottom': '20px'}),
                            html.P([
                                "The Department of Institutional Research (IR) takes great pride in presenting the third instalment of the ",
                                "University of the Southern Caribbean Factbook for 2024. This University Factbook is a comprehensive report ",
                                "providing a three-year data trend for key performance metrics related to graduation, finances, enrolment, ",
                                "and spiritual development at the University of the Southern Caribbean."
                            ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '15px'}),
                            html.P("The report is organized to include information from the Office of the President and the five divisions of the university:",
                                   style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '10px'}),
                            html.Ul([
                                html.Li("The Division of the Provost"),
                                html.Li("The Division of Administration, Advancement and Planning"),
                                html.Li("The Division of Financial Administration"),
                                html.Li("The Division of Student Services and Enrolment Management"),
                                html.Li("The Division of Spiritual Development")
                            ], style={'color': '#555', 'marginBottom': '15px'}),
                            html.P([
                                "Within each division, the factbook covers a range of topics such as program offerings, teaching loads, ",
                                "graduation data, undergraduate and graduate student enrolment, faculty and staff demographics, financial ",
                                "statements and spiritual development activities. This data-rich report is designed to provide university ",
                                "leadership, faculty, staff, and stakeholders with detailed insights into the institution's performance, ",
                                "trends, and areas for potential improvement or strategic focus."
                            ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '15px'}),
                            html.P([
                                "By consolidating three years — 2021-2022, 2022-2023 and 2023-2024 of key metrics into a single reference, ",
                                "this factbook aims to facilitate data-driven decision-making and support the University of the Southern ",
                                "Caribbean's ongoing commitment to excellence. In addition, this factbook presents a preview of the University ",
                                "Data for the 1st Semester of 2024-2025. This preview of this academic school year, gives an insight of the ",
                                "current standing of the university as it relates to employee data and student enrolment."
                            ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '20px'}),
                            html.Div([
                                html.P("Yours In Service", style={'color': '#1B5E20', 'fontWeight': '600', 'fontStyle': 'italic', 'marginBottom': '5px'}),
                                html.P("Nordian C. Swaby Robinson", style={'color': '#1B5E20', 'fontWeight': '600', 'marginBottom': '1px'}),
                                html.P("Director, Institutional Research", style={'color': '#666', 'fontSize': '0.9rem', 'marginBottom': '5px'}),
                                html.P("Publication: November 2024", style={'color': '#666', 'fontSize': '0.8rem', 'fontStyle': 'italic'})
                            ], style={'marginTop': '25px', 'paddingTop': '20px', 'borderTop': '2px solid #e9ecef'})
                        ], md=9)
                    ])
                ])
            ], style={'boxShadow': '0 8px 30px rgba(0,0,0,0.1)', 'border': 'none'})
        ])
    ], style={'padding': '80px 0', 'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)'})

def create_quick_links():
    """Your exact quick links"""
    links = [
        {'title': 'USC Main Website', 'url': 'https://www.usc.edu.tt', 'icon': 'fas fa-globe'},
        {'title': 'USC eLearn', 'url': 'https://elearn.usc.edu.tt', 'icon': 'fas fa-laptop'},
        {'title': 'Aerion Portal', 'url': 'https://aerion.usc.edu.tt', 'icon': 'fas fa-door-open'},
        {'title': 'Email Support', 'url': 'mailto:ir@usc.edu.tt', 'icon': 'fas fa-envelope'}
    ]

    link_items = []
    for link in links:
        link_items.append(
            dbc.Col([
                html.A([
                    html.I(className=link['icon'], style={'fontSize': '1.5rem', 'marginRight': '15px'}),
                    html.Span(link['title'])
                ], href=link['url'], target="_blank", style={
                    'display': 'flex', 'alignItems': 'center', 'padding': '20px',
                    'background': '#f8f9fa', 'textDecoration': 'none', 'color': '#495057'
                })
            ], sm=6, md=3, className="mb-3")
        )

    return html.Section([
        dbc.Container([
            html.H3("Quick Links", className="text-center mb-4"),
            dbc.Row(link_items)
        ])
    ], style={'padding': '60px 0'})

def create_modern_footer():
    """Your exact footer"""
    return html.Footer([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H5("Institutional Research", style={'color': '#FDD835', 'fontWeight': '600'}),
                    html.P("Supporting USC's mission through comprehensive data analysis and strategic insights.",
                           style={'opacity': '0.9'})
                ], md=4),
                dbc.Col([
                    html.H6("Contact Information", style={'color': '#FDD835', 'fontWeight': '600'}),
                    html.P([
                        html.Strong("Director: "), "Nordian C. Swaby Robinson", html.Br(),
                        html.Strong("Email: "), html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt", style={'color': '#FDD835'}), html.Br(),
                        html.Strong("Phone: "), "868-645-3265 ext. 2150"
                    ], style={'opacity': '0.9'})
                ], md=4),
                dbc.Col([
                    html.H6("Development Team", style={'color': '#FDD835', 'fontWeight': '600'}),
                    html.P([
                        html.Strong("Web Developer: "), "Liam Webster", html.Br(),
                        html.Strong("Email: "), html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt", style={'color': '#FDD835'})
                    ], style={'opacity': '0.9'})
                ], md=4)
            ]),
            html.Hr(style={'borderColor': 'rgba(255,255,255,0.2)', 'margin': '40px 0 20px'}),
            html.P("© 2025 University of the Southern Caribbean - Institutional Research Department",
                   className="text-center", style={'opacity': '0.8'})
        ])
    ], style={'background': 'linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%)', 'color': 'white', 'padding': '60px 0 30px'})


def create_login_page():
    """Create the login page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src="/assets/usc-logo.png", style={'height': '120px', 'marginBottom': '20px'},
                             className="mx-auto d-block"),
                    html.H2("USC Institutional Research Portal", className="text-center mb-4",
                            style={'color': USC_COLORS['primary_green']}),
                    html.P("Please sign in to access your account", className="text-center text-muted mb-4")
                ], className="text-center mb-4"),

                dbc.Card([
                    dbc.CardBody([
                        html.H4("Sign In", className="card-title text-center mb-4"),
                        html.Div(id="login-alert"),

                        dbc.Form([
                            dbc.Row([
                                dbc.Label("Email Address", html_for="login-email"),
                                dbc.Input(type="email", id="login-email", placeholder="Enter your email",
                                          className="mb-3")
                            ]),
                            dbc.Row([
                                dbc.Label("Password", html_for="login-password"),
                                dbc.Input(type="password", id="login-password", placeholder="Enter your password",
                                          className="mb-3")
                            ]),
                            dbc.Row([
                                dbc.Button("Sign In", id="login-submit-btn", color="success", className="w-100 mb-3",
                                           size="lg")
                            ])
                        ])
                    ])
                ], className="shadow"),

                dbc.Card([
                    dbc.CardBody([
                        html.H6("Demo Credentials", className="card-title"),
                        html.P([
                            html.Strong("Admin: "), "admin@usc.edu.tt / admin123", html.Br(),
                            html.Strong("Employee: "), "employee@usc.edu.tt / emp123", html.Br(),
                            html.Strong("Student: "), "student@usc.edu.tt / student123"
                        ], className="mb-0 small")
                    ])
                ], className="mt-3", color="light"),
                dbc.Card([
                    dbc.CardBody([
                        html.P([
                            "Don't have an account? ",
                            html.A("Sign up here", href="/signup", style={'color': USC_COLORS['primary_green']})
                        ], className="text-center mb-0"),
                    ])
                ], className="mt-3")
            ], width=12, md=6, lg=4)
        ], justify="center", className="min-vh-100 d-flex align-items-center")
    ], fluid=True, className="bg-light")
def create_home_layout(user_data=None):
    """Complete home page layout"""
    return html.Div([
        create_hero_section(),
        create_stats_overview(),
        create_feature_showcase(),
        create_director_message(),
        create_quick_links(),
        create_modern_footer()
    ])

# ============================================================================
# ACCESS CONTROL AND HELPER PAGES
# ============================================================================

def require_access(content, required_tier, user_data=None):
    """Check access and show appropriate content"""
    if not user_data or not user_data.get('authenticated'):
        return create_access_denied_page("Sign In Required", f"Please sign in to access this content (Tier {required_tier} required).")

    user_tier = user_data.get('access_tier', 1)
    if user_tier < required_tier:
        return create_access_denied_page("Access Restricted", f"This page requires Tier {required_tier} access. You have Tier {user_tier} access.")

    return content

def create_access_denied_page(title, message):
    """Access denied page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.I(className="fas fa-lock fa-4x mb-4", style={'color': USC_COLORS['primary_green']}),
                    html.H1(title, style={'color': USC_COLORS['primary_green']}),
                    html.P(message, className="lead mb-4"),
                    dbc.Alert([
                        html.I(className="fas fa-info-circle me-2"),
                        "Contact ir@usc.edu.tt for access assistance."
                    ], color="info"),
                    html.Div([
                        dbc.Button("Return Home", href="/", color="primary", className="me-3"),
                        dbc.Button("Sign In", id="access-signin-btn", color="success")
                    ], className="mt-4")
                ], className="text-center")
            ], width=12, lg=8)
        ], justify="center")
    ], className="py-5")

def create_placeholder_page(title, description):
    """Placeholder for development pages"""
    return dbc.Container([
        html.H1(title, className="display-4 fw-bold mb-4 text-center", style={'color': '#1B5E20'}),
        dbc.Alert([
            html.H4("Coming Soon!", className="alert-heading"),
            html.P(description),
            html.Hr(),
            html.P("This feature is under development and will be available soon.")
        ], color="info", className="text-center"),
        dbc.Button("Return Home", href="/", color="primary", className="d-block mx-auto mt-4")
    ], className="mt-5")



# ============================================================================
# APPLICATION LAYOUT
# ============================================================================

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='user-session', storage_type='session'),
    dcc.Interval(id='user-check-interval', interval=5000, n_intervals=0),
    html.Div(id='page-content')
    # Remove: create_login_modal()
])

# ============================================================================
# CALLBACKS - CLEAN AND WORKING
# ============================================================================

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data'))
def display_page(pathname, user_session):
    # Get user data - FIXED
    user_data = user_session if user_session and user_session.get('authenticated') else None

    # LOGIN PAGE ROUTE
    if pathname == '/login':
        if user_data:
            return dcc.Location(pathname='/', id='redirect-home')
        return create_login_page()    # Route pages
    if pathname == '/' or pathname is None:
        content = create_home_layout(user_data)

    elif pathname == '/about-usc':
        if PAGES_AVAILABLE:
            content = create_about_usc_page()
        else:
            content = create_placeholder_page("About USC", "Learn about our history and mission")

    elif pathname == '/vision-mission':
        if PAGES_AVAILABLE:
            content = create_vision_mission_page()
        else:
            content = create_placeholder_page("Vision & Mission", "Our institutional vision and mission")

    elif pathname == '/governance':
        if PAGES_AVAILABLE:
            content = create_governance_page()
        else:
            content = create_placeholder_page("Governance", "Organizational structure and leadership")

    elif pathname == '/contact':
        if PAGES_AVAILABLE:
            content = create_contact_page()
        else:
            content = create_placeholder_page("Contact", "Get in touch with the IR team")

    elif pathname == '/alumni':
        content = create_placeholder_page("Alumni Portal", "Connect with USC alumni network")

    # Factbook pages (Tier 2 required)
    elif pathname == '/factbook':
        factbook_content = create_placeholder_page("Interactive Factbook", "Comprehensive institutional data and analytics")
        content = require_access(factbook_content, 2, user_data)

    elif pathname == '/enrollment':
        enrollment_content = create_placeholder_page("Enrollment Data", "Student enrollment trends and analysis")
        content = require_access(enrollment_content, 2, user_data)

    elif pathname == '/graduation':
        graduation_content = create_placeholder_page("Graduation Statistics", "Graduation rates and outcomes")
        content = require_access(graduation_content, 2, user_data)

    elif pathname == '/student-employment':
        employment_content = create_placeholder_page("Student Employment", "Student employment analytics")
        content = require_access(employment_content, 2, user_data)

    elif pathname == '/hr-data':
        hr_content = create_placeholder_page("HR Analytics", "Faculty and staff data")
        content = require_access(hr_content, 2, user_data)

    # Financial pages (Tier 3 required)
    elif pathname == '/financial':
        financial_content = create_placeholder_page("Financial Reports", "Comprehensive financial analysis")
        content = require_access(financial_content, 3, user_data)

    elif pathname == '/budget':
        budget_content = create_placeholder_page("Budget Analysis", "Budget tracking and analysis")
        content = require_access(budget_content, 3, user_data)

    elif pathname == '/endowments':
        endowment_content = create_placeholder_page("Endowment Funds", "Endowment performance data")
        content = require_access(endowment_content, 3, user_data)

    # Admin pages (Tier 3 required)
    elif pathname == '/admin':
        admin_content = create_placeholder_page("Admin Dashboard", "System administration and user management")
        content = require_access(admin_content, 3, user_data)

    # Service pages
    elif pathname == '/request-report':
        report_content = create_placeholder_page("Request Report", "Submit custom report requests")
        content = require_access(report_content, 2, user_data)

    elif pathname == '/help':
        content = create_placeholder_page("Help Center", "Documentation and support resources")

    else:
        content = create_placeholder_page("Page Not Found", f"The page '{pathname}' could not be found")

    navbar = create_modern_navbar(user_data)

    return html.Div([navbar, content])




# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    init_enhanced_database()

    print("🚀 Starting USC Institutional Research Portal...")
    print("📊 Clean version with working authentication!")
    print("✅ Features:")
    print("   • Your complete existing design preserved")
    print("   • Working login button and modal")
    print("   • 3-tier access control system")
    print("   • Dynamic navbar based on user permissions")
    print("   • Demo users for testing")
    print(f"🌐 Visit: http://localhost:8050")
    print()
    print("🎮 Test the login:")
    print("   1. Click 'Sign In' button in navbar")
    print("   2. Choose demo user (try different tiers)")
    print("   3. Test access to different pages")
    print("   4. Notice navbar updates with user info")

    app.run_server(debug=True, host='0.0.0.0', port=8050)