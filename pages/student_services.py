"""
USC Institutional Research Portal - Student Services Pages
Public information about student services and academic programs
"""

from dash import html
import dash_bootstrap_components as dbc
from components.navbar import create_navbar, USC_COLORS

def create_admissions_page():
    """Admissions information page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Admissions", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            # Admission requirements
            dbc.Card([
                dbc.CardHeader([
                    html.H3("Admission Requirements", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("Undergraduate Admission", className="fw-bold mb-3"),
                            html.Ul([
                                html.Li("Completed secondary education (CXC/CAPE/High School Diploma)"),
                                html.Li("Official transcripts from all previous institutions"),
                                html.Li("Letters of recommendation"),
                                html.Li("Personal statement"),
                                html.Li("English proficiency (for non-native speakers)")
                            ])
                        ], width=6),
                        dbc.Col([
                            html.H5("Graduate Admission", className="fw-bold mb-3"),
                            html.Ul([
                                html.Li("Bachelor's degree from accredited institution"),
                                html.Li("Minimum GPA requirements (varies by program)"),
                                html.Li("Graduate Record Examination (GRE) scores"),
                                html.Li("Professional experience (program dependent)"),
                                html.Li("Research proposal (for research programs)")
                            ])
                        ], width=6)
                    ])
                ])
            ], className="mb-5"),
            
            # Application process
            html.H3("Application Process", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-file-alt fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                                html.H5("1. Submit Application", className="fw-bold"),
                                html.P("Complete the online application form with all required information and documents.")
                            ], className="text-center")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-search fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                                html.H5("2. Review Process", className="fw-bold"),
                                html.P("Admissions committee reviews application materials and academic credentials.")
                            ], className="text-center")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-comments fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                                html.H5("3. Interview", className="fw-bold"),
                                html.P("Selected candidates may be invited for an interview (program dependent).")
                            ], className="text-center")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-check-circle fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                                html.H5("4. Decision", className="fw-bold"),
                                html.P("Receive admission decision and enrollment instructions via email.")
                            ], className="text-center")
                        ])
                    ])
                ], width=3)
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_programs_page():
    """Academic programs page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Academic Programs", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            # Schools and departments
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("School of Education and Humanities", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.Ul([
                                html.Li("Bachelor of Arts in English"),
                                html.Li("Bachelor of Arts in History"),
                                html.Li("Bachelor of Science in Elementary Education"),
                                html.Li("Bachelor of Science in Secondary Education"),
                                html.Li("Master of Arts in Teaching"),
                                html.Li("Master of Education in Curriculum and Instruction")
                            ])
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("School of Sciences and Technology", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.Ul([
                                html.Li("Bachelor of Science in Biology"),
                                html.Li("Bachelor of Science in Chemistry"),
                                html.Li("Bachelor of Science in Mathematics"),
                                html.Li("Bachelor of Science in Computer Science"),
                                html.Li("Associate in Computer Information Systems"),
                                html.Li("Certificate in Information Technology")
                            ])
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("School of Business", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.Ul([
                                html.Li("Bachelor of Science in Accounting"),
                                html.Li("Bachelor of Science in Business Administration"),
                                html.Li("Bachelor of Science in Management"),
                                html.Li("Master of Business Administration (MBA)"),
                                html.Li("Associate in Business Administration"),
                                html.Li("Certificate in Entrepreneurship")
                            ])
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("School of Social Sciences", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.Ul([
                                html.Li("Bachelor of Science in Psychology"),
                                html.Li("Bachelor of Science in Social Work"),
                                html.Li("Bachelor of Arts in Religion"),
                                html.Li("Master of Arts in Counseling Psychology"),
                                html.Li("Certificate in Family Life Education"),
                                html.Li("Certificate in Substance Abuse Counseling")
                            ])
                        ])
                    ])
                ], width=6)
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_calendar_page():
    """Academic calendar page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Academic Calendar", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            # Current academic year
            dbc.Card([
                dbc.CardHeader([
                    html.H3("Academic Year 2024-2025", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("Fall Semester 2024", className="fw-bold mb-3"),
                            html.P([
                                html.Strong("Classes Begin: "), "August 26, 2024", html.Br(),
                                html.Strong("Mid-term Exams: "), "October 14-18, 2024", html.Br(),
                                html.Strong("Final Exams: "), "December 9-13, 2024", html.Br(),
                                html.Strong("Semester Ends: "), "December 13, 2024"
                            ])
                        ], width=6),
                        dbc.Col([
                            html.H5("Spring Semester 2025", className="fw-bold mb-3"),
                            html.P([
                                html.Strong("Classes Begin: "), "January 13, 2025", html.Br(),
                                html.Strong("Mid-term Exams: "), "March 3-7, 2025", html.Br(),
                                html.Strong("Final Exams: "), "April 28 - May 2, 2025", html.Br(),
                                html.Strong("Commencement: "), "May 11, 2025"
                            ])
                        ], width=6)
                    ])
                ])
            ], className="mb-5"),
            
            # Important dates
            html.H3("Important Dates", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("Registration Periods", className="fw-bold mb-3"),
                            html.P([
                                html.Strong("Early Registration: "), "April 1-30, 2025", html.Br(),
                                html.Strong("Regular Registration: "), "July 1-August 15, 2025", html.Br(),
                                html.Strong("Late Registration: "), "August 16-30, 2025", html.Br(),
                                html.Strong("Add/Drop Period: "), "First week of classes"
                            ])
                        ], width=6),
                        dbc.Col([
                            html.H5("Payment Deadlines", className="fw-bold mb-3"),
                            html.P([
                                html.Strong("Full Payment Due: "), "First day of classes", html.Br(),
                                html.Strong("Payment Plan Option: "), "Available with approval", html.Br(),
                                html.Strong("Financial Aid: "), "Priority deadline March 1", html.Br(),
                                html.Strong("Late Payment Fee: "), "Applied after deadline"
                            ])
                        ], width=6)
                    ])
                ])
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_student_life_page():
    """Student life page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Student Life", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            # Campus life sections
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-home fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                                html.H4("Residence Life", className="fw-bold mb-3"),
                                html.P("Safe, comfortable on-campus housing with residential advisors and community-building programs.")
                            ], className="text-center")
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-users fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                                html.H4("Student Organizations", className="fw-bold mb-3"),
                                html.P("Over 20 student clubs and organizations including academic, cultural, and service groups.")
                            ], className="text-center")
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-running fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                                html.H4("Recreation & Sports", className="fw-bold mb-3"),
                                html.P("Intramural sports, fitness facilities, and outdoor recreation opportunities on our beautiful campus.")
                            ], className="text-center")
                        ])
                    ])
                ], width=4)
            ], className="mb-5"),
            
            # Student services
            html.H3("Student Services", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-utensils fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Dining Services", className="fw-bold"),
                        html.P("Cafeteria and meal plans available with healthy, diverse food options.")
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-bus fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Transportation", className="fw-bold"),
                        html.P("Campus shuttle services and transportation assistance for students.")
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-medkit fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Health Services", className="fw-bold"),
                        html.P("On-campus health clinic and wellness programs for student wellbeing.")
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-pray fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                        html.H5("Spiritual Life", className="fw-bold"),
                        html.P("Chapel services, prayer groups, and spiritual development opportunities.")
                    ], className="text-center")
                ], width=3)
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})

