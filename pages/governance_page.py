"""
Governance Structure Page - Separate Component
"""

import dash_bootstrap_components as dbc
from dash import html

# USC Brand Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA'
}

def create_governance_page():
    """Governance Structure page"""
    return dbc.Container([
        html.H1("Governance Structure", className="display-4 fw-bold mb-5 text-center", 
                style={'color': USC_COLORS['primary_green']}),
        
        # Board of Trustees Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("Board of Trustees", style={'color': USC_COLORS['primary_green']}, className="mb-0"),
                        html.I(className="fas fa-users-cog fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        html.P([
                            "The Board of Trustees serves as the governing body of the University of the Southern Caribbean. ",
                            "Comprised of distinguished leaders from various fields, the Board provides strategic oversight ",
                            "and ensures the university fulfills its mission and maintains its Christian identity."
                        ], className="lead"),
                        html.H5("Board Responsibilities:", style={'color': USC_COLORS['secondary_green'], 'marginTop': '2rem'}),
                        dbc.Row([
                            dbc.Col([
                                html.Ul([
                                    html.Li("Setting institutional policy and strategic direction"),
                                    html.Li("Approving budgets and major financial decisions")
                                ], style={'fontSize': '1.1rem'})
                            ], md=6),
                            dbc.Col([
                                html.Ul([
                                    html.Li("Selecting and evaluating the University President"),
                                    html.Li("Ensuring academic quality and institutional integrity")
                                ], style={'fontSize': '1.1rem'})
                            ], md=6)
                        ])
                    ])
                ], className="mb-4", style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ]),
        
        # University Administration Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("University Administration", style={'color': USC_COLORS['primary_green']}, className="mb-0"),
                        html.I(className="fas fa-building fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        # President Section
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Office of the President", style={'color': USC_COLORS['secondary_green']}),
                                html.P([
                                    html.Strong("Dr. Colwick M. Wilson"), " serves as the University President, providing executive leadership ",
                                    "and representing the institution to external stakeholders. The President's office oversees all ",
                                    "university operations and ensures alignment with the institutional mission and strategic goals."
                                ])
                            ])
                        ], className="mb-3", style={'background': '#f8f9fa'}),
                        
                        # Five Divisions
                        html.H4("Administrative Structure", style={'color': USC_COLORS['secondary_green'], 'marginTop': '2rem'}),
                        html.P("The university operates through five main divisions, each led by a senior administrator:"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("The Division of the Provost", style={'color': USC_COLORS['primary_green']}),
                                        html.P("Academic affairs, curriculum, faculty development", className="small")
                                    ])
                                ], style={'background': '#e8f5e8', 'border': f'2px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3"),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Division of Administration, Advancement & Planning", style={'color': USC_COLORS['primary_green']}),
                                        html.P("Strategic planning, institutional advancement, operations", className="small")
                                    ])
                                ], style={'background': '#e8f5e8', 'border': f'2px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3")
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Division of Financial Administration", style={'color': USC_COLORS['primary_green']}),
                                        html.P("Financial management, budgeting, accounting", className="small")
                                    ])
                                ], style={'background': '#e8f5e8', 'border': f'2px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3"),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Division of Student Services & Enrolment Management", style={'color': USC_COLORS['primary_green']}),
                                        html.P("Student life, enrollment, admissions, support services", className="small")
                                    ])
                                ], style={'background': '#e8f5e8', 'border': f'2px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3")
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Division of Spiritual Development", style={'color': USC_COLORS['primary_green']}),
                                        html.P("Campus ministry, spiritual life, community service", className="small")
                                    ])
                                ], style={'background': '#e8f5e8', 'border': f'2px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3")
                        ])
                    ])
                ], className="mb-4", style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ]),
        
        # Academic Governance Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("Academic Governance", style={'color': USC_COLORS['primary_green']}, className="mb-0"),
                        html.I(className="fas fa-graduation-cap fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        html.P([
                            "Academic governance at USC involves faculty participation in curriculum development, ",
                            "academic policy formation, and institutional planning through various committees and councils. ",
                            "This shared governance model ensures that academic decisions are made collaboratively."
                        ], className="lead"),
                        html.H5("Key Academic Governance Bodies:", style={'color': USC_COLORS['secondary_green'], 'marginTop': '2rem'}),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("Faculty Senate", style={'color': USC_COLORS['primary_green']}),
                                    html.P("Primary faculty governing body for academic matters", className="small mb-3"),
                                    html.H6("Academic Council", style={'color': USC_COLORS['primary_green']}),
                                    html.P("Administrative and faculty collaboration on policies", className="small")
                                ])
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.H6("Curriculum Committees", style={'color': USC_COLORS['primary_green']}),
                                    html.P("Program development and curriculum review", className="small mb-3"),
                                    html.H6("Graduate Council", style={'color': USC_COLORS['primary_green']}),
                                    html.P("Graduate program oversight and policy", className="small")
                                ])
                            ], md=6)
                        ])
                    ])
                ], style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ]),
        
        # Organizational Chart Section
        # Organizational Chart Section - UPDATED
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("Organizational Structure", style={'color': USC_COLORS['primary_green']},
                                className="mb-0"),
                        html.I(className="fas fa-sitemap fa-2x",
                               style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        html.Div([
                            html.P(
                                "USC's organizational structure provides clear lines of authority and accountability:",
                                className="text-center mb-4"),

                            # Your PNG organizational chart
                            html.Div([
                                html.Img(
                                    src="/assets/organisationalchart.png",
                                    style={
                                        'width': '100%',
                                        'height': 'auto',
                                        'maxWidth': '900px',
                                        'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
                                        'borderRadius': '8px'
                                    },
                                    className="img-fluid"
                                )
                            ], className="text-center")
                        ])
                    ])
                ], style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ])
    ], className="my-5")
