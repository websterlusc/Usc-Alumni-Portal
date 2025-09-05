"""
USC Institutional Research Portal - Request Reports Page
Form for requesting custom reports and analysis
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from components.navbar import create_navbar, create_footer, USC_COLORS

def create_request_reports_page(user=None):
    """Create request reports page with comprehensive form"""
    
    return html.Div([
        create_navbar(user),
        dbc.Container([
            # Header section
            html.Div([
                html.H1("Request Custom Reports", className="display-4 fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                html.P("Submit a request for custom data analysis, reports, or institutional research studies", 
                       className="lead text-muted mb-5")
            ], className="text-center mb-5"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3("Report Request Form", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            dbc.Form([
                                # Personal Information
                                html.H5("Contact Information", className="fw-bold mb-3", style={'color': USC_COLORS['secondary_green']}),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Full Name *", className="fw-bold"),
                                        dbc.Input(type="text", placeholder="Your full name", required=True, className="mb-3")
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Email Address *", className="fw-bold"),
                                        dbc.Input(type="email", placeholder="your.email@usc.edu.tt", required=True, className="mb-3")
                                    ], width=6)
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Department/Office *", className="fw-bold"),
                                        dbc.Input(type="text", placeholder="Your department or office", required=True, className="mb-3")
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Position/Title", className="fw-bold"),
                                        dbc.Input(type="text", placeholder="Your position or title", className="mb-3")
                                    ], width=6)
                                ]),
                                
                                html.Hr(className="my-4"),
                                
                                # Request Details
                                html.H5("Request Details", className="fw-bold mb-3", style={'color': USC_COLORS['secondary_green']}),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Report Type *", className="fw-bold"),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Enrollment Analysis", "value": "enrollment"},
                                                {"label": "Graduation & Retention Data", "value": "graduation"},
                                                {"label": "Financial Analysis", "value": "financial"},
                                                {"label": "HR & Faculty Analytics", "value": "hr"},
                                                {"label": "Student Performance", "value": "performance"},
                                                {"label": "Program Evaluation", "value": "program"},
                                                {"label": "Survey Analysis", "value": "survey"},
                                                {"label": "Comparative Study", "value": "comparative"},
                                                {"label": "Trend Analysis", "value": "trends"},
                                                {"label": "Custom Research", "value": "custom"}
                                            ],
                                            placeholder="Select the type of report you need",
                                            className="mb-3"
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Priority Level", className="fw-bold"),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Routine (4-6 weeks)", "value": "routine"},
                                                {"label": "Standard (2-3 weeks)", "value": "standard"},
                                                {"label": "Urgent (1-2 weeks)", "value": "urgent"},
                                                {"label": "Emergency (< 1 week)", "value": "emergency"}
                                            ],
                                            placeholder="Select priority level",
                                            value="standard",
                                            className="mb-3"
                                        )
                                    ], width=6)
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Time Period *", className="fw-bold"),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Current Academic Year (2024-2025)", "value": "current"},
                                                {"label": "Previous Academic Year (2023-2024)", "value": "previous"},
                                                {"label": "Last 3 Years", "value": "3years"},
                                                {"label": "Last 5 Years", "value": "5years"},
                                                {"label": "Historical (10+ years)", "value": "historical"},
                                                {"label": "Specific Date Range", "value": "custom"},
                                                {"label": "Current Semester Only", "value": "semester"}
                                            ],
                                            placeholder="Select time period for analysis",
                                            className="mb-3"
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Needed By Date", className="fw-bold"),
                                        dbc.Input(type="date", className="mb-3")
                                    ], width=6)
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Report Title *", className="fw-bold"),
                                        dbc.Input(type="text", placeholder="Brief, descriptive title for your report", required=True, className="mb-3")
                                    ])
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Detailed Description *", className="fw-bold"),
                                        dbc.Textarea(
                                            placeholder="Please provide a detailed description of what you need:\n\n• What specific data or metrics do you need?\n• What is the purpose of this report?\n• Who is the intended audience?\n• What questions are you trying to answer?\n• Any specific format requirements?",
                                            rows=8,
                                            required=True,
                                            className="mb-3"
                                        )
                                    ])
                                ]),
                                
                                html.Hr(className="my-4"),
                                
                                # Additional Information
                                html.H5("Additional Information", className="fw-bold mb-3", style={'color': USC_COLORS['secondary_green']}),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Preferred Format", className="fw-bold"),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "PDF Report", "value": "pdf"},
                                                {"label": "Excel Spreadsheet", "value": "excel"},
                                                {"label": "PowerPoint Presentation", "value": "powerpoint"},
                                                {"label": "Interactive Dashboard", "value": "dashboard"},
                                                {"label": "Data Files Only", "value": "data"},
                                                {"label": "Multiple Formats", "value": "multiple"}
                                            ],
                                            placeholder="Select preferred format",
                                            value="pdf",
                                            className="mb-3"
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Confidentiality Level", className="fw-bold"),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Public", "value": "public"},
                                                {"label": "Internal Use Only", "value": "internal"},
                                                {"label": "Restricted Access", "value": "restricted"},
                                                {"label": "Confidential", "value": "confidential"}
                                            ],
                                            placeholder="Select confidentiality level",
                                            value="internal",
                                            className="mb-3"
                                        )
                                    ], width=6)
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Additional Notes", className="fw-bold"),
                                        dbc.Textarea(
                                            placeholder="Any additional information, special requirements, or context that would be helpful...",
                                            rows=3,
                                            className="mb-4"
                                        )
                                    ])
                                ]),
                                
                                # Submit section
                                html.Hr(className="my-4"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Div([
                                            dbc.Button([
                                                html.I(className="fas fa-paper-plane me-2"),
                                                "Submit Request"
                                            ], color="success", size="lg", className="me-3"),
                                            dbc.Button([
                                                html.I(className="fas fa-undo me-2"),
                                                "Reset Form"
                                            ], color="outline-secondary", size="lg")
                                        ], className="text-center")
                                    ])
                                ])
                            ])
                        ])
                    ])
                ], width=8),
                
                # Information sidebar
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Request Guidelines", className="fw-bold mb-0", style={'color': USC_COLORS['primary_green']})
                        ]),
                        dbc.CardBody([
                            html.H6("Typical Turnaround Times:", className="fw-bold mb-2"),
                            html.Ul([
                                html.Li("Standard reports: 2-3 weeks"),
                                html.Li("Complex analysis: 3-4 weeks"),
                                html.Li("Urgent requests: 1-2 weeks"),
                                html.Li("Emergency requests: 2-5 days")
                            ], className="mb-3"),
                            
                            html.H6("What We Can Provide:", className="fw-bold mb-2"),
                            html.Ul([
                                html.Li("Enrollment & demographic analysis"),
                                html.Li("Graduation & retention studies"),
                                html.Li("Financial trend analysis"),
                                html.Li("Faculty & staff analytics"),
                                html.Li("Survey design & analysis"),
                                html.Li("Benchmarking studies"),
                                html.Li("Predictive modeling")
                            ], className="mb-3"),
                            
                            html.H6("Need Help?", className="fw-bold mb-2"),
                            html.P([
                                "Contact us to discuss your request: ",
                                html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt"), 
                                " or 868-645-3265 ext. 2150"
                            ])
                        ])
                    ]),
                    
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Frequently Requested", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                            html.P("• Annual enrollment trends", className="mb-1"),
                            html.P("• Graduation rate analysis", className="mb-1"),
                            html.P("• Student retention studies", className="mb-1"),
                            html.P("• Program effectiveness reviews", className="mb-1"),
                            html.P("• Financial aid impact analysis", className="mb-1"),
                            html.P("• Faculty workload distribution", className="mb-0")
                        ])
                    ], className="mt-3")
                ], width=4)
            ])
        ], fluid=True, className="px-4"),
        create_footer()
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})