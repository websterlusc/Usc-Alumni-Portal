"""
USC Institutional Research Portal - Clean Working Version
Your exact design with properly working authentication
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import sqlite3
import os
from dash import ALL  # Add this line
from datetime import datetime
from factbook.factbook import create_factbook_landing_page
from callback_registry import initialize_callback_registry
from callback_registry import initialize_callback_registry
import hashlib
# Load environment variables
from data_requests import (
    init_data_requests_database,
    create_data_request_page,
    create_admin_data_requests_tab
)
from components.usc_footer_component import create_usc_footer
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
from posts_system import init_posts_database
# Add these imports to the top of app.py
from posts_system import (
    init_posts_database,
    get_active_posts,
    cleanup_expired_posts
)
from posts_ui import (
    create_news_feed_section,
    create_news_page,
    create_posts_management_tab,
)
# Don't just import - explicitly register callbacks
PILL_NAV_CSS = """
/* Pill Navigation Styles */
.nav-pill {
    display: inline-flex;
    align-items: center;
    padding: 10px 24px;
    border-radius: 0px;
    background: #f5f5f5;
    border: 2px solid transparent;
    color: #424242;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    white-space: nowrap;
}

.nav-pill:hover {
    background: #e8f5e9;
    color: #1B5E20;
    border-color: #4CAF50;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(27, 94, 32, 0.2);
}

.nav-pill.active {
    background: linear-gradient(135deg, #1B5E20 0%, #388E3C 100%);
    color: white;
    border-color: #1B5E20;
    box-shadow: 0 4px 16px rgba(27, 94, 32, 0.3);
}

.nav-pill.active:hover {
    background: linear-gradient(135deg, #1B5E20 0%, #388E3C 100%);
    color: white;
    transform: translateY(-2px);
}

/* Icon styling within pills */
.nav-pill i {
    font-size: 0.9rem;
    opacity: 0.8;
}

.nav-pill.active i {
    opacity: 1;
}

/* Smooth scroll behavior */
html {
    scroll-behavior: smooth;
}

/* Optional: Hide pill nav initially, show after scroll */
.pill-nav-hidden {
    transform: translateY(-100%);
    opacity: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .nav-pill {
        padding: 8px 18px;
        font-size: 0.85rem;
    }

    #pill-nav-container {
        top: 60px !important;
    }
}
"""
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

callback_registry = initialize_callback_registry(app)
app._favicon = 'usc-logo.png'
app.title = "USC Institutional Research Portal"
server = app.server
# 2. Initialize databases
print("🔧 Initializing databases...")
try:
    from posts_system import init_posts_database
    init_posts_database()
    print("✅ Posts database initialized")
except Exception as e:
    print(f"❌ Database error: {e}")

# 3. THEN import callbacks (MUST be after app creation)
print("🔧 Importing posts callbacks...")
import posts_callbacks
print("✅ Posts callbacks import complete")
# Add this CSS for hero link hover effects
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .hero-link:hover {
                color: #FDD835 !important;
                text-decoration-color: #FDD835 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# Add these functions to your existing app.py

# ============================================================================
# ENHANCED DATABASE SETUP WITH PASSWORD HASHING
# ============================================================================

def init_enhanced_database():
    """Initialize database with enhanced user management and handle migrations"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    init_data_requests_database()

    print("✅ Enhanced database with data requests initialized")
    # Check if users table exists and what columns it has
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [column[1] for column in cursor.fetchall()]

    if not existing_columns:
        # Create new users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE users (
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
    else:
        # Add missing columns to existing table
        if 'password_hash' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN password_hash TEXT')

        if 'registration_status' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN registration_status TEXT DEFAULT "approved"')

        if 'is_active' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE')

        if 'created_at' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')

        if 'last_login' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN last_login TIMESTAMP')

    # Create access requests table
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

    # Create password reset tokens table
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

    # Update existing demo users with password hashes if they don't have them
    demo_users = [
        ('admin@usc.edu.tt', 'admin123', 'USC Administrator', 'admin', 3, 'approved'),
        ('employee@usc.edu.tt', 'emp123', 'USC Employee', 'employee', 2, 'approved'),
        ('student@usc.edu.tt', 'student123', 'USC Student', 'student', 1, 'approved'),
        ('demo@usc.edu.tt', 'demo123', 'Demo User', 'employee', 2, 'approved'),
        ('nrobinson@usc.edu.tt', 'admin123', 'Nordian Robinson', 'admin', 3, 'approved'),
        ('websterl@usc.edu.tt', 'admin123', 'Liam Webster', 'admin', 3, 'approved')
    ]

    for email, password, name, role, tier, status in demo_users:
        # Check if user exists
        cursor.execute('SELECT id, password_hash FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Update existing user if they don't have a password hash
            user_id, existing_hash = existing_user
            if not existing_hash:
                password_hash = hash_password(password)
                cursor.execute('''
                    UPDATE users 
                    SET password_hash = ?, registration_status = ?, access_tier = ?
                    WHERE id = ?
                ''', (password_hash, status, tier, user_id))
        else:
            # Create new user
            password_hash = hash_password(password)
            cursor.execute('''
                INSERT OR REPLACE INTO users (email, password_hash, full_name, role, access_tier, registration_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, name, role, tier, status))

    conn.commit()
    conn.close()
    print("✅ Enhanced database initialized with migrations")
TIER_INFO = {
    1: {"name": "Basic Access", "description": "Public information only", "color": "secondary"},
    2: {"name": "Limited Access", "description": "Basic factbook data", "color": "info"},
    3: {"name": "Complete Access", "description": "Full factbook including financial", "color": "success"},
    4: {"name": "Admin Access", "description": "System administration", "color": "warning"}
}

def get_tier_permissions(tier):
    """Get what each tier can access"""
    permissions = {
        1: ["Public pages", "About USC", "Contact info"],
        2: ["Basic factbook", "Enrollment data", "Student info"],
        3: ["Complete factbook", "Financial data", "All reports"],
        4: ["Everything", "Admin dashboard", "User management"]
    }
    return permissions.get(tier, [])
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash


def create_user_admin(email, full_name, role, access_tier, admin_id):
    """Admin creates user with email notification"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Check if user exists
        cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return {"success": False, "message": "Email already exists"}

        # Generate random password
        from auth_utils import generate_random_password, send_account_creation_email
        temp_password = generate_random_password()
        password_hash = hash_password(temp_password)

        # Create user
        cursor.execute('''
            INSERT INTO users (email, password_hash, full_name, role, access_tier, registration_status, is_active)
            VALUES (?, ?, ?, ?, ?, 'approved', 1)
        ''', (email, password_hash, full_name, role, access_tier))

        conn.commit()

        # Send email with credentials
        email_sent = send_account_creation_email(email, full_name, temp_password, "admin")

        message = f"User {full_name} created successfully"
        if email_sent:
            message += f" and credentials sent to {email}"
        else:
            message += " but email notification failed"

        return {"success": True, "message": message}

    except Exception as e:
        return {"success": False, "message": f"Error creating user: {str(e)}"}
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
                    html.Img(src="assets/usc-logo.png", style={'height': '120px', 'marginBottom': '20px'},
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
    """Updated profile page with 4-tier system"""
    if not user_data:
        return create_access_denied_page("Authentication Required", "Please sign in to view your profile.")

    navbar = create_modern_navbar(user_data)
    current_tier = user_data.get('access_tier', 1)
    tier = TIER_INFO.get(current_tier, TIER_INFO[1])

    content = dbc.Container([
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
                                       user_data.get('created_at', 'N/A')[:10] if user_data.get('created_at') else 'N/A'])
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.H6("Current Access Tier"),
                                    dbc.Badge(f"Tier {current_tier}: {tier['name']}",
                                             color=tier['color'], className="mb-2 fs-6"),
                                    html.P(tier['description'], className="text-muted small mb-2"),
                                    html.P([
                                        html.Strong("You can access: "), html.Br(),
                                        ", ".join(get_tier_permissions(current_tier))
                                    ], className="small text-success")
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

                                # Only show if user can request higher access (not admin)
                                dbc.Form([
                                    dbc.Label("Requested Access Tier"),
                                    dbc.RadioItems(
                                        id="access-tier-request",
                                        options=[
                                            {"label": "Tier 2: Limited Access", "value": 2,
                                             "disabled": current_tier >= 2},
                                            {"label": "Tier 3: Complete Access", "value": 3,
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
                                    dbc.Alert([
                                        "You have complete access. Super Admin access (Tier 4) can only be assigned by current administrators."
                                    ], color="info")
                                ]) if current_tier == 3 else html.Div([
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
                ], className="mb-4")

            ], width=12, lg=10)
        ], justify="center")
    ], className="py-4")

    return html.Div([navbar, content])

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================
# ============================================================================
# ADMIN DASHBOARD FUNCTIONS - FIXED VERSION
# ============================================================================

def get_all_users():
    """Get all users with their complete information"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT id, email, full_name, role, access_tier, registration_status, 
                   is_active, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        ''')

        return cursor.fetchall()
    finally:
        conn.close()


def get_user_statistics():
    """Get comprehensive user statistics"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        stats = {}

        # Total users by status
        cursor.execute('SELECT registration_status, COUNT(*) FROM users GROUP BY registration_status')
        stats['by_status'] = dict(cursor.fetchall())

        # Users by access tier (only approved users)
        cursor.execute(
            'SELECT access_tier, COUNT(*) FROM users WHERE registration_status = "approved" GROUP BY access_tier')
        stats['by_tier'] = dict(cursor.fetchall())

        # Active vs inactive
        cursor.execute('SELECT is_active, COUNT(*) FROM users GROUP BY is_active')
        stats['by_activity'] = dict(cursor.fetchall())

        # Recent registrations (last 30 days)
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE created_at > datetime('now', '-30 days')
        ''')
        stats['recent_registrations'] = cursor.fetchone()[0]

        # Pending requests count
        cursor.execute('SELECT COUNT(*) FROM access_requests WHERE status = "pending"')
        stats['pending_requests'] = cursor.fetchone()[0]

        return stats
    finally:
        conn.close()


def update_user_info(user_id, email, full_name, role, access_tier, is_active, admin_id):
    """Update user information"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE users 
            SET email = ?, full_name = ?, role = ?, access_tier = ?, is_active = ?
            WHERE id = ?
        ''', (email, full_name, role, access_tier, is_active, user_id))

        conn.commit()
        return {"success": True, "message": "User information updated successfully"}

    except Exception as e:
        return {"success": False, "message": f"Error updating user: {str(e)}"}
    finally:
        conn.close()


def delete_user(user_id, admin_id):
    """Delete a user account"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Don't allow deletion of the admin performing the action
        if user_id == admin_id:
            return {"success": False, "message": "Cannot delete your own account"}

        # Delete related records first
        cursor.execute('DELETE FROM access_requests WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM password_reset_tokens WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))

        conn.commit()
        return {"success": True, "message": "User deleted successfully"}

    except Exception as e:
        return {"success": False, "message": f"Error deleting user: {str(e)}"}
    finally:
        conn.close()


def reset_user_password(user_id, new_password, admin_id):
    """Admin reset of user password with email notification"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Get user details
        cursor.execute('SELECT email, full_name FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()

        if not user_data:
            return {"success": False, "message": "User not found"}

        user_email, user_name = user_data

        # Update password
        password_hash = hash_password(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        conn.commit()

        # Send email notification
        from auth_utils import send_password_reset_email
        email_sent = send_password_reset_email(user_email, user_name, new_password, "admin")

        message = "Password reset successfully"
        if email_sent:
            message += f" and notification sent to {user_email}"
        else:
            message += " but email notification failed"

        return {"success": True, "message": message}

    except Exception as e:
        return {"success": False, "message": f"Error resetting password: {str(e)}"}
    finally:
        conn.close()


def get_access_request_history():
    """Get all access requests with history"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT ar.id, u.email, u.full_name, ar.current_tier, ar.requested_tier,
                   ar.justification, ar.status, ar.created_at, ar.reviewed_at,
                   reviewer.full_name as reviewer_name, ar.admin_notes
            FROM access_requests ar
            JOIN users u ON ar.user_id = u.id
            LEFT JOIN users reviewer ON ar.reviewed_by = reviewer.id
            ORDER BY ar.created_at DESC
        ''')

        return cursor.fetchall()
    finally:
        conn.close()


# ============================================================================
# ENHANCED ADMIN DASHBOARD COMPONENTS
# ============================================================================

def create_comprehensive_admin_dashboard(user_data):
    """Create comprehensive admin dashboard"""
    if not user_data or user_data.get('access_tier', 1) < 3:
        return create_access_denied_page("Admin Access Required",
                                         "You need administrative access to view this page.")

    return dbc.Container([
        html.H1("Admin Dashboard", className="display-5 fw-bold mb-4",
                style={'color': USC_COLORS['primary_green']}),

        html.Div(id="admin-alerts", className="mb-4"),

        dbc.Tabs([
            dbc.Tab(label="Overview", tab_id="overview"),
            dbc.Tab(label="User Management", tab_id="users"),
            dbc.Tab(label="Registration Requests", tab_id="registrations"),
            dbc.Tab(label="Access Requests", tab_id="access-requests"),
            dbc.Tab(label="Data Requests", tab_id="data-requests"),
            dbc.Tab(label="Posts Management", tab_id="posts-management"),
            dbc.Tab(label="Request History", tab_id="history")
        ], id="admin-tabs", active_tab="overview"),

        html.Div(id="admin-content", className="mt-4"),
        dcc.Store(id='delete-post-id-store', storage_type='memory'),
        dcc.Store(id='posts-refresh-trigger', storage_type='memory'),
        # Edit User Modal
        dbc.Modal([
            dbc.ModalHeader("Edit User Information"),
            dbc.ModalBody([
                html.Div(id="edit-user-alerts"),
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Full Name"),
                            dbc.Input(id="edit-user-name", type="text", className="mb-3")
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Email Address"),
                            dbc.Input(id="edit-user-email", type="email", className="mb-3")
                        ], md=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Role"),
                            dbc.Select(
                                id="edit-user-role",
                                options=[
                                    {"label": "Basic", "value": "basic"},
                                    {"label": "Limited", "value": "limited"},
                                    {"label": "Complete", "value": "complete"},
                                    {"label": "Admin", "value": "Admin"}
                                ],
                                className="mb-3"
                            )
                        ], md=4),
                        dbc.Col([
                            dbc.Label("Access Tier"),
                            dbc.Select(
                                id="edit-user-tier",
                                options=[
                                    {"label": "Tier 1: Basic", "value": 1},
                                    {"label": "Tier 2: Limited", "value": 2},
                                    {"label": "Tier 3: Complete", "value": 3},
                                    {"label": "Tier 4: Admin", "value": 4}
                                ],
                                className="mb-3"
                            )
                        ], md=4),
                        dbc.Col([
                            dbc.Label("Account Status"),
                            dbc.Select(
                                id="edit-user-status",
                                options=[
                                    {"label": "Active", "value": "true"},
                                    {"label": "Inactive", "value": "false"}
                                ],
                                className="mb-3"
                            )
                        ], md=4)
                    ])
                ]),
                dcc.Store(id="edit-user-id")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-edit-user", color="secondary"),
                dbc.Button("Save Changes", id="save-edit-user", color="primary")
            ])
        ], id="edit-user-modal", size="lg", is_open=False),

        # Password Reset Modal
        dbc.Modal([
            dbc.ModalHeader("Reset User Password"),
            dbc.ModalBody([
                html.Div(id="reset-password-alerts"),
                dbc.Form([
                    dbc.Label("New Password"),
                    dbc.Input(id="new-password-input", type="password", className="mb-3"),
                    dbc.Label("Confirm Password"),
                    dbc.Input(id="confirm-password-input", type="password", className="mb-3")
                ]),
                dcc.Store(id="reset-password-user-id")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-reset-password", color="secondary"),
                dbc.Button("Reset Password", id="confirm-reset-password", color="warning")
            ])
        ], id="reset-password-modal", size="md", is_open=False)

    ], className="py-4")


