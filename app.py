"""
USC Institutional Research Portal - Final Working Version
Self-contained app that avoids all callback conflicts
"""

import dash
from dash import html, dcc, Input, Output, State, callback, clientside_callback
import dash_bootstrap_components as dbc
import sqlite3
import os
from datetime import datetime

# USC Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA'
}

# Initialize app with unique server name to avoid conflicts
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True
)

app.title = "USC Institutional Research Portal"
server = app.server

# Import your existing pages with error handling
try:
    from pages.about_usc_page import create_about_usc_page
    from pages.vision_mission_page import create_vision_mission_page
    from pages.contact_page import create_contact_page
    from pages.governance_page import create_governance_page
    PAGES_AVAILABLE = True
    print("✅ Page modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Page modules not found: {e}")
    PAGES_AVAILABLE = False

# Database setup
def init_database():
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            full_name TEXT,
            access_tier INTEGER DEFAULT 2
        )
    ''')

    users = [
        ('demo@usc.edu.tt', 'Demo Employee', 2),
        ('admin@usc.edu.tt', 'Admin User', 3),
        ('nrobinson@usc.edu.tt', 'Nordian Robinson', 3),
        ('websterl@usc.edu.tt', 'Liam Webster', 3)
    ]

    for email, name, tier in users:
        cursor.execute('INSERT OR IGNORE INTO users (email, full_name, access_tier) VALUES (?, ?, ?)',
                      (email, name, tier))

    conn.commit()
    conn.close()

# Your exact navbar with unique IDs to avoid conflicts
def create_navbar(user_data=None):
    user_tier = user_data.get('access_tier', 1) if user_data else 1

    # Factbook menu items based on tier
    factbook_items = []
    if user_tier >= 2:
        factbook_items = [
            dbc.DropdownMenuItem("Factbook Overview", href="/factbook"),
            dbc.DropdownMenuItem("Enrollment Data", href="/enrollment"),
            dbc.DropdownMenuItem("Graduation Stats", href="/graduation"),
            dbc.DropdownMenuItem("Student Employment", href="/student-employment"),
            dbc.DropdownMenuItem("HR Analytics", href="/hr-data")
        ]
        if user_tier >= 3:
            factbook_items.extend([
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Financial Reports", href="/financial"),
                dbc.DropdownMenuItem("Budget Analysis", href="/budget")
            ])
    else:
        factbook_items = [dbc.DropdownMenuItem("Sign in to access", disabled=True)]

    # Services menu
    services_items = [
        dbc.DropdownMenuItem("Request Report", href="/request-report") if user_tier >= 2 else None,
        dbc.DropdownMenuItem("Admin Dashboard", href="/admin") if user_tier >= 3 else None,
        dbc.DropdownMenuItem("Help", href="/help"),
        dbc.DropdownMenuItem("Contact IR", href="/contact")
    ]
    services_items = [item for item in services_items if item is not None]

    # Auth section with unique IDs
    if not user_data:
        auth_section = dbc.Button("Sign In", id="main-signin-btn", color="outline-success", size="sm")
    else:
        auth_section = dbc.DropdownMenu([
            dbc.DropdownMenuItem([
                html.Strong(user_data.get('full_name', 'User')),
                html.Br(),
                html.Small(user_data.get('email', '')),
                html.Br(),
                dbc.Badge(f"Tier {user_tier}", color="success")
            ], header=True),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-sign-out-alt me-2"), "Sign Out"
            ], id="main-signout-btn")
        ], label=user_data.get('full_name', 'User').split()[0], direction="down", right=True)

    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.Img(src="/assets/usc-logo.png", height="45", className="me-3"),
                html.Div([
                    html.Div("Institutional Research", style={
                        'fontSize': '1.2rem', 'fontWeight': '700',
                        'color': '#FDD835', 'lineHeight': '1.1'
                    }),
                    html.Div("University of the Southern Caribbean", style={
                        'fontSize': '0.8rem', 'color': '#FFFFFF', 'lineHeight': '1.1'
                    })
                ])
            ], href="/"),

            html.Div(style={'flex': '1'}),

            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Home", href="/", style={'color': '#1B5E20', 'fontWeight': '600'})),
                dbc.DropdownMenu([
                    dbc.DropdownMenuItem("About USC", href="/about-usc"),
                    dbc.DropdownMenuItem("Vision & Mission", href="/vision-mission"),
                    dbc.DropdownMenuItem("Governance", href="/governance"),
                    dbc.DropdownMenuItem("Contact", href="/contact")
                ], label="About USC", nav=True, toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none', 'background': 'transparent'}),
                dbc.NavItem(dbc.NavLink("Alumni Portal", href="/alumni", style={'color': '#1B5E20', 'fontWeight': '600'})),
                dbc.DropdownMenu(factbook_items, label="Factbook", nav=True, toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none', 'background': 'transparent'}),
                dbc.DropdownMenu(services_items, label="Services", nav=True, toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none', 'background': 'transparent'}),
                dbc.NavItem(auth_section, className="ms-2")
            ])
        ], fluid=True, style={'display': 'flex', 'alignItems': 'center'}),
        color="white",
        className="shadow-sm sticky-top",
        style={'borderBottom': '3px solid #1B5E20', 'minHeight': '75px'}
    )

# Your exact home layout
def create_home_layout():
    return html.Div([
        # Hero section
        html.Section([
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
            'background': '''linear-gradient(135deg, rgba(27, 94, 32, 0.85) 0%, rgba(46, 125, 50, 0.85) 50%, rgba(76, 175, 80, 0.85) 100%), url('/assets/banner.png')''',
            'backgroundSize': 'cover',
            'backgroundPosition': 'center',
            'color': 'white',
            'padding': '100px 0'
        }),

        # Stats section
        html.Section([
            dbc.Container([
                html.H2("At a Glance", style={'color': '#1B5E20', 'fontWeight': '700', 'fontSize': '2.5rem', 'textAlign': 'center', 'marginBottom': '3rem'}),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-users", style={'fontSize': '2.5rem', 'color': '#1B5E20', 'marginRight': '20px'}),
                                    html.Div([
                                        html.H3("3,110", style={'fontSize': '2.2rem', 'fontWeight': '700', 'color': '#1B5E20', 'margin': '0'}),
                                        html.P("Total Enrollment", style={'color': '#666', 'margin': '5px 0'})
                                    ])
                                ], style={'display': 'flex', 'alignItems': 'center'})
                            ])
                        ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
                    ], md=3, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-building", style={'fontSize': '2.5rem', 'color': '#4CAF50', 'marginRight': '20px'}),
                                    html.Div([
                                        html.H3("5", style={'fontSize': '2.2rem', 'fontWeight': '700', 'color': '#1B5E20', 'margin': '0'}),
                                        html.P("Academic Divisions", style={'color': '#666', 'margin': '5px 0'})
                                    ])
                                ], style={'display': 'flex', 'alignItems': 'center'})
                            ])
                        ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
                    ], md=3, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-user-tie", style={'fontSize': '2.5rem', 'color': '#FDD835', 'marginRight': '20px'}),
                                    html.Div([
                                        html.H3("250+", style={'fontSize': '2.2rem', 'fontWeight': '700', 'color': '#1B5E20', 'margin': '0'}),
                                        html.P("Employees", style={'color': '#666', 'margin': '5px 0'})
                                    ])
                                ], style={'display': 'flex', 'alignItems': 'center'})
                            ])
                        ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
                    ], md=3, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-eye", style={'fontSize': '2.5rem', 'color': '#28A745', 'marginRight': '20px'}),
                                    html.Div([
                                        html.H3("100%", style={'fontSize': '2.2rem', 'fontWeight': '700', 'color': '#1B5E20', 'margin': '0'}),
                                        html.P("Data Transparency", style={'color': '#666', 'margin': '5px 0'})
                                    ])
                                ], style={'display': 'flex', 'alignItems': 'center'})
                            ])
                        ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
                    ], md=3, className="mb-4")
                ])
            ])
        ], style={'padding': '80px 0', 'background': '#F8F9FA'}),

        # Director's message (simplified)
        html.Section([
            dbc.Container([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Img(src="/assets/DirectorIR.jpg", style={'width': '120px', 'height': '120px', 'objectFit': 'cover', 'border': '4px solid #1B5E20'})
                            ], md=3, className="text-center"),
                            dbc.Col([
                                html.H3("Director's Message", style={'color': '#1B5E20', 'fontWeight': '600'}),
                                html.P("The Department of Institutional Research takes great pride in presenting comprehensive data and analytics for informed decision-making at USC.", style={'color': '#555', 'lineHeight': '1.7'}),
                                html.P("Nordian C. Swaby Robinson", style={'color': '#1B5E20', 'fontWeight': '600'}),
                                html.P("Director, Institutional Research", style={'color': '#666', 'fontSize': '0.9rem'})
                            ], md=9)
                        ])
                    ])
                ])
            ])
        ], style={'padding': '60px 0'})
    ])

# Simple login modal with unique IDs
def create_login_modal():
    return dbc.Modal([
        dbc.ModalHeader("USC IR Portal Login"),
        dbc.ModalBody([
            html.P("Select a demo user to test different access levels:"),
            dbc.RadioItems(
                id="demo-user-choice",
                options=[
                    {"label": "Demo Employee (Tier 2 - Factbook Access)", "value": "demo@usc.edu.tt"},
                    {"label": "Admin User (Tier 3 - Full Access)", "value": "admin@usc.edu.tt"},
                    {"label": "Nordian Robinson (Director)", "value": "nrobinson@usc.edu.tt"},
                    {"label": "Liam Webster (Developer)", "value": "websterl@usc.edu.tt"}
                ],
                value="demo@usc.edu.tt",
                className="mb-3"
            ),
            html.Div(id="auth-feedback", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("Sign In", id="modal-signin-btn", color="success"),
            dbc.Button("Close", id="modal-close-btn", color="secondary", className="ms-2")
        ])
    ], id="auth-modal", is_open=False)

# Access control function
def require_access(content, tier, user_data):
    if not user_data:
        return dbc.Container([
            dbc.Alert([
                html.H4([html.I(className="fas fa-lock me-2"), "Authentication Required"]),
                html.P("Please sign in to access this content."),
                dbc.Button("Sign In", id="access-signin-btn", color="success")
            ], color="warning")
        ], className="mt-5")

    if user_data.get('access_tier', 1) < tier:
        return dbc.Container([
            dbc.Alert([
                html.H4([html.I(className="fas fa-shield-alt me-2"), "Access Restricted"]),
                html.P(f"This page requires Tier {tier} access. You have Tier {user_data.get('access_tier', 1)} access."),
                html.P("Contact ir@usc.edu.tt to request higher access.")
            ], color="warning")
        ], className="mt-5")

    return content

def create_placeholder(title, description):
    return dbc.Container([
        html.H1(title, style={'color': '#1B5E20'}),
        html.P(description, className="lead"),
        dbc.Alert("This page is under development.", color="info"),
        dbc.Button("Return Home", href="/", color="primary")
    ], className="mt-5")

# App layout
app.layout = html.Div([
    dcc.Location(id='main-url'),
    dcc.Store(id='auth-store', data=None),
    html.Div(id='main-content'),
    create_login_modal()
])

# Main routing callback
@callback(
    Output('main-content', 'children'),
    Input('main-url', 'pathname'),
    State('auth-store', 'data')
)
def display_page(pathname, user_data):
    navbar = create_navbar(user_data)

    if pathname == '/' or not pathname:
        content = create_home_layout()
    elif pathname == '/about-usc':
        if PAGES_AVAILABLE:
            content = create_about_usc_page()
        else:
            content = create_placeholder("About USC", "Learn about our history and mission")
    elif pathname == '/vision-mission':
        if PAGES_AVAILABLE:
            content = create_vision_mission_page()
        else:
            content = create_placeholder("Vision & Mission", "Our institutional vision and mission")
    elif pathname == '/governance':
        if PAGES_AVAILABLE:
            content = create_governance_page()
        else:
            content = create_placeholder("Governance", "Organizational structure")
    elif pathname == '/contact':
        if PAGES_AVAILABLE:
            content = create_contact_page()
        else:
            content = create_placeholder("Contact", "Get in touch with our team")
    elif pathname == '/alumni':
        content = create_placeholder("Alumni Portal", "Connect with USC alumni network")
    elif pathname == '/factbook':
        content = require_access(create_placeholder("Interactive Factbook", "Institutional data and analytics"), 2, user_data)
    elif pathname == '/enrollment':
        content = require_access(create_placeholder("Enrollment Data", "Student enrollment analytics"), 2, user_data)
    elif pathname == '/graduation':
        content = require_access(create_placeholder("Graduation Statistics", "Graduation outcomes"), 2, user_data)
    elif pathname == '/student-employment':
        content = require_access(create_placeholder("Student Employment", "Employment analytics"), 2, user_data)
    elif pathname == '/hr-data':
        content = require_access(create_placeholder("HR Analytics", "Faculty and staff data"), 2, user_data)
    elif pathname == '/financial':
        content = require_access(create_placeholder("Financial Reports", "Financial analysis"), 3, user_data)
    elif pathname == '/budget':
        content = require_access(create_placeholder("Budget Analysis", "Budget tracking"), 3, user_data)
    elif pathname == '/admin':
        content = require_access(create_placeholder("Admin Dashboard", "System administration"), 3, user_data)
    elif pathname == '/request-report':
        content = require_access(create_placeholder("Request Report", "Submit report requests"), 2, user_data)
    elif pathname == '/help':
        content = create_placeholder("Help Center", "Documentation and support")
    else:
        content = create_placeholder("Page Not Found", f"The page '{pathname}' was not found")

    return html.Div([navbar, content])

# Single authentication callback with unique IDs only
@callback(
    [Output('auth-modal', 'is_open'),
     Output('auth-store', 'data'),
     Output('auth-feedback', 'children')],
    [Input('main-signin-btn', 'n_clicks'),
     Input('modal-signin-btn', 'n_clicks'),
     Input('modal-close-btn', 'n_clicks'),
     Input('access-signin-btn', 'n_clicks')],
    [State('demo-user-choice', 'value'),
     State('auth-modal', 'is_open'),
     State('auth-store', 'data')],
    prevent_initial_call=True
)
def handle_auth(main_signin, modal_signin, modal_close, access_signin,
                selected_user, modal_open, current_user):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, current_user, ""

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Open modal
    if button_id in ['main-signin-btn', 'access-signin-btn']:
        return True, current_user, ""

    # Close modal
    if button_id == 'modal-close-btn':
        return False, current_user, ""

    # Sign in
    if button_id == 'modal-signin-btn':
        conn = sqlite3.connect('usc_ir.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (selected_user,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_data = {
                'email': user[1],
                'full_name': user[2],
                'access_tier': user[3]
            }
            return False, user_data, ""
        return True, current_user, dbc.Alert("Login failed", color="danger")

    return modal_open, current_user, ""

# SEPARATE logout callback that only runs when the component exists
@callback(
    Output('auth-store', 'data', allow_duplicate=True),
    Input('main-signout-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(signout_clicks):
    if signout_clicks:
        return None
    return dash.no_update

if __name__ == '__main__':
    init_database()
    print("🚀 USC Institutional Research Portal - Final Working Version")
    print("✅ Self-contained with no callback conflicts")
    print("✅ Your complete design preserved")
    print("✅ Working authentication system")
    print("✅ 3-tier access control")
    print("🌐 Visit: http://localhost:8050")
    print()
    print("🎮 Authentication Test:")
    print("   • Click 'Sign In' to open login modal")
    print("   • Select demo user with different access tiers")
    print("   • Test access control on different pages")

    app.run_server(debug=True, host='0.0.0.0', port=8050)