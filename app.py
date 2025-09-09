# app.py - USC Institutional Research Portal with Authentication
"""
USC Institutional Research Portal - Complete Application
Integrated Google OAuth authentication with tier-based access control
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
from datetime import datetime
import requests

# Import authentication components
from auth.auth_routes import register_auth_routes
from auth.google_auth import init_database
from components.auth_components import (
    create_auth_status_store, create_auth_interval, create_access_request_modal,
    create_logout_confirmation_modal, get_user_navbar_content,
    require_auth_wrapper, register_auth_callbacks, create_session_timeout_warning
)

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
    ],
    suppress_callback_exceptions=True
)

app.title = "USC Institutional Research Portal"
server = app.server

# Register authentication routes
register_auth_routes(server)

def create_navbar(auth_status=None):
    """Create responsive navigation bar with authentication"""

    # Get navigation items based on access tier
    nav_items = get_navigation_items(auth_status.get('access_tier', 1) if auth_status else 1)

    return dbc.Navbar(
        dbc.Container([
            # Brand
            dbc.NavbarBrand([
                html.Img(
                    src="/assets/usc-logo.png",
                    height="40px",
                    className="me-2"
                ),
                html.Span("Institutional Research", className="fw-bold")
            ], href="/", className="text-white"),

            # Toggle button for mobile
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),

            # Collapsible content
            dbc.Collapse([
                dbc.Nav([
                    # Navigation items
                    *[dbc.NavItem(
                        dbc.NavLink(
                            item["name"],
                            href=item["url"],
                            className="text-white-50"
                        )
                    ) for item in nav_items],

                    # User authentication section
                    dbc.NavItem([
                        html.Div(
                            id="navbar-auth-content",
                            children=get_user_navbar_content(auth_status)
                        )
                    ], className="ms-auto")
                ], className="w-100 justify-content-between")
            ], id="navbar-collapse", is_open=False, navbar=True)
        ], fluid=True),
        color=USC_COLORS['primary_green'],
        dark=True,
        className="mb-0",
        style={'minHeight': '60px'}
    )

def get_navigation_items(access_tier):
    """Get navigation items based on user access tier"""
    base_items = [
        {"name": "Home", "url": "/", "tier": 1},
        {"name": "About USC", "url": "/about", "tier": 1},
        {"name": "Vision & Mission", "url": "/vision-mission", "tier": 1},
        {"name": "Governance", "url": "/governance", "tier": 1}
    ]

    factbook_items = [
        {"name": "Factbook", "url": "/factbook", "tier": 2},
        {"name": "Enrollment", "url": "/enrollment", "tier": 2},
        {"name": "Graduation", "url": "/graduation", "tier": 2},
        {"name": "HR Data", "url": "/hr-data", "tier": 2},
        {"name": "Student Employment", "url": "/student-employment", "tier": 2}
    ]

    financial_items = [
        {"name": "Financial Reports", "url": "/financial", "tier": 3},
        {"name": "Budget Analysis", "url": "/budget", "tier": 3},
        {"name": "Endowments", "url": "/endowments", "tier": 3}
    ]

    all_items = base_items + factbook_items + financial_items
    return [item for item in all_items if item["tier"] <= access_tier]

def create_home_page(auth_status=None):
    """Create enhanced home page with authentication-aware content"""
    is_authenticated = auth_status and auth_status.get('authenticated', False)
    user = auth_status.get('user') if is_authenticated else None
    access_tier = auth_status.get('access_tier', 1) if auth_status else 1

    # Welcome message based on authentication status
    if is_authenticated and user:
        welcome_msg = f"Welcome back, {user.get('full_name', 'User').split()[0]}!"
        subtitle = "Access your institutional research dashboard below."
    else:
        welcome_msg = "Welcome to USC Institutional Research"
        subtitle = "Data-driven insights for informed decision making. Sign in to access detailed analytics."

    # Feature cards based on access tier
    feature_cards = []

    # Public features
    public_features = [
        {
            "title": "About USC",
            "description": "Learn about our history, mission, and organizational structure.",
            "icon": "fas fa-university",
            "link": "/about",
            "color": "primary"
        },
        {
            "title": "Vision & Mission",
            "description": "Discover our institutional vision, mission, and core values.",
            "icon": "fas fa-eye",
            "link": "/vision-mission",
            "color": "success"
        },
        {
            "title": "Governance",
            "description": "Explore our governance structure and organizational chart.",
            "icon": "fas fa-sitemap",
            "link": "/governance",
            "color": "info"
        }
    ]

    # Employee features (Tier 2+)
    employee_features = [
        {
            "title": "Interactive Factbook",
            "description": "Comprehensive institutional data with interactive visualizations.",
            "icon": "fas fa-chart-bar",
            "link": "/factbook",
            "color": "primary"
        },
        {
            "title": "Enrollment Analytics",
            "description": "Student enrollment trends and demographic analysis.",
            "icon": "fas fa-users",
            "link": "/enrollment",
            "color": "success"
        },
        {
            "title": "Graduation Data",
            "description": "Graduation rates and outcomes tracking.",
            "icon": "fas fa-graduation-cap",
            "link": "/graduation",
            "color": "warning"
        },
        {
            "title": "HR Analytics",
            "description": "Human resources data and faculty information.",
            "icon": "fas fa-user-tie",
            "link": "/hr-data",
            "color": "info"
        }
    ]

    # Financial features (Tier 3)
    financial_features = [
        {
            "title": "Financial Reports",
            "description": "Comprehensive financial analysis and reporting.",
            "icon": "fas fa-dollar-sign",
            "link": "/financial",
            "color": "warning"
        },
        {
            "title": "Budget Analysis",
            "description": "Budget tracking and variance analysis.",
            "icon": "fas fa-calculator",
            "link": "/budget",
            "color": "danger"
        },
        {
            "title": "Endowment Funds",
            "description": "Endowment fund performance and allocation.",
            "icon": "fas fa-piggy-bank",
            "link": "/endowments",
            "color": "success"
        }
    ]

    # Add features based on access tier
    feature_cards.extend(public_features)
    if access_tier >= 2:
        feature_cards.extend(employee_features)
    if access_tier >= 3:
        feature_cards.extend(financial_features)

    # Quick stats (dummy data for demo)
    stats_cards = [
        {"title": "Total Students", "value": "3,110", "icon": "fas fa-users", "color": "primary"},
        {"title": "Graduates (2025)", "value": "612", "icon": "fas fa-graduation-cap", "color": "success"},
        {"title": "Faculty Members", "value": "156", "icon": "fas fa-chalkboard-teacher", "color": "info"},
        {"title": "Programs Offered", "value": "45", "icon": "fas fa-book-open", "color": "warning"}
    ]

    return html.Div([
        # Hero section
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1(welcome_msg, className="display-4 fw-bold mb-3",
                           style={'color': USC_COLORS['primary_green']}),
                    html.P(subtitle, className="lead mb-4",
                           style={'color': USC_COLORS['dark_gray']}),

                    # Call-to-action based on auth status
                    html.Div([
                        dbc.Button(
                            [html.I(className="fab fa-google me-2"), "Sign in with Google"],
                            id="home-login-btn",
                            color="success",
                            size="lg",
                            className="me-3"
                        ) if not is_authenticated else html.Div(),

                        dbc.Button(
                            [html.I(className="fas fa-chart-line me-2"), "View Factbook"],
                            href="/factbook",
                            color="outline-primary",
                            size="lg"
                        ) if access_tier >= 2 else dbc.Button(
                            [html.I(className="fas fa-info-circle me-2"), "Learn More"],
                            href="/about",
                            color="outline-primary",
                            size="lg"
                        )
                    ])
                ], width=12, lg=8)
            ], justify="center", className="text-center py-5")
        ], fluid=True, className="bg-light"),

        # Quick stats section
        dbc.Container([
            html.H2("Quick Stats", className="text-center mb-4",
                   style={'color': USC_COLORS['primary_green']}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className=f"{stat['icon']} fa-2x mb-3",
                                      style={'color': f"var(--bs-{stat['color']})"})
                            ], className="text-center"),
                            html.H3(stat["value"], className="text-center fw-bold"),
                            html.P(stat["title"], className="text-center text-muted mb-0")
                        ])
                    ], className="h-100 shadow-sm border-0")
                ], width=6, lg=3) for stat in stats_cards
            ], className="g-4")
        ], className="py-5"),

        # Features section
        dbc.Container([
            html.H2("Available Features", className="text-center mb-4",
                   style={'color': USC_COLORS['primary_green']}),
            html.P("Explore the tools and resources available based on your access level.",
                   className="text-center text-muted mb-5"),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className=f"{card['icon']} fa-2x mb-3",
                                      style={'color': f"var(--bs-{card['color']})"})
                            ], className="text-center"),
                            html.H5(card["title"], className="card-title text-center"),
                            html.P(card["description"], className="card-text text-center text-muted"),
                            html.Div([
                                dbc.Button(
                                    "Access",
                                    href=card["link"],
                                    color=card["color"],
                                    size="sm",
                                    className="w-100"
                                )
                            ], className="text-center")
                        ])
                    ], className="h-100 shadow-sm border-0 hover-card")
                ], width=12, md=6, lg=4, className="mb-4") for card in feature_cards
            ])
        ], className="py-5"),

        # Access tier information (if authenticated)
        html.Div([
            dbc.Container([
                dbc.Alert([
                    html.H5([
                        html.I(className="fas fa-info-circle me-2"),
                        "Your Access Level"
                    ]),
                    html.P([
                        f"You currently have ",
                        html.Strong(f"Tier {access_tier}"),
                        " access. ",
                        "Contact the Institutional Research office to request higher access levels." if access_tier < 3 else "You have full access to all features."
                    ], className="mb-0")
                ], color="info", className="border-0")
            ])
        ], className="py-3") if is_authenticated else html.Div()
    ])

def create_page_layout(content, auth_status=None, required_tier=1):
    """Create page layout with authentication wrapper"""
    navbar = create_navbar(auth_status)

    # Check access requirements
    if required_tier > 1:
        content = require_auth_wrapper(content, required_tier, auth_status)

    return html.Div([
        navbar,
        content,

        # Authentication modals and components
        create_access_request_modal(),
        create_logout_confirmation_modal(),
        create_session_timeout_warning(),
        html.Div(id="access-request-feedback"),

        # Hidden components for callbacks
        create_auth_status_store(),
        create_auth_interval()
    ])

# Application layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Main page routing callback
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('auth-status-store', 'data')
)
def display_page(pathname, auth_status):
    """Route pages based on URL and authentication status"""

    # Handle query parameters for login/logout feedback
    if pathname == '/' and hasattr(display_page, 'search'):
        # This would handle ?login=success or ?error=... parameters
        pass

    # Route to appropriate page
    if pathname == '/':
        content = create_home_page(auth_status)
        return create_page_layout(content, auth_status)

    elif pathname == '/about':
        content = create_placeholder_page("About USC", "Learn about our rich history and academic excellence.", 1)
        return create_page_layout(content, auth_status)

    elif pathname == '/vision-mission':
        content = create_placeholder_page("Vision & Mission", "Our institutional vision, mission, and core values.", 1)
        return create_page_layout(content, auth_status)

    elif pathname == '/governance':
        content = create_placeholder_page("Governance", "Organizational structure and leadership.", 1)
        return create_page_layout(content, auth_status)

    # Factbook pages (Tier 2)
    elif pathname == '/factbook':
        content = create_placeholder_page("Interactive Factbook", "Comprehensive institutional data and analytics.", 2)
        return create_page_layout(content, auth_status, required_tier=2)

    elif pathname == '/enrollment':
        content = create_placeholder_page("Enrollment Data", "Student enrollment trends and analysis.", 2)
        return create_page_layout(content, auth_status, required_tier=2)

    elif pathname == '/graduation':
        content = create_placeholder_page("Graduation Data", "Graduation rates and outcomes.", 2)
        return create_page_layout(content, auth_status, required_tier=2)

    elif pathname == '/hr-data':
        content = create_placeholder_page("HR Analytics", "Human resources and faculty data.", 2)
        return create_page_layout(content, auth_status, required_tier=2)

    elif pathname == '/student-employment':
        content = create_placeholder_page("Student Employment", "Student employment analytics and trends.", 2)
        return create_page_layout(content, auth_status, required_tier=2)

    # Financial pages (Tier 3)
    elif pathname == '/financial':
        content = create_placeholder_page("Financial Reports", "Comprehensive financial analysis.", 3)
        return create_page_layout(content, auth_status, required_tier=3)

    elif pathname == '/budget':
        content = create_placeholder_page("Budget Analysis", "Budget tracking and variance analysis.", 3)
        return create_page_layout(content, auth_status, required_tier=3)

    elif pathname == '/endowments':
        content = create_placeholder_page("Endowment Funds", "Endowment performance and allocation.", 3)
        return create_page_layout(content, auth_status, required_tier=3)

    # User pages
    elif pathname == '/profile':
        content = create_placeholder_page("User Profile", "Manage your account and access requests.", 2)
        return create_page_layout(content, auth_status, required_tier=1)

    elif pathname == '/request-access':
        content = create_placeholder_page("Request Access", "Submit access level upgrade requests.", 2)
        return create_page_layout(content, auth_status, required_tier=1)

    elif pathname == '/admin':
        content = create_placeholder_page("Admin Dashboard", "Manage users and access requests.", 3)
        return create_page_layout(content, auth_status, required_tier=3)

    else:
        content = create_placeholder_page("Page Not Found", "The requested page could not be found.", 1)
        return create_page_layout(content, auth_status)

def create_placeholder_page(title, description, tier):
    """Create placeholder page content"""
    tier_badges = {
        1: {"text": "Public", "color": "secondary"},
        2: {"text": "Employee Access", "color": "success"},
        3: {"text": "Financial Access", "color": "warning"}
    }

    badge_info = tier_badges.get(tier, tier_badges[1])

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Badge(badge_info["text"], color=badge_info["color"], className="mb-3"),
                    html.H1(title, className="mb-3", style={'color': USC_COLORS['primary_green']}),
                    html.P(description, className="lead mb-4"),
                    html.Hr(),
                    html.P("This page is currently under development and will be available soon.",
                           className="text-muted")
                ])
            ], width=12, lg=8)
        ], justify="center")
    ], className="py-5")

# Register authentication callbacks
register_auth_callbacks(app)

# Additional callbacks for mobile navigation
@callback(
    Output('navbar-collapse', 'is_open'),
    Input('navbar-toggler', 'n_clicks'),
    State('navbar-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_navbar_collapse(n_clicks, is_open):
    """Toggle mobile navigation menu"""
    if n_clicks:
        return not is_open
    return is_open

# Callback to update navbar auth content based on auth status
@callback(
    Output('navbar-auth-content', 'children'),
    Input('auth-status-store', 'data'),
    prevent_initial_call=False
)
def update_navbar_auth_content(auth_status):
    """Update navbar authentication content"""
    return get_user_navbar_content(auth_status)

# Client-side callback for home page login button
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            window.location.href = '/auth/login';
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('home-login-btn', 'id'),
    Input('home-login-btn', 'n_clicks'),
    prevent_initial_call=True
)

if __name__ == '__main__':
    # Initialize database
    init_database()

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    print("🚀 Starting USC Institutional Research Portal...")
    print("📊 Features enabled:")
    print("   ✅ Google OAuth Authentication")
    print("   ✅ 3-Tier Access Control")
    print("   ✅ Modern responsive design")
    print("   ✅ USC brand compliance")
    print("   ✅ Session management")
    print("   ✅ Interactive dashboard")
    print(f"🌐 Visit: http://localhost:8050")
    print("🔐 Authentication endpoints:")
    print("   • /auth/login - Google OAuth login")
    print("   • /auth/status - Check auth status")
    print("   • /auth/logout - Logout")
    print("   • /auth/request-access - Request higher access")

    # Run the application
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050,
        dev_tools_ui=True,
        dev_tools_props_check=True
    )