def create_overview_tab():
    """Create admin overview dashboard"""
    stats = get_user_statistics()

    # Summary cards
    summary_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(str(stats.get('by_status', {}).get('approved', 0)),
                            className="text-success"),
                    html.P("Active Users", className="mb-0")
                ])
            ], color="success", outline=True)
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(str(stats.get('by_status', {}).get('pending', 0)),
                            className="text-warning"),
                    html.P("Pending Approval", className="mb-0")
                ])
            ], color="warning", outline=True)
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(str(stats.get('pending_requests', 0)),
                            className="text-info"),
                    html.P("Access Requests", className="mb-0")
                ])
            ], color="info", outline=True)
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(str(stats.get('recent_registrations', 0)),
                            className="text-primary"),
                    html.P("New (30 days)", className="mb-0")
                ])
            ], color="primary", outline=True)
        ], md=3)
    ], className="mb-4")

    # Access tier distribution
    tier_stats = stats.get('by_tier', {})
    tier_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(str(tier_stats.get(1, 0))),
                    html.P("Tier 1: General", className="mb-0")
                ])
            ])
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(str(tier_stats.get(2, 0))),
                    html.P("Tier 2: Employee", className="mb-0")
                ])
            ])
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(str(tier_stats.get(3, 0))),
                    html.P("Tier 3: Admin", className="mb-0")
                ])
            ])
        ], md=4)
    ])

    return html.Div([
        html.H4("System Overview", className="mb-3"),
        summary_cards,
        html.H5("Access Tier Distribution", className="mb-3 mt-4"),
        tier_cards
    ])


def create_user_management_tab():
    """Enhanced user management with search functionality"""
    return html.Div([
        # Search and Filter Controls
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    id="user-search-input",
                    placeholder="Search by name or email...",
                    type="text",
                    className="mb-3"
                )
            ], md=4),
            dbc.Col([
                dbc.Select(
                    id="tier-filter-select",
                    options=[
                        {"label": "All Tiers", "value": "all"},
                        {"label": "Tier 1 (General)", "value": "1"},
                        {"label": "Tier 2 (Employee)", "value": "2"},
                        {"label": "Tier 3 (Admin)", "value": "3"}
                    ],
                    value="all",
                    className="mb-3"
                )
            ], md=3),
            dbc.Col([
                dbc.Select(
                    id="status-filter-select",
                    options=[
                        {"label": "All Status", "value": "all"},
                        {"label": "Active", "value": "approved"},
                        {"label": "Pending", "value": "pending"},
                        {"label": "Denied", "value": "denied"}
                    ],
                    value="all",
                    className="mb-3"
                )
            ], md=3),
            dbc.Col([
                dbc.Button("Add New User", id="add-user-btn", color="success", className="w-100 mb-3")
            ], md=2)
        ]),

        # User Results Container
        html.Div(id="filtered-users-container")
    ])


