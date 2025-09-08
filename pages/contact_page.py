"""
Contact Information Page - Separate Component
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

def create_contact_page():
    """Contact Information page"""
    return dbc.Container([
        html.H1("Contact Information", className="display-4 fw-bold mb-5 text-center", 
                style={'color': USC_COLORS['primary_green']}),
        
        # Main University Contact
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("University of the Southern Caribbean", style={'color': USC_COLORS['primary_green']}, className="mb-0"),
                        html.I(className="fas fa-university fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Main Campus Address", style={'color': USC_COLORS['secondary_green']}),
                                html.P([
                                    html.I(className="fas fa-map-marker-alt me-2", style={'color': USC_COLORS['primary_green']}),
                                    "Maracas Valley", html.Br(),
                                    "St. Joseph, Trinidad and Tobago", html.Br(),
                                    "West Indies"
                                ], style={'fontSize': '1.1rem', 'lineHeight': '1.8'}),
                                
                                html.H5("Contact Details", style={'color': USC_COLORS['secondary_green'], 'marginTop': '2rem'}),
                                html.P([
                                    html.I(className="fas fa-phone me-2", style={'color': USC_COLORS['primary_green']}),
                                    html.Strong("Phone: "), "868-645-3265", html.Br(),
                                    html.I(className="fas fa-fax me-2", style={'color': USC_COLORS['primary_green']}),
                                    html.Strong("Fax: "), "868-645-3265", html.Br(),
                                    html.I(className="fas fa-envelope me-2", style={'color': USC_COLORS['primary_green']}),
                                    html.Strong("Email: "), html.A("info@usc.edu.tt", href="mailto:info@usc.edu.tt", 
                                                                   style={'color': USC_COLORS['accent_yellow']})
                                ], style={'fontSize': '1.1rem', 'lineHeight': '1.8'})
                            ], md=6),
                            dbc.Col([
                                html.H5("Campus Hours", style={'color': USC_COLORS['secondary_green']}),
                                html.P([
                                    html.I(className="fas fa-clock me-2", style={'color': USC_COLORS['primary_green']}),
                                    html.Strong("Monday - Thursday: "), "7:00 AM - 10:00 PM", html.Br(),
                                    html.Strong("Friday: "), "7:00 AM - 3:00 PM", html.Br(),
                                    html.Strong("Saturday: "), "Closed", html.Br(),
                                    html.Strong("Sunday: "), "Worship Services Only"
                                ], style={'fontSize': '1.1rem', 'lineHeight': '1.8'}),
                                
                                html.H5("Quick Links", style={'color': USC_COLORS['secondary_green'], 'marginTop': '2rem'}),
                                html.P([
                                    html.A([html.I(className="fas fa-globe me-2"), "USC Website"], 
                                           href="https://www.usc.edu.tt", target="_blank", 
                                           style={'color': USC_COLORS['accent_yellow'], 'textDecoration': 'none'}), html.Br(),
                                    html.A([html.I(className="fas fa-laptop me-2"), "USC eLearn"], 
                                           href="https://elearn.usc.edu.tt", target="_blank", 
                                           style={'color': USC_COLORS['accent_yellow'], 'textDecoration': 'none'}), html.Br(),
                                    html.A([html.I(className="fas fa-door-open me-2"), "Aerion Portal"], 
                                           href="https://aerion.usc.edu.tt", target="_blank", 
                                           style={'color': USC_COLORS['accent_yellow'], 'textDecoration': 'none'})
                                ], style={'fontSize': '1.1rem', 'lineHeight': '1.8'})
                            ], md=6)
                        ])
                    ])
                ], className="mb-4", style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ]),
        
        # Institutional Research Department
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("Institutional Research Department", style={'color': USC_COLORS['primary_green']}, className="mb-0"),
                        html.I(className="fas fa-chart-bar fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Director Information", style={'color': USC_COLORS['secondary_green']}),
                                html.P([
                                    html.I(className="fas fa-user me-2", style={'color': USC_COLORS['primary_green']}),
                                    html.Strong("Director: "), "Nordian C. Swaby Robinson", html.Br(),
                                    html.I(className="fas fa-envelope me-2", style={'color': USC_COLORS['primary_green']}),
                                    html.Strong("Email: "), html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt", 
                                                                   style={'color': USC_COLORS['accent_yellow']}), html.Br(),
                                    html.I(className="fas fa-phone me-2", style={'color': USC_COLORS['primary_green']}),
                                    html.Strong("Phone: "), "868-645-3265 ext. 2150", html.Br(),
                                    html.I(className="fas fa-map-marker-alt me-2", style={'color': USC_COLORS['primary_green']}),
                                    html.Strong("Office: "), "Administration Building, Room 201"
                                ], style={'fontSize': '1.1rem', 'lineHeight': '1.8'})
                            ], md=6),
                            dbc.Col([
                                html.H5("Office Hours", style={'color': USC_COLORS['secondary_green']}),
                                html.P([
                                    html.I(className="fas fa-clock me-2", style={'color': USC_COLORS['primary_green']}),
                                    html.Strong("Monday - Friday: "), "8:00 AM - 4:30 PM"
                                ], style={'fontSize': '1.1rem', 'lineHeight': '1.8'}),
                                
                                html.H5("Services Offered", style={'color': USC_COLORS['secondary_green'], 'marginTop': '2rem'}),
                                html.Ul([
                                    html.Li("Institutional data analysis and reporting"),
                                    html.Li("Custom research requests"),
                                    html.Li("Compliance and accreditation support"),
                                    html.Li("Strategic planning assistance")
                                ], style={'fontSize': '1rem', 'lineHeight': '1.6'})
                            ], md=6)
                        ])
                    ])
                ], className="mb-4", style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ]),
        
        # Key Departments
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("Key Departments", style={'color': USC_COLORS['primary_green']}, className="mb-0"),
                        html.I(className="fas fa-building fa-2x", style={'color': USC_COLORS['accent_yellow'], 'float': 'right'})
                    ], style={'background': USC_COLORS['light_gray']}),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Admissions Office", style={'color': USC_COLORS['secondary_green']}),
                                        html.P([
                                            html.I(className="fas fa-envelope me-2", style={'color': USC_COLORS['primary_green']}),
                                            html.A("admissions@usc.edu.tt", href="mailto:admissions@usc.edu.tt", 
                                                   style={'color': USC_COLORS['accent_yellow']}), html.Br(),
                                            html.I(className="fas fa-phone me-2", style={'color': USC_COLORS['primary_green']}),
                                            "868-645-3265 ext. 2200"
                                        ])
                                    ])
                                ], style={'background': '#f0f8f0', 'border': f'1px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3"),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Student Services", style={'color': USC_COLORS['secondary_green']}),
                                        html.P([
                                            html.I(className="fas fa-envelope me-2", style={'color': USC_COLORS['primary_green']}),
                                            html.A("studentservices@usc.edu.tt", href="mailto:studentservices@usc.edu.tt", 
                                                   style={'color': USC_COLORS['accent_yellow']}), html.Br(),
                                            html.I(className="fas fa-phone me-2", style={'color': USC_COLORS['primary_green']}),
                                            "868-645-3265 ext. 2300"
                                        ])
                                    ])
                                ], style={'background': '#f0f8f0', 'border': f'1px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3")
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Financial Aid", style={'color': USC_COLORS['secondary_green']}),
                                        html.P([
                                            html.I(className="fas fa-envelope me-2", style={'color': USC_COLORS['primary_green']}),
                                            html.A("financialaid@usc.edu.tt", href="mailto:financialaid@usc.edu.tt", 
                                                   style={'color': USC_COLORS['accent_yellow']}), html.Br(),
                                            html.I(className="fas fa-phone me-2", style={'color': USC_COLORS['primary_green']}),
                                            "868-645-3265 ext. 2400"
                                        ])
                                    ])
                                ], style={'background': '#f0f8f0', 'border': f'1px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3"),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Academic Affairs", style={'color': USC_COLORS['secondary_green']}),
                                        html.P([
                                            html.I(className="fas fa-envelope me-2", style={'color': USC_COLORS['primary_green']}),
                                            html.A("academics@usc.edu.tt", href="mailto:academics@usc.edu.tt", 
                                                   style={'color': USC_COLORS['accent_yellow']}), html.Br(),
                                            html.I(className="fas fa-phone me-2", style={'color': USC_COLORS['primary_green']}),
                                            "868-645-3265 ext. 2100"
                                        ])
                                    ])
                                ], style={'background': '#f0f8f0', 'border': f'1px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3")
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Library Services", style={'color': USC_COLORS['secondary_green']}),
                                        html.P([
                                            html.I(className="fas fa-envelope me-2", style={'color': USC_COLORS['primary_green']}),
                                            html.A("library@usc.edu.tt", href="mailto:library@usc.edu.tt", 
                                                   style={'color': USC_COLORS['accent_yellow']}), html.Br(),
                                            html.I(className="fas fa-phone me-2", style={'color': USC_COLORS['primary_green']}),
                                            "868-645-3265 ext. 2500"
                                        ])
                                    ])
                                ], style={'background': '#f0f8f0', 'border': f'1px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3"),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("IT Support", style={'color': USC_COLORS['secondary_green']}),
                                        html.P([
                                            html.I(className="fas fa-envelope me-2", style={'color': USC_COLORS['primary_green']}),
                                            html.A("itsupport@usc.edu.tt", href="mailto:itsupport@usc.edu.tt", 
                                                   style={'color': USC_COLORS['accent_yellow']}), html.Br(),
                                            html.I(className="fas fa-phone me-2", style={'color': USC_COLORS['primary_green']}),
                                            "868-645-3265 ext. 2600"
                                        ])
                                    ])
                                ], style={'background': '#f0f8f0', 'border': f'1px solid {USC_COLORS["secondary_green"]}'})
                            ], md=6, className="mb-3")
                        ])
                    ])
                ], style={'boxShadow': '0 8px 25px rgba(0,0,0,0.15)', 'border': 'none'})
            ])
        ]),
        
        # Emergency Contact
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("Emergency Contact", style={'color': USC_COLORS['primary_green']}, className="mb-0"),
                        html.I(className="fas fa-exclamation-triangle fa-2x", style={'color': 'red', 'float': 'right'})
                    ], style={'background': '#ffe6e6'}),
                    dbc.CardBody([
                        html.P([
                            html.Strong("Campus Security: "), "868-645-3265 ext. 911", html.Br(),
                            html.Strong("Medical Emergency: "), "999 (National Emergency)", html.Br(),
                            html.Strong("Fire Emergency: "), "990", html.Br(),
                            html.Strong("Police Emergency: "), "999"
                        ], style={'fontSize': '1.1rem', 'lineHeight': '1.8', 'color': 'red', 'fontWeight': 'bold'})
                    ])
                ], style={'border': '3px solid red'})
            ])
        ], className="mt-4")
    ], className="my-5")

                