# usc_footer_final.py
"""
USC Footer Component - Final Version Matching Exact Layout
- Four columns: USC Info | Address | Quick Links | Follow Us
- Address section with contact information
- Circular social media icons
- "JOIN OUR CHANNEL" button
- Roberto font typography
"""

import dash_bootstrap_components as dbc
from dash import html


def create_usc_footer():
    """Create complete USC footer matching the exact layout with address section"""

    # USC Quick Links organized in single column
    quick_links = [
        {'name': 'About USC', 'url': 'https://usc.edu.tt/about-us/we-are-usc/'},
        {'name': 'Contact us', 'url': 'https://usc.edu.tt/about-us/contact-us/'},
        {'name': 'Forde Library', 'url': 'https://library.usc.edu.tt'},
        {'name': 'University Calendars', 'url': 'https://calendar.usc.edu.tt'}
    ]

    return html.Footer([
        # Main Footer Section
        html.Div([
            dbc.Container([
                dbc.Row([
                    # Column 1 - USC Brand Image and Mission
                    dbc.Col([
                        html.Div([
                            # USC Brand Image instead of text
                            html.Img(
                                src="/assets/usc_footer_brand.png",
                                alt="University of the Southern Caribbean",
                                style={
                                    'maxWidth': '100%',
                                    'height': 'auto',
                                    'marginBottom': '0.8rem'
                                }
                            ),
                            html.P([
                                "The University of the Southern Caribbean offers holistic ",
                                "education, preparing students for service to God and ",
                                "humanity."
                            ], style={
                                'color': 'white',
                                'fontSize': '0.8rem',
                                'lineHeight': '1.3',
                                'opacity': '0.9',
                                'marginBottom': '0',
                                'fontFamily': '"Roberto", sans-serif'
                            })
                        ])
                    ], md=3, style={
                        'paddingRight': '1rem',
                        'position': 'relative'
                    }),

                    # Yellow Divider 1
                    html.Div(style={
                        'position': 'absolute',
                        'left': '25%',
                        'top': '20px',
                        'bottom': '20px',
                        'width': '2px',
                        'backgroundColor': '#FCCA18',
                        'zIndex': '1'
                    }),

                    # Yellow Divider 1
                    html.Div(style={
                        'position': 'absolute',
                        'left': '25%',
                        'top': '20px',
                        'bottom': '20px',
                        'width': '2px',
                        'backgroundColor': '#FCCA18',
                        'zIndex': '1'
                    }),

                    # Column 2 - Address Information
                    dbc.Col([
                        html.H5("Address", style={
                            'color': 'white',
                            'fontWeight': '600',
                            'marginBottom': '1.2rem',
                            'fontSize': '1.2rem',  # Larger header
                            'fontFamily': '"Roberto", sans-serif'
                        }),

                        html.Div([
                            html.P([
                                "Maracas Royal Road,", html.Br(),
                                "St. Joseph, Trinidad.", html.Br(),
                                "Tel: +1 868-662-2241", html.Br(),
                                "E-Mail: info@usc.edu.tt"
                            ], style={
                                'color': 'white',
                                'fontSize': '0.8rem',
                                'lineHeight': '1.4',
                                'opacity': '0.9',
                                'marginBottom': '0',
                                'fontFamily': '"Roberto", sans-serif'
                            })
                        ])
                    ], md=3, style={
                        'paddingLeft': '2rem',
                        'paddingRight': '1rem',
                        'position': 'relative'
                    }),

                    # Column 3 - Quick Links
                    dbc.Col([
                        html.H5("Quick Links", style={
                            'color': 'white',
                            'fontWeight': '600',
                            'marginBottom': '0.2rem',
                            'fontSize': '1.2rem',  # Larger header
                            'fontFamily': '"Roberto", sans-serif'
                        }),

                        html.Ul([
                            html.Li(
                                html.A(
                                    link['name'],
                                    href=link['url'],
                                    target="_blank",
                                    style={
                                        'color': 'white',
                                        'textDecoration': 'none',
                                        'fontSize': '0.8rem',
                                        'opacity': '0.9',
                                        'fontFamily': '"Roberto", sans-serif'
                                    },
                                    className="footer-link"
                                ),
                                style={'marginBottom': '0.0rem'}  # Reduced spacing
                            ) for link in quick_links
                        ], style={
                            'listStyle': 'none',
                            'padding': '0',
                            'margin': '0'
                        })
                    ], md=3, style={
                        'paddingLeft': '1rem',
                        'paddingRight': '1rem',
                        'position': 'relative'
                    }),

                    # Yellow Divider 2 (between Quick Links and Follow Us)
                    html.Div(style={
                        'position': 'absolute',
                        'left': '75%',
                        'top': '20px',
                        'bottom': '20px',
                        'width': '2px',
                        'backgroundColor': '#FCCA18',
                        'zIndex': '1'
                    }),

                    # Column 4 - Follow Us
                    dbc.Col([
                        html.H5("Follow Us", style={
                            'color': 'white',
                            'fontWeight': '600',
                            'marginBottom': '1.2rem',
                            'fontSize': '1.2rem',  # Larger header
                            'fontFamily': '"Roberto", sans-serif'
                        }),

                        # WhatsApp Channel Button
                        html.Div([
                            dbc.Button([
                                "JOIN OUR CHANNEL ",
                                html.I(className="fa-solid fa-angles-right", style={'fontSize': '0.7rem'})
                            ],
                                href="https://whatsapp.com/channel/0029VbBJ9Bs1CYoRXBGZzn1y",
                                target="_blank",
                                style={
                                    'backgroundColor': '#FCCA18',  # USC Yellow
                                    'borderColor': '#FCCA18',
                                    'color': '#2E2E2E',
                                    'fontWeight': '600',
                                    'fontSize': '0.7rem',
                                    'padding': '0.4rem 0.8rem',
                                    'marginBottom': '1.2rem',
                                    'fontFamily': '"Roberto", sans-serif',
                                    'border': 'none'
                                })
                        ]),

                        # Social Media Icons with Hollow Circles
                        html.Div([
                            html.A([
                                html.I(className="fab fa-facebook-f")
                            ],
                                href="https://www.facebook.com/usctt/",
                                target="_blank",
                                style={
                                    'display': 'inline-flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'width': '40px',
                                    'height': '40px',
                                    'backgroundColor': 'transparent',  # Transparent background
                                    'color': 'white',  # White icon color
                                    'borderRadius': '50%',
                                    'textDecoration': 'none',
                                    'marginRight': '0.6rem',
                                    'fontSize': '1rem',
                                    'transition': 'all 0.3s ease',
                                    'border': '2px solid white'  # White circle border
                                },
                                className="social-icon-circle"),

                            html.A([
                                html.I(className="fab fa-tiktok")
                            ],
                                href="https://www.tiktok.com/@usccaribbean",
                                target="_blank",
                                style={
                                    'display': 'inline-flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'width': '40px',
                                    'height': '40px',
                                    'backgroundColor': 'transparent',  # Transparent background
                                    'color': 'white',  # White icon color
                                    'borderRadius': '50%',
                                    'textDecoration': 'none',
                                    'marginRight': '0.6rem',
                                    'fontSize': '1rem',
                                    'transition': 'all 0.3s ease',
                                    'border': '2px solid white'  # White circle border
                                },
                                className="social-icon-circle"),

                            html.A([
                                html.I(className="fab fa-youtube")
                            ],
                                href="https://www.youtube.com/c/universityofthesoutherncaribbean",
                                target="_blank",
                                style={
                                    'display': 'inline-flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'width': '40px',
                                    'height': '40px',
                                    'backgroundColor': 'transparent',  # Transparent background
                                    'color': 'white',  # White icon color
                                    'borderRadius': '50%',
                                    'textDecoration': 'none',
                                    'marginRight': '0.6rem',
                                    'fontSize': '1rem',
                                    'transition': 'all 0.3s ease',
                                    'border': '2px solid white'  # White circle border
                                },
                                className="social-icon-circle"),

                            html.A([
                                html.I(className="fab fa-instagram")
                            ],
                                href="https://www.instagram.com/usctt/",
                                target="_blank",
                                style={
                                    'display': 'inline-flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'width': '40px',
                                    'height': '40px',
                                    'backgroundColor': 'transparent',  # Transparent background
                                    'color': 'white',  # White icon color
                                    'borderRadius': '50%',
                                    'textDecoration': 'none',
                                    'marginRight': '0.6rem',
                                    'fontSize': '1rem',
                                    'transition': 'all 0.3s ease',
                                    'border': '2px solid white'  # White circle border
                                },
                                className="social-icon-circle"),

                            html.A([
                                html.I(className="fab fa-linkedin-in")
                            ],
                                href="https://www.linkedin.com/school/usctt/",
                                target="_blank",
                                style={
                                    'display': 'inline-flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'width': '40px',
                                    'height': '40px',
                                    'backgroundColor': 'transparent',  # Transparent background
                                    'color': 'white',  # White icon color
                                    'borderRadius': '50%',
                                    'textDecoration': 'none',
                                    'fontSize': '1rem',
                                    'transition': 'all 0.3s ease',
                                    'border': '2px solid white'  # White circle border
                                },
                                className="social-icon-circle")
                        ], style={'marginBottom': '0'})

                    ], md=3, style={'paddingLeft': '2rem'})

                ], align="start", className="g-0", style={'position': 'relative'})
            ], fluid=True, style={'maxWidth': '1200px'})
        ], style={
            'backgroundColor': '#4A4A4A',  # Dark gray background like USC site
            'padding': '2.5rem 0 2rem 0',
            'position': 'relative'
        }),

        # Bottom Copyright Section
        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        # Left side - Links
                        html.Div([
                            html.A("USC Sitemap",
                                   href="/sitemap",
                                   style={'color': 'white', 'textDecoration': 'none', 'fontSize': '0.75rem',
                                          'fontFamily': '"Roberto", sans-serif'},
                                   className="footer-bottom-link"),
                            html.Span(" | ", style={'color': 'white', 'margin': '0 0.5rem', 'fontSize': '0.75rem'}),
                            html.A("Site Use and Privacy",
                                   href="/privacy",
                                   style={'color': 'white', 'textDecoration': 'none', 'fontSize': '0.75rem',
                                          'fontFamily': '"Roberto", sans-serif'},
                                   className="footer-bottom-link"),
                            html.Span(" | ", style={'color': 'white', 'margin': '0 0.5rem', 'fontSize': '0.75rem'}),
                            html.A("Feedback",
                                   href="/feedback",
                                   style={'color': 'white', 'textDecoration': 'none', 'fontSize': '0.75rem',
                                          'fontFamily': '"Roberto", sans-serif'},
                                   className="footer-bottom-link")
                        ], style={'textAlign': 'center', 'marginBottom': '0.8rem'})
                    ], width=12),
                    dbc.Col([
                        # Copyright text
                        html.Div([
                            html.P([
                                "Copyright © 2025 University of the Southern Caribbean."
                            ], style={
                                'color': 'white',
                                'fontSize': '0.75rem',
                                'marginBottom': '0.3rem',
                                'textAlign': 'center',
                                'fontFamily': '"Roberto", sans-serif'
                            }),
                            html.P([
                                "A Seventh-day Adventist institution of higher education. All rights reserved."
                            ], style={
                                'color': 'white',
                                'fontSize': '0.75rem',
                                'marginBottom': '0',
                                'textAlign': 'center',
                                'fontFamily': '"Roberto", sans-serif'
                            })
                        ])
                    ], width=12)
                ])
            ], fluid=True)
        ], style={
            'backgroundColor': '#1A1A1A',  # Almost black background
            'padding': '1.5rem 0',
            'borderTop': '1px solid #333'
        })
    ])


def get_complete_footer_styles():
    """Return CSS styles for the complete footer component"""
    return """
    /* Footer Link Hover Effects */
    .footer-link:hover {
        color: #FCCA18 !important;
        opacity: 1 !important;
        transition: all 0.3s ease;
    }

    /* Bottom Footer Link Hover Effects */
    .footer-bottom-link:hover {
        color: #FCCA18 !important;
        text-decoration: underline !important;
        transition: all 0.3s ease;
    }

    /* Circular Social Icon Hover Effects */
    .social-icon-circle:hover {
        background-color: #FCCA18 !important;
        border-color: #FCCA18 !important;
        color: #2E2E2E !important;
        transform: translateY(-2px);
    }

    /* Newsletter Button Hover */
    .btn-warning:hover {
        background-color: #E6B515 !important;
        border-color: #E6B515 !important;
        transform: translateY(-1px);
    }

    /* Responsive adjustments for dividers */
    @media (max-width: 768px) {
        .footer-main > div > div > div[style*="position: absolute"] {
            display: none !important;
        }
    }
    """