def filter_and_display_users(search_term="", tier_filter="all", status_filter="all"):
    """Filter users based on search criteria"""
    users = get_all_users()

    # Apply filters
    filtered_users = []
    for user in users:
        user_id, email, full_name, role, access_tier, reg_status, is_active, created_at, last_login = user

        # Search filter
        if search_term:
            if not (search_term.lower() in (full_name or "").lower() or
                    search_term.lower() in email.lower()):
                continue

        # Tier filter
        if tier_filter != "all" and str(access_tier) != tier_filter:
            continue

        # Status filter
        if status_filter != "all" and reg_status != status_filter:
            continue

        filtered_users.append(user)

    if not filtered_users:
        return dbc.Alert("No users match your search criteria", color="info")

    # Create user cards
    user_cards = []
    for user_id, email, full_name, role, access_tier, reg_status, is_active, created_at, last_login in filtered_users:
        # Status badge
        if reg_status == 'approved':
            status_badge = dbc.Badge("Active" if is_active else "Inactive",
                                     color="success" if is_active else "secondary")
        elif reg_status == 'pending':
            status_badge = dbc.Badge("Pending", color="warning")
        else:
            status_badge = dbc.Badge("Denied", color="danger")

        # Tier badge
        tier_colors = {1: "secondary", 2: "success", 3: "warning"}
        tier_badge = dbc.Badge(f"Tier {access_tier}", color=tier_colors.get(access_tier, "secondary"))

        user_card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5(full_name or "N/A", className="card-title"),
                        html.P([
                            html.Strong("Email: "), email, html.Br(),
                            html.Strong("Role: "), role.title(), html.Br(),
                            html.Strong("Last Login: "), last_login[:10] if last_login else "Never"
                        ], className="card-text")
                    ], md=6),
                    dbc.Col([
                        html.Div([
                            tier_badge, " ", status_badge
                        ], className="mb-3"),
                        dbc.ButtonGroup([
                            dbc.Button("Edit", id={"type": "edit-user", "user_id": user_id}, color="primary",
                                       size="sm"),
                            dbc.Button("Reset Password", id={"type": "reset-pwd", "user_id": user_id}, color="warning",
                                       size="sm"),
                            dbc.Button("Delete", id={"type": "delete-user", "user_id": user_id}, color="danger",
                                       size="sm")
                        ])
                    ], md=6)
                ])
            ])
        ], className="mb-3")

        user_cards.append(user_card)

    return html.Div([
        html.H4(f"Users Found: {len(filtered_users)}", className="mb-3"),
        html.Div(user_cards)
    ])


def approve_user_registration(user_id, approved_tier, admin_id):
    """Approve a user's registration with specific tier"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE users 
            SET registration_status = 'approved', access_tier = ?
            WHERE id = ?
        ''', (approved_tier, user_id))

        conn.commit()
        return {"success": True, "message": f"User approved with Tier {approved_tier} access"}

    except Exception as e:
        return {"success": False, "message": f"Error approving user: {str(e)}"}
    finally:
        conn.close()


def deny_user_registration(user_id, reason, admin_id):
    """Deny a user's registration"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE users 
            SET registration_status = 'denied'
            WHERE id = ?
        ''', (user_id,))

        conn.commit()
        return {"success": True, "message": "User registration denied"}

    except Exception as e:
        return {"success": False, "message": f"Error denying user: {str(e)}"}
    finally:
        conn.close()


def approve_access_request(request_id, admin_id):
    """Approve an access tier upgrade request"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Get request details
        cursor.execute('''
            SELECT user_id, requested_tier FROM access_requests WHERE id = ?
        ''', (request_id,))

        result = cursor.fetchone()
        if not result:
            return {"success": False, "message": "Request not found"}

        user_id, requested_tier = result

        # Update user's access tier
        cursor.execute('''
            UPDATE users SET access_tier = ? WHERE id = ?
        ''', (requested_tier, user_id))

        # Update request status
        cursor.execute('''
            UPDATE access_requests 
            SET status = 'approved', reviewed_at = ?, reviewed_by = ?
            WHERE id = ?
        ''', (datetime.now(), admin_id, request_id))

        conn.commit()
        return {"success": True, "message": f"Access upgraded to Tier {requested_tier}"}

    except Exception as e:
        return {"success": False, "message": f"Error approving request: {str(e)}"}
    finally:
        conn.close()


def deny_access_request(request_id, reason, admin_id):
    """Deny an access tier upgrade request"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE access_requests 
            SET status = 'denied', reviewed_at = ?, reviewed_by = ?, admin_notes = ?
            WHERE id = ?
        ''', (datetime.now(), admin_id, reason, request_id))

        conn.commit()
        return {"success": True, "message": "Access request denied"}

    except Exception as e:
        return {"success": False, "message": f"Error denying request: {str(e)}"}
    finally:
        conn.close()
def create_request_history_tab():
    """Create access request history tab"""
    requests = get_access_request_history()

    if not requests:
        return dbc.Alert("No access requests found", color="info")

    # Create history cards
    history_cards = []
    for req_id, email, full_name, current_tier, requested_tier, justification, status, created_at, reviewed_at, reviewer_name, admin_notes in requests:
        # Status badge
        status_colors = {"pending": "warning", "approved": "success", "denied": "danger"}
        status_badge = dbc.Badge(status.title(), color=status_colors.get(status, "secondary"))

        history_card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5(f"{full_name} ({email})", className="card-title"),
                        html.P([
                            html.Strong("Request: "), f"Tier {current_tier} → Tier {requested_tier}", html.Br(),
                            html.Strong("Status: "), status_badge, html.Br(),
                            html.Strong("Requested: "), created_at[:10] if created_at else "N/A", html.Br(),
                            html.Strong("Reviewed by: "), reviewer_name or "N/A"
                        ], className="card-text")
                    ], md=8),
                    dbc.Col([
                        html.H6("Justification:"),
                        html.P(justification[:100] + "..." if len(justification) > 100 else justification,
                               className="small text-muted")
                    ], md=4)
                ])
            ])
        ], className="mb-3")

        history_cards.append(history_card)

    return html.Div([
        html.H4(f"Access Request History ({len(requests)} total)", className="mb-4"),
        html.Div(history_cards)
    ])


def get_pending_users():
    """Get all users awaiting approval"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT id, email, full_name, created_at, access_tier
            FROM users WHERE registration_status = 'pending'
            ORDER BY created_at ASC
        ''')

        return cursor.fetchall()
    finally:
        conn.close()


def get_pending_users_with_proper_ids():
    """Get pending users with their actual database IDs"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT id, email, full_name, created_at, access_tier
            FROM users WHERE registration_status = 'pending'
            ORDER BY created_at ASC
        ''')

        results = cursor.fetchall()
        return results
    finally:
        conn.close()


def get_pending_access_requests_with_proper_ids():
    """Get pending access requests with proper IDs"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT ar.id, u.email, u.full_name, ar.current_tier, ar.requested_tier, 
                   ar.justification, ar.created_at, u.id as user_id
            FROM access_requests ar
            JOIN users u ON ar.user_id = u.id
            WHERE ar.status = 'pending'
            ORDER BY ar.created_at ASC
        ''')

        return cursor.fetchall()
    finally:
        conn.close()

