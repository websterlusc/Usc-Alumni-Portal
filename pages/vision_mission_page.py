"""
Vision, Mission & Motto Page - FIXED VERSION
Green motto box with Roboto typography for better legibility
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

def create_vision_mission_page():
    """Vision, Mission & Motto page with improved styling"""
    return dbc.Container([
        html.H1("Vision, Mission & Motto", className="display-4 fw-bold mb-5 text-center",
                style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),

        # Vision Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H2("Vision", style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}, className="mb-0"),
                        html.I(className="fas fa-eye fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        html.P([
                            "To be a premier institution of higher learning in the Caribbean region, recognized for ",
                            "academic excellence, innovative research, and the development of principled leaders ",
                            "who serve God and humanity."
                        ], className="lead", style={'fontSize': '1.3rem', 'lineHeight': '1.6', 'fontFamily': 'Roboto, sans-serif'})
                    ])
                ], className="mb-4", style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ]),

        # Mission Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H2("Mission", style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}, className="mb-0"),
                        html.I(className="fas fa-compass fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        html.P([
                            "The University of the Southern Caribbean exists to provide quality Christian higher education ",
                            "that develops the intellectual, spiritual, physical, and social dimensions of students, ",
                            "preparing them for productive careers and responsible citizenship in a diverse, global society."
                        ], className="lead", style={'fontSize': '1.2rem', 'lineHeight': '1.6', 'fontFamily': 'Roboto, sans-serif'}),
                        html.Hr(),
                        html.H4("We are committed to:", style={'color': USC_COLORS['secondary_green'], 'marginTop': '2rem', 'fontFamily': 'Roboto, sans-serif'}),
                        dbc.Row([
                            dbc.Col([
                                html.Ul([
                                    html.Li("Excellence in teaching, learning, and scholarship"),
                                    html.Li("Integration of faith and learning"),
                                    html.Li("Development of critical thinking and ethical reasoning")
                                ], style={'fontSize': '1.1rem', 'lineHeight': '1.8', 'fontFamily': 'Roboto, sans-serif'})
                            ], md=6),
                            dbc.Col([
                                html.Ul([
                                    html.Li("Service to the church and the broader community"),
                                    html.Li("Promotion of cultural diversity and global awareness"),
                                    html.Li("Holistic development of each student")
                                ], style={'fontSize': '1.1rem', 'lineHeight': '1.8', 'fontFamily': 'Roboto, sans-serif'})
                            ], md=6)
                        ])
                    ])
                ], className="mb-4", style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ]),

        # FIXED: Motto Section with GREEN background and improved typography
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H2("Motto", style={'color': USC_COLORS['white'], 'fontFamily': 'Roboto, sans-serif'}, className="mb-0"),
                        html.I(className="fas fa-star fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['primary_green']}),  # FIXED: Green background
                    dbc.CardBody([
                        html.Div([
                            html.H1("\"Beyond Excellence\"",
                                    className="text-center mb-4",
                                    style={
                                        'color': USC_COLORS['primary_green'],
                                        'fontSize': '4rem',
                                        'fontStyle': 'italic',
                                        'fontWeight': 'bold',
                                        'textShadow': '2px 2px 4px rgba(0,0,0,0.3)',
                                        'fontFamily': 'Roboto, sans-serif'  # ADDED: Roboto font
                                    }),
                            html.P([
                                "Our motto 'Beyond Excellence' represents our commitment to not just meeting standards, ",
                                "but exceeding them in all that we do. It embodies our pursuit of the highest quality ",
                                "in education, research, service, and personal development."
                            ], className="text-center lead", style={
                                'fontSize': '1.2rem',
                                'lineHeight': '1.7',
                                'fontFamily': 'Roboto, sans-serif',  # ADDED: Roboto font
                                'color': USC_COLORS['primary_green']  # ADDED: Better contrast
                            }),
                            html.Hr(),
                            html.P([
                                "This motto challenges every member of the USC community - students, faculty, staff, and ",
                                "alumni - to strive for excellence in their personal and professional endeavors, while ",
                                "always seeking to go beyond what is expected."
                            ], className="text-center", style={
                                'fontSize': '1.1rem',
                                'color': USC_COLORS['secondary_green'],
                                'fontFamily': 'Roboto, sans-serif'  # ADDED: Roboto font
                            })
                        ], style={'padding': '2rem', 'background': USC_COLORS['light_gray'], 'borderRadius': '8px'})  # ADDED: Light background for content
                    ])
                ], style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ]),

        # Core Values Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("Core Values", style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}, className="mb-0"),
                        html.I(className="fas fa-heart fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Integrity", style={'color': USC_COLORS['secondary_green'], 'fontFamily': 'Roboto, sans-serif'}),
                                html.P("Demonstrating honesty, transparency, and moral uprightness in all endeavors.", style={'fontFamily': 'Roboto, sans-serif'})
                            ], md=4),
                            dbc.Col([
                                html.H5("Excellence", style={'color': USC_COLORS['secondary_green'], 'fontFamily': 'Roboto, sans-serif'}),
                                html.P("Pursuing the highest standards in academic achievement and personal development.", style={'fontFamily': 'Roboto, sans-serif'})
                            ], md=4),
                            dbc.Col([
                                html.H5("Service", style={'color': USC_COLORS['secondary_green'], 'fontFamily': 'Roboto, sans-serif'}),
                                html.P("Serving God, community, and humanity with compassion and dedication.", style={'fontFamily': 'Roboto, sans-serif'})
                            ], md=4)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.H5("Diversity", style={'color': USC_COLORS['secondary_green'], 'fontFamily': 'Roboto, sans-serif'}),
                                html.P("Embracing and celebrating cultural, ethnic, and intellectual diversity.", style={'fontFamily': 'Roboto, sans-serif'})
                            ], md=4),
                            dbc.Col([
                                html.H5("Innovation", style={'color': USC_COLORS['secondary_green'], 'fontFamily': 'Roboto, sans-serif'}),
                                html.P("Encouraging creativity, critical thinking, and progressive solutions.", style={'fontFamily': 'Roboto, sans-serif'})
                            ], md=4),
                            dbc.Col([
                                html.H5("Stewardship", style={'color': USC_COLORS['secondary_green'], 'fontFamily': 'Roboto, sans-serif'}),
                                html.P("Responsible management of resources and environmental sustainability.", style={'fontFamily': 'Roboto, sans-serif'})
                            ], md=4)
                        ])
                    ])
                ], style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ], className="mt-4")
    ], className="my-5")