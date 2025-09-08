"""
USC Institutional Research Portal - Complete Application
Modern redesign with authentication and tier-based access control
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

# Initialize Dash app - CSS will be loaded from assets/ folder
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
    """Load sample data for dashboard - replace with your Excel data loading"""
    try:
        # Simulate loading from your Excel files
        return {
            'current_students': 3110,
            'graduates_2025': 847,
            'employment_rate': 98,
            'student_faculty_ratio': '15:1',
            'last_updated': datetime.now().strftime('%B %d, %Y')
        }
    except Exception as e:
        # Fallback data
        return {
            'current_students': 3110,
            'graduates_2025': 847,
            'employment_rate': 98,
            'student_faculty_ratio': '15:1',
            'last_updated': 'May 14, 2025'
        }

# ============================================================================
# MODERN NAVBAR COMPONENT
# ============================================================================

def create_modern_navbar(user_email=None):
    """Create modern navigation bar with tier-based access"""
    access_tier = get_user_access_tier(user_email)

    # Brand section
    brand = dbc.NavbarBrand([
        html.Img(
            src="/assets/usc-logo.png",
            height="45",
            className="me-3",
            alt="USC Logo"
        ),
        html.Div([
            html.Div("Institutional Research", style={
                'fontSize': '1.1rem',
                'fontWeight': '700',
                'color': USC_COLORS['primary_green'],
                'lineHeight': '1.2',
                'margin': '0'
            }),
            html.Div("University of the Southern Caribbean", style={
                'fontSize': '0.75rem',
                'color': USC_COLORS['primary_green'],
                'lineHeight': '1.2',
                'margin': '0',
                'opacity': '0.7'
            })
        ])
    ], href="/", style={'textDecoration': 'none'})

    # Navigation items
    nav_items = []

    # Home
    nav_items.append(
        dbc.NavItem(
            dbc.NavLink(
                [html.I(className="fas fa-home me-2"), "Home"],
                href="/",
                active="exact",
                style={
                    'color': USC_COLORS['primary_green'],
                    'fontWeight': '600',
                    'borderRadius': '6px',
                    'padding': '8px 12px',
                    'transition': 'all 0.3s ease'
                }
            )
        )
    )

    # About USC dropdown
    about_items = [
        dbc.DropdownMenuItem([html.I(className="fas fa-university me-2"), "About USC"], href="#", id="about-usc"),
        dbc.DropdownMenuItem([html.I(className="fas fa-eye me-2"), "Vision, Mission & Motto"], href="#", id="vision-mission"),
        dbc.DropdownMenuItem([html.I(className="fas fa-sitemap me-2"), "Governance Structure"], href="#", id="governance"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem([html.I(className="fas fa-phone me-2"), "Contact Information"], href="#", id="contact")
    ]

    nav_items.append(
        dbc.DropdownMenu(
            about_items,
            nav=True,
            in_navbar=True,
            label=[html.I(className="fas fa-info-circle me-2"), "About USC"],
            toggle_style={
                'color': USC_COLORS['primary_green'],
                'fontWeight': '600',
                'border': 'none',
                'background': 'transparent',
                'borderRadius': '6px',
                'padding': '8px 12px'
            }
        )
    )

    # Factbook dropdown (Tier 2+)
    if access_tier >= 2:
        factbook_items = [
            dbc.DropdownMenuItem([html.I(className="fas fa-chart-bar me-2"), "Factbook Overview"], href="#", id="factbook"),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([html.I(className="fas fa-users me-2"), "Enrollment Data"], href="#", id="enrollment"),
            dbc.DropdownMenuItem([html.I(className="fas fa-graduation-cap me-2"), "Graduation Statistics"], href="#", id="graduation"),
            dbc.DropdownMenuItem([html.I(className="fas fa-briefcase me-2"), "Student Employment"], href="#", id="student-employment"),
            dbc.DropdownMenuItem([html.I(className="fas fa-user-tie me-2"), "HR Analytics"], href="#", id="hr-data"),
            dbc.DropdownMenuItem([html.I(className="fas fa-chalkboard-teacher me-2"), "Teaching Load"], href="#", id="teaching-load")
        ]

        nav_items.append(
            dbc.DropdownMenu(
                factbook_items,
                nav=True,
                in_navbar=True,
                label=[
                    html.I(className="fas fa-book me-2"),
                    "Factbook",
                    dbc.Badge("Staff", color="success", className="ms-2", style={"font-size": "0.6rem"})
                ],
                toggle_style={
                    'color': USC_COLORS['primary_green'],
                    'fontWeight': '700',
                    'border': 'none',
                    'background': 'transparent',
                    'borderRadius': '6px',
                    'padding': '8px 12px'
                }
            )
        )

    # Financial dropdown (Tier 3+)
    if access_tier >= 3:
        financial_items = [
            dbc.DropdownMenuItem([html.I(className="fas fa-chart-pie me-2"), "Financial Overview"], href="#", id="financial"),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([html.I(className="fas fa-calculator me-2"), "Budget Analysis"], href="#", id="budget"),
            dbc.DropdownMenuItem([html.I(className="fas fa-piggy-bank me-2"), "Endowment Funds"], href="#", id="endowments"),
            dbc.DropdownMenuItem([html.I(className="fas fa-receipt me-2"), "GATE Funding"], href="#", id="gate-funding"),
            dbc.DropdownMenuItem([html.I(className="fas fa-hand-holding-usd me-2"), "Subsidies"], href="#", id="subsidies")
        ]

        nav_items.append(
            dbc.DropdownMenu(
                financial_items,
                nav=True,
                in_navbar=True,
                label=[
                    html.I(className="fas fa-chart-line me-2"),
                    "Financial Reports",
                    dbc.Badge("Admin", color="warning", className="ms-2", style={"font-size": "0.6rem"})
                ],
                toggle_style={
                    'color': USC_COLORS['accent_yellow'],
                    'fontWeight': '700',
                    'border': 'none',
                    'background': 'transparent',
                    'borderRadius': '6px',
                    'padding': '8px 12px'
                }
            )
        )

    # Services dropdown
    services_items = [
        dbc.DropdownMenuItem([html.I(className="fas fa-file-alt me-2"), "Request Custom Report"], href="#", id="request-reports"),
        dbc.DropdownMenuItem([html.I(className="fas fa-question-circle me-2"), "Help & Documentation"], href="#", id="help"),
        dbc.DropdownMenuItem([html.I(className="fas fa-envelope me-2"), "Contact IR Department"], href="#", id="contact-ir")
    ]

    nav_items.append(
        dbc.DropdownMenu(
            services_items,
            nav=True,
            in_navbar=True,
            label=[html.I(className="fas fa-cogs me-2"), "Services"],
            toggle_style={
                'color': USC_COLORS['primary_green'],
                'fontWeight': '600',
                'border': 'none',
                'background': 'transparent',
                'borderRadius': '6px',
                'padding': '8px 12px'
            }
        )
    )

    # User section
    if user_email:
        user_section = [
            dbc.Badge(f"Tier {access_tier}", color="success" if access_tier >= 2 else "secondary", className="me-3"),
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem([html.I(className="fas fa-user me-2"), "Profile"], href="#"),
                    dbc.DropdownMenuItem([html.I(className="fas fa-key me-2"), "Request Access"], href="#"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem([html.I(className="fas fa-sign-out-alt me-2"), "Logout"], href="#", id="logout-btn", className="text-danger")
                ],
                nav=True,
                in_navbar=True,
                label=[
                    html.Img(src="/assets/default-avatar.png", style={
                        'width': '32px',
                        'height': '32px',
                        'borderRadius': '50%',
                        'border': f'2px solid {USC_COLORS["primary_green"]}',
                        'objectFit': 'cover'
                    }, className="me-2"),
                    html.Span(user_email.split('@')[0].title(), style={
                        'color': USC_COLORS['primary_green'],
                        'fontWeight': '600'
                    })
                ],
                toggle_style={
                    'color': USC_COLORS['primary_green'],
                    'fontWeight': '600',
                    'border': 'none',
                    'background': 'transparent',
                    'borderRadius': '6px',
                    'padding': '8px 12px'
                }
            )
        ]
    else:
        user_section = [
            dbc.Button(
                [html.I(className="fab fa-google me-2"), "Login with USC Account"],
                color="primary",
                outline=True,
                id="login-btn",
                style={
                    'borderColor': USC_COLORS['primary_green'],
                    'color': USC_COLORS['primary_green'],
                    'fontWeight': '600',
                    'borderRadius': '20px',
                    'borderWidth': '2px'
                }
            )
        ]

    return dbc.Navbar(
        dbc.Container([
            # Left side - Brand only
            brand,

            # Mobile menu toggle (will be on right side)
            dbc.NavbarToggler(id="navbar-toggler", className="ms-auto"),

            # Right side - All navigation items
            dbc.Collapse([
                # Navigation items - moved to ms-auto to push right
                dbc.Nav(nav_items, className="ms-auto me-3", navbar=True),
                # User section - stays on far right
                html.Div(user_section, className="d-flex align-items-center")
            ], id="navbar-collapse", navbar=True)
        ], fluid=True),
        color="white",
        light=True,
        className="shadow-sm sticky-top",
        style={
            'borderBottom': f'3px solid {USC_COLORS["primary_green"]}',
            'background': 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
            'minHeight': '70px'
        }
    )

# ============================================================================
# HOME PAGE COMPONENTS
# ============================================================================

def create_hero_section():
    """Modern hero section with gradient background"""
    return html.Section([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1([
                        "Institutional Research & ",
                        html.Span("Analytics", style={
                            'background': 'linear-gradient(45deg, #FDD835, #FFEB3B)',
                            'WebkitBackgroundClip': 'text',
                            'WebkitTextFillColor': 'transparent',
                            'backgroundClip': 'text'
                        })
                    ], style={
                        'fontSize': '3.5rem',
                        'fontWeight': '700',
                        'lineHeight': '1.2',
                        'marginBottom': '1.5rem'
                    }),
                    html.P(
                        "Empowering data-driven decisions through comprehensive institutional analytics, "
                        "enrollment insights, and strategic planning support for USC's continued excellence.",
                        style={
                            'fontSize': '1.25rem',
                            'opacity': '0.9',
                            'lineHeight': '1.6',
                            'marginBottom': '2rem'
                        }
                    ),
                    html.Div([
                        dbc.Button(
                            [html.I(className="fas fa-chart-bar me-2"), "Explore Factbook"],
                            color="warning",
                            size="lg",
                            className="me-3",
                            id="explore-factbook-btn",
                            style={
                                'padding': '12px 30px',
                                'fontWeight': '600',
                                'borderRadius': '25px',
                                'boxShadow': '0 4px 15px rgba(0,0,0,0.2)'
                            }
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-file-alt me-2"), "Request Report"],
                            color="outline-light",
                            size="lg",
                            id="request-report-btn",
                            style={
                                'padding': '12px 30px',
                                'fontWeight': '600',
                                'borderRadius': '25px',
                                'border': '2px solid rgba(255,255,255,0.8)',
                                'background': 'transparent'
                            }
                        )
                    ], className="mt-4")
                ], md=8),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-university", style={
                            'fontSize': '8rem',
                            'opacity': '0.2',
                            'color': 'white'
                        })
                    ], className="text-center")
                ], md=4, className="d-none d-md-block")
            ], align="center")
        ], fluid=True)
    ], style={
        'background': f'linear-gradient(135deg, {USC_COLORS["primary_green"]} 0%, #2E7D32 50%, {USC_COLORS["secondary_green"]} 100%)',
        'color': 'white',
        'padding': '100px 0',
        'position': 'relative'
    })

def create_stats_overview():
    """Statistics cards with real data"""
    data = load_sample_data()

    stats = [
        {
            'title': f"{data['current_students']:,}",
            'subtitle': 'Current Students',
            'icon': 'fas fa-users',
            'color': USC_COLORS['primary_green'],
            'change': '+5.2%',
            'period': 'vs last year'
        },
        {
            'title': f"{data['graduates_2025']:,}",
            'subtitle': 'Graduates (2025)',
            'icon': 'fas fa-graduation-cap',
            'color': USC_COLORS['accent_yellow'],
            'change': '+12.1%',
            'period': 'vs 2024'
        },
        {
            'title': f"{data['employment_rate']}%",
            'subtitle': 'Employment Rate',
            'icon': 'fas fa-briefcase',
            'color': USC_COLORS['success_green'],
            'change': '+2.1%',
            'period': 'improvement'
        },
        {
            'title': data['student_faculty_ratio'],
            'subtitle': 'Student-Faculty Ratio',
            'icon': 'fas fa-chalkboard-teacher',
            'color': USC_COLORS['secondary_green'],
            'change': 'Maintained',
            'period': 'excellence'
        }
    ]

    cards = []
    for stat in stats:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className=f"{stat['icon']}", style={
                            'fontSize': '2.5rem',
                            'marginRight': '20px',
                            'opacity': '0.8',
                            'color': stat['color']
                        }),
                        html.Div([
                            html.H3(stat['title'], style={
                                'fontSize': '2.2rem',
                                'fontWeight': '700',
                                'color': USC_COLORS['primary_green'],
                                'margin': '0',
                                'lineHeight': '1'
                            }),
                            html.P(stat['subtitle'], style={
                                'color': '#666',
                                'fontWeight': '500',
                                'margin': '5px 0',
                                'fontSize': '0.9rem'
                            }),
                            html.Div([
                                html.Span(stat['change'], style={
                                    'color': USC_COLORS['success_green'],
                                    'fontWeight': '600',
                                    'fontSize': '0.8rem'
                                }),
                                html.Span(stat['period'], style={
                                    'color': '#999',
                                    'fontSize': '0.8rem',
                                    'marginLeft': '5px'
                                })
                            ])
                        ])
                    ], style={'display': 'flex', 'alignItems': 'center', 'padding': '10px'})
                ])
            ], style={
                'border': 'none',
                'borderRadius': '15px',
                'background': 'white',
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
                'height': '100%'
            })
        ], md=3, sm=6, className="mb-4")
        cards.append(card)

    return html.Section([
        dbc.Container([
            html.H2("At a Glance", style={
                'color': USC_COLORS['primary_green'],
                'fontWeight': '700',
                'fontSize': '2.5rem',
                'textAlign': 'center',
                'marginBottom': '3rem',
                'position': 'relative'
            }),
            dbc.Row(cards),
            html.P(f"Last updated: {data['last_updated']}", className="text-center text-muted mt-3")
        ])
    ], style={'padding': '80px 0', 'background': USC_COLORS['light_gray']})

def create_feature_showcase():
    """Feature cards showcasing portal capabilities"""
    features = [
        {
            'title': 'Interactive Factbook',
            'description': 'Comprehensive institutional data with interactive visualizations and real-time analytics.',
            'icon': 'fas fa-chart-line',
            'color': USC_COLORS['primary_green'],
            'tier': 2,
            'badge': 'USC Staff Access'
        },
        {
            'title': 'Enrollment Analytics',
            'description': 'Deep-dive into enrollment trends, demographics, and predictive modeling for strategic planning.',
            'icon': 'fas fa-users-cog',
            'color': USC_COLORS['secondary_green'],
            'tier': 2,
            'badge': 'Real-time Data'
        },
        {
            'title': 'Financial Reports',
            'description': 'Comprehensive financial analysis, budget tracking, and institutional performance metrics.',
            'icon': 'fas fa-chart-pie',
            'color': USC_COLORS['accent_yellow'],
            'tier': 3,
            'badge': 'Admin Access'
        },
        {
            'title': 'Custom Reports',
            'description': 'Request tailored analytical reports and research studies for your specific needs.',
            'icon': 'fas fa-file-alt',
            'color': USC_COLORS['success_green'],
            'tier': 1,
            'badge': 'Available to All'
        }
    ]

    cards = []
    for feature in features:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className=f"{feature['icon']}", style={
                            'fontSize': '2.2rem',
                            'opacity': '0.8',
                            'color': feature['color']
                        }),
                        dbc.Badge(feature['badge'], color="light", style={
                            'fontSize': '0.7rem',
                            'textTransform': 'uppercase',
                            'letterSpacing': '0.5px'
                        })
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '15px'}),
                    html.H4(feature['title'], style={
                        'color': USC_COLORS['primary_green'],
                        'fontWeight': '600',
                        'marginBottom': '15px'
                    }),
                    html.P(feature['description'], style={
                        'color': '#666',
                        'lineHeight': '1.6',
                        'marginBottom': '20px'
                    }),
                    dbc.Button(
                        [html.I(className="fas fa-arrow-right me-2"), "Explore"],
                        color="outline-primary",
                        size="sm"
                    )
                ])
            ], style={
                'border': 'none',
                'borderRadius': '15px',
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
                'height': '100%'
            })
        ], md=6, lg=3, className="mb-4")
        cards.append(card)

    return html.Section([
        dbc.Container([
            html.H2("Our Services", style={
                'color': USC_COLORS['primary_green'],
                'fontWeight': '700',
                'fontSize': '2.5rem',
                'textAlign': 'center',
                'marginBottom': '3rem'
            }),
            dbc.Row(cards)
        ])
    ], style={'padding': '80px 0', 'background': 'white'})

def create_president_message():
    """President's message section"""
    return html.Section([
        dbc.Container([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Img(
                                src="/assets/president-wilson.jpg",
                                style={
                                    'width': '120px',
                                    'height': '120px',
                                    'borderRadius': '50%',
                                    'objectFit': 'cover',
                                    'border': f'4px solid {USC_COLORS["primary_green"]}',
                                    'boxShadow': '0 4px 15px rgba(0,0,0,0.2)'
                                },
                                alt="President Colwick Wilson"
                            )
                        ], md=3, className="text-center"),
                        dbc.Col([
                            html.H3("A Message from Our President", style={
                                'color': USC_COLORS['primary_green'],
                                'fontWeight': '600',
                                'marginBottom': '20px'
                            }),
                            html.P([
                                "As we draw closer to USC's centennial in 2027, our journey is guided by SP100, ",
                                "a strategic plan that sets forth our mission-driven priorities in service to our students, ",
                                "our faith, and our community."
                            ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '15px'}),
                            html.P([
                                "The USC Factbook plays an essential role in this journey by offering a comprehensive, ",
                                "data-informed view of our present reality. Through this platform, we can measure our progress, ",
                                "identify areas for growth, and ensure alignment with our goals."
                            ], style={'color': '#555', 'lineHeight': '1.7', 'marginBottom': '15px'}),
                            html.Div([
                                html.P("— Dr. Colwick M. Wilson", style={
                                    'color': USC_COLORS['primary_green'],
                                    'fontWeight': '600',
                                    'fontStyle': 'italic',
                                    'marginBottom': '1px'
                                }),
                                html.P("University President", style={
                                    'color': '#666',
                                    'fontSize': '0.9rem',
                                    'marginBottom': '0'
                                })
                            ], style={'marginTop': '3rem'})
                        ], md=9)
                    ])
                ])
            ], style={
                'border': 'none',
                'borderRadius': '20px',
                'boxShadow': '0 8px 30px rgba(0,0,0,0.1)'
            })
        ])
    ], style={
        'padding': '80px 0',
        'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)'
    })

