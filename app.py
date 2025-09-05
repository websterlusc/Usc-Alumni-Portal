#!/usr/bin/env python3
"""
USC Institutional Research Portal - Main Application
Clean main app with organized imports from separate page files
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

# Import components and pages
from components.navbar import create_navbar, create_footer, USC_COLORS
from pages.facts_about_usc import (
    create_about_usc_page, create_vision_mission_page, create_governance_page,
    create_usc_history_page, create_campus_info_page, create_contact_page
)
from pages.student_services import (
    create_admissions_page, create_programs_page, create_calendar_page,
    create_student_life_page, create_student_support_page
)
from pages.access_control import (
    create_login_page, create_access_denied_page, create_profile_page,
    create_request_access_page, create_login_history_page
)
from pages.factbook_landing import create_factbook_landing_page
from pages.request_reports import create_request_reports_page
from pages.placeholder_pages import (
    create_admin_dashboard_page, create_user_management_page
)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE = os.getenv('DATABASE_PATH', 'usc_ir.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'usc-ir-secret-key-change-in-production-2025')


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

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

    # Update user last login
    cursor.execute('''
        UPDATE users SET last_login = datetime('now') WHERE id = ?
    ''', (user_id,))

    # Create session
    cursor.execute('''
        INSERT INTO user_sessions (session_token, user_id, expires_at)
        VALUES (?, ?, ?)
    ''', (session_token, user_id, expires_at))

    conn.commit()
    conn.close()

    return session_token


def create_homepage(user=None):
    """Create homepage content"""
    return html.Div([
        create_navbar(user),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1("University of Southern Caribbean",
                                className="display-4 mb-3",
                                style={'color': USC_COLORS['primary_green']}),
                        html.H2("Institutional Research Portal",
                                className="h3 text-muted mb-4"),
                        html.P([
                            "Welcome to the USC Institutional Research Portal. ",
                            "Access comprehensive data and insights about our university community, ",
                            "academic programs, and institutional effectiveness."
                        ], className="lead mb-4"),

                        # Quick stats
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("3,110", className="text-primary mb-0"),
                                        html.P("Current Students", className="small text-muted mb-0")
                                    ])
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("350+", className="text-primary mb-0"),
                                        html.P("Faculty & Staff", className="small text-muted mb-0")
                                    ])
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("15+", className="text-primary mb-0"),
                                        html.P("Academic Programs", className="small text-muted mb-0")
                                    ])
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("98", className="text-primary mb-0"),
                                        html.P("Years of Excellence", className="small text-muted mb-0")
                                    ])
                                ], className="text-center")
                            ], width=3)
                        ], className="g-3 mb-4"),

                        # Access info
                        html.Div([
                            html.H5("Data Access", className="mb-3"),
                            html.P([
                                "Access to institutional data is provided based on your role and authorization level. ",
                                "Please log in to access the factbook and analytical tools."
                            ], className="mb-3"),

                            dbc.ButtonGroup([
                                dbc.Button("View Factbook", href="/factbook", color="primary", size="lg")
                                if user and user.get('access_tier', 1) >= 2
                                else dbc.Button("Login to Access Data", href="/login", color="outline-primary",
                                                size="lg"),

                                dbc.Button("Request Access", href="/request-access", color="outline-secondary",
                                           size="lg")
                                if user and user.get('access_tier', 1) < 3
                                else None
                            ], className="d-flex flex-wrap gap-2")
                        ])
                    ])
                ], width=8),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Quick Links", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dbc.ListGroup([
                                dbc.ListGroupItem([
                                    dbc.Button("About USC", href="/about-usc", color="link", className="p-0")
                                ], className="border-0"),
                                dbc.ListGroupItem([
                                    dbc.Button("Vision & Mission", href="/vision-mission-motto", color="link",
                                               className="p-0")
                                ], className="border-0"),
                                dbc.ListGroupItem([
                                    dbc.Button("Governance", href="/governance", color="link", className="p-0")
                                ], className="border-0"),
                                dbc.ListGroupItem([
                                    dbc.Button("Academic Programs", href="/programs", color="link", className="p-0")
                                ], className="border-0"),
                                dbc.ListGroupItem([
                                    dbc.Button("Campus Life", href="/student-life", color="link", className="p-0")
                                ], className="border-0"),
                                dbc.ListGroupItem([
                                    dbc.Button("Contact Us", href="/contact", color="link", className="p-0")
                                ], className="border-0")
                            ], flush=True)
                        ])
                    ])
                ], width=4)
            ])
        ], fluid=True, className="py-4"),

        # Contact info footer
        dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Institutional Research Department", className="mb-2"),
                        html.P([
                            html.Strong("Email: "), html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt"), html.Br(),
                            html.Strong("Phone: "), "(868) 663-9932, ext. 2150", html.Br(),
                            html.Strong("Office: "), "Administration Building", html.Br(),
                            html.Strong("Web Developer: "), "Liam Webster (websterl@usc.edu.tt, ext. 1014)"
                        ])
                    ])
                ], width=12)
            ], className="g-4")
        ], fluid=True, className="px-4"),
        create_footer()
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def create_app():
    """Create Dash application"""

    # Flask server
    server = Flask(__name__)
    server.secret_key = SECRET_KEY

    # Dash app
    app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
        ],
        title="USC Institutional Research"
    )

    # App layout
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    # ========================================================================
    # FLASK ROUTES
    # ========================================================================

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

    # ========================================================================
    # DASH CALLBACKS
    # ========================================================================

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

        # Route to appropriate page
        if pathname == '/login':
            return create_login_page()

        # Facts About USC pages (public)
        elif pathname == '/about-usc':
            return create_about_usc_page()
        elif pathname == '/vision-mission-motto':
            return create_vision_mission_page()
        elif pathname == '/governance':
            return create_governance_page()
        elif pathname == '/usc-history':
            return create_usc_history_page()
        elif pathname == '/campus-info':
            return create_campus_info_page()
        elif pathname == '/contact':
            return create_contact_page()

        # Student Services pages (public)
        elif pathname == '/admissions':
            return create_admissions_page()
        elif pathname == '/programs':
            return create_programs_page()
        elif pathname == '/calendar':
            return create_calendar_page()
        elif pathname == '/student-life':
            return create_student_life_page()
        elif pathname == '/student-support':
            return create_student_support_page()

        # Factbook landing page
        elif pathname == '/factbook':
            return create_factbook_landing_page(user)

        # Request reports page
        elif pathname == '/request-reports':
            return create_request_reports_page(user)

        # User pages
        elif pathname == '/profile' and user:
            return create_profile_page(user)
        elif pathname == '/request-access':
            return create_request_access_page(user)
        elif pathname == '/login-history' and user:
            return create_login_history_page(user)
        elif pathname == '/account-settings' and user:
            return create_profile_page(user)

        # Admin pages
        elif pathname == '/admin' and user and user.get('is_admin'):
            return create_admin_dashboard_page()
        elif pathname == '/user-management' and user and user.get('is_admin'):
            return create_user_management_page()

        # Factbook data pages (to be implemented)
        elif pathname.startswith('/factbook/'):
            if not user:
                return create_access_denied_page(required_tier=2)
            elif user['access_tier'] < 2:
                return create_access_denied_page(required_tier=2)
            elif pathname in ['/factbook/debt-collection', '/factbook/endowment-funds',
                              '/factbook/financial-data', '/factbook/gate-funding',
                              '/factbook/income-units', '/factbook/scholarships',
                              '/factbook/subsidies'] and user['access_tier'] < 3:
                return create_access_denied_page(required_tier=3)
            else:
                return create_factbook_landing_page(user)

        # Default to homepage
        else:
            return create_homepage(user)

    return app


# ============================================================================
# CREATE APP INSTANCE AND EXPOSE SERVER
# ============================================================================

# Create the app instance
app = create_app()

# CRITICAL: Expose the Flask server for Gunicorn
server = app.server

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("🎓 Starting USC Institutional Research Portal...")

    # Check if database exists
    if not os.path.exists(DATABASE):
        print("❌ Database not found! Please run database_init.py first.")
        # Don't exit in production, try to continue

    # Get configuration from environment
    debug_mode = os.getenv('DEBUG', 'True').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8050))

    print("✅ Application initialized")
    print(f"📍 Access the portal at: http://{host}:{port}")
    print("🔑 Default admin login: admin@usc.edu.tt / admin123")
    print("🗂️  Application now uses organized file structure")

    app.run_server(debug=debug_mode, host=host, port=port)