def create_student_support_page():
    """Student support services page"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Student Support Services", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            # Support services
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Academic Support", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.Ul([
                                html.Li("Academic advising and course planning"),
                                html.Li("Tutoring and study groups"),
                                html.Li("Writing center and academic skills workshops"),
                                html.Li("Library research assistance"),
                                html.Li("Disability support services"),
                                html.Li("Academic probation support")
                            ])
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Personal Support", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.Ul([
                                html.Li("Counseling and mental health services"),
                                html.Li("Career guidance and job placement"),
                                html.Li("Financial aid and scholarship assistance"),
                                html.Li("International student services"),
                                html.Li("Crisis intervention and support"),
                                html.Li("Wellness and health promotion programs")
                            ])
                        ])
                    ])
                ], width=6)
            ], className="mb-5"),
            
            # Contact information for services
            html.H3("Contact Support Services", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Student Success Center", className="fw-bold mb-3"),
                            html.P([
                                html.Strong("Phone: "), "868-645-3265 ext. 2200", html.Br(),
                                html.Strong("Email: "), "studentsuccess@usc.edu.tt", html.Br(),
                                html.Strong("Hours: "), "Monday-Friday, 8AM-5PM"
                            ])
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Counseling Services", className="fw-bold mb-3"),
                            html.P([
                                html.Strong("Phone: "), "868-645-3265 ext. 2300", html.Br(),
                                html.Strong("Email: "), "counseling@usc.edu.tt", html.Br(),
                                html.Strong("Hours: "), "Monday-Friday, 9AM-4PM"
                            ])
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Financial Aid Office", className="fw-bold mb-3"),
                            html.P([
                                html.Strong("Phone: "), "868-645-3265 ext. 2100", html.Br(),
                                html.Strong("Email: "), "financialaid@usc.edu.tt", html.Br(),
                                html.Strong("Hours: "), "Monday-Friday, 8AM-4PM"
                            ])
                        ])
                    ])
                ], width=4)
            ])
        ], fluid=True, className="px-4")
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})