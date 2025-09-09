"""
Simple Authentication Components for USC IR Portal
Clean components without circular dependencies
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

# USC Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA'
}

def create_login_modal():
    """Simple login modal"""
    return dbc.Modal([
        dbc.ModalHeader("Login to USC IR Portal"),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Label("Email", className="fw-bold"),
                    dbc.Input(id="login-email", type="email", placeholder="your.email@usc.edu.tt", className="mb-3")
                ]),
                dbc.Row([
                    dbc.Label("Password", className="fw-bold"),
                    dbc.Input(id="login-password", type="password", placeholder="Enter password", className="mb-3")
                ]),
                html.Div(id="login-alerts", className="mb-3"),
                dbc.Button("Login", id="login-submit-btn", color="success", className="w-100 mb-2"),
                html.Hr(),
                dbc.Button("Register New Account", id="show-register-btn", color="outline-primary", className="w-100")
            ])
        ])
    ], id="login-modal", is_open=False, size="md")

def create_register_modal():
    """Simple registration modal"""
    return dbc.Modal([
        dbc.ModalHeader("Register for USC IR Portal"),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Label("Full Name *", className="fw-bold"),
                    dbc.Input(id="register-fullname", type="text", placeholder="Your full name", className="mb-3")
                ]),
                dbc.Row([
                    dbc.Label("Email *", className="fw-bold"),
                    dbc.Input(id="register-email", type="email", placeholder="your.email@usc.edu.tt", className="mb-3"),
                    dbc.FormText("USC employees (@usc.edu.tt) get automatic factbook access")
                ]),
                dbc.Row([
                    dbc.Label("Department", className="fw-bold"),
                    dbc.Input(id="register-department", type="text", placeholder="Your department", className="mb-3")
                ]),
                dbc.Row([
                    dbc.Label("Password *", className="fw-bold"),
                    dbc.Input(id="register-password", type="password", placeholder="Create password", className="mb-3")
                ]),
                html.Div(id="register-alerts", className="mb-3"),
                dbc.Button("Create Account", id="register-submit-btn", color="success", className="w-100 mb-2"),
                html.Hr(),
                dbc.Button("Back to Login", id="show-login-btn", color="outline-secondary", className="w-100")
            ])
        ])
    ], id="register-modal", is_open=False, size="md")

def create_access_request_modal():
    """Access request modal"""
    return dbc.Modal([
        dbc.ModalHeader("Request Higher Access"),
        dbc.ModalBody([
            dbc.Alert([
                html.H5("Access Tiers", className="alert-heading"),
                html.P([
                    html.Strong("Tier 2: "), "Factbook data, enrollment, HR analytics", html.Br(),
                    html.Strong("Tier 3: "), "Financial data, budget reports", html.Br(),
                    html.Strong("Tier 4: "), "Admin access, user management"
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
                        placeholder="Explain why you need this access level...",
                        rows=4,
                        className="mb-3"
                    )
                ]),
                html.Div(id="request-alerts", className="mb-3"),
                dbc.Button("Submit Request", id="request-submit-btn", color="primary", className="w-100")
            ])
        ])
    ], id="access-request-modal", is_open=False, size="lg")

def create_admin_modal():
    """Simple admin dashboard modal"""
    return dbc.Modal([
        dbc.ModalHeader("Admin Dashboard"),
        dbc.ModalBody([
            dbc.Tabs([
                dbc.Tab(label="Pending Requests", tab_id="requests"),
                dbc.Tab(label="User Management", tab_id="users")
            ], id="admin-tabs", active_tab="requests"),
            html.Div(id="admin-content", className="mt-3")
        ])
    ], id="admin-modal", is_open=False, size="xl")

def create_navbar_with_auth(user_info=None):
    """Create navbar with authentication buttons"""
    # Build nav items based on access tier
    access_tier = user_info.get('access_tier', 1) if user_info else 1
    
    nav_items = [
        dbc.NavItem(dbc.NavLink("Home", href="/", style={'color': USC_COLORS['accent_yellow']})),
        dbc.NavItem(dbc.NavLink("About USC", href="/about-usc", style={'color': USC_COLORS['accent_yellow']})),
        dbc.NavItem(dbc.NavLink("Vision & Mission", href="/vision-mission", style={'color': USC_COLORS['accent_yellow']})),
        dbc.NavItem(dbc.NavLink("Governance", href="/governance", style={'color': USC_COLORS['accent_yellow']}))
    ]
    
    # Factbook access (Tier 2+)
    if access_tier >= 2:
        factbook_dropdown = dbc.DropdownMenu([
            dbc.DropdownMenuItem("Factbook Home", href="/factbook"),
            dbc.DropdownMenuItem("Enrollment Data", href="/enrollment"),
            dbc.DropdownMenuItem("Student Employment", href="/student-employment")
        ], label="Factbook", nav=True, style={'color': USC_COLORS['accent_yellow']})
        nav_items.append(factbook_dropdown)
    
    # Financial access (Tier 3+)
    if access_tier >= 3:
        financial_dropdown = dbc.DropdownMenu([
            dbc.DropdownMenuItem("Financial Dashboard", href="/financial"),
            dbc.DropdownMenuItem("Budget Analysis", href="/budget")
        ], label="Financial", nav=True, style={'color': USC_COLORS['accent_yellow']})
        nav_items.append(financial_dropdown)
    
    # Admin access (Tier 4+)
    if access_tier >= 4:
        nav_items.append(dbc.NavItem(dbc.NavLink("Admin", id="admin-btn", href="#", style={'color': USC_COLORS['accent_yellow']})))
    
    # User menu or login button
    if user_info:
        user_dropdown = dbc.DropdownMenu([
            dbc.DropdownMenuItem([html.I(className="fas fa-user me-2"), "Profile"], href="#"),
            dbc.DropdownMenuItem([html.I(className="fas fa-key me-2"), "Request Access"], id="request-access-btn"),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([html.I(className="fas fa-sign-out-alt me-2"), "Logout"], id="logout-btn")
        ], label=[
            html.I(className="fas fa-user-circle me-2"),
            user_info['full_name'],
            f" (Tier {access_tier})"
        ], nav=True, style={'color': USC_COLORS['accent_yellow']})
        nav_items.append(user_dropdown)
    else:
        nav_items.append(dbc.NavItem(dbc.Button("Login", id="login-btn", color="outline-light", size="sm")))
    
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

def create_access_denied_alert(required_tier):
    """Create access denied alert"""
    return dbc.Container([
        dbc.Alert([
            html.H4("Access Denied", className="alert-heading"),
            html.P(f"You need Tier {required_tier} access to view this page."),
            html.Hr(),
            html.P("Please contact your administrator or request higher access.")
        ], color="danger", className="text-center"),
        dbc.Row([
            dbc.Col([
                dbc.Button("Return Home", href="/", color="primary"),
                dbc.Button("Request Access", id="request-access-from-denied", color="success", className="ms-2")
            ], className="text-center")
        ])
    ], className="mt-5")

def create_pending_requests_table(requests):
    """Create table for pending access requests"""
    if not requests:
        return dbc.Alert("No pending requests", color="info")
    
    rows = []
    for req in requests:
        row = html.Tr([
            html.Td(req['full_name']),
            html.Td(req['email']),
            html.Td(f"Tier {req['current_tier']} → {req['requested_tier']}"),
            html.Td(req['justification'][:50] + "..." if len(req['justification']) > 50 else req['justification']),
            html.Td([
                dbc.ButtonGroup([
                    dbc.Button("Approve", size="sm", color="success", id=f"approve-{req['id']}"),
                    dbc.Button("Deny", size="sm", color="danger", id=f"deny-{req['id']}")
                ])
            ])
        ])
        rows.append(row)
    
    return dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Name"),
                html.Th("Email"),
                html.Th("Access Change"),
                html.Th("Justification"),
                html.Th("Actions")
            ])
        ]),
        html.Tbody(rows)
    ], striped=True, bordered=True, hover=True, responsive=True)
