"""
USC Institutional Research Portal - Factbook Landing Page
Central hub with links to all data sections based on access tiers
"""

from dash import html
import dash_bootstrap_components as dbc
from components.navbar import create_navbar, create_footer, USC_COLORS

def create_factbook_landing_page(user=None):
    """Create factbook landing page with tiered access to data sections"""
    user_tier = user['access_tier'] if user else 1
    
    # Define all factbook sections based on your file list
    # REMOVE Student Labour from tier_2_sections:
    tier_2_sections = [
        {"title": "Counselling Services", "href": "/factbook/counselling", "icon": "fas fa-heart",
         "file": "counselling.xlsx"},
        {"title": "Credits Analysis", "href": "/factbook/credits", "icon": "fas fa-graduation-cap",
         "file": "credits.xlsx"},
        {"title": "Enrollment Data", "href": "/factbook/enrollment", "icon": "fas fa-users",
         "file": "enrolment_data.xlsx"},
        {"title": "Graduation Statistics", "href": "/factbook/graduation", "icon": "fas fa-certificate",
         "file": "GraduationData.xlsx"},
        {"title": "Governance & Administration", "href": "/factbook/governance-admin", "icon": "fas fa-sitemap",
         "file": "GovernenceAndAdmin.xlsx"},
        {"title": "Higher Faculty", "href": "/factbook/higher-faculty", "icon": "fas fa-chalkboard-teacher",
         "file": "HigherFaculty.xlsx"},
        {"title": "HR Appointments", "href": "/factbook/hr-appointments", "icon": "fas fa-user-plus",
         "file": "HrAppointments.xlsx"},
        {"title": "HR Data", "href": "/factbook/hr-data", "icon": "fas fa-user-tie", "file": "HrData.xlsx"},
        {"title": "OJT Training Report", "href": "/factbook/ojt-training", "icon": "fas fa-tools",
         "file": "ojt_training_report.xlsx"},
        {"title": "Outreach Activities", "href": "/factbook/outreach", "icon": "fas fa-hands-helping",
         "file": "outreach_activities.xlsx"},
        {"title": "Programme Offerings", "href": "/factbook/programmes", "icon": "fas fa-book-open",
         "file": "ProgrammeOffering.xlsx"},
        # REMOVED: Student Labour Report - moved to tier_3_sections
        {"title": "Teaching Load", "href": "/factbook/teaching-load", "icon": "fas fa-chalkboard",
         "file": "Teaching Load.xlsx"}
    ]

    # ADD Student Labour to tier_3_sections:
    tier_3_sections = [
        {"title": "Debt Collection", "href": "/factbook/debt-collection", "icon": "fas fa-file-invoice-dollar",
         "file": "debt_collection.xlsx"},
        {"title": "Endowment Funds", "href": "/factbook/endowment-funds", "icon": "fas fa-piggy-bank",
         "file": "endowment_funds.xlsx"},
        {"title": "Financial Data", "href": "/factbook/financial-data", "icon": "fas fa-chart-line",
         "file": "financial.xlsx"},
        {"title": "GATE Funding", "href": "/factbook/gate-funding", "icon": "fas fa-graduation-cap",
         "file": "gate_funding.xlsx"},
        {"title": "Income Generating Units", "href": "/factbook/income-units", "icon": "fas fa-dollar-sign",
         "file": "income_generating_units.xlsx"},
        {"title": "Scholarships & Discounts", "href": "/factbook/scholarships", "icon": "fas fa-award",
         "file": "scholarship_discount_tuition.xlsx"},
        {"title": "Student Labour Report", "href": "/factbook/student-labour", "icon": "fas fa-briefcase",
         "file": "student_labour_report.xlsx"},  # MOVED HERE
        {"title": "Subsidies", "href": "/factbook/subsidies", "icon": "fas fa-hand-holding-usd",
         "file": "subsidies.xlsx"}
    ]
    
    def create_section_card(section, accessible=True, tier_required=2):
        """Create a card for each factbook section"""
        if accessible:
            card_style = {
                'border': f'2px solid {USC_COLORS["secondary_green"]}',
                'borderRadius': '8px',
                'height': '100%',
                'transition': 'transform 0.2s, box-shadow 0.2s'
            }
            card_class = "factbook-card-accessible"
            button_props = {"color": "success", "href": section["href"]}
            button_text = "View Data"
        else:
            card_style = {
                'border': f'2px solid {USC_COLORS["text_gray"]}',
                'borderRadius': '8px',
                'height': '100%',
                'opacity': '0.6'
            }
            card_class = "factbook-card-locked"
            button_props = {"color": "secondary", "disabled": True}
            button_text = f"Requires Tier {tier_required}"
        
        return dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className=f"{section['icon']} fa-2x mb-3", 
                          style={'color': USC_COLORS['secondary_green'] if accessible else USC_COLORS['text_gray']}),
                    html.H5(section['title'], className="fw-bold mb-2", 
                           style={'color': USC_COLORS['primary_green'] if accessible else USC_COLORS['text_gray']}),
                    html.P(f"Data source: {section['file']}", className="text-muted small mb-3"),
                    dbc.Button(button_text, size="sm", className="w-100", **button_props)
                ], className="text-center")
            ])
        ], style=card_style, className=card_class)
    
    return html.Div([
        create_navbar(user),
        dbc.Container([
            # Header section
            html.Div([
                html.H1("USC Factbook", className="display-4 fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                html.P("Comprehensive institutional data and analytics organized by access level", 
                       className="lead text-muted mb-5")
            ], className="text-center mb-5"),
            
            # Access level indicator
            html.Div([
                dbc.Alert([
                    html.H5(f"Your Access Level: Tier {user_tier}" if user else "Public Access", className="alert-heading mb-2"),
                    html.P("You can view data sections up to your access tier. Contact IR for access upgrades." if user else "Please log in to access detailed institutional data.")
                ], color="info" if user else "warning", className="text-center")
            ], className="mb-5"),
            
            # Tier 2 - General Factbook Data
            html.Div([
                html.H2("General Institutional Data", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                html.P("Academic, enrollment, and operational data (Requires Tier 2 Access)", className="text-muted mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        create_section_card(section, accessible=(user_tier >= 2), tier_required=2)
                    ], width=3, className="mb-4")
                    for section in tier_2_sections
                ], className="g-3")
            ], className="mb-5"),
            
            # Tier 3 - Financial Data
            html.Div([
                html.H2("Financial Data", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                html.P("Budget, revenue, and financial information (Requires Tier 3 Access)", className="text-muted mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        create_section_card(section, accessible=(user_tier >= 3), tier_required=3)
                    ], width=3, className="mb-4")
                    for section in tier_3_sections
                ], className="g-3")
            ], className="mb-5"),
            
            # Additional resources
            html.Hr(className="my-5"),
            html.Div([
                html.H3("Need Help?", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Request Access Upgrade", className="fw-bold mb-3"),
                                html.P("Need access to higher tier data? Submit a request for access level upgrade."),
                                dbc.Button("Request Access", href="/request-access", color="success", size="sm")
                            ])
                        ])
                    ], width=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Request Custom Report", className="fw-bold mb-3"),
                                html.P("Need a specific analysis or custom report? Request one from our team."),
                                dbc.Button("Request Report", href="/request-reports", color="outline-success", size="sm")
                            ])
                        ])
                    ], width=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Contact IR Team", className="fw-bold mb-3"),
                                html.P("Questions about the data or need assistance with analysis?"),
                                dbc.Button("Contact Us", href="mailto:ir@usc.edu.tt", color="outline-secondary", size="sm")
                            ])
                        ])
                    ], width=4)
                ], className="g-3")
            ])
        ], fluid=True, className="px-4"),
        create_footer()
    ], style={'backgroundColor': '#fafafa', 'minHeight': '100vh'})