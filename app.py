"""
USC Institutional Research Portal - Complete Application with Authentication
Integrates your existing design with full 4-tier authentication system
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
import secrets
import os
from datetime import datetime, timedelta
import json

# Import your existing page components
from pages.about_usc_page import create_about_usc_page
from pages.vision_mission_page import create_vision_mission_page
from pages.contact_page import create_contact_page
from pages.governance_page import create_governance_page

# Import the new authentication system
from auth_database import db
from auth_system import (
    auth, create_login_form, create_registration_form,
    create_access_request_form, create_admin_dashboard,
    create_user_profile_page, create_enhanced_navbar,
    create_access_denied_page
)

# Import authentication callbacks (this will register all the callbacks)
import auth_callbacks

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
        {"name": "description", "content": "USC Institutional Research Portal - Data-driven insights and analytics"}
    ]
)

app.title = "USC Institutional Research Portal"
server = app.server

# ============================================================================
# ENHANCED HOME PAGE WITH AUTHENTICATION
# ============================================================================

def create_authenticated_home_layout(user_info=None):
    """Create home page with authentication-aware content"""
    access_tier = user_info.get('access_tier', 1) if user_info else 1

    # Welcome section
    if user_info:
        welcome_section = dbc.Jumbotron([
            html.H1(f"Welcome back, {user_info['full_name']}",
                   className="display-4 fw-bold",
                   style={'color': USC_COLORS['primary_green']}),
            html.P(f"Access Level: Tier {access_tier} | Last Login: Today",
                   className="lead text-muted"),
            html.Hr(),
            html.P("Access your institutional research data and analytics below.")
        ], fluid=True, style={'background': USC_COLORS['light_gray']})
    else:
        welcome_section = dbc.Jumbotron([
            html.H1("USC Institutional Research Portal",
                   className="display-4 fw-bold",
                   style={'color': USC_COLORS['primary_green']}),
            html.P("Data-driven insights for the University of the Southern Caribbean",
                   className="lead"),
            html.Hr(),
            html.P("Login to access factbook data and institutional analytics.")
        ], fluid=True, style={'background': USC_COLORS['light_gray']})

    # Feature cards based on access level
    feature_cards = []

    # Public features (Tier 1+)
    public_cards = [
        {
            'title': 'About USC',
            'description': 'Learn about our history, mission, and values',
            'icon': 'fas fa-university',
            'link': '/about-usc',
            'color': 'primary'
        },
        {
            'title': 'Vision & Mission',
            'description': 'Our institutional vision and mission statement',
            'icon': 'fas fa-eye',
            'link': '/vision-mission',
            'color': 'info'
        },
        {
            'title': 'Governance',
            'description': 'Leadership structure and governance framework',
            'icon': 'fas fa-users-cog',
            'link': '/governance',
            'color': 'secondary'
        }
    ]

    # Factbook features (Tier 2+)
    factbook_cards = [
        {
            'title': 'Student Analytics',
            'description': 'Enrollment trends, graduation rates, and student data',
            'icon': 'fas fa-chart-line',
            'link': '/enrollment',
            'color': 'success'
        },
        {
            'title': 'HR Analytics',
            'description': 'Faculty and staff data, employment trends',
            'icon': 'fas fa-users',
            'link': '/hr-data',
            'color': 'warning'
        },
        {
            'title': 'Interactive Factbook',
            'description': 'Comprehensive institutional data dashboard',
            'icon': 'fas fa-book-open',
            'link': '/factbook',
            'color': 'info'
        }
    ]

    # Financial features (Tier 3+)
    financial_cards = [
        {
            'title': 'Financial Dashboard',
            'description': 'Budget analysis, revenue tracking, financial reports',
            'icon': 'fas fa-chart-pie',
            'link': '/financial',
            'color': 'danger'
        },
        {
            'title': 'Budget Analysis',
            'description': 'Detailed budget breakdowns and variance analysis',
            'icon': 'fas fa-calculator',
            'link': '/budget',
            'color': 'warning'
        }
    ]

    # Admin features (Tier 4+)
    admin_cards = [
        {
            'title': 'Admin Dashboard',
            'description': 'User management, system administration',
            'icon': 'fas fa-cogs',
            'link': '/admin',
            'color': 'dark'
        }
    ]

    # Build feature cards based on access level
    all_cards = public_cards.copy()

    if access_tier >= 2:
        all_cards.extend(factbook_cards)
    elif not user_info:
        # Show locked cards for non-authenticated users
        locked_cards = [
            {
                'title': 'Factbook Data',
                'description': 'Login required for access to institutional data',
                'icon': 'fas fa-lock',
                'link': '#',
                'color': 'secondary',
                'locked': True
            }
        ]
        all_cards.extend(locked_cards)

    if access_tier >= 3:
        all_cards.extend(financial_cards)

    if access_tier >= 4:
        all_cards.extend(admin_cards)

    # Create card components
    for card_info in all_cards:
        if card_info.get('locked'):
            card = dbc.Card([
                dbc.CardBody([
                    html.H4([
                        html.I(className=f"{card_info['icon']} me-2"),
                        card_info['title']
                    ], style={'color': USC_COLORS['medium_gray']}),
                    html.P(card_info['description'], style={'color': USC_COLORS['medium_gray']}),
                    dbc.Button("Login Required", color="secondary", disabled=True)
                ])
            ], className="h-100", outline=True, color="secondary")
        else:
            card = dbc.Card([
                dbc.CardBody([
                    html.H4([
                        html.I(className=f"{card_info['icon']} me-2"),
                        card_info['title']
                    ], style={'color': USC_COLORS['primary_green']}),
                    html.P(card_info['description']),
                    dbc.Button("Explore", href=card_info['link'],
                              color=card_info['color'], external_link=True)
                ])
            ], className="h-100")

        feature_cards.append(card)

    # Quick stats section
    stats_section = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("3,110", className="text-center fw-bold",
                           style={'color': USC_COLORS['primary_green']}),
                    html.P("Total Students", className="text-center text-muted")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("247", className="text-center fw-bold",
                           style={'color': USC_COLORS['primary_green']}),
                    html.P("Faculty & Staff", className="text-center text-muted")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("450+", className="text-center fw-bold",
                           style={'color': USC_COLORS['primary_green']}),
                    html.P("Graduates (2025)", className="text-center text-muted")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("15", className="text-center fw-bold",
                           style={'color': USC_COLORS['primary_green']}),
                    html.P("Academic Programs", className="text-center text-muted")
                ])
            ])
        ], width=3)
    ], className="mb-5")

    # Authentication prompt for logged out users
    auth_section = None
    if not user_info:
        auth_section = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Access Your Data", className="text-center mb-4"),
                        html.P("Login to access institutional research data and analytics."),
                        html.Div(id="auth-form-container", children=create_login_form())
                    ])
                ])
            ], width=8, className="mx-auto")
        ], className="mt-5")

    # Combine all sections
    layout_components = [
        welcome_section,
        dbc.Container([
            stats_section,
            html.H2("Features & Services", className="mb-4 text-center",
                   style={'color': USC_COLORS['primary_green']}),
            dbc.Row([
                dbc.Col(card, width=4, className="mb-4") for card in feature_cards[:3]
            ]),
            dbc.Row([
                dbc.Col(card, width=4, className="mb-4") for card in feature_cards[3:6]
            ]) if len(feature_cards) > 3 else None,
            dbc.Row([
                dbc.Col(card, width=4, className="mb-4") for card in feature_cards[6:]
            ]) if len(feature_cards) > 6 else None,
        ], fluid=True, className="mt-4")
    ]

    if auth_section:
        layout_components.append(auth_section)

    return html.Div(layout_components)

# ============================================================================
# PLACEHOLDER PAGES FOR DEVELOPMENT
# ============================================================================

def create_placeholder_page(title, description, required_tier=1):
    """Create placeholder page for routes under development"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H4(title, className="alert-heading"),
                    html.P(description),
                    html.Hr(),
                    html.P(f"Required Access: Tier {required_tier}+", className="mb-0")
                ], color="info", className="text-center"),
                dbc.Button("Return Home", href="/", color="primary", className="d-block mx-auto mt-4")
            ])
        ])
    ], className="mt-5")

