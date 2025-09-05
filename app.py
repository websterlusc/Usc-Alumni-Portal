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

DATABASE = 'usc_ir.db'
SECRET_KEY = 'usc-ir-secret-key-change-in-production-2025'


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

    cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        return dict(user)
    return None


def create_session(user_id):
    """Create user session"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=8)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, token, expires_at))
    conn.commit()
    conn.close()

    return token


def load_enrollment_stats():
    """Load quick enrollment statistics"""
    try:
        df = pd.read_excel('data/enrolment_data.xlsx', sheet_name='2024-2025')

        stats = {
            'total_students': len(df),
            'undergraduate': len(df[df['Course Level'] == 'Undergraduate']) if 'Course Level' in df.columns else 0,
            'graduate': len(df[df['Course Level'] == 'Graduate']) if 'Course Level' in df.columns else 0,
            'campuses': df['Campus'].nunique() if 'Campus' in df.columns else 1
        }
        return stats
    except Exception as e:
        print(f"Error loading enrollment data: {e}")
        return {
            'total_students': 3110,
            'undergraduate': 2800,
            'graduate': 310,
            'campuses': 4
        }


# ============================================================================
# HOMEPAGE COMPONENTS
# ============================================================================

def create_stats_cards():
    """Create statistics cards"""
    stats = load_enrollment_stats()

    card_style = {
        'border': f'2px solid {USC_COLORS["light_gray"]}',
        'borderRadius': '10px',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
        'transition': 'transform 0.2s',
        'height': '100%'
    }

    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-users",
                               style={'fontSize': '2rem', 'color': USC_COLORS['secondary_green'],
                                      'marginBottom': '1rem'}),
                        html.H2(f"{stats['total_students']:,}", className="fw-bold mb-2",
                                style={'color': USC_COLORS['primary_green']}),
                        html.H6("Total Students", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], style=card_style)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-graduation-cap",
                               style={'fontSize': '2rem', 'color': USC_COLORS['secondary_green'],
                                      'marginBottom': '1rem'}),
                        html.H2(f"{stats['undergraduate']:,}", className="fw-bold mb-2",
                                style={'color': USC_COLORS['primary_green']}),
                        html.H6("Undergraduates", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], style=card_style)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-user-graduate",
                               style={'fontSize': '2rem', 'color': USC_COLORS['secondary_green'],
                                      'marginBottom': '1rem'}),
                        html.H2(f"{stats['graduate']:,}", className="fw-bold mb-2",
                                style={'color': USC_COLORS['primary_green']}),
                        html.H6("Graduate Students", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], style=card_style)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-building",
                               style={'fontSize': '2rem', 'color': USC_COLORS['secondary_green'],
                                      'marginBottom': '1rem'}),
                        html.H2(f"{stats['campuses']}", className="fw-bold mb-2",
                                style={'color': USC_COLORS['primary_green']}),
                        html.H6("Campuses", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], style=card_style)
        ], width=3),
    ], className="mb-5 g-3")


def create_homepage(user=None):
    """Create homepage layout focused on IR services"""

    # Hero section
    hero_section = dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H1("USC Institutional Research", className="display-4 fw-bold mb-4",
                        style={'color': USC_COLORS['primary_green']}),
                html.P([
                    "We provide comprehensive data analysis, research support, and evidence-based insights ",
                    "to inform strategic decision-making across the University of the Southern Caribbean. ",
                    "Our team transforms raw institutional data into actionable intelligence for administrators, ",
                    "faculty, and stakeholders."
                ], className="lead mb-4", style={'fontSize': '1.1rem', 'lineHeight': '1.6'})
            ], className="text-center py-4")
        ])
    ], style={
        'background': f'linear-gradient(135deg, {USC_COLORS["white"]}, {USC_COLORS["light_gray"]})',
        'border': f'3px solid {USC_COLORS["primary_green"]}',
        'borderRadius': '15px',
        'marginBottom': '3rem'
    })

    # What we do section
    services_section = html.Div([
        html.H2("What We Do", className="text-center mb-5 fw-bold", style={'color': USC_COLORS['primary_green']}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-chart-line fa-3x mb-3",
                                   style={'color': USC_COLORS['secondary_green']}),
                            html.H4("Data Analytics & Reporting", className="fw-bold mb-3"),
                            html.P(
                                "We analyze enrollment trends, graduation rates, retention statistics, and academic performance metrics to support institutional planning and accreditation requirements.")
                        ], className="text-center")
                    ])
                ])
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-search fa-3x mb-3",
                                   style={'color': USC_COLORS['secondary_green']}),
                            html.H4("Research Support", className="fw-bold mb-3"),
                            html.P(
                                "We conduct institutional research studies, surveys, and assessments to evaluate program effectiveness and support evidence-based decision making.")
                        ], className="text-center")
                    ])
                ])
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-file-alt fa-3x mb-3",
                                   style={'color': USC_COLORS['secondary_green']}),
                            html.H4("Custom Reports", className="fw-bold mb-3"),
                            html.P(
                                "We create tailored reports and analyses for specific departments, committees, and administrative needs across the university.")
                        ], className="text-center")
                    ])
                ])
            ], width=4)
        ], className="g-4 mb-5")
    ])

    # Quick request form section
    request_form_section = dbc.Card([
        dbc.CardHeader([
            html.H3("Request a Custom Report", className="fw-bold mb-0 text-center",
                    style={'color': USC_COLORS['primary_green']})
        ]),
        dbc.CardBody([
            html.P(
                "Need specific data analysis or a custom report? Submit your request below and our team will get back to you.",
                className="text-center mb-4"),
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Your Name", className="fw-bold"),
                        dbc.Input(type="text", placeholder="Full Name", className="mb-3")
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Email Address", className="fw-bold"),
                        dbc.Input(type="email", placeholder="your.email@usc.edu.tt", className="mb-3")
                    ], width=6)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Department/Office", className="fw-bold"),
                        dbc.Input(type="text", placeholder="Your Department", className="mb-3")
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Report Type", className="fw-bold"),
                        dbc.Select(
                            options=[
                                {"label": "Enrollment Analysis", "value": "enrollment"},
                                {"label": "Graduation Data", "value": "graduation"},
                                {"label": "Financial Analysis", "value": "financial"},
                                {"label": "HR Analytics", "value": "hr"},
                                {"label": "Custom Analysis", "value": "custom"},
                                {"label": "Other", "value": "other"}
                            ],
                            placeholder="Select report type",
                            className="mb-3"
                        )
                    ], width=6)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Request Details", className="fw-bold"),
                        dbc.Textarea(
                            placeholder="Please describe what data you need, the purpose of the report, any specific metrics or time periods, and when you need it by...",
                            rows=4,
                            className="mb-3"
                        )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-paper-plane me-2"),
                            "Submit Request"
                        ], color="success", size="lg", className="w-100")
                    ], width={"size": 6, "offset": 3})
                ])
            ])
        ])
    ], className="mb-5")

    return html.Div([
        create_navbar(user),
        dbc.Container([
            hero_section,
            create_stats_cards(),
            services_section,
            request_form_section,

            # Contact section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("Contact Our Team", className="mb-0 fw-bold",
                                               style={'color': USC_COLORS['primary_green']})),
                        dbc.CardBody([
                            html.P([
                                html.Strong("Director: "), "Nordian C. Swaby Robinson", html.Br(),
                                html.Strong("Email: "), html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt"), html.Br(),
                                html.Strong("Phone: "), "868-645-3265 ext. 2150", html.Br(),
                                html.Strong("Office: "), "Administration Building", html.Br(),
                                html.Strong("Web Developer: "), "Liam Webster (websterl@usc.edu.tt, ext. 1014)"
                            ])
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
# RUN APPLICATION
# ============================================================================

# ============================================================================
# DEPLOYMENT SETUP
# ============================================================================

# Create app instance for deployment
app = create_app()
server = app.server  # Expose Flask server for Gunicorn

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    import os

    print("🎓 Starting USC Institutional Research Portal...")

    # Skip database check for deployment
    # if not os.path.exists(DATABASE):
    #     print("❌ Database not found! Please run fix_database.py first.")
    #     exit(1)

    print("✅ Application initialized")
    print("📍 Access the portal at: http://localhost:8050")
    print("🔑 Default admin login: ir@usc.edu.tt / admin123!USC")
    print("🗂️  Application now uses organized file structure")

    # Get port from environment for deployment
    port = int(os.environ.get('PORT', 8050))

    app.run_server(debug=False, host='0.0.0.0', port=port)