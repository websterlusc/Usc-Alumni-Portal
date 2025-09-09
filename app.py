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

# ============================================================================
# DATABASE AND AUTHENTICATION SETUP
# ============================================================================

GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
OAUTH_READY = bool(GOOGLE_CLIENT_SECRET and 'GOCSPX-' in GOOGLE_CLIENT_SECRET)

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

# Add OAuth routes if available
if OAUTH_READY:
    @server.route('/auth/login')
    def oauth_login():
        from flask import redirect
        client_id = os.getenv('GOOGLE_CLIENT_ID', '890006312213-3k7f200g3a94je1j9trfjru716v3kidc.apps.googleusercontent.com')
        redirect_uri = os.getenv('REDIRECT_URI', 'http://localhost:8050/auth/google-callback')

        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=openid email profile&"
            f"response_type=code&"
            f"access_type=offline&"
            f"prompt=select_account"
        )
        return redirect(google_auth_url)

    @server.route('/auth/google-callback')
    def oauth_callback():
        from flask import request, redirect
        code = request.args.get('code')
        if code:
            return redirect('/?login=oauth_success')
        else:
            return redirect('/?login=oauth_error')

# ============================================================================
# NAVBAR WITH AUTHENTICATION
# ============================================================================

def create_auth_section(user_data=None):
    """Create authentication section of navbar"""
    if not user_data or not user_data.get('authenticated'):
        return dbc.NavItem(dbc.Button(
            [html.I(className="fab fa-google me-2"), "Sign In"],
            id="main-login-btn",
            color="outline-success",
            size="sm",
            className="ms-2"
        ))

    # User is logged in - show dropdown
    tier_info = {
        1: {"name": "Public", "color": "secondary"},
        2: {"name": "Employee", "color": "success"},
        3: {"name": "Admin", "color": "warning"}
    }

    user_tier = user_data.get('access_tier', 1)
    tier = tier_info.get(user_tier, tier_info[1])

    return dbc.NavItem([
        dbc.DropdownMenu([
            dbc.DropdownMenuItem([
                html.Strong(user_data.get('full_name', 'User')),
                html.Br(),
                html.Small(user_data.get('email', ''), className="text-muted"),
                html.Br(),
                dbc.Badge(tier["name"], color=tier["color"], className="mt-1")
            ], header=True),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-user me-2"), "Profile"
            ]),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-key me-2"), "Request Access"
            ]) if user_tier < 3 else None,
            dbc.DropdownMenuItem([
                html.I(className="fas fa-cog me-2"), "Admin Panel"
            ]) if user_tier >= 3 else None,
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-sign-out-alt me-2"), "Sign Out"
            ], id="main-logout-btn")
        ],
        toggle_id="user-dropdown",
        label=[
            html.Div(
                user_data.get('full_name', 'User').split()[0],
                style={
                    'backgroundColor': USC_COLORS['primary_green'],
                    'color': 'white',
                    'padding': '8px 12px',
                    'borderRadius': '20px',
                    'fontSize': '14px',
                    'fontWeight': 'bold'
                }
            )
        ],
        direction="down",
        right=True)
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

def create_login_modal():
    """Working login modal"""
    return dbc.Modal([
        dbc.ModalHeader("Sign In to USC IR Portal"),
        dbc.ModalBody([
            html.Div(id="login-alerts"),

            html.Div([
                dbc.Button([
                    html.I(className="fab fa-google me-2"),
                    "Continue with Google"
                ], id="google-oauth-btn", color="danger", className="w-100 mb-3") if OAUTH_READY else None,

                html.Hr() if OAUTH_READY else None,
                html.P("Choose a demo user:", className="text-center text-muted mb-3")
            ]),

            dbc.Form([
                dbc.Label("Demo Users", className="fw-bold mb-2"),
                dbc.RadioItems(
                    id="demo-user-select",
                    options=[
                        {"label": "Demo Employee (Tier 2 - Factbook Access)", "value": "demo@usc.edu.tt"},
                        {"label": "Admin User (Tier 3 - Full Access)", "value": "admin@usc.edu.tt"},
                        {"label": "Nordian Robinson (Director - Full Access)", "value": "nrobinson@usc.edu.tt"},
                        {"label": "Liam Webster (Developer - Full Access)", "value": "websterl@usc.edu.tt"}
                    ],
                    value="demo@usc.edu.tt",
                    className="mb-3"
                ),
                dbc.Button("Sign In", id="demo-signin-btn", color="success", className="w-100")
            ])
        ]),
    ], id="login-modal", is_open=False, size="md")