# ============================================================================
# MAIN APPLICATION LAYOUT
# ============================================================================

def serve_layout():
    """Main application layout with session management"""
    return html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='user-session', storage_type='session'),
        html.Div(id='page-content')
    ])

app.layout = serve_layout

# ============================================================================
# MAIN ROUTING CALLBACK
# ============================================================================

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def display_page(pathname, session_data):
    """Main routing callback with authentication"""

    # Get user information
    user_info = auth.get_user_info(session_data)
    access_tier = user_info.get('access_tier', 1) if user_info else 1

    # Create navbar with user context
    navbar = create_enhanced_navbar(user_info)

    # Route definitions with required access tiers
    routes = {
        '/': (create_authenticated_home_layout, 1),
        '/about-usc': (create_about_usc_page, 1),
        '/vision-mission': (create_vision_mission_page, 1),
        '/governance': (create_governance_page, 1),
        '/contact': (create_contact_page, 1),
        '/profile': (lambda: create_user_profile_page(user_info), 2),
        '/admin': (create_admin_dashboard, 4),
        '/factbook': (lambda: create_placeholder_page("Interactive Factbook", "Comprehensive institutional data dashboard", 2), 2),
        '/enrollment': (lambda: create_placeholder_page("Enrollment Analytics", "Student enrollment trends and analysis", 2), 2),
        '/graduation': (lambda: create_placeholder_page("Graduation Statistics", "Graduation rates and degree completion data", 2), 2),
        '/hr-data': (lambda: create_placeholder_page("HR Analytics", "Faculty and staff employment data", 2), 2),
        '/student-employment': (lambda: create_placeholder_page("Student Employment", "Student work and employment analytics", 2), 2),
        '/financial': (lambda: create_placeholder_page("Financial Dashboard", "Comprehensive financial data and reports", 3), 3),
        '/budget': (lambda: create_placeholder_page("Budget Analysis", "Detailed budget breakdowns and variance analysis", 3), 3),
        '/revenue': (lambda: create_placeholder_page("Revenue Reports", "Revenue tracking and analysis", 3), 3),
        '/endowments': (lambda: create_placeholder_page("Endowment Funds", "Endowment and funding analysis", 3), 3)
    }

    # Get route handler and required tier
    if pathname in routes:
        page_function, required_tier = routes[pathname]

        # Check access permissions
        if access_tier < required_tier:
            content = create_access_denied_page(required_tier)
        else:
            if pathname == '/':
                content = page_function(user_info)
            else:
                content = page_function()
    else:
        # 404 page
        content = create_placeholder_page(
            "Page Not Found",
            f"The page '{pathname}' does not exist.",
            1
        )

    return html.Div([navbar, content])

# ============================================================================
# SESSION VALIDATION CALLBACK
# ============================================================================

@callback(
    Output('user-session', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def validate_session(pathname, session_data):
    """Validate session on page changes"""
    if not session_data or 'session_token' not in session_data:
        return session_data

    # Check if session is still valid
    user_info = auth.get_user_info(session_data)
    if not user_info:
        # Session expired or invalid
        return {}

    return session_data

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    # Initialize database
    print("🔧 Initializing authentication database...")
    db.init_database()

    print("🚀 Starting USC Institutional Research Portal...")
    print("🌐 Visit: http://localhost:8050")
    print("👤 Default admin: admin@usc.edu.tt / admin123")
    print("📧 USC emails (@usc.edu.tt) auto-approved for Tier 2")

    app.run_server(debug=True, host='0.0.0.0', port=8050)