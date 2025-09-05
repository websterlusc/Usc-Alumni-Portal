"""
USC Institutional Research Portal - Access Control Pages
Login, access denied, and user profile pages
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from components.navbar import create_navbar, USC_COLORS

def create_login_page():
    """Create login page"""
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Header
                    html.Div([
                        html.I(className="fas fa-university", style={'fontSize': '4rem', 'color': 'white', 'marginBottom': '1rem'}),
                        html.H2("USC Institutional Research", className="text-white fw-bold mb-2"),
                        html.P("Secure Portal Access", className="text-white-50 mb-4")
                    ], className="text-center mb-4"),
                    
                    # Login card
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3("Sign In", className="text-center mb-2", style={'color': USC_COLORS['primary_green']}),
                            html.P("Enter your credentials", className="text-center text-muted mb-0")
                        ]),
                        dbc.CardBody([
                            html.Div(id="login-alerts", className="mb-3"),
                            dbc.Form([
                                dbc.Label("Username", className="fw-bold mb-2"),
                                dbc.InputGroup([
                                    dbc.InputGroupText(html.I(className="fas fa-user")),
                                    dbc.Input(type="text", id="username", placeholder="Enter username", style={'padding': '0.75rem'})
                                ], className="mb-3"),
                                
                                dbc.Label("Password", className="fw-bold mb-2"),
                                dbc.InputGroup([
                                    dbc.InputGroupText(html.I(className="fas fa-lock")),
                                    dbc.Input(type="password", id="password", placeholder="Enter password", style={'padding': '0.75rem'})
                                ], className="mb-4"),
                                
                                dbc.Button([
                                    html.I(className="fas fa-sign-in-alt me-2"),
                                    "Sign In"
                                ], id="login-btn", color="success", size="lg", className="w-100 fw-bold")
                            ])
                        ]),
                        dbc.CardFooter([
                            html.P([
                                "Need access? Contact ",
                                html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt", style={'color': USC_COLORS['secondary_green']})
                            ], className="text-center text-muted mb-0")
                        ])
                    ], style={
                        'width': '100%',
                        'maxWidth': '450px',
                        'boxShadow': '0 10px 25px rgba(0,0,0,0.2)',
                        'borderRadius': '10px'
                    })
                ], width=12, className="d-flex flex-column align-items-center")
            ], className="justify-content-center align-items-center", style={"minHeight": "100vh"})
        ], fluid=True)
    ], style={
        "background": f"linear-gradient(135deg, {USC_COLORS['primary_green']}, {USC_COLORS['secondary_green']})",
        "minHeight": "100vh"
    })

def create_access_denied_page(required_tier=2):
    """Create access denied page with request access option"""
    
    tier_names = {1: "Public", 2: "Factbook", 3: "Financial"}
    tier_descriptions = {
        2: "This content requires Factbook access (Tier 2). Please log in or request access upgrade.",
        3: "This content requires Financial access (Tier 3). Please contact the IR team for approval."
    }
    
    return html.Div([
        create_navbar(),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-lock fa-5x mb-4", style={'color': USC_COLORS['text_gray']}),
                                html.H1("Access Required", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                                html.H4(f"Tier {required_tier} ({tier_names.get(required_tier, 'Unknown')}) Access Needed", 
                                        className="mb-4", style={'color': USC_COLORS['secondary_green']}),
                                html.P(tier_descriptions.get(required_tier, "This content requires additional permissions."), 
                                      className="lead mb-4"),
                                
                                # Action buttons
                                html.Div([
                                    dbc.Button([
                                        html.I(className="fas fa-sign-in-alt me-2"),
                                        "Login"
                                    ], href="/login", color="success", size="lg", className="me-3"),
                                    
                                    dbc.Button([
                                        html.I(className="fas fa-key me-2"),
                                        "Request Access"
                                    ], href="/request-access", color="outline-success", size="lg", className="me-3"),
                                    
                                    dbc.Button([
                                        html.I(className="fas fa-envelope me-2"),
                                        "Contact IR Team"
                                    ], href="mailto:ir@usc.edu.tt", color="outline-secondary", size="lg")
                                ], className="mb-4"),
                                
                                # Access tier information
                                html.Hr(),
                                html.H5("Access Tiers", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                                dbc.Row([
                                    dbc.Col([
                                        html.Div([
                                            html.I(className="fas fa-globe fa-2x mb-2", style={'color': USC_COLORS['text_gray']}),
                                            html.H6("Tier 1 - Public", className="fw-bold"),
                                            html.Small("General USC information, available to everyone")
                                        ], className="text-center")
                                    ], width=4),
                                    dbc.Col([
                                        html.Div([
                                            html.I(className="fas fa-chart-bar fa-2x mb-2", 
                                                   style={'color': USC_COLORS['secondary_green'] if required_tier <= 2 else USC_COLORS['text_gray']}),
                                            html.H6("Tier 2 - Factbook", className="fw-bold"),
                                            html.Small("Student data, analytics, requires login")
                                        ], className="text-center")
                                    ], width=4),
                                    dbc.Col([
                                        html.Div([
                                            html.I(className="fas fa-dollar-sign fa-2x mb-2", 
                                                   style={'color': USC_COLORS['accent_yellow'] if required_tier <= 3 else USC_COLORS['text_gray']}),
                                            html.H6("Tier 3 - Financial", className="fw-bold"),
                                            html.Small("Financial reports, requires approval")
                                        ], className="text-center")
                                    ], width=4)
                                ])
                            ], className="text-center py-5")
                        ])
                    ])
                ], width=10, className="mx-auto")
            ], className="justify-content-center", style={"minHeight": "70vh"})
        ], className="d-flex align-items-center")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_profile_page(user):
    """User profile page"""
    tier_names = {1: "Public", 2: "Factbook", 3: "Financial"}
    tier_colors = {1: "secondary", 2: "info", 3: "warning"}
    
    return html.Div([
        create_navbar(user),
        dbc.Container([
            html.H1("User Profile", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Profile Information", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.P([html.Strong("Full Name: "), user['full_name']]),
                                    html.P([html.Strong("Email: "), user['email']]),
                                    html.P([html.Strong("Username: "), user['username']]),
                                ], width=6),
                                dbc.Col([
                                    html.P([html.Strong("Department: "), user.get('department', 'Not specified')]),
                                    html.P([html.Strong("Position: "), user.get('position', 'Not specified')]),
                                    html.P([html.Strong("Phone: "), user.get('phone', 'Not specified')]),
                                ], width=6)
                            ])
                        ])
                    ])
                ], width=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Access Level", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.Div([
                                dbc.Badge(f"Tier {user['access_tier']} - {tier_names.get(user['access_tier'], 'Unknown')}", 
                                         color=tier_colors.get(user['access_tier'], 'secondary'), 
                                         pill=True, className="fs-6 mb-3"),
                                html.P("Your current access level allows you to view:"),
                                html.Ul([
                                    html.Li("General USC information"),
                                    html.Li("Student data and analytics") if user['access_tier'] >= 2 else html.Li("Student data (requires upgrade)", className="text-muted"),
                                    html.Li("Financial reports and data") if user['access_tier'] >= 3 else html.Li("Financial reports (requires approval)", className="text-muted")
                                ]),
                                html.Hr(),
                                dbc.Button("Request Access Upgrade", href="/request-access", color="outline-success", size="sm", className="w-100") if user['access_tier'] < 3 else None
                            ], className="text-center")
                        ])
                    ])
                ], width=4)
            ], className="mb-5"),
            
            # Account activity
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Account Activity", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P([html.Strong("Account Created: "), user.get('created_at', 'N/A')]),
                            html.P([html.Strong("Last Login: "), user.get('last_login', 'N/A')]),
                        ], width=6),
                        dbc.Col([
                            html.P([html.Strong("Account Status: "), dbc.Badge("Active", color="success") if user.get('is_active', True) else dbc.Badge("Inactive", color="danger")]),
                            html.P([html.Strong("Admin User: "), dbc.Badge("Yes", color="warning") if user.get('is_admin', False) else dbc.Badge("No", color="secondary")]),
                        ], width=6)
                    ])
                ])
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_request_access_page(user=None):
    """Request access upgrade page"""
    return html.Div([
        create_navbar(user),
        dbc.Container([
            html.H1("Request Access Upgrade", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Access Upgrade Request", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.P(f"Current Access Level: Tier {user['access_tier'] if user else 1} ") if user else html.P("Please log in to request access."),
                            
                            # Access request form (if logged in)
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Requested Access Level", className="fw-bold"),
                                        dcc.Dropdown(
                                            id="requested-tier",
                                            options=[
                                                {'label': 'Tier 2 - Factbook Access', 'value': 2, 'disabled': user['access_tier'] >= 2 if user else False},
                                                {'label': 'Tier 3 - Financial Access', 'value': 3, 'disabled': user['access_tier'] >= 3 if user else False}
                                            ],
                                            placeholder="Select access level",
                                            className="mb-3"
                                        )
                                    ])
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Justification", className="fw-bold"),
                                        dbc.Textarea(
                                            id="justification",
                                            placeholder="Please explain why you need this access level and how it relates to your work/studies at USC...",
                                            rows=5,
                                            className="mb-3"
                                        )
                                    ])
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button([
                                            html.I(className="fas fa-paper-plane me-2"),
                                            "Submit Request"
                                        ], id="submit-request", color="success", size="lg", disabled=not user)
                                    ])
                                ])
                            ]) if user else dbc.Alert([
                                html.H5("Login Required", className="alert-heading"),
                                "You must be logged in to request access upgrades. ",
                                html.A("Click here to login", href="/login", className="alert-link")
                            ], color="warning")
                        ])
                    ])
                ], width=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Access Levels", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.Div([
                                html.H6("Tier 1 - Public Access", className="fw-bold", style={'color': USC_COLORS['text_gray']}),
                                html.Small("• General USC information", className="d-block mb-2"),
                                html.Small("• Campus and contact details", className="d-block mb-3"),
                                
                                html.H6("Tier 2 - Factbook Access", className="fw-bold", style={'color': USC_COLORS['secondary_green']}),
                                html.Small("• Student enrollment data", className="d-block mb-1"),
                                html.Small("• Graduation statistics", className="d-block mb-1"),
                                html.Small("• HR and academic analytics", className="d-block mb-3"),
                                
                                html.H6("Tier 3 - Financial Access", className="fw-bold", style={'color': USC_COLORS['accent_yellow']}),
                                html.Small("• Budget and financial reports", className="d-block mb-1"),
                                html.Small("• Revenue and expense data", className="d-block mb-1"),
                                html.Small("• Sensitive financial information", className="d-block mb-3"),
                            ])
                        ])
                    ]),
                    
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Need Help?", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.P("Contact the Institutional Research team for assistance with access requests:"),
                            html.P([
                                html.Strong("Email: "), html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt"), html.Br(),
                                html.Strong("Phone: "), "868-645-3265 ext. 2150"
                            ])
                        ])
                    ], className="mt-3")
                ], width=4)
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_login_history_page(user):
    """Login history page"""
    return html.Div([
        create_navbar(user),
        dbc.Container([
            html.H1("Login History", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Recent Login Activity", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                ]),
                dbc.CardBody([
                    dbc.Alert([
                        html.I(className="fas fa-info-circle me-2"),
                        "Login history tracking will be implemented in a future update. This feature will show your recent login attempts, session details, and security information."
                    ], color="info"),
                    
                    # Placeholder for login history table
                    html.Div([
                        html.H5("Current Session Information", className="fw-bold mb-3"),
                        html.P([html.Strong("Current Login: "), datetime.now().strftime("%Y-%m-%d %H:%M:%S")]),
                        html.P([html.Strong("Session Status: "), dbc.Badge("Active", color="success")]),
                        html.P([html.Strong("Access Level: "), f"Tier {user['access_tier']}"])
                    ])
                ])
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafaba', 'minHeight': '100vh'})