def get_pending_access_requests():
    """Get all pending access upgrade requests"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT ar.id, u.email, u.full_name, ar.current_tier, ar.requested_tier, 
                   ar.justification, ar.created_at
            FROM access_requests ar
            JOIN users u ON ar.user_id = u.id
            WHERE ar.status = 'pending'
            ORDER BY ar.created_at ASC
        ''')

        return cursor.fetchall()
    finally:
        conn.close()
def create_user_registrations_tab():
    """Create user registrations tab with working approval buttons"""
    pending_users = get_pending_users_with_proper_ids()

    if not pending_users:
        return dbc.Alert("No pending user registrations", color="info")

    user_cards = []
    for user_id, email, full_name, created_at, current_tier in pending_users:
        card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5(full_name or "N/A", className="card-title"),
                        html.P([
                            html.Strong("Email: "), email, html.Br(),
                            html.Strong("Applied: "), created_at[:10] if created_at else 'N/A', html.Br(),
                            html.Strong("Current Tier: "), f"Tier {current_tier}"
                        ], className="card-text")
                    ], md=6),
                    dbc.Col([
                        html.H6("Approve with access tier:"),
                        dbc.RadioItems(
                            id={"type": "approve-tier", "user_id": user_id},
                            options=[
                                {"label": "Tier 1: Basic Access", "value": 1},
                                {"label": "Tier 2: Limited Access", "value": 2},
                                {"label": "Tier 3: Complete Access", "value": 3},
                                {"label": "Tier 4: Admin Access", "value": 4}
                            ],
                            value=2,  # Default to limited access
                            className="mb-3"
                        ),
                        dbc.ButtonGroup([
                            dbc.Button("Approve",
                                     id={"type": "approve-user", "user_id": user_id},
                                     color="success", size="sm"),
                            dbc.Button("Deny",
                                     id={"type": "deny-user", "user_id": user_id},
                                     color="danger", size="sm")
                        ])
                    ], md=6)
                ])
            ])
        ], className="mb-3")
        user_cards.append(card)

    return html.Div([
        html.H4(f"Pending User Registrations ({len(pending_users)})", className="mb-3"),
        html.P("Review and approve new user registrations. Note: Only admins can assign Tier 4 access.",
               className="text-muted mb-3"),
        html.Div(user_cards)
    ])


def create_access_requests_tab():
    """Create access requests tab with working buttons"""
    pending_requests = get_pending_access_requests_with_proper_ids()

    if not pending_requests:
        return dbc.Alert("No pending access requests", color="info")

    request_cards = []
    for req_id, email, full_name, current_tier, requested_tier, justification, created_at, user_id in pending_requests:
        # Don't allow requests for Tier 4 (Admin)
        if requested_tier >= 4:
            continue

        card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5(f"{full_name} ({email})", className="card-title"),
                        html.P([
                            html.Strong("Current: "), f"Tier {current_tier} - {TIER_INFO[current_tier]['name']}", html.Br(),
                            html.Strong("Requested: "), f"Tier {requested_tier} - {TIER_INFO[requested_tier]['name']}", html.Br(),
                            html.Strong("Requested: "), created_at[:10] if created_at else 'N/A'
                        ], className="card-text"),
                        html.P([
                            html.Strong("Justification: "), html.Br(),
                            justification
                        ], className="card-text",
                           style={'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '5px'})
                    ], md=8),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Approve",
                                     id={"type": "approve-access", "request_id": req_id},
                                     color="success", size="sm", className="mb-2"),
                            dbc.Button("Deny",
                                     id={"type": "deny-access", "request_id": req_id},
                                     color="danger", size="sm", className="mb-2")
                        ], vertical=True),
                        html.Div([
                            dbc.Label("Denial Reason (if denying):"),
                            dbc.Textarea(id={"type": "deny-reason", "request_id": req_id},
                                       placeholder="Reason for denial...",
                                       rows=3, size="sm")
                        ], className="mt-3")
                    ], md=4)
                ])
            ])
        ], className="mb-3")
        request_cards.append(card)

    if not request_cards:
        return dbc.Alert("No valid access requests (Tier 4 requests not allowed)", color="info")

    return html.Div([
        html.H4(f"Pending Access Requests ({len(request_cards)})", className="mb-3"),
        html.P("Users can only request up to Tier 3. Tier 4 (Admin) must be assigned manually.",
               className="text-muted mb-3"),
        html.Div(request_cards)
    ])


# Access request approval callbacks - FIXED
# USER REGISTRATION APPROVAL - WORKING VERSION

def handle_user_registrations(approve_clicks, deny_clicks, tier_values, user_session, active_tab):
    """Handle user registration approvals and denials"""
    ctx = dash.callback_context
    if not ctx.triggered or not user_session.get('authenticated'):
        return dash.no_update, dash.no_update

    admin_id = user_session.get('id')
    triggered = ctx.triggered[0]

    # Parse the triggered component
    import json
    component_id = json.loads(triggered['prop_id'].split('.')[0])
    user_id = component_id['user_id']
    action_type = component_id['type']

    if action_type == "approve-user":
        # Find the corresponding tier value
        pending_users = get_pending_users_with_proper_ids()
        tier_index = None
        for i, (uid, _, _, _, _) in enumerate(pending_users):
            if uid == user_id:
                tier_index = i
                break

        selected_tier = tier_values[tier_index] if tier_index is not None and tier_index < len(tier_values) else 2
        result = approve_user_registration(user_id, selected_tier, admin_id)

    elif action_type == "deny-user":
        result = deny_user_registration(user_id, "Denied by admin", admin_id)
    else:
        return dash.no_update, dash.no_update

    alert = dbc.Alert(result["message"],
                      color="success" if result["success"] else "danger",
                      dismissable=True)

    # Refresh the registrations tab
    new_content = create_user_registrations_tab() if active_tab == "registrations" else dash.no_update

    return alert, new_content


@callback(
    Output('add-user-modal', 'is_open'),
    [Input('add-user-btn', 'n_clicks'),
     Input('cancel-add-user', 'n_clicks')],
    [State('add-user-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_add_user_modal(add_clicks, cancel_clicks, is_open):
    """Toggle add user modal"""
    if add_clicks or cancel_clicks:
        return not is_open
    return is_open


@callback(
    [Output('admin-alerts', 'children', allow_duplicate=True),
     Output('add-user-modal', 'is_open', allow_duplicate=True),
     Output('admin-content', 'children', allow_duplicate=True),
     Output('add-user-name', 'value'),
     Output('add-user-email', 'value'),
     Output('add-user-password', 'value'),
     Output('add-user-confirm-password', 'value')],
    Input('save-add-user', 'n_clicks'),
    [State('add-user-name', 'value'),
     State('add-user-email', 'value'),
     State('add-user-password', 'value'),
     State('add-user-confirm-password', 'value'),
     State('add-user-role', 'value'),
     State('add-user-tier', 'value'),
     State('add-user-status', 'value'),
     State('user-session', 'data'),
     State('admin-tabs', 'active_tab')],
    prevent_initial_call=True
)
def create_new_user(save_clicks, name, email, password, confirm_password, role, tier, status, user_session, active_tab):
    """Create new user"""
    if not save_clicks or not user_session.get('authenticated'):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Validation
    if not all([name, email, password, confirm_password]):
        alert = dbc.Alert("Please fill in all fields", color="danger", dismissable=True)
        return alert, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    if password != confirm_password:
        alert = dbc.Alert("Passwords do not match", color="danger", dismissable=True)
        return alert, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    if len(password) < 6:
        alert = dbc.Alert("Password must be at least 6 characters", color="danger", dismissable=True)
        return alert, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Create user directly in database
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Check if user already exists
        cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            alert = dbc.Alert("Email already exists", color="danger", dismissable=True)
            return alert, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        # Create user
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (email, password_hash, full_name, role, access_tier, registration_status, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, name, role, int(tier), status, True))

        conn.commit()
        alert = dbc.Alert("User created successfully", color="success", dismissable=True)

        # Refresh user management tab
        new_content = create_user_management_tab() if active_tab == "users" else dash.no_update

        # Clear form fields
        return alert, False, new_content, "", "", "", ""

    except Exception as e:
        alert = dbc.Alert(f"Error creating user: {str(e)}", color="danger", dismissable=True)
        return alert, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    finally:
        conn.close()

@callback(
    Output('profile-alerts', 'children'),
    Input('request-access-btn', 'n_clicks'),
    [State('access-tier-request', 'value'),
     State('access-justification', 'value'),
     State('user-session', 'data')],
    prevent_initial_call=True
)
def handle_profile_access_request(n_clicks, requested_tier, justification, user_session):
    if not n_clicks or not user_session.get('authenticated'):
        return ""

    if not justification or len(justification.strip()) < 10:
        return dbc.Alert("Please provide a detailed justification (at least 10 characters)", color="danger")

    result = request_access_upgrade(user_session['id'], requested_tier, justification)

    return dbc.Alert(result["message"],
                     color="success" if result["success"] else "danger",
                     dismissable=True)

# ACCESS REQUEST APPROVAL - WORKING VERSION
@callback(
    [Output('admin-alerts', 'children', allow_duplicate=True),
     Output('admin-content', 'children', allow_duplicate=True)],
    [Input({"type": "approve-user", "user_id": ALL}, 'n_clicks'),
     Input({"type": "deny-user", "user_id": ALL}, 'n_clicks'),
     Input({"type": "approve-access", "request_id": ALL}, 'n_clicks'),
     Input({"type": "deny-access", "request_id": ALL}, 'n_clicks')],
    [State({"type": "approve-tier", "user_id": ALL}, 'value'),
     State({"type": "deny-reason", "request_id": ALL}, 'value'),
     State('user-session', 'data'),
     State('admin-tabs', 'active_tab')],
    prevent_initial_call=True
)
def handle_access_requests(approve_clicks, deny_clicks, deny_reasons, user_session, active_tab):
    """Handle access request approvals and denials"""
    ctx = dash.callback_context
    if not ctx.triggered or not user_session.get('authenticated'):
        return dash.no_update, dash.no_update

    admin_id = user_session.get('id')
    triggered = ctx.triggered[0]

    # Parse the triggered component
    import json
    component_id = json.loads(triggered['prop_id'].split('.')[0])
    request_id = component_id['request_id']
    action_type = component_id['type']

    if action_type == "approve-access":
        result = approve_access_request(request_id, admin_id)

    elif action_type == "deny-access":
        # Find the corresponding denial reason
        pending_requests = get_pending_access_requests_with_proper_ids()
        reason_index = None
        for i, (rid, _, _, _, _, _, _, _) in enumerate(pending_requests):
            if rid == request_id:
                reason_index = i
                break

        reason = deny_reasons[reason_index] if reason_index is not None and reason_index < len(deny_reasons) and \
                                               deny_reasons[reason_index] else "No reason provided"
        result = deny_access_request(request_id, reason, admin_id)
    else:
        return dash.no_update, dash.no_update

    alert = dbc.Alert(result["message"],
                      color="success" if result["success"] else "danger",
                      dismissable=True)

    # Refresh the access requests tab
    new_content = create_access_requests_tab() if active_tab == "access-requests" else dash.no_update

    return alert, new_content
# ============================================================================
# FIXED ADMIN CALLBACKS
# ============================================================================

@callback(
    Output('admin-content', 'children'),
    Input('admin-tabs', 'active_tab'),        # Parameter 1
    Input('posts-refresh-trigger', 'data'),   # Parameter 2 (you added this)
    State('user-session', 'data')              # Parameter 3
)
def render_admin_content(active_tab, refresh_trigger, user_session):  # ✅ 3 parameters now
    """Render content based on active admin tab"""

    if not user_session or user_session.get('access_tier', 0) < 3:
        return dbc.Alert("Access Denied", color="danger")

    if active_tab == "overview":
        return create_overview_tab()

    elif active_tab == "users":
        return create_user_management_tab()

    elif active_tab == "registrations":
        return create_user_registrations_tab()

    elif active_tab == "access-requests":
        return create_access_requests_tab()

    elif active_tab == "data-requests":
        return create_admin_data_requests_tab()

    elif active_tab == "posts-management":
        if user_session.get('access_tier', 0) < 4:
            return dbc.Alert([
                html.I(className="fas fa-lock me-2"),
                "Posts management requires Tier 4 (Admin) access."
            ], color="warning")

        from posts_system import get_active_posts
        from posts_ui import create_posts_management_tab

        posts = get_active_posts(user_tier=4, include_expired=True)
        return create_posts_management_tab(posts)

    elif active_tab == "history":
        return create_request_history_tab()

    return html.Div("Select a tab to view content")

@callback(
    [Output('edit-user-modal', 'is_open'),
     Output('edit-user-name', 'value'),
     Output('edit-user-email', 'value'),
     Output('edit-user-role', 'value'),
     Output('edit-user-tier', 'value'),
     Output('edit-user-status', 'value'),
     Output('edit-user-id', 'data')],
    [Input({"type": "edit-user", "user_id": ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def handle_edit_user_clicks(edit_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(edit_clicks):
        return False, "", "", "", "", "", None

    # Find which button was clicked
    button_id = ctx.triggered[0]['prop_id']
    import json
    user_id = json.loads(button_id.split('.')[0])['user_id']

    # Get user data
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT email, full_name, role, access_tier, is_active
            FROM users WHERE id = ?
        ''', (user_id,))

        user_data = cursor.fetchone()
        if user_data:
            email, full_name, role, access_tier, is_active = user_data
            return True, full_name, email, role, access_tier, str(is_active).lower(), user_id
    finally:
        conn.close()

    return False, "", "", "", "", "", None

@callback(
    [Output('admin-alerts', 'children', allow_duplicate=True),  # Add this
     Output('edit-user-modal', 'is_open', allow_duplicate=True),
     Output('admin-content', 'children', allow_duplicate=True)],  # Add this
    Input('save-edit-user', 'n_clicks'),
    [State('edit-user-id', 'data'),
     State('edit-user-name', 'value'),
     State('edit-user-email', 'value'),
     State('edit-user-role', 'value'),
     State('edit-user-tier', 'value'),
     State('edit-user-status', 'value'),
     State('user-session', 'data'),
     State('admin-tabs', 'active_tab')],
    prevent_initial_call=True
)
def save_user_changes(save_clicks, user_id, name, email, role, tier, status, user_session, active_tab):
    """Save user changes"""
    if not save_clicks or not user_session.get('authenticated'):
        return dash.no_update, dash.no_update, dash.no_update

    admin_id = user_session.get('id')
    is_active = status == "true"

    result = update_user_info(user_id, email, name, role, int(tier), is_active, admin_id)

    alert = dbc.Alert(result["message"],
                      color="success" if result["success"] else "danger",
                      dismissable=True)

    # Refresh the current tab
    if active_tab == "users":
        new_content = create_user_management_tab()
    else:
        new_content = dash.no_update

    return alert, False, new_content


@callback(
    Output('edit-user-modal', 'is_open', allow_duplicate=True),
    Input('cancel-edit-user', 'n_clicks'),
    prevent_initial_call=True
)
def cancel_edit_user(cancel_clicks):
    """Cancel edit user modal"""
    if cancel_clicks:
        return False
    return dash.no_update


# Delete user callbacks
@callback(
    [Output('admin-alerts', 'children', allow_duplicate=True),
     Output('admin-content', 'children', allow_duplicate=True)],
    [Input({"type": "delete-user", "user_id": ALL}, 'n_clicks')],
    [State('user-session', 'data'),
     State('admin-tabs', 'active_tab')],
    prevent_initial_call=True
)
def handle_delete_user(delete_clicks, user_session, active_tab):
    ctx = dash.callback_context
    if not ctx.triggered or not any(delete_clicks):
        return dash.no_update, dash.no_update

    if not user_session.get('authenticated'):
        return dash.no_update, dash.no_update

    import json
    button_id = ctx.triggered[0]['prop_id']
    user_id = json.loads(button_id.split('.')[0])['user_id']
    admin_id = user_session.get('id')

    result = delete_user(user_id, admin_id)

    alert = dbc.Alert(result["message"],
                      color="success" if result["success"] else "danger",
                      dismissable=True)

    new_content = create_user_management_tab() if active_tab == "users" else dash.no_update

    return alert, new_content
def create_admin_dashboard(user_data):
    return create_comprehensive_admin_dashboard(user_data)


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

def create_user(email, password, full_name):
    """Create a new user account"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return {"success": False, "message": "Email already registered"}

        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (email, password_hash, full_name, access_tier, registration_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, password_hash, full_name, 1, 'pending'))  # Make sure full_name is here

        conn.commit()
        return {"success": True, "message": "Account created successfully"}

    except Exception as e:
        return {"success": False, "message": f"Error creating account: {str(e)}"}
    finally:
        conn.close()

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

    # Your existing validation...
    if not all([name, email, password, confirm_password]):
        return dbc.Alert("Please fill in all fields", color="danger"), dash.no_update

    if password != confirm_password:
        return dbc.Alert("Passwords do not match", color="danger"), dash.no_update

    if len(password) < 6:
        return dbc.Alert("Password must be at least 6 characters", color="danger"), dash.no_update

    # Create user
    result = create_user(email.strip().lower(), password, name.strip())

    if result["success"]:
        # Send confirmation email
        from auth_utils import send_signup_confirmation_email
        send_signup_confirmation_email(email.strip().lower(), name.strip())

        return dbc.Alert("Account created! Check your email for confirmation. Please wait for admin approval.",
                         color="success"), "/login"
    else:
        return dbc.Alert(result["message"], color="danger"), dash.no_update


