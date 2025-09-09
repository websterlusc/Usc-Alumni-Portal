"""
USC Institutional Research Portal - Standard Login System
Username/password authentication with user registration
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import sqlite3
import hashlib
import secrets
from datetime import datetime

# USC Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA'
}

# Initialize app
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

# Import your existing pages
try:
    from pages.about_usc_page import create_about_usc_page
    from pages.vision_mission_page import create_vision_mission_page
    from pages.contact_page import create_contact_page
    from pages.governance_page import create_governance_page
    PAGES_AVAILABLE = True
except ImportError:
    PAGES_AVAILABLE = False

# Database setup with password hashing
def hash_password(password):
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

def init_database():
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    # Users table with password hash
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            access_tier INTEGER DEFAULT 1,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            session_token TEXT UNIQUE,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create default admin user if not exists
    admin_password = hash_password("admin123")
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, full_name, password_hash, access_tier)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@usc.edu.tt', 'System Administrator', admin_password, 3))

    # Create demo users
    demo_users = [
        ('nrobinson', 'nrobinson@usc.edu.tt', 'Nordian Robinson', hash_password('password123'), 3),
        ('websterl', 'websterl@usc.edu.tt', 'Liam Webster', hash_password('password123'), 3),
        ('employee1', 'employee1@usc.edu.tt', 'Demo Employee', hash_password('password123'), 2),
        ('student1', 'student1@usc.edu.tt', 'Demo Student', hash_password('password123'), 1)
    ]

    for username, email, name, password_hash, tier in demo_users:
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, full_name, password_hash, access_tier)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, name, password_hash, tier))

    conn.commit()
    conn.close()
    print("Database initialized with demo accounts:")
    print("  admin / admin123 (Tier 3)")
    print("  nrobinson / password123 (Tier 3)")
    print("  websterl / password123 (Tier 3)")
    print("  employee1 / password123 (Tier 2)")
    print("  student1 / password123 (Tier 1)")

def authenticate_user(username, password):
    """Authenticate user credentials"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, username, email, full_name, password_hash, access_tier, is_active
        FROM users WHERE username = ? AND is_active = 1
    ''', (username,))

    user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user[4]):
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[3],
            'access_tier': user[5]
        }
    return None

def register_user(username, email, full_name, password):
    """Register new user"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, full_name, password_hash, access_tier)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, full_name, password_hash, 1))  # Default tier 1

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        return {
            'id': user_id,
            'username': username,
            'email': email,
            'full_name': full_name,
            'access_tier': 1
        }
    except sqlite3.IntegrityError as e:
        conn.close()
        if 'username' in str(e):
            return {'error': 'Username already exists'}
        elif 'email' in str(e):
            return {'error': 'Email already exists'}
        else:
            return {'error': 'Registration failed'}
    except Exception as e:
        conn.close()
        return {'error': 'Registration failed'}

# Your exact navbar
def create_navbar(user_data=None):
    user_tier = user_data.get('access_tier', 1) if user_data else 1

    # Dynamic factbook menu
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
        factbook_items = [dbc.DropdownMenuItem("Login to access factbook", disabled=True)]

    # Services menu
    services_items = [
        dbc.DropdownMenuItem("Request Report", href="/request-report") if user_tier >= 2 else None,
        dbc.DropdownMenuItem("Admin Dashboard", href="/admin") if user_tier >= 3 else None,
        dbc.DropdownMenuItem("Help", href="/help"),
        dbc.DropdownMenuItem("Contact IR", href="/contact")
    ]
    services_items = [item for item in services_items if item is not None]

    # Auth section
    if not user_data:
        auth_section = dbc.ButtonGroup([
            dbc.Button("Login", id="login-btn", color="outline-success", size="sm"),
            dbc.Button("Register", id="register-btn", color="success", size="sm")
        ])
    else:
        auth_section = dbc.DropdownMenu([
            dbc.DropdownMenuItem([
                html.Strong(user_data.get('full_name', 'User')),
                html.Br(),
                html.Small(f"@{user_data.get('username', '')}", className="text-muted"),
                html.Br(),
                dbc.Badge(f"Tier {user_tier}", color="success", className="mt-1")
            ], header=True),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([html.I(className="fas fa-user me-2"), "Profile"], href="/profile"),
            dbc.DropdownMenuItem([html.I(className="fas fa-key me-2"), "Request Access"]) if user_tier < 3 else None,
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([html.I(className="fas fa-sign-out-alt me-2"), "Logout"], id="logout-btn")
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

# Your exact home layout (simplified)
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
        ], style={'padding': '80px 0', 'background': '#F8F9FA'})
    ])

# Login modal
def create_login_modal():
    return dbc.Modal([
        dbc.ModalHeader("Login to USC IR Portal"),
        dbc.ModalBody([
            html.Div(id="login-alerts"),
            dbc.Form([
                dbc.Row([
                    dbc.Label("Username", width=3),
                    dbc.Col([
                        dbc.Input(id="login-username", type="text", placeholder="Enter username")
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Password", width=3),
                    dbc.Col([
                        dbc.Input(id="login-password", type="password", placeholder="Enter password")
                    ], width=9)
                ], className="mb-3"),
                html.Small("Demo accounts: admin/admin123, employee1/password123, student1/password123", className="text-muted")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Login", id="login-submit", color="success"),
            dbc.Button("Close", id="login-close", color="secondary")
        ])
    ], id="login-modal", is_open=False)

# Register modal
def create_register_modal():
    return dbc.Modal([
        dbc.ModalHeader("Register for USC IR Portal"),
        dbc.ModalBody([
            html.Div(id="register-alerts"),
            dbc.Form([
                dbc.Row([
                    dbc.Label("Full Name", width=3),
                    dbc.Col([
                        dbc.Input(id="register-fullname", type="text", placeholder="Your full name")
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Username", width=3),
                    dbc.Col([
                        dbc.Input(id="register-username", type="text", placeholder="Choose a username")
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Email", width=3),
                    dbc.Col([
                        dbc.Input(id="register-email", type="email", placeholder="your.email@example.com")
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Password", width=3),
                    dbc.Col([
                        dbc.Input(id="register-password", type="password", placeholder="Choose a password")
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Confirm Password", width=3),
                    dbc.Col([
                        dbc.Input(id="register-confirm", type="password", placeholder="Confirm password")
                    ], width=9)
                ], className="mb-3"),
                html.Small("New accounts start with Tier 1 (Public) access. Contact administrators for higher access.", className="text-muted")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Register", id="register-submit", color="success"),
            dbc.Button("Close", id="register-close", color="secondary")
        ])
    ], id="register-modal", is_open=False)

# Access control
def require_access(content, tier, user_data):
    if not user_data:
        return dbc.Container([
            dbc.Alert([
                html.H4([html.I(className="fas fa-lock me-2"), "Login Required"]),
                html.P("Please log in to access this content."),
                dbc.Button("Login", id="access-login-btn", color="success")
            ], color="warning")
        ], className="mt-5")

    if user_data.get('access_tier', 1) < tier:
        return dbc.Container([
            dbc.Alert([
                html.H4([html.I(className="fas fa-shield-alt me-2"), "Access Restricted"]),
                html.P(f"This page requires Tier {tier} access. You have Tier {user_data.get('access_tier', 1)} access."),
                html.P("Contact administrators to request higher access.")
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
    dcc.Location(id='url'),
    dcc.Store(id='user-store', data=None),
    html.Div(id='content'),
    create_login_modal(),
    create_register_modal()
])

# Main routing
@callback(
    Output('content', 'children'),
    Input('url', 'pathname'),
    State('user-store', 'data')
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
            content = create_placeholder("Vision & Mission", "Our institutional vision")
    elif pathname == '/governance':
        if PAGES_AVAILABLE:
            content = create_governance_page()
        else:
            content = create_placeholder("Governance", "Organizational structure")
    elif pathname == '/contact':
        if PAGES_AVAILABLE:
            content = create_contact_page()
        else:
            content = create_placeholder("Contact", "Get in touch")
    elif pathname == '/alumni':
        content = create_placeholder("Alumni Portal", "Connect with USC alumni")
    elif pathname == '/factbook':
        content = require_access(create_placeholder("Interactive Factbook", "Institutional data"), 2, user_data)
    elif pathname == '/enrollment':
        content = require_access(create_placeholder("Enrollment Data", "Student enrollment"), 2, user_data)
    elif pathname == '/graduation':
        content = require_access(create_placeholder("Graduation Statistics", "Graduation data"), 2, user_data)
    elif pathname == '/student-employment':
        content = require_access(create_placeholder("Student Employment", "Employment data"), 2, user_data)
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

# Authentication callbacks
@callback(
    [Output('login-modal', 'is_open'),
     Output('register-modal', 'is_open'),
     Output('user-store', 'data'),
     Output('login-alerts', 'children'),
     Output('register-alerts', 'children')],
    [Input('login-btn', 'n_clicks'),
     Input('register-btn', 'n_clicks'),
     Input('login-submit', 'n_clicks'),
     Input('register-submit', 'n_clicks'),
     Input('login-close', 'n_clicks'),
     Input('register-close', 'n_clicks'),
     Input('logout-btn', 'n_clicks'),
     Input('access-login-btn', 'n_clicks')],
    [State('login-username', 'value'),
     State('login-password', 'value'),
     State('register-fullname', 'value'),
     State('register-username', 'value'),
     State('register-email', 'value'),
     State('register-password', 'value'),
     State('register-confirm', 'value'),
     State('login-modal', 'is_open'),
     State('register-modal', 'is_open'),
     State('user-store', 'data')],
    prevent_initial_call=True
)
def handle_auth(login_btn, register_btn, login_submit, register_submit,
                login_close, register_close, logout_btn, access_login,
                username, password, fullname, reg_username, email,
                reg_password, confirm_password, login_open, register_open, current_user):

    ctx = dash.callback_context
    if not ctx.triggered:
        return False, False, current_user, "", ""

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Open modals
    if button_id in ['login-btn', 'access-login-btn']:
        return True, False, current_user, "", ""
    if button_id == 'register-btn':
        return False, True, current_user, "", ""

    # Close modals
    if button_id == 'login-close':
        return False, register_open, current_user, "", ""
    if button_id == 'register-close':
        return login_open, False, current_user, "", ""

    # Login
    if button_id == 'login-submit':
        if not username or not password:
            return True, False, current_user, dbc.Alert("Please enter username and password", color="danger"), ""

        user = authenticate_user(username, password)
        if user:
            return False, False, user, "", ""
        else:
            return True, False, current_user, dbc.Alert("Invalid username or password", color="danger"), ""

    # Register
    if button_id == 'register-submit':
        if not all([fullname, reg_username, email, reg_password, confirm_password]):
            return False, True, current_user, "", dbc.Alert("Please fill in all fields", color="danger")

        if reg_password != confirm_password:
            return False, True, current_user, "", dbc.Alert("Passwords do not match", color="danger")

        if len(reg_password) < 6:
            return False, True, current_user, "", dbc.Alert("Password must be at least 6 characters", color="danger")

        result = register_user(reg_username, email, fullname, reg_password)
        if 'error' in result:
            return False, True, current_user, "", dbc.Alert(result['error'], color="danger")
        else:
            return False, False, result, "", ""

    # Logout
    if button_id == 'logout-btn':
        return False, False, None, "", ""

    return login_open, register_open, current_user, "", ""

if __name__ == '__main__':
    init_database()
    print("USC Institutional Research Portal - Standard Login System")
    print("Your complete design with username/password authentication")
    print("Visit: http://localhost:8050")
    app.run_server(debug=True, host='0.0.0.0', port=8050)