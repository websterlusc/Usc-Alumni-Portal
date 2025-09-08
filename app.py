"""
USC Institutional Research Portal - Complete Working Version
With all requested changes: gold/white navbar text, employees stat, alumni portal & yearly reports services
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
# DATABASE & SESSION MANAGEMENT
# ============================================================================

def init_database():
    """Initialize SQLite database for users and sessions"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'employee',
            access_tier INTEGER DEFAULT 2,
            google_id TEXT,
            profile_picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY,
            session_token TEXT UNIQUE,
            user_id INTEGER,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def get_user_access_tier(user_email=None):
    """Determine user access tier - simplified for demo"""
    if not user_email:
        return 1  # Public access

    if user_email.endswith('@usc.edu.tt'):
        if user_email.startswith('admin') or user_email in ['nrobinson@usc.edu.tt', 'websterl@usc.edu.tt']:
            return 3  # Financial access
        return 2  # Factbook access

    return 1  # Public access

def load_sample_data():
    """Load sample data for dashboard"""
    return {
        'current_students': 3110,
        'graduates_2025': 847,
        'employment_rate': 98,
        'student_faculty_ratio': '15:1',
        'last_updated': datetime.now().strftime('%B %d, %Y')
    }

# ============================================================================
# NAVBAR - GOLD/WHITE TEXT, RIGHT ALIGNED
# ============================================================================

def create_modern_navbar(user_email=None):
    """Navbar with gold title, white subtitle, green nav items, right aligned"""

    return dbc.Navbar(
        dbc.Container([
            # Brand (stays left)
            dbc.NavbarBrand([
                html.Img(src="/assets/usc-logo.png", height="45", className="me-3"),
                html.Div([
                    html.Div("Institutional Research", style={
                        'fontSize': '1.2rem', 'fontWeight': '700',
                        'color': '#FDD835', 'lineHeight': '1.1'  # GOLD
                    }),
                    html.Div("University of the Southern Caribbean", style={
                        'fontSize': '0.8rem', 'color': '#FFFFFF',
                        'lineHeight': '1.1'  # WHITE
                    })
                ])
            ], href="/"),

            # Spacer to push everything right
            html.Div(style={'flex': '1'}),

            # Right-aligned navigation
            dbc.Nav([
                dbc.NavItem(dbc.NavLink(
                    "Home", href="/",
                    style={'color': '#1B5E20', 'fontWeight': '600'}
                )),
                dbc.DropdownMenu([
                    dbc.DropdownMenuItem("About USC", href="#"),
                    dbc.DropdownMenuItem("Vision & Mission", href="#"),
                    dbc.DropdownMenuItem("Governance", href="#"),
                    dbc.DropdownMenuItem("Contact", href="#")
                ],
                label="About USC", nav=True,
                toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none', 'background': 'transparent'}
                ),
                dbc.NavItem(dbc.NavLink(
                    "Alumni Portal", href="/alumni",
                    style={'color': '#1B5E20', 'fontWeight': '600'}
                )),
                dbc.DropdownMenu([
                    dbc.DropdownMenuItem("Factbook Overview", href="#"),
                    dbc.DropdownMenuItem("Enrollment Data", href="#"),
                    dbc.DropdownMenuItem("Graduation Stats", href="#"),
                    dbc.DropdownMenuItem("Student Employment", href="#"),
                    dbc.DropdownMenuItem("HR Analytics", href="#")
                ],
                label="Factbook", nav=True,
                toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none', 'background': 'transparent'}
                ),
                dbc.DropdownMenu([
                    dbc.DropdownMenuItem("Request Report", href="#"),
                    dbc.DropdownMenuItem("Help", href="#"),
                    dbc.DropdownMenuItem("Contact IR", href="#")
                ],
                label="Services", nav=True,
                toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none', 'background': 'transparent'}
                ),
                dbc.NavItem(dbc.Button(
                    "Login", color="outline-success",
                    size="sm", id="login-btn", className="ms-2"
                ))
            ])
        ], fluid=True, style={'display': 'flex', 'alignItems': 'center'}),
        color="white",
        className="shadow-sm sticky-top",
        style={'borderBottom': '3px solid #1B5E20', 'minHeight': '75px'}
    )

