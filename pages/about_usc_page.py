"""
About USC Page - Separate Component
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

def create_about_usc_page():
    """About USC page"""
    return dbc.Container([
        html.H1("About USC", className="display-4 fw-bold mb-5 text-center", 
                style={'color': USC_COLORS['primary_green']}),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("Our History", style={'color': USC_COLORS['primary_green']}),
                        html.P([
                            "The University of the Southern Caribbean (USC) was established in 1927 as a beacon of ",
                            "higher education in the Caribbean region. For nearly a century, USC has been committed ",
                            "to academic excellence, spiritual development, and service to the community."
                        ]),
                        html.P([
                            "Located in beautiful Maracas Valley, Trinidad and Tobago, USC serves students from ",
                            "across the Caribbean and beyond, offering undergraduate and graduate programs that ",
                            "prepare students for leadership and service in their chosen fields."
                        ])
                    ])
                ], className="mb-4", style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("Our Campus", style={'color': USC_COLORS['primary_green']}),
                        html.P([
                            "Situated on 400 acres of lush tropical landscape, the USC campus provides an ideal ",
                            "environment for learning and personal growth. Our facilities include modern classrooms, ",
                            "state-of-the-art laboratories, a comprehensive library, and comfortable residence halls."
                        ]),
                        html.P([
                            "The campus also features recreational facilities, dining services, and beautiful ",
                            "outdoor spaces that foster community and wellness among our students, faculty, and staff."
                        ])
                    ])
                ], className="mb-4", style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
            ], md=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("Academic Excellence", style={'color': USC_COLORS['primary_green']}),
                        html.P([
                            "USC offers a wide range of undergraduate and graduate programs through our five academic divisions:"
                        ]),
                        html.Ul([
                            html.Li("School of Business and Entrepreneur"),
                            html.Li("School of Science, Technology and Allied Health"),
                            html.Li("School of Social Sciences"),
                            html.Li("School of Education and Humanities"),
                            html.Li("School of Theology and Religion")
                        ], style={'color': USC_COLORS['secondary_green'], 'fontWeight': '500'}),
                        html.P([
                            "Our programs are designed to integrate academic rigor with practical application, ",
                            "preparing students for successful careers and meaningful service."
                        ])
                    ])
                ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("Student Life", style={'color': USC_COLORS['primary_green']}),
                        html.P([
                            "At USC, student life extends far beyond the classroom. We offer a vibrant campus community ",
                            "with numerous opportunities for personal growth, leadership development, and spiritual enrichment."
                        ]),
                        html.P([
                            "Students can participate in:",
                            html.Ul([
                                html.Li("Student government and leadership roles"),
                                html.Li("Cultural and recreational activities"),
                                html.Li("Community service and outreach programs"),
                                html.Li("Spiritual development and worship services"),
                                html.Li("Athletic and fitness programs")
                            ])
                        ])
                    ])
                ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("Global Impact", style={'color': USC_COLORS['primary_green']}),
                        html.P([
                            "USC graduates serve in leadership positions throughout the Caribbean and around the world. ",
                            "Our alumni work in diverse fields including education, healthcare, business, ministry, ",
                            "and public service."
                        ]),
                        html.P([
                            "The university maintains partnerships with institutions globally, providing students with ",
                            "opportunities for international study, research collaboration, and cultural exchange."
                        ])
                    ])
                ], style={'boxShadow': '0 4px 15px rgba(0,0,0,0.1)', 'border': 'none'})
            ], md=6)
        ], className="mt-4")
    ], className="my-5")