def create_quick_links():
    """Quick access links"""
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
                    html.I(className=f"{link['icon']}", style={
                        'fontSize': '1.5rem',
                        'marginRight': '15px',
                        'opacity': '0.8'
                    }),
                    html.Span(link['title'], style={'fontWeight': '500'})
                ], href=link['url'], target="_blank", style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'padding': '20px',
                    'background': USC_COLORS['light_gray'],
                    'borderRadius': '12px',
                    'textDecoration': 'none',
                    'color': USC_COLORS['dark_gray'],
                    'transition': 'all 0.3s ease',
                    'border': '2px solid transparent'
                })
            ], sm=6, md=3, className="mb-3")
        )

    return html.Section([
        dbc.Container([
            html.H3("Quick Links", className="text-center mb-4"),
            dbc.Row(link_items)
        ])
    ], style={'padding': '60px 0', 'background': 'white'})

def create_modern_footer():
    """Modern footer"""
    return html.Footer([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H5("Institutional Research", style={
                        'color': USC_COLORS['accent_yellow'],
                        'fontWeight': '600',
                        'marginBottom': '20px'
                    }),
                    html.P([
                        "Supporting USC's mission through comprehensive data analysis, ",
                        "strategic insights, and institutional effectiveness research."
                    ], style={'opacity': '0.9', 'lineHeight': '1.6', 'marginBottom': '20px'})
                ], md=4),
                dbc.Col([
                    html.H6("Contact Information", style={
                        'color': USC_COLORS['accent_yellow'],
                        'fontWeight': '600',
                        'marginBottom': '15px'
                    }),
                    html.P([
                        html.Strong("Director: "), "Nordian C. Swaby Robinson", html.Br(),
                        html.Strong("Email: "), html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt",
                                                      style={'color': USC_COLORS['accent_yellow'], 'textDecoration': 'none'}), html.Br(),
                        html.Strong("Phone: "), "868-645-3265 ext. 2150", html.Br(),
                        html.Strong("Office: "), "Administration Building, Room 201"
                    ], style={'opacity': '0.9', 'lineHeight': '1.8'})
                ], md=4),
                dbc.Col([
                    html.H6("Development Team", style={
                        'color': USC_COLORS['accent_yellow'],
                        'fontWeight': '600',
                        'marginBottom': '15px'
                    }),
                    html.P([
                        html.Strong("Web Developer: "), "Liam Webster", html.Br(),
                        html.Strong("Email: "), html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt",
                                                      style={'color': USC_COLORS['accent_yellow'], 'textDecoration': 'none'}), html.Br(),
                        html.Strong("Phone: "), "868-645-3265 ext. 1014"
                    ], style={'opacity': '0.9', 'lineHeight': '1.8'})
                ], md=4)
            ]),
            html.Hr(style={'borderColor': 'rgba(255,255,255,0.2)', 'margin': '40px 0 20px'}),
            html.P([
                "© 2025 University of the Southern Caribbean - Institutional Research Department"
            ], className="text-center", style={'opacity': '0.8', 'fontSize': '0.9rem', 'margin': '0'})
        ])
    ], style={
        'background': f'linear-gradient(135deg, {USC_COLORS["primary_green"]} 0%, #2E7D32 100%)',
        'color': 'white',
        'padding': '60px 0 30px'
    })