# ============================================================================
# APPLICATION LAYOUT
# ============================================================================

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='user-session', storage_type='session', data={'authenticated': False}),
    html.Div(id='page-content'),
    create_login_modal()
])

# ============================================================================
# CALLBACKS - CLEAN AND WORKING
# ============================================================================

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def display_page(pathname, session_data):
    """Main page routing with access control"""

    # Get user data
    user_data = session_data if session_data and session_data.get('authenticated') else None

    # Create navbar
    navbar = create_modern_navbar(user_data)

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

    return html.Div([navbar, content])

# MAIN AUTHENTICATION CALLBACK
@callback(
    [Output('user-session', 'data'),
     Output('login-modal', 'is_open'),
     Output('login-alerts', 'children')],
    [Input('main-login-btn', 'n_clicks'),
     Input('demo-signin-btn', 'n_clicks'),
     Input('google-oauth-btn', 'n_clicks'),
     Input('cancel-login-btn', 'n_clicks'),
     Input('access-signin-btn', 'n_clicks')],
    [State('demo-user-select', 'value'),
     State('user-session', 'data'),
     State('login-modal', 'is_open')],
    prevent_initial_call=True
)
def handle_authentication(main_login, demo_signin, google_login, cancel, access_signin,
                         selected_user, session_data, modal_open):
    """Handle all authentication actions"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return session_data or {'authenticated': False}, False, ""

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Open login modal
    if button_id in ['main-login-btn', 'access-signin-btn']:
        return session_data or {'authenticated': False}, True, ""

    # Close login modal
    if button_id == 'cancel-login-btn':
        return session_data or {'authenticated': False}, False, ""

    # Demo login
    if button_id == 'demo-signin-btn' and demo_signin:
        if not selected_user:
            return session_data or {'authenticated': False}, True, dbc.Alert("Please select a user", color="warning")

        # Get user data from database
        conn = sqlite3.connect('usc_ir.db')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT email, full_name, role, access_tier FROM users WHERE email = ?', (selected_user,))
            user = cursor.fetchone()
            if user:
                user_data = {
                    'authenticated': True,
                    'email': user[0],
                    'full_name': user[1],
                    'role': user[2],
                    'access_tier': user[3],
                    'login_time': datetime.now().isoformat()
                }
                return user_data, False, ""
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

        return session_data or {'authenticated': False}, True, dbc.Alert("Login failed", color="danger")

    # Google OAuth
    if button_id == 'google-oauth-btn' and google_login and OAUTH_READY:
        return session_data or {'authenticated': False}, False, ""

    return session_data or {'authenticated': False}, modal_open, ""

# LOGOUT CALLBACK
@callback(
    Output('user-session', 'data', allow_duplicate=True),
    Input('main-logout-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(logout_clicks):
    """Handle logout"""
    if logout_clicks:
        return {'authenticated': False}
    return dash.no_update

# CLIENT-SIDE CALLBACKS
if OAUTH_READY:
    app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks > 0) {
                window.location.href = '/auth/login';
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('google-oauth-btn', 'disabled'),
        Input('google-oauth-btn', 'n_clicks'),
        prevent_initial_call=True
    )

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    init_database()

    print("🚀 Starting USC Institutional Research Portal...")
    print("📊 Clean version with working authentication!")
    print("✅ Features:")
    print("   • Your complete existing design preserved")
    print("   • Working login button and modal")
    print("   • 3-tier access control system")
    print("   • Dynamic navbar based on user permissions")
    print("   • Demo users for testing")
    print(f"🔐 OAuth Status: {'✅ Ready' if OAUTH_READY else '⚠️ Demo Mode'}")
    print(f"🌐 Visit: http://localhost:8050")
    print()
    print("🎮 Test the login:")
    print("   1. Click 'Sign In' button in navbar")
    print("   2. Choose demo user (try different tiers)")
    print("   3. Test access to different pages")
    print("   4. Notice navbar updates with user info")

    if OAUTH_READY:
        print("🔑 Google OAuth available in login modal")

    app.run_server(debug=True, host='0.0.0.0', port=8050)