@callback(
    [Output('reset-password-modal', 'is_open'),
     Output('reset-password-user-id', 'data')],
    [Input({"type": "reset-pwd", "user_id": ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def open_reset_password_modal(reset_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(reset_clicks):
        return False, None

    import json
    button_id = ctx.triggered[0]['prop_id']
    user_id = json.loads(button_id.split('.')[0])['user_id']

    return True, user_id


@callback(
    [Output('admin-alerts', 'children', allow_duplicate=True),
     Output('reset-password-modal', 'is_open', allow_duplicate=True)],
    Input('confirm-reset-password', 'n_clicks'),
    [State('new-password-input', 'value'),
     State('confirm-password-input', 'value'),
     State('reset-password-user-id', 'data'),
     State('user-session', 'data')],
    prevent_initial_call=True
)
def confirm_password_reset(confirm_clicks, new_password, confirm_password, user_id, user_session):
    if not confirm_clicks or not user_session.get('authenticated'):
        return dash.no_update, dash.no_update

    if not new_password or not confirm_password:
        return dbc.Alert("Please fill in both password fields", color="danger"), dash.no_update

    if new_password != confirm_password:
        return dbc.Alert("Passwords do not match", color="danger"), dash.no_update

    if len(new_password) < 6:
        return dbc.Alert("Password must be at least 6 characters", color="danger"), dash.no_update

    admin_id = user_session.get('id')
    result = reset_user_password(user_id, new_password, admin_id)

    alert = dbc.Alert(result["message"],
                      color="success" if result["success"] else "danger",
                      dismissable=True)

    return alert, False


@callback(
    Output('reset-password-modal', 'is_open', allow_duplicate=True),
    Input('cancel-reset-password', 'n_clicks'),
    prevent_initial_call=True
)
def cancel_reset_password(cancel_clicks):
    if cancel_clicks:
        return False
    return dash.no_update
# Profile page callbacks
# Profile access request callback - FIXED
@callback(
    [Output('admin-alerts', 'children', allow_duplicate=True),
     Output('admin-content', 'children', allow_duplicate=True)],
    [Input({"type": "approve-access", "request_id": ALL}, 'n_clicks'),
     Input({"type": "deny-access", "request_id": ALL}, 'n_clicks')],
    [State({"type": "deny-reason", "request_id": ALL}, 'value'),
     State('user-session', 'data'),
     State('admin-tabs', 'active_tab')],
    prevent_initial_call=True
)
def handle_access_requests(approve_clicks, deny_clicks, deny_reasons, user_session, active_tab):
    """Handle access request approvals and denials"""
    ctx = dash.callback_context
    if not ctx.triggered or not user_session.get('authenticated'):
        return dash.no_update, dash.no_update

    admin_id = user_session.get('id')
    triggered = ctx.triggered[0]

    # Parse the triggered component
    import json
    component_id = json.loads(triggered['prop_id'].split('.')[0])
    request_id = component_id['request_id']
    action_type = component_id['type']

    if action_type == "approve-access":
        result = approve_access_request(request_id, admin_id)

    elif action_type == "deny-access":
        # Find the corresponding denial reason
        pending_requests = get_pending_access_requests_with_proper_ids()
        reason_index = None
        for i, (rid, _, _, _, _, _, _, _) in enumerate(pending_requests):
            if rid == request_id:
                reason_index = i
                break

        reason = deny_reasons[reason_index] if reason_index is not None and reason_index < len(deny_reasons) and \
                                               deny_reasons[reason_index] else "No reason provided"
        result = deny_access_request(request_id, reason, admin_id)
    else:
        return dash.no_update, dash.no_update

    alert = dbc.Alert(result["message"],
                      color="success" if result["success"] else "danger",
                      dismissable=True)

    # Refresh the access requests tab
    new_content = create_access_requests_tab() if active_tab == "access-requests" else dash.no_update

    return alert, new_content

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

# User search and filter callback
@callback(
    Output('filtered-users-container', 'children'),
    [Input('user-search-input', 'value'),
     Input('tier-filter-select', 'value'),
     Input('status-filter-select', 'value')],
    prevent_initial_call=False
)
def update_user_list(search_term, tier_filter, status_filter):
    """Update user list based on filters"""
    return filter_and_display_users(
        search_term or "",
        tier_filter or "all",
        status_filter or "all"
    )
# ============================================================================
# UPDATE YOUR EXISTING FUNCTIONS
# ============================================================================

# Replace your authenticate_user function with authenticate_user_enhanced
# Add /signup and /profile routes to your display_page callback
# Update init_database() call to init_enhanced_database()
# Add "Sign Up" link to your login page



# ============================================================================
# NAVBAR WITH AUTHENTICATION
# ============================================================================

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

    user = authenticate_user_enhanced(email.strip().lower(), password)
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
    """Pill-styled authentication section for navbar"""
    if not user_data or not user_data.get('authenticated'):
        return dbc.NavItem(
            html.A([
                html.I(className="fas fa-sign-in-alt me-2"),
                "Sign In"
            ],
                href="/login",
                className="nav-pill-navbar",
                style={
                    'textDecoration': 'none',
                    'borderRadius': '6px'  # ← Add this line
                }
            )
        )


    user_tier = user_data.get('access_tier', 1)
    tier_info = TIER_INFO.get(user_tier, TIER_INFO[1])

    # Build dropdown menu items
    dropdown_items = [
        dbc.DropdownMenuItem([
            html.Strong(user_data.get('full_name', 'User')),
            html.Br(),
            html.Small(user_data.get('email', ''), className="text-muted"),
            html.Br(),
            dbc.Badge(f"Tier {user_tier}: {tier_info['name']}",
                      color=tier_info['color'], className="mt-1")
        ], header=True),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem([
            html.I(className="fas fa-user me-2"), "My Profile"
        ], href="/profile")
    ]

    # Add Admin button for Tier 4 users only
    if user_tier >= 4:
        dropdown_items.append(
            dbc.DropdownMenuItem([
                html.I(className="fas fa-cog me-2"), "Admin Dashboard"
            ], href="/admin")
        )

    # Add logout
    dropdown_items.extend([
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem([
            html.I(className="fas fa-sign-out-alt me-2"), "Logout"
        ], id="navbar-logout-btn")
    ])

    return dbc.NavItem([
        dbc.DropdownMenu(
            dropdown_items,
            label=user_data.get('email', 'User'),
            nav=True,
            align_end=True
        )
    ])


def create_modern_navbar(user_data=None):
    """Updated navbar with news link"""
    user_access_tier = user_data.get('access_tier', 1) if user_data else 1

    # Dynamic services menu
    services_items = [
        dbc.DropdownMenuItem("Request Report", href="/request-report"),
        dbc.DropdownMenuItem(divider=True) if user_access_tier >= 2 else None,
        dbc.DropdownMenuItem("Help", href="/help"),
        dbc.DropdownMenuItem("Contact IR", href="/contact")
    ]
    services_items = [item for item in services_items if item is not None]

    return dbc.Navbar(
        dbc.Container([
            # Brand
            dbc.NavbarBrand([
                html.Img(src="assets/usc-logo.png", height="45", className="me-3"),
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
                    toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none',
                                  'background': 'transparent'}
                ),

                # ADD THIS: News link
                dbc.NavItem(dbc.NavLink(
                    [html.I(className=""
                                      ""), "News"],
                    href="/news",
                    style={'color': '#1B5E20', 'fontWeight': '600'}
                )),

                # UPDATED: Single factbook link
                dbc.NavItem(dbc.NavLink(
                    "Factbook", href="/factbook",
                    style={'color': '#1B5E20', 'fontWeight': '600'}
                )),
                dbc.DropdownMenu(
                    services_items,
                    label="Services", nav=True,
                    toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none',
                                  'background': 'transparent'}
                ),

                # Authentication section (your existing code)
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
    """Hero section with banner background (without navigation)"""
    return html.Section([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1([
                        html.Span("Institutional Research", style={
                            'background': 'linear-gradient(45deg, #FDD835, #FFEB3B)',
                            'WebkitBackgroundClip': 'text',
                            'WebkitTextFillColor': 'transparent'
                        })
                    ], style={
                        'fontSize': '3.5rem',
                        'fontWeight': '700',
                        'marginBottom': '1.5rem',
                        'textAlign': 'center'
                    }),
                    html.P(
                        "Empowering data-driven decisions through comprehensive institutional analytics, "
                        "enrollment insights, and strategic planning support for USC's continued excellence.",
                        style={
                            'fontSize': '1.25rem',
                            'opacity': '0.9',
                            'marginBottom': '2.5rem',
                            'textAlign': 'center'
                        }
                    )
                ], md=10, lg=8)
            ], justify="center")
        ], fluid=True, className="text-white", style={'position': 'relative', 'zIndex': '2'})
    ], style={
        'background': '''
            linear-gradient(135deg, rgba(27, 94, 32, 0.85) 0%, rgba(46, 125, 50, 0.85) 50%, rgba(76, 175, 80, 0.85) 100%),
            url('/assets/banner.png')
        ''',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'backgroundRepeat': 'no-repeat',
        'padding': '120px 0 60px 0',
        'minHeight': '400px',
        'position': 'relative'
    })


def create_sticky_pill_navigation():
    """Sticky pill navigation bar - separate component"""
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        # Stats Button
                        html.Button([
                            html.I(className="fas fa-chart-bar me-2"),
                            "Stats"
                        ],
                            id="scroll-to-stats",
                            className="nav-pill",
                            **{'data-target': 'stats-section'}
                        ),
                        # About IR Button
                        html.Button([
                            html.I(className="fas fa-info-circle me-2"),
                            "About IR"
                        ],
                            id="scroll-to-about",
                            className="nav-pill",
                            **{'data-target': 'about-ir-section'}
                        ),





                        # Services Button
                        html.Button([
                            html.I(className="fas fa-cogs me-2"),
                            "Services"
                        ],
                            id="scroll-to-services",
                            className="nav-pill",
                            **{'data-target': 'services-section'}
                        ),

                        # Team Button
                        html.Button([
                            html.I(className="fas fa-users me-2"),
                            "Team"
                        ],
                            id="scroll-to-team",
                            className="nav-pill",
                            **{'data-target': 'team-section'}
                        ),
                        # Factbook Button
                        html.A([
                            html.I(className="fas fa-book me-2"),
                            "Factbook"
                        ],
                            href="/factbook",
                            className="nav-pill",
                            style={'textDecoration': 'none'}
                        )
                    ], style={
                        'display': 'flex',
                        'gap': '12px',
                        'flexWrap': 'wrap',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    })
                ])
            ], justify="center")
        ])
    ], id="pill-nav-container", style={
        'position': 'sticky',
        'top': '75px',  # Height of your navbar
        'zIndex': '999',
        'background': 'white',
        'padding': '15px 0',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
        'borderBottom': '1px solid #e0e0e0',
        'transition': 'all 0.3s ease'
    })

