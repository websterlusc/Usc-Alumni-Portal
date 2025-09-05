"""
USC Institutional Research Portal - Placeholder Pages
Placeholder pages for Data & Analytics and Financial sections
"""

from dash import html
import dash_bootstrap_components as dbc
from components.navbar import create_navbar, USC_COLORS

# ============================================================================
# DATA & ANALYTICS PLACEHOLDER PAGES (Tier 2)
# ============================================================================

def create_factbook_overview_page():
    """Factbook overview placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Interactive Factbook", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            dbc.Alert([
                html.H4("Factbook Content Coming Soon", className="alert-heading"),
                "The interactive factbook with comprehensive institutional data will be integrated here. ",
                "This will include enrollment trends, graduation rates, and detailed analytics."
            ], color="success", className="text-center mb-5"),
            
            # Preview of what will be included
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-chart-line fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                            html.H4("Enrollment Trends"),
                            html.P("Multi-year enrollment data with interactive visualizations")
                        ], className="text-center")
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-graduation-cap fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                            html.H4("Graduation Analytics"),
                            html.P("Graduation rates, degree completions, and outcome tracking")
                        ], className="text-center")
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-users fa-3x mb-3", style={'color': USC_COLORS['secondary_green']}),
                            html.H4("Demographics"),
                            html.P("Student and faculty demographics with diversity metrics")
                        ], className="text-center")
                    ])
                ], width=4)
            ])
        ])
    ])

def create_enrollment_page():
    """Enrollment data placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Enrollment Data", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Detailed enrollment analytics will be displayed here with interactive charts and data tables.", color="success", className="text-center")
        ])
    ])

def create_graduation_page():
    """Graduation statistics placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Graduation Statistics", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Graduation data and completion rates will be displayed here.", color="success", className="text-center")
        ])
    ])

def create_student_employment_page():
    """Student employment placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Student Employment", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Student employment data and work-study analytics will be displayed here.", color="success", className="text-center")
        ])
    ])

def create_hr_data_page():
    """HR analytics placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("HR Analytics", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Human resources analytics and faculty data will be displayed here.", color="success", className="text-center")
        ])
    ])

def create_program_analytics_page():
    """Program analytics placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Program Analytics", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Academic program performance and analytics will be displayed here.", color="success", className="text-center")
        ])
    ])

def create_counselling_page():
    """Counselling services placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Counselling Services Data", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Counselling services utilization data will be displayed here.", color="success", className="text-center")
        ])
    ])

def create_outreach_page():
    """Outreach activities placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Outreach Activities", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Community outreach activities and impact data will be displayed here.", color="success", className="text-center")
        ])
    ])

# ============================================================================
# FINANCIAL PAGES PLACEHOLDERS (Tier 3)
# ============================================================================

def create_financial_overview_page():
    """Financial overview placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Financial Overview", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            dbc.Alert([
                html.H4("Financial Reports Access", className="alert-heading"),
                "Comprehensive financial data and reports will be displayed here. ",
                "This section includes budget analysis, revenue tracking, and detailed financial statements."
            ], color="warning", className="text-center mb-5"),
            
            # Preview of financial sections
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-chart-pie fa-3x mb-3", style={'color': USC_COLORS['accent_yellow']}),
                            html.H4("Budget Overview"),
                            html.P("Annual budget breakdown and departmental allocations")
                        ], className="text-center")
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-dollar-sign fa-3x mb-3", style={'color': USC_COLORS['accent_yellow']}),
                            html.H4("Revenue Analysis"),
                            html.P("Revenue sources, trends, and financial performance metrics")
                        ], className="text-center")
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-file-invoice-dollar fa-3x mb-3", style={'color': USC_COLORS['accent_yellow']}),
                            html.H4("Financial Statements"),
                            html.P("Audited financial statements and compliance reports")
                        ], className="text-center")
                    ])
                ], width=4)
            ])
        ])
    ])

def create_budget_page():
    """Budget analysis placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Budget Analysis", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Detailed budget analysis and departmental breakdowns will be displayed here.", color="warning", className="text-center")
        ])
    ])

def create_revenue_page():
    """Revenue reports placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Revenue Reports", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Revenue analysis, tuition income, and funding sources will be displayed here.", color="warning", className="text-center")
        ])
    ])

def create_endowments_page():
    """Endowment funds placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Endowment Funds", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Endowment fund performance and investment data will be displayed here.", color="warning", className="text-center")
        ])
    ])

def create_financial_statements_page():
    """Financial statements placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Financial Statements", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Audited financial statements and annual reports will be displayed here.", color="warning", className="text-center")
        ])
    ])

def create_scholarships_page():
    """Scholarships and aid placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Scholarships & Financial Aid", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Scholarship distribution data and financial aid analytics will be displayed here.", color="warning", className="text-center")
        ])
    ])

def create_tuition_page():
    """Tuition and fees placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Tuition & Fees", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("Tuition rates, fee structures, and payment analytics will be displayed here.", color="warning", className="text-center")
        ])
    ])

# ============================================================================
# ADMIN PAGES PLACEHOLDERS
# ============================================================================

def create_admin_dashboard_page():
    """Admin dashboard placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("Admin Dashboard", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            
            dbc.Alert([
                html.H4("Admin Functionality", className="alert-heading"),
                "Admin dashboard with user management, access control, and system settings will be implemented here."
            ], color="danger", className="text-center mb-5"),
            
            # Admin feature preview
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-users-cog fa-3x mb-3", style={'color': USC_COLORS['primary_green']}),
                            html.H4("User Management"),
                            html.P("Create, edit, and manage user accounts and access levels")
                        ], className="text-center")
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-key fa-3x mb-3", style={'color': USC_COLORS['primary_green']}),
                            html.H4("Access Requests"),
                            html.P("Review and approve user access upgrade requests")
                        ], className="text-center")
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-chart-bar fa-3x mb-3", style={'color': USC_COLORS['primary_green']}),
                            html.H4("System Analytics"),
                            html.P("Monitor system usage, user activity, and performance metrics")
                        ], className="text-center")
                    ])
                ], width=4)
            ])
        ])
    ])

def create_user_management_page():
    """User management placeholder"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            html.H1("User Management", className="display-4 fw-bold mb-5 text-center", style={'color': USC_COLORS['primary_green']}),
            dbc.Alert("User management interface with account creation, editing, and access control will be implemented here.", color="danger", className="text-center")
        ])
    ])