# ============================================================================
# HOME PAGE COMPONENTS
# ============================================================================

def create_hero_section():
    """Modern hero section with banner as translucent background"""
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
                        dbc.Button("Explore Factbook", color="warning", size="lg", className="me-3"),
                        dbc.Button("Request Report", color="outline-light", size="lg")
                    ])
                ], md=8),
                dbc.Col([
                    # Empty column for spacing
                ], md=4)
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
    """At a Glance - Updated with EMPLOYEES instead of Years of Data"""
    stats = [
        {'title': '3,110', 'subtitle': 'Total Enrollment', 'icon': 'fas fa-users', 'color': '#1B5E20'},
        {'title': '5', 'subtitle': 'Academic Divisions', 'icon': 'fas fa-building', 'color': '#4CAF50'},
        {'title': '250+', 'subtitle': 'Employees', 'icon': 'fas fa-user-tie', 'color': '#FDD835'},  # CHANGED
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
    """Our Services - Updated with ALUMNI PORTAL and YEARLY REPORTS"""
    features = [
        {'title': 'Interactive Factbook', 'desc': 'Comprehensive institutional data with interactive visualizations.', 'icon': 'fas fa-chart-line'},
        {'title': 'Alumni Portal', 'desc': 'Connect with USC alumni and access alumni services and networks.', 'icon': 'fas fa-graduation-cap'},  # CHANGED
        {'title': 'Yearly Reports', 'desc': 'Annual institutional reports and comprehensive data analysis.', 'icon': 'fas fa-calendar-alt'},  # CHANGED
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

# ============================================================================
# IR DIRECTOR'S MESSAGE
# ============================================================================

def create_director_message():
    """IR Director's message section with full text"""
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
                                "By consolidating three years – 2021-2022, 2022-2023 and 2023-2024 of key metrics into a single reference, ",
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
    """Quick access links - Fixed Aerion URL"""
    links = [
        {'title': 'USC Main Website', 'url': 'https://www.usc.edu.tt', 'icon': 'fas fa-globe'},
        {'title': 'USC eLearn', 'url': 'https://elearn.usc.edu.tt', 'icon': 'fas fa-laptop'},
        {'title': 'Aerion Portal', 'url': 'https://aerion.usc.edu.tt', 'icon': 'fas fa-door-open'},  # FIXED URL
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
    """Modern footer"""
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

def create_home_layout(user_email=None):
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
# PLACEHOLDER PAGES
# ============================================================================

def create_placeholder_page(title, description, tier_required=1):
    """Create placeholder page"""
    return dbc.Container([
        html.H1(title, className="display-4 fw-bold mb-4 text-center", style={'color': '#1B5E20'}),
        dbc.Alert([
            html.H4("Coming Soon!", className="alert-heading"),
            html.P(description)
        ], color="info", className="text-center"),
        dbc.Button("Return Home", href="/", color="primary", className="d-block mx-auto mt-4")
    ], className="mt-5")

# ============================================================================
# MAIN APPLICATION LAYOUT
# ============================================================================

def serve_layout():
    """Main application layout"""
    return html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='user-session', storage_type='session'),
        html.Div(id='page-content')
    ])

app.layout = serve_layout

# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def display_page(pathname, session_data):
    """Main routing callback"""

    user_email = session_data.get('user_email') if session_data else None
    if not user_email:
        user_email = "demo@usc.edu.tt"  # Demo for now

    navbar = create_modern_navbar(user_email)

    if pathname == '/' or pathname is None:
        content = create_home_layout(user_email)
    elif pathname == '/alumni':
        content = create_placeholder_page("Alumni Portal", "Connect with USC alumni and access alumni services.", 1)
    else:
        content = create_placeholder_page("Page Under Development", f"The page '{pathname}' is being developed.", 1)

    return html.Div([navbar, content])

@callback(
    Output('user-session', 'data'),
    Input('login-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_login(n_clicks):
    """Handle login"""
    if n_clicks:
        return {'user_email': 'demo@usc.edu.tt', 'user_name': 'Demo User'}
    return {}

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    init_database()
    print("🚀 Starting USC Institutional Research Portal...")
    print("🌐 Visit: http://localhost:8050")
    app.run_server(debug=True, host='0.0.0.0', port=8050)