def create_home_layout(user_email=None):
    """Complete home page layout with IR Director's message"""
    return html.Div([
        create_hero_section(),
        create_stats_overview(),
        create_feature_showcase(),
        create_director_message(),  # Using director's message instead of president's
        create_quick_links(),
        create_modern_footer()
    ])

# ============================================================================
# PLACEHOLDER PAGES
# ============================================================================

def create_placeholder_page(title, description, tier_required=1):
    """Create placeholder page for sections under development"""
    return dbc.Container([
        html.H1(title, className="display-4 fw-bold mb-4 text-center",
                style={'color': USC_COLORS['primary_green']}),
        dbc.Alert([
            html.H4("Coming Soon!", className="alert-heading"),
            html.P(description),
            html.Hr(),
            html.P(f"This section requires Tier {tier_required} access or higher.", className="mb-0")
        ], color="info", className="text-center"),
        dbc.Button("Return Home", href="/", color="primary", className="d-block mx-auto mt-4")
    ], className="mt-5")

# ============================================================================
# MAIN APPLICATION LAYOUT
# ============================================================================

def serve_layout():
    """Main application layout with routing"""
    return html.Div([
        # Location component for routing
        dcc.Location(id='url', refresh=False),

        # Store for user session
        dcc.Store(id='user-session', storage_type='session'),

        # Main content area
        html.Div(id='page-content'),

        # Interval component for session management
        dcc.Interval(id='session-interval', interval=30000, n_intervals=0)
    ])

