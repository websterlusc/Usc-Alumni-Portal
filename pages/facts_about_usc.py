"""
USC Institutional Research Portal - Facts About USC Pages
All public information about the university
"""

from dash import html
import dash_bootstrap_components as dbc
from components.navbar import create_navbar, USC_COLORS

def create_about_usc_page():
    """Create About USC page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            # Header
            html.Div([
                html.H1("About USC", className="display-4 fw-bold mb-4",
                        style={'color': USC_COLORS['primary_green']}),
                html.P(
                    "The University of the Southern Caribbean - Excellence in Education Since 1927",
                    className="lead text-muted mb-5"
                )
            ], className="text-center mb-5"),

            # Overview section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Our Heritage", className="fw-bold mb-3",
                                    style={'color': USC_COLORS['primary_green']}),
                            html.P(
                                "Founded in 1927, the University of the Southern Caribbean has been a "
                                "beacon of academic excellence in the Caribbean region for nearly a century. "
                                "Our institution has grown from humble beginnings to become a leading center "
                                "of higher education."
                            )
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Our Mission", className="fw-bold mb-3",
                                    style={'color': USC_COLORS['primary_green']}),
                            html.P(
                                "To provide quality education in a Christian environment, fostering academic "
                                "excellence, spiritual growth, and service to humanity while preparing students "
                                "for meaningful careers and lifelong learning."
                            )
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),

            # Student portal card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.A([
                                html.I(className="fas fa-user-circle me-2"),
                                "USC Aerion Student Portal"
                            ], href="https://aerion.usc.edu.tt", target="_blank",
                               className="btn btn-outline-success w-100 mb-2")
                        ])
                    ])
                ], width=4)
            ], className="mb-5"),

            # Quick facts
            html.H3("USC at a Glance", className="fw-bold mb-4",
                    style={'color': USC_COLORS['primary_green']}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-calendar-alt fa-2x mb-3",
                               style={'color': USC_COLORS['secondary_green']}),
                        html.H4("Founded", className="fw-bold"),
                        html.P("1927")
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-users fa-2x mb-3",
                               style={'color': USC_COLORS['secondary_green']}),
                        html.H4("Students", className="fw-bold"),
                        html.P("3,100+")
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-graduation-cap fa-2x mb-3",
                               style={'color': USC_COLORS['secondary_green']}),
                        html.H4("Programs", className="fw-bold"),
                        html.P("50+ Degree Programs")
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-globe fa-2x mb-3",
                               style={'color': USC_COLORS['secondary_green']}),
                        html.H4("Countries", className="fw-bold"),
                        html.P("40+ Represented")
                    ], className="text-center")
                ], width=3)
            ], className="mb-5")
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})


def create_vision_mission_page():
    """Create Vision, Mission & Motto page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            # Header
            html.Div([
                html.H1("Vision, Mission & Motto", className="display-4 fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                html.P("Our guiding principles and aspirations", className="lead text-muted mb-5")
            ], className="text-center mb-5"),
            
            # Vision
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-eye fa-3x mb-4", style={'color': USC_COLORS['secondary_green']}),
                        html.H2("Our Vision", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                        html.P("To be a premier Seventh-day Adventist institution of higher learning in the Caribbean, known for academic excellence, spiritual vitality, and service to humanity.", 
                               className="lead", style={'fontSize': '1.3rem', 'lineHeight': '1.6'})
                    ], className="text-center")
                ])
            ], className="mb-5", style={'border': f'3px solid {USC_COLORS["primary_green"]}'}),
            
            # Mission
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-bullseye fa-3x mb-4", style={'color': USC_COLORS['accent_yellow']}),
                        html.H2("Our Mission", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                        html.P("The University of the Southern Caribbean exists to provide quality tertiary education in a distinctly Christian environment, preparing graduates for productive careers and responsible citizenship while fostering spiritual, intellectual, physical, and social development.", 
                               className="lead", style={'fontSize': '1.3rem', 'lineHeight': '1.6'})
                    ], className="text-center")
                ])
            ], className="mb-5", style={'border': f'3px solid {USC_COLORS["accent_yellow"]}'}),
            
            # Motto
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-star fa-3x mb-4", style={'color': USC_COLORS['primary_green']}),
                        html.H2("Our Motto", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                        html.H1("\"Beyond Excellence\"", 
                               className="display-3 fw-bold", 
                               style={'color': USC_COLORS['secondary_green'], 'fontStyle': 'italic'})
                    ], className="text-center")
                ])
            ], className="mb-5", style={'border': f'3px solid {USC_COLORS["secondary_green"]}'}),
            
            # Core values
            html.H3("Our Core Values", className="text-center fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-heart fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Integrity", className="fw-bold"),
                        html.P("Commitment to honesty, transparency, and ethical conduct in all endeavors.")
                    ], className="text-center")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-lightbulb fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Excellence", className="fw-bold"),
                        html.P("Pursuit of the highest standards in education, research, and service.")
                    ], className="text-center")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-hands-helping fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Service", className="fw-bold"),
                        html.P("Dedication to serving our community, nation, and the world.")
                    ], className="text-center")
                ], width=4)
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_governance_page():
    """Create Governance page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Governance Structure", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            # Board of Trustees
            dbc.Card([
                dbc.CardHeader([
                    html.H3("Board of Trustees", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                ]),
                dbc.CardBody([
                    html.P("The Board of Trustees serves as the governing body of USC, providing strategic oversight and ensuring the institution fulfills its mission and maintains its accreditation standards."),
                    html.P("The Board consists of representatives from the Seventh-day Adventist Church, community leaders, alumni, and academic professionals who guide the university's strategic direction.")
                ])
            ], className="mb-4"),
            
            # Administration
            dbc.Card([
                dbc.CardHeader([
                    html.H3("Senior Administration", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("Office of the President", className="fw-bold"),
                            html.P("Executive leadership and institutional governance, strategic planning, and external relations.")
                        ], width=6),
                        dbc.Col([
                            html.H5("Provost & Vice President for Academic Affairs", className="fw-bold"),
                            html.P("Academic programs, faculty development, and student academic success initiatives.")
                        ], width=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Vice President for Finance", className="fw-bold"),
                            html.P("Financial planning, budget management, and fiscal oversight of university operations.")
                        ], width=6),
                        dbc.Col([
                            html.H5("Vice President for Student Services", className="fw-bold"),
                            html.P("Student life, enrollment management, and comprehensive student support services.")
                        ], width=6)
                    ])
                ])
            ], className="mb-4")
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_usc_history_page():
    """Create USC History page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("USC History", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            # Timeline
            dbc.Card([
                dbc.CardBody([
                    html.H3("Our Journey Through Time", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                    dbc.Row([
                        dbc.Col([
                            html.H4("1927", className="fw-bold", style={'color': USC_COLORS['secondary_green']}),
                            html.P("Founded as Caribbean Training College by the Seventh-day Adventist Church to provide Christian education in the Caribbean region.")
                        ], width=3),
                        dbc.Col([
                            html.H4("1950s", className="fw-bold", style={'color': USC_COLORS['secondary_green']}),
                            html.P("Expanded academic programs and facilities, establishing a strong foundation for higher education in Trinidad and Tobago.")
                        ], width=3),
                        dbc.Col([
                            html.H4("1980s", className="fw-bold", style={'color': USC_COLORS['secondary_green']}),
                            html.P("Achieved university status and began offering degree programs, marking a significant milestone in institutional development.")
                        ], width=3),
                        dbc.Col([
                            html.H4("Today", className="fw-bold", style={'color': USC_COLORS['secondary_green']}),
                            html.P("Leading Caribbean institution serving 3,100+ students from over 40 countries with comprehensive academic and support services.")
                        ], width=3)
                    ])
                ])
            ], className="mb-5"),
            
            # Milestones
            html.H3("Key Milestones", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
            dbc.Card([
                dbc.CardBody([
                    html.Ul([
                        html.Li("1927: Founded as Caribbean Training College"),
                        html.Li("1950: First graduation ceremony held"),
                        html.Li("1980: Achieved university status"),
                        html.Li("1990: Launched first graduate programs"),
                        html.Li("2000: Established online learning platform"),
                        html.Li("2010: Opened new campus facilities"),
                        html.Li("2020: Launched USC eLearn distance education"),
                        html.Li("2025: Serving over 3,100 students globally")
                    ])
                ])
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_campus_info_page():
    """Create Campus Information page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Campus Information", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Main Campus", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                            html.P([
                                html.Strong("Location: "), "Maracas Valley, Trinidad", html.Br(),
                                html.Strong("Size: "), "400+ acres of beautiful campus grounds", html.Br(),
                                html.Strong("Facilities: "), "Academic buildings, student residences, recreational facilities, library, cafeteria", html.Br(),
                                html.Strong("Environment: "), "Peaceful, mountainous setting conducive to learning and spiritual growth"
                            ])
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Online Campus", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                            html.P([
                                html.Strong("Platform: "), "USC eLearn - Advanced learning management system", html.Br(),
                                html.Strong("Programs: "), "Full degree programs available online", html.Br(),
                                html.Strong("Support: "), "24/7 technical support and student services", html.Br(),
                                html.Strong("Reach: "), "Serving students across the Caribbean and beyond"
                            ])
                        ])
                    ])
                ], width=6)
            ], className="mb-5"),
            
            # Facilities
            html.H3("Campus Facilities", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-book fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Library & Learning Resources", className="fw-bold"),
                        html.P("Comprehensive library with digital and physical resources supporting all academic programs.")
                    ], className="text-center")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-flask fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Laboratories & Research", className="fw-bold"),
                        html.P("Modern science labs and research facilities supporting hands-on learning experiences.")
                    ], className="text-center")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-home fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Student Residences", className="fw-bold"),
                        html.P("Safe, comfortable on-campus housing with supportive residential life programs.")
                    ], className="text-center")
                ], width=4)
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_contact_page():
    """Contact information page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Contact Information", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Institutional Research Department", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.P([
                                html.Strong("Director: "), "Nordian C. Swaby Robinson", html.Br(),
                                html.Strong("Email: "), html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt", style={'color': USC_COLORS['secondary_green']}), html.Br(),
                                html.Strong("Phone: "), "868-645-3265 ext. 2150", html.Br(),
                                html.Strong("Office: "), "Administration Building", html.Br(),
                                html.Strong("Hours: "), "Monday - Friday, 8:00 AM - 5:00 PM"
                            ])
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("University Main Office", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.P([
                                html.Strong("Address: "), "Maracas Valley, Trinidad and Tobago", html.Br(),
                                html.Strong("Main Phone: "), "868-645-3265", html.Br(),
                                html.Strong("Fax: "), "868-645-3265", html.Br(),
                                html.Strong("Website: "), html.A("www.usc.edu.tt", href="https://www.usc.edu.tt", target="_blank", style={'color': USC_COLORS['secondary_green']}), html.Br(),
                                html.Strong("Email: "), html.A("info@usc.edu.tt", href="mailto:info@usc.edu.tt", style={'color': USC_COLORS['secondary_green']})
                            ])
                        ])
                    ])
                ], width=6)
            ], className="mb-5"),
            
            # Quick links
            html.H3("Quick Links", className="fw-bold mb-4 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.A([
                                html.I(className="fas fa-external-link-alt me-2"),
                                "USC Main Website"
                            ], href="https://www.usc.edu.tt", target="_blank", 
                            className="btn btn-outline-success w-100 mb-2")
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.A([
                                html.I(className="fas fa-graduation-cap me-2"),
                                "USC eLearn Platform"
                            ], href="https://elearn.usc.edu.tt", target="_blank", 
                            className="btn btn-outline-success w-100 mb-2")
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.A([
                                html.I(className="fas fa-user-circle me-2"),
                                "USC Aerion Student Portal"
                            ], href="https://aerion.usc.edu.tt", target="_blank",
                            className="btn btn-outline-success w-100 mb-2")
                        ])
                    ])
                ], width=4)
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})