#!/usr/bin/env python3
"""
USC Institutional Research Portal - Main Application
Fixed for Render deployment with Gunicorn
"""

import os
import sqlite3
import secrets
import bcrypt
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, session, request, redirect, url_for, flash
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE = os.getenv('DATABASE_PATH', 'usc_ir.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'usc-ir-secret-key-change-in-production-2025')


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def init_database():
    """Initialize database if it doesn't exist"""
    if not os.path.exists(DATABASE):
        print("🔧 Creating database...")
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Create basic users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'employee',
                access_tier INTEGER DEFAULT 2,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Create default admin
        admin_password = "admin123"
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, full_name, role, access_tier)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@usc.edu.tt', password_hash, 'System Administrator', 'admin', 3))

        conn.commit()
        conn.close()
        print("✅ Database initialized")


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def get_user_by_session(session_token):
    """Get user by session token"""
    if not session_token:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.* FROM users u
        JOIN user_sessions s ON u.id = s.user_id
        WHERE s.session_token = ? AND s.expires_at > datetime('now')
    ''', (session_token,))

    user = cursor.fetchone()
    conn.close()

    return dict(user) if user else None


def verify_user(username, password):
    """Verify user login"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, username))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        return dict(user)
    return None


def create_session(user_id):
    """Create user session"""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=8)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_sessions (session_token, user_id, expires_at)
        VALUES (?, ?, ?)
    ''', (session_token, user_id, expires_at))

    conn.commit()
    conn.close()

    return session_token


# ============================================================================
# SAFE COMPONENT IMPORTS
# ============================================================================

def safe_import_components():
    """Safely import components, create fallbacks if missing"""
    global create_navbar, create_footer, USC_COLORS
    global create_home_page, create_factbook_landing_page
    global create_login_page, create_access_denied_page

    try:
        from components.navbar import create_navbar, create_footer, USC_COLORS
        print("✅ Navbar components imported")
    except ImportError as e:
        print(f"⚠️ Navbar import failed: {e}")
        # Fallback navbar
        USC_COLORS = {'primary_green': '#1B5E20', 'accent_yellow': '#FDD835'}

        def create_navbar(user=None):
            return dbc.NavbarSimple(
                brand="USC IR Portal",
                brand_href="/",
                color="primary",
                dark=True,
                children=[
                    dbc.NavItem(dbc.NavLink("Home", href="/")),
                    dbc.NavItem(dbc.NavLink("Login", href="/login")) if not user else
                    dbc.NavItem(dbc.NavLink("Logout", href="/logout"))
                ]
            )

        def create_footer():
            return html.Footer("USC Institutional Research Portal", className="text-center p-3")

    try:
        from pages.home import create_home_page
        print("✅ Home page imported")
    except ImportError:
        print("⚠️ Home page import failed, using fallback")

        def create_home_page(user=None):
            return dbc.Container([
                html.H1("USC Institutional Research Portal", className="text-center my-4"),
                html.P("Welcome to the USC IR Portal", className="text-center"),
                dbc.Button("View Factbook", href="/factbook", color="primary") if user else
                dbc.Button("Login", href="/login", color="primary")
            ])

    try:
        from pages.factbook_landing import create_factbook_landing_page
        print("✅ Factbook landing imported")
    except ImportError:
        print("⚠️ Factbook landing import failed, using fallback")

        def create_factbook_landing_page(user=None):
            return dbc.Container([
                html.H1("Factbook", className="text-center my-4"),
                html.P("Institutional Research Data Portal", className="text-center"),
                html.P(f"Welcome, {user.get('full_name', 'User') if user else 'Guest'}")
            ])

    try:
        from pages.access_control import create_login_page, create_access_denied_page
        print("✅ Access control imported")
    except ImportError:
        print("⚠️ Access control import failed, using fallback")

        def create_login_page():
            return dbc.Container([
                html.H2("Login", className="text-center my-4"),
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Username"),
                            dbc.Input(type="text", name="username", required=True),
                        ], width=12),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Password"),
                            dbc.Input(type="password", name="password", required=True),
                        ], width=12),
                    ], className="mb-3"),
                    dbc.Button("Login", type="submit", color="primary")
                ], action="/login", method="post")
            ])

        def create_access_denied_page():
            return dbc.Container([
                html.H2("Access Denied", className="text-center my-4 text-danger"),
                html.P("You don't have permission to access this resource.", className="text-center"),
                dbc.Button("Go Home", href="/", color="primary")
            ])


# ============================================================================
# CREATE APPLICATION
# ============================================================================

# Initialize database
init_database()

# Import components safely
safe_import_components()

# Create Flask server
server = Flask(__name__)
server.secret_key = SECRET_KEY

# Create Dash app
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="USC Institutional Research"
)

# CRITICAL: Expose server for Gunicorn
print("✅ Server variable created and exposed")


# ============================================================================
# FLASK ROUTES
# ============================================================================

@server.route('/login', methods=['POST'])
def handle_login():
    """Handle login form submission"""
    username = request.form.get('username')
    password = request.form.get('password')

    if username and password:
        user = verify_user(username, password)
        if user:
            session_token = create_session(user['id'])
            session['session_token'] = session_token
            session['user_id'] = user['id']
            return redirect('/')
        else:
            flash('Invalid username or password', 'error')

    return redirect('/login')


@server.route('/logout')
def handle_logout():
    """Handle logout"""
    session.clear()
    return redirect('/')


# ============================================================================
# DASH LAYOUT
# ============================================================================

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# ============================================================================
# DASH CALLBACKS
# ============================================================================

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route pages based on URL"""

    # Get current user from session
    user = None
    try:
        session_token = session.get('session_token')
        if session_token:
            user = get_user_by_session(session_token)
    except:
        pass

    # Create page layout with navbar and footer
    navbar = create_navbar(user)
    footer = create_footer()

    # Route to appropriate page
    if pathname == '/login':
        content = create_login_page()
    elif pathname == '/factbook':
        if user and user.get('access_tier', 1) >= 2:
            content = create_factbook_landing_page(user)
        else:
            content = create_access_denied_page()
    elif pathname == '/admin':
        if user and user.get('role') == 'admin':
            content = dbc.Container([
                html.H1("Admin Dashboard", className="my-4"),
                html.P("Admin functionality coming soon...")
            ])
        else:
            content = create_access_denied_page()
    else:
        # Default to home page
        content = create_home_page(user)

    # Combine layout
    return html.Div([
        navbar,
        content,
        footer
    ])


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    # Get configuration from environment
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8050))

    print(f"🚀 Starting USC IR Portal...")
    print(f"   Debug: {debug_mode}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Database: {DATABASE}")

    app.run_server(
        debug=debug_mode,
        host=host,
        port=port
    )
else:
    print("✅ App loaded for Gunicorn")