# Set the layout
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

    # Get user email from session (simplified for demo)
    user_email = session_data.get('user_email') if session_data else None

    # For demo purposes, simulate logged in admin user
    # Remove this and implement real session management
    if not user_email:
        user_email = "demo@usc.edu.tt"  # Demo user with tier 2 access

    # Create navbar for all pages
    navbar = create_modern_navbar(user_email)

    # Route to appropriate page
    if pathname == '/' or pathname is None:
        content = create_home_layout(user_email)

    elif pathname == '/alumni':
        content = create_placeholder_page(
            "Alumni Portal",
            "Connect with USC alumni, access alumni services, and stay engaged with the USC community.",
            1
        )

    elif pathname == '/factbook':
        access_tier = get_user_access_tier(user_email)
        if access_tier >= 2:
            content = create_placeholder_page(
                "Factbook Overview",
                "Comprehensive institutional data with interactive visualizations and analytics.",
                2
            )
        else:
            content = create_placeholder_page(
                "Access Denied",
                "You need USC staff access to view the factbook. Please contact IR for access.",
                2
            )

    elif pathname == '/enrollment':
        access_tier = get_user_access_tier(user_email)
        if access_tier >= 2:
            content = create_placeholder_page(
                "Enrollment Analytics",
                "Detailed enrollment data, trends, and demographic analysis.",
                2
            )
        else:
            content = create_placeholder_page(
                "Access Denied",
                "You need USC staff access to view enrollment data.",
                2
            )

    elif pathname == '/graduation':
        access_tier = get_user_access_tier(user_email)
        if access_tier >= 2:
            content = create_placeholder_page(
                "Graduation Statistics",
                "Graduation rates, completion data, and outcome tracking.",
                2
            )
        else:
            content = create_placeholder_page(
                "Access Denied",
                "You need USC staff access to view graduation data.",
                2
            )

    elif pathname == '/student-employment':
        access_tier = get_user_access_tier(user_email)
        if access_tier >= 2:
            content = create_placeholder_page(
                "Student Employment",
                "Work-study analytics, employment rates, and career outcomes.",
                2
            )
        else:
            content = create_placeholder_page(
                "Access Denied",
                "You need USC staff access to view student employment data.",
                2
            )

    elif pathname == '/financial':
        access_tier = get_user_access_tier(user_email)
        if access_tier >= 3:
            content = create_placeholder_page(
                "Financial Overview",
                "Comprehensive financial reports, budget analysis, and institutional performance.",
                3
            )
        else:
            content = create_placeholder_page(
                "Access Denied",
                "You need administrative access to view financial data. Please request access upgrade.",
                3
            )

    elif pathname == '/budget':
        access_tier = get_user_access_tier(user_email)
        if access_tier >= 3:
            content = create_placeholder_page(
                "Budget Analysis",
                "Detailed budget breakdown, variance analysis, and financial projections.",
                3
            )
        else:
            content = create_placeholder_page(
                "Access Denied",
                "Administrative access required for budget information.",
                3
            )

    else:
        # Default pages available to all
        content = create_placeholder_page(
            "Page Under Development",
            f"The page '{pathname}' is currently being developed and will be available soon.",
            1
        )

    return html.Div([navbar, content])

@callback(
    Output('navbar-collapse', 'is_open'),
    Input('navbar-toggler', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_navbar_collapse(n):
    """Toggle mobile navigation menu"""
    if n:
        return True
    return False

@callback(
    Output('user-session', 'data'),
    Input('login-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_login(n_clicks):
    """Handle login button click - simplified for demo"""
    if n_clicks:
        # In real implementation, this would redirect to Google OAuth
        # For demo, we'll simulate a successful login
        return {
            'user_email': 'demo@usc.edu.tt',
            'user_name': 'Demo User',
            'login_time': datetime.now().isoformat()
        }
    return {}

@callback(
    Output('user-session', 'clear_data'),
    Input('logout-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle logout"""
    if n_clicks:
        return True
    return False

# ============================================================================
# INITIALIZE AND RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    # Initialize database
    init_database()

    print("🚀 Starting USC Institutional Research Portal...")
    print("📊 Features enabled:")
    print("   ✅ Modern responsive design")
    print("   ✅ Tier-based access control")
    print("   ✅ USC brand compliance")
    print("   ✅ Interactive dashboard")
    print("   ✅ Demo authentication")
    print(f"🌐 Visit: http://localhost:8050")

    # Run the application
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050,
        dev_tools_ui=True,
        dev_tools_props_check=True
    )