def create_about_ir_section():
    """New About Institutional Research section"""
    return html.Section([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("About Institutional Research", style={
                        'color': '#1B5E20', 'fontWeight': '700', 'fontSize': '2.5rem',
                        'textAlign': 'center', 'marginBottom': '3rem'
                    }),

                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div([
                                        html.I(className="fas fa-bullseye fa-3x mb-3",
                                               style={'color': '#1B5E20'}),
                                        html.H4("Our Mission", style={'color': '#1B5E20', 'fontWeight': '600'}),
                                        html.P(
                                            "To provide comprehensive data analysis and strategic insights that drive informed decision-making across all levels of the university, supporting USC's commitment to academic excellence and institutional effectiveness.")
                                    ], className="text-center")
                                ])
                            ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none', 'height': '100%'})
                        ], md=4, className="mb-4"),

                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div([
                                        html.I(className="fas fa-chart-line fa-3x mb-3",
                                               style={'color': '#4CAF50'}),
                                        html.H4("What We Do", style={'color': '#1B5E20', 'fontWeight': '600'}),
                                        html.P(
                                            "We collect, analyze, and report on institutional data including enrollment trends, graduation rates, financial performance, faculty metrics, and student outcomes to support strategic planning and accreditation efforts.")
                                    ], className="text-center")
                                ])
                            ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none', 'height': '100%'})
                        ], md=4, className="mb-4"),

                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div([
                                        html.I(className="fas fa-users fa-3x mb-3",
                                               style={'color': '#FDD835'}),
                                        html.H4("Who We Serve", style={'color': '#1B5E20', 'fontWeight': '600'}),
                                        html.P(
                                            "University leadership, faculty, staff, students, and external stakeholders who require accurate, timely institutional data for planning, assessment, reporting, and continuous improvement initiatives.")
                                    ], className="text-center")
                                ])
                            ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none', 'height': '100%'})
                        ], md=4, className="mb-4")
                    ])
                ])
            ])
        ])
    ], style={'padding': '80px 0', 'background': 'white'}, id="about-ir-section")


def create_scroll_trigger():
    """Enhanced hidden div for scroll callback trigger"""
    return html.Div([
        html.Div(id='scroll-trigger', style={'display': 'none'}),
        html.Div(id='active-section-store', style={'display': 'none'})
    ])


# Enhanced clientside callback with scroll spy functionality
app.clientside_callback(
    '''
    function(about_clicks, stats_clicks, services_clicks, team_clicks, scroll_interval) {
        // PART 1: Handle button clicks for smooth scrolling
        const ctx = window.dash_clientside.callback_context;

        if (ctx.triggered.length > 0) {
            const triggered_id = ctx.triggered[0].prop_id.split('.')[0];

            const scrollTargets = {
                'scroll-to-about': 'about-ir-section',
                'scroll-to-stats': 'stats-section',
                'scroll-to-services': 'services-section',
                'scroll-to-team': 'team-section'
            };

            const targetId = scrollTargets[triggered_id];
            if (targetId) {
                const element = document.getElementById(targetId);
                if (element) {
                    const navbarHeight = 75;
                    const pillNavHeight = 60;
                    const offset = navbarHeight + pillNavHeight;

                    const elementPosition = element.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - offset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        }

        // PART 2: Scroll spy - highlight active section
        const sections = [
            'about-ir-section',
            'stats-section',
            'services-section',
            'team-section'
        ];

        const navButtons = {
            'about-ir-section': 'scroll-to-about',
            'stats-section': 'scroll-to-stats',
            'services-section': 'scroll-to-services',
            'team-section': 'scroll-to-team'
        };

        let activeSection = null;
        const navbarHeight = 75;
        const pillNavHeight = 60;
        const scrollOffset = navbarHeight + pillNavHeight + 100;

        // Find which section is currently in view
        for (let sectionId of sections) {
            const element = document.getElementById(sectionId);
            if (element) {
                const rect = element.getBoundingClientRect();
                // Check if section is in viewport
                if (rect.top <= scrollOffset && rect.bottom >= scrollOffset) {
                    activeSection = sectionId;
                    break;
                }
            }
        }

        // Update active class on buttons
        Object.entries(navButtons).forEach(([sectionId, buttonId]) => {
            const button = document.getElementById(buttonId);
            if (button) {
                if (sectionId === activeSection) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            }
        });

        return window.dash_clientside.no_update;
    }
    ''',
    Output('scroll-trigger', 'children'),
    [
        Input('scroll-to-about', 'n_clicks'),
        Input('scroll-to-stats', 'n_clicks'),
        Input('scroll-to-services', 'n_clicks'),
        Input('scroll-to-team', 'n_clicks'),
        Input('scroll-interval', 'n_intervals')
    ],
    prevent_initial_call=False
)


def create_scroll_spy_interval():
    """Interval component for scroll spy updates"""
    return dcc.Interval(
        id='scroll-interval',
        interval=200,  # Update every 200ms
        n_intervals=0
    )

def create_stats_overview():
    """Your exact stats section"""
    stats = [
        {'title': '3,110', 'subtitle': 'Total Enrollment', 'icon': 'fas fa-users', 'color': '#1B5E20'},
        {'title': '5', 'subtitle': 'Academic Divisions', 'icon': 'fas fa-building', 'color': '#4CAF50'},
        {'title': '250+', 'subtitle': 'Employees', 'icon': 'fas fa-user-tie', 'color': '#FDD835'},
        {'title': '25+', 'subtitle': 'Areas of Data Collected', 'icon': 'fas fa-eye', 'color': '#28A745'}
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
    ], style={'padding': '80px 0', 'background': '#F8F9FA'}, id="stats-section")

def create_feature_showcase():
    """Your exact feature showcase"""
    features = [
        {'title': 'Interactive Factbook', 'desc': 'Comprehensive institutional data with interactive visualizations.', 'icon': 'fas fa-chart-line', 'href': 'https://your-factbook-url.com', 'external': True},
        {'title': 'Alumni Portal', 'desc': 'Connect with USC alumni and access alumni services and networks.', 'icon': 'fas fa-graduation-cap'},
        {'title': 'Yearly Reports', 'desc': 'Annual institutional reports and comprehensive data analysis.', 'icon': 'fas fa-calendar-alt'},
        {'title': 'Custom Reports', 'desc': 'Request tailored analytical reports for your specific needs.', 'icon': 'fas fa-file-alt'}
    ]

    cards = []
    for feature in features:
        if feature['title'] == 'Custom Reports':
            button = dbc.Button("Request Report", color="outline-primary", size="sm", href="/request-report")
        elif feature['title'] == 'Interactive Factbook':
            # External factbook link
            button = html.A([
                dbc.Button([
                    html.I(className="fas fa-external-link-alt me-1"),
                    "Access Factbook"
                ], color="outline-primary", size="sm")
            ],
                href=feature['href'],
                target="_blank",
                rel="noopener noreferrer",
                style={'textDecoration': 'none'}
            )
        else:
            button = dbc.Button("Explore", color="outline-primary", size="sm")

        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className=feature['icon'],
                               style={'fontSize': '2.2rem', 'color': '#1B5E20', 'marginBottom': '15px'}),
                        html.H4(feature['title'], style={'color': '#1B5E20', 'fontWeight': '600'}),
                        html.P(feature['desc'], style={'color': '#666', 'marginBottom': '20px'}),
                        button  # Use the conditional button
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
    ], style={'padding': '80px 0', 'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)'}, id="services-section")


def create_director_message():
    """Enhanced team section with Director and second team member"""
    return html.Section([
        dbc.Container([
            # Meet The Team Title
            html.H2("Meet The Team", style={
                'color': '#1B5E20', 'fontWeight': '700', 'fontSize': '2.5rem',
                'textAlign': 'center', 'marginBottom': '3rem'
            }),

            # Team Cards Row
            dbc.Row([
                # Director Card (Left Side)
                dbc.Col([
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
                                ], md=12, className="text-center mb-3"),
                                dbc.Col([
                                    html.H3("Director",
                                            style={'color': '#1B5E20', 'fontWeight': '600', 'marginBottom': '20px',
                                                   'textAlign': 'center'}),
                                    html.P([
                                        "As Director of Institutional Research, I lead the strategic analysis and reporting that drives ",
                                        "data-informed decision making across USC. Our department takes pride in delivering comprehensive ",
                                        "institutional insights through detailed factbooks, enrollment analytics, and performance metrics."
                                    ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '15px'}),
                                    html.P([
                                        "We collaborate closely with all five university divisions to provide leadership, faculty, and staff ",
                                        "with the critical data needed to support USC's mission of educational excellence. Our reports cover ",
                                        "graduation trends, financial analysis, student demographics, and institutional effectiveness measures."
                                    ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '15px'}),
                                    html.P([
                                        "Through this new digital portal, we're making institutional research more accessible and actionable ",
                                        "than ever before. Our commitment is to transform data into insights that support USC's continued ",
                                        "growth and academic distinction."
                                    ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '20px'}),
                                    html.Div([
                                        html.P("Yours In Service",
                                               style={'color': '#1B5E20', 'fontWeight': '600', 'fontStyle': 'italic',
                                                      'marginBottom': '5px'}),
                                        html.P("Nordian C. Swaby Robinson",
                                               style={'color': '#1B5E20', 'fontWeight': '600', 'marginBottom': '1px'}),
                                        html.P("Director, Institutional Research",
                                               style={'color': '#666', 'fontSize': '0.9rem', 'marginBottom': '5px'}),
                                        html.P("Leading Data-Driven Excellence",
                                               style={'color': '#666', 'fontSize': '0.8rem', 'fontStyle': 'italic'})
                                    ], style={'marginTop': '25px', 'paddingTop': '20px',
                                              'borderTop': '2px solid #e9ecef', 'textAlign': 'center'})
                                ], md=12)
                            ])
                        ])
                    ], style={'boxShadow': '0 8px 30px rgba(0,0,0,0.1)', 'border': 'none', 'height': '100%'})
                ], md=6, className="mb-4"),

                # Second Team Member Card (Right Side)
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Img(
                                        src="/assets/team-member-2.jpg",  # You'll need to add this image
                                        style={
                                            'width': '120px', 'height': '120px', 'objectFit': 'cover',
                                            'border': '4px solid #1B5E20', 'boxShadow': '0 4px 15px rgba(0,0,0,0.2)'
                                        }
                                    )
                                ], md=12, className="text-center mb-3"),
                                dbc.Col([
                                    html.H3("Web Developer",
                                            style={'color': '#1B5E20', 'fontWeight': '600', 'marginBottom': '20px',
                                                   'textAlign': 'center'}),
                                    html.P([
                                        "As the Web Developer for the Institutional Research department, I am responsible for creating ",
                                        "and maintaining the digital infrastructure that powers our data-driven decision making processes. ",
                                        "This portal represents the culmination of extensive collaboration between the IR team and our ",
                                        "commitment to making institutional data accessible and actionable."
                                    ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '15px'}),
                                    html.P([
                                        "The development of this platform focuses on user experience, data security, and scalable architecture ",
                                        "to ensure that faculty, staff, and administrators can easily access the insights they need. Through ",
                                        "interactive visualizations and comprehensive reporting tools, we're transforming how USC uses its data."
                                    ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '15px'}),
                                    html.P([
                                        "I'm passionate about leveraging technology to support educational excellence and institutional growth. ",
                                        "This portal is designed to evolve with the university's needs, providing a foundation for data-driven ",
                                        "strategic planning and continuous improvement."
                                    ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '20px'}),
                                    html.Div([
                                        html.P("In Development Excellence",
                                               style={'color': '#1B5E20', 'fontWeight': '600', 'fontStyle': 'italic',
                                                      'marginBottom': '5px'}),
                                        html.P("Liam Webster",
                                               style={'color': '#1B5E20', 'fontWeight': '600', 'marginBottom': '1px'}),
                                        html.P("Web Developer, Institutional Research",
                                               style={'color': '#666', 'fontSize': '0.9rem', 'marginBottom': '5px'}),
                                        html.P("Portal Launch: 2025",
                                               style={'color': '#666', 'fontSize': '0.8rem', 'fontStyle': 'italic'})
                                    ], style={'marginTop': '25px', 'paddingTop': '20px',
                                              'borderTop': '2px solid #e9ecef', 'textAlign': 'center'})
                                ], md=12)
                            ])
                        ])
                    ], style={'boxShadow': '0 8px 30px rgba(0,0,0,0.1)', 'border': 'none', 'height': '100%'})
                ], md=6, className="mb-4")
            ])
        ])
    ], style={'padding': '80px 0', 'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)'}, id="team-section")

def create_quick_links():
    """Enhanced quick links with modern design - external links only"""
    links = [
        {'title': 'USC Main Website', 'url': 'https://www.usc.edu.tt', 'icon': 'fas fa-globe', 'color': '#1B5E20'},
        {'title': 'USC eLearn', 'url': 'https://elearn.usc.edu.tt', 'icon': 'fas fa-laptop', 'color': '#4CAF50'},
        {'title': 'Aeorion Portal', 'url': 'https://aeorion.usc.edu.tt', 'icon': 'fas fa-door-open', 'color': '#FDD835'},
        {'title': 'Email Support', 'url': 'mailto:ir@usc.edu.tt', 'icon': 'fas fa-envelope', 'color': '#28A745'},
        {'title': 'Donate', 'url': 'https://usc.edu.tt/give/', 'icon': 'fas fa-handshake', 'color': '#28A745'},
        {'title': 'Directory', 'url': 'https://directory.usc.edu.tt/', 'icon': 'fas fa-address-book', 'color': '#28A745'}
    ]

    link_items = []
    for link in links:
        link_items.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className=link['icon'], style={
                                'fontSize': '2.5rem', 'color': link['color'], 'marginBottom': '15px'
                            }),
                            html.H5(link['title'], style={
                                'color': '#1B5E20', 'fontWeight': '600', 'marginBottom': '10px'
                            }),
                            html.A([
                                "Visit ", html.I(className="fas fa-external-link-alt ms-1")
                            ],
                            href=link['url'],
                            target="_blank",
                            className="btn btn-outline-primary btn-sm",
                            style={'borderRadius': '20px', 'textDecoration': 'none'})
                        ], className="text-center")
                    ])
                ], style={
                    'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
                    'border': 'none',
                    'height': '100%',
                    'transition': 'transform 0.3s ease, box-shadow 0.3s ease'
                }, className="h-100")
            ], sm=4, md=4, className="mb-4")
        )

    return html.Section([
        dbc.Container([
            html.H2("Quick Links", style={
                'color': '#1B5E20', 'fontWeight': '700', 'fontSize': '2.5rem',
                'textAlign': 'center', 'marginBottom': '3rem'
            }),
            dbc.Row(link_items)
        ])
    ], style={'padding': '80px 0', 'background': '#F8F9FA'})
"""
def create_modern_footer():
    Your exact footer
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
                        html.Strong("Phone: "), "1868-662-2241 ext. 1005"
                    ], style={'opacity': '0.9'})
                ], md=4),
                dbc.Col([
                    html.H6("Development Team", style={'color': '#FDD835', 'fontWeight': '600'}),
                    html.P([
                        html.Strong("Web Developer: "), "Liam Webster", html.Br(),
                        html.Strong("Email: "), html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt", style={'color': '#FDD835'}),html.Br(),
                        html.Strong("Phone: "), "1868-662-2241 ext. 1004"
                    ], style={'opacity': '0.9'})
                ], md=4)
            ]),
            html.Hr(style={'borderColor': 'rgba(255,255,255,0.2)', 'margin': '40px 0 20px'}),
            html.P("© 2025 University of the Southern Caribbean - Institutional Research Department",
                   className="text-center", style={'opacity': '0.8'})
        ])
    ], style={'background': 'linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%)', 'color': 'white', 'padding': '60px 0 30px'})
"""

def create_login_page():
    """Create the login page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src="assets/usc-logo.png", style={'height': '120px', 'marginBottom': '20px'},
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

                    ])
                ], className="mt-3", color="light"),
                dbc.Card([
                    dbc.CardBody([
                        html.P([
                            "Don't have an account? ",
                            html.A("Sign up here", href="/signup", style={'color': USC_COLORS['primary_green']})
                        ], className="text-center mb-0"),
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Forgot Password?", className="card-title"),
                            html.P("Enter your email to receive a new password:", className="small"),
                            dbc.Input(id="forgot-email", type="email", placeholder="Enter your email",
                                      className="mb-2"),
                            dbc.Button("Send New Password", id="forgot-password-btn", color="outline-primary",
                                       size="sm"),
                            html.Div(id="forgot-password-alert", className="mt-2")
                        ])
                    ], className="mt-3")
                    ])
                ], className="mt-3")
            ], width=12, md=6, lg=4),

        ], justify="center", className="min-vh-100 d-flex align-items-center")
    ], fluid=True, className="bg-light")


@callback(
    Output('forgot-password-alert', 'children'),
    Input('forgot-password-btn', 'n_clicks'),
    State('forgot-email', 'value'),
    prevent_initial_call=True
)
def handle_forgot_password(n_clicks, email):
    if not n_clicks or not email:
        return ""

    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Check if user exists
        cursor.execute('SELECT id, full_name FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()

        if not user_data:
            return dbc.Alert("Email not found in our system", color="danger", dismissable=True)

        user_id, user_name = user_data

        # Generate new password
        from auth_utils import generate_random_password, send_password_reset_email
        new_password = generate_random_password()

        # Update password in database
        password_hash = hash_password(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        conn.commit()

        # Send email
        email_sent = send_password_reset_email(email, user_name, new_password, "forgot")

        if email_sent:
            return dbc.Alert("New password sent to your email", color="success", dismissable=True)
        else:
            return dbc.Alert("Password reset but email failed to send", color="warning", dismissable=True)

    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True)
    finally:
        conn.close()


def create_home_layout(user_data=None):
    """Complete home page layout with sticky pill navigation"""

    # Get posts for news feed
    from posts_system import get_active_posts
    user_tier = user_data.get('access_tier', 1) if user_data else 1
    posts = get_active_posts(user_tier=user_tier, include_expired=False)

    # Import news feed component
    from posts_ui import create_news_feed_section

    return html.Div([
        create_hero_section(),  # Hero content
        create_sticky_pill_navigation(),  # Pill nav (SEPARATE - will stick!)
        create_stats_overview(),

        # News feed section
        create_news_feed_section(posts, user_data) if posts else html.Div(),

        create_about_ir_section(),
        create_feature_showcase(),
        create_director_message(),
        #create_quick_links(),
       # create_modern_footer(),
        create_usc_footer(),
        create_scroll_trigger(),
        create_scroll_spy_interval()  # ADD THIS for scroll spy
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
    """Access denied page with working sign in button"""
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
                        dbc.Button("Sign In", href="/login", color="success")  # FIXED: Use href instead of id
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

    # ✅ Posts system components
    dcc.Store(id='posts-refresh-trigger', storage_type='memory'),
    dcc.Store(id='delete-post-id-store', storage_type='memory'),
    dcc.Store(id='cleanup-status-dummy', storage_type='memory'),
    dcc.Interval(id='cleanup-interval', interval=3600000, n_intervals=0),

    # ✅ Delete confirmation modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Confirm Deletion")),
        dbc.ModalBody([
            html.I(className="fas fa-exclamation-triangle fa-3x text-warning mb-3 d-block text-center"),
            html.H5("Are you sure you want to delete this post?", className="text-center"),
            html.P("This action cannot be undone.", className="text-muted text-center")
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-delete-post", color="secondary"),
            dbc.Button("Delete", id="confirm-delete-post", color="danger")
        ])
    ], id='delete-post-modal', centered=True),

    html.Div(id='page-content')
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
        return create_login_page()

    # Route pages
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

    # ADD THIS NEW FACTBOOK ROUTE
    # ENSURE ONLY ONE FACTBOOK ROUTE IN app.py:

    elif pathname == '/factbook':

        content = dbc.Container([

            dbc.Alert([

                html.H4("Factbook Moved", className="alert-heading"),

                html.P("The USC Factbook is now available as a separate application."),

                html.Hr(),

                dbc.Button("Access Factbook",

                           href="https://your-factbook-url.com",  # ⚠️ REPLACE

                           target="_blank",

                           color="primary",

                           external_link=True)

            ], color="info")

        ], className="py-5")

    elif pathname == '/admin':
        if not user_data or user_data.get('access_tier', 1) < 3:
            content = create_access_denied_page("Admin Access Required",
                                                "You need administrative access to view this page.")
        else:
            content = create_comprehensive_admin_dashboard(user_data)

    elif pathname == '/signup':
        if user_data:
            return dcc.Location(pathname='/', id='redirect-home')
        return create_signup_page()

    elif pathname == '/request-report':
        content = create_data_request_page()

    elif pathname == '/profile':
        if not user_data:
            return dcc.Location(pathname='/login', id='redirect-login')
        return create_profile_page(user_data)

    # Service pages
    elif pathname == '/help':
        content = create_placeholder_page("Help Center", "Documentation and support resources")



    elif pathname == '/news':
        from posts_system import get_active_posts
        from posts_ui import create_news_page

        user_tier = user_data.get('access_tier', 1) if user_data else 1
        posts = get_active_posts(user_tier=user_tier, include_expired=False)

        content = html.Div([
            #create_modern_navbar(user_data),  # ✅ One navbar here
            create_news_page(posts, user_data)  # ✅ No navbar inside
        ])

    elif pathname == '/factbook/enrollment':
        from pages.universal_factbook_page import create_universal_factbook_page
        content = create_universal_factbook_page('enrollment')
        content = require_access(content, 2, user_data)

    elif pathname == '/factbook/financial-data':
        from pages.universal_factbook_page import create_universal_factbook_page
        content = create_universal_factbook_page('financial-data')
        content = require_access(content, 3, user_data)

    elif pathname == '/factbook/hr-data':
        from pages.universal_factbook_page import create_universal_factbook_page
        content = create_universal_factbook_page('hr-data')
        content = require_access(content, 2, user_data)
    elif pathname == '/factbook/student-labour':
        try:
            # Add debug print to see if we reach this route
            print(f"[DEBUG] Accessing student-labour route for user: {user_data}")

            from factbook.student_labour_report import create_factbook_student_labour_page
            content = create_factbook_student_labour_page()

            # Check user access level
            user_tier = user_data.get('access_tier', 1) if user_data else 1
            print(f"[DEBUG] User tier: {user_tier}, Required: 3")

            content = require_access(content, 3, user_data)  # Tier 3 for financial data

        except ImportError as e:
            print(f"[ERROR] Import failed for student_labour_report: {e}")
            content = create_placeholder_page(
                "Student Labour Report",
                "Student employment and financial analytics. Import error - check file exists."
            )
            content = require_access(content, 3, user_data)

        except Exception as e:
            print(f"[ERROR] Student labour page creation failed: {e}")
            content = create_placeholder_page(
                "Student Labour Report Error",
                f"An error occurred loading the page: {str(e)}"
            )
            content = require_access(content, 3, user_data)


    else:
        content = create_placeholder_page("Page Not Found", f"The page '{pathname}' could not be found")

    navbar = create_modern_navbar(user_data)
    return html.Div([navbar, content])




# ============================================================================
# RUN APPLICATION
# ============================================================================
try:
    from posts_system import init_posts_database
    print("🔧 Initializing posts database...")
    init_posts_database()
    print("✅ Posts database ready")
except Exception as e:
    print(f"❌ Database init error: {e}")

if __name__ == '__main__':
    #init_enhanced_database()
    from posts_system import init_posts_database

    init_posts_database()
    import posts_callbacks
    port = int(os.environ.get('PORT', 8050))
    app.run_server(
        debug=False,  # Set to False for production
        host='0.0.0.0',
        port=port
    )