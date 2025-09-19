"""
USC Institutional Research Portal - Factbook Landing Page
Central hub with tiered access to all factbook data sections
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

# USC Brand Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA',
    'medium_gray': '#E9ECEF',
    'dark_gray': '#495057',
    'text_dark': '#212529',
    'success_green': '#28A745'
}

def create_factbook_landing_page(user_data=None):
    """Create comprehensive factbook landing page with tiered access"""
    user_tier = user_data.get('access_tier', 1) if user_data else 1
    user_authenticated = user_data and user_data.get('authenticated', False)
    
    # Define factbook sections organized by access tier
    tier_2_sections = [
        {
            "title": "Enrollment Data", 
            "href": "/factbook/enrollment", 
            "icon": "fas fa-users", 
            "description": "Student enrollment trends, demographics, and registration analytics",
            "stats": "3,110 current students"
        },
        {
            "title": "Graduation Statistics", 
            "href": "/factbook/graduation", 
            "icon": "fas fa-graduation-cap", 
            "description": "Graduation rates, degree completion trends, and alumni outcomes",
            "stats": "May 2025 graduates"
        },
        {
            "title": "HR Data & Appointments", 
            "href": "/factbook/hr-data", 
            "icon": "fas fa-user-tie", 
            "description": "Faculty and staff analytics, hiring trends, and employment data",
            "stats": "250+ employees"
        },
        {
            "title": "Programme Offerings", 
            "href": "/factbook/programmes", 
            "icon": "fas fa-book-open", 
            "description": "Academic programs, course offerings, and curriculum analytics",
            "stats": "5 academic divisions"
        },
        {
            "title": "Teaching Load Analysis", 
            "href": "/factbook/teaching-load", 
            "icon": "fas fa-chalkboard", 
            "description": "Faculty workload distribution, class sizes, and teaching assignments",
            "stats": "Faculty analytics"
        },
        {
            "title": "Student Employment", 
            "href": "/factbook/student-labour", 
            "icon": "fas fa-briefcase", 
            "description": "Work-study programs, student employment, and labour analytics",
            "stats": "Work-study data"
        },
        {
            "title": "OJT Training Reports", 
            "href": "/factbook/ojt-training", 
            "icon": "fas fa-tools", 
            "description": "On-the-job training programs and vocational education metrics",
            "stats": "Training programs"
        },
        {
            "title": "Counselling Services", 
            "href": "/factbook/counselling", 
            "icon": "fas fa-heart", 
            "description": "Student counselling usage, wellness programs, and support services",
            "stats": "Student wellness"
        },
        {
            "title": "Outreach Activities", 
            "href": "/factbook/outreach", 
            "icon": "fas fa-hands-helping", 
            "description": "Community engagement, service learning, and outreach programs",
            "stats": "Community impact"
        },
        {
            "title": "Credits & Academic Analysis", 
            "href": "/factbook/credits", 
            "icon": "fas fa-certificate", 
            "description": "Credit hour analytics, academic progression, and degree requirements",
            "stats": "Academic progress"
        },
        {
            "title": "Governance & Administration", 
            "href": "/factbook/governance-admin", 
            "icon": "fas fa-sitemap", 
            "description": "Organizational structure, leadership analytics, and administrative data",
            "stats": "Leadership structure"
        },
        {
            "title": "Higher Faculty Analytics", 
            "href": "/factbook/higher-faculty", 
            "icon": "fas fa-chalkboard-teacher", 
            "description": "Advanced faculty metrics, research activities, and academic leadership",
            "stats": "Faculty research"
        }
    ]
    
    tier_3_sections = [
        {
            "title": "Financial Reports", 
            "href": "/factbook/financial-data", 
            "icon": "fas fa-chart-line", 
            "description": "Comprehensive financial statements, budget analysis, and fiscal health",
            "stats": "Complete financials"
        },
        {
            "title": "Endowment Funds", 
            "href": "/factbook/endowment-funds", 
            "icon": "fas fa-piggy-bank", 
            "description": "Endowment performance, investment returns, and fund management",
            "stats": "Investment portfolio"
        },
        {
            "title": "GATE Funding", 
            "href": "/factbook/gate-funding", 
            "icon": "fas fa-graduation-cap", 
            "description": "Government funding, scholarship distributions, and financial aid analytics",
            "stats": "Student funding"
        },
        {
            "title": "Income Generating Units", 
            "href": "/factbook/income-units", 
            "icon": "fas fa-dollar-sign", 
            "description": "Revenue streams, auxiliary services, and income diversification",
            "stats": "Revenue analysis"
        },
        {
            "title": "Scholarships & Discounts", 
            "href": "/factbook/scholarships", 
            "icon": "fas fa-award", 
            "description": "Merit awards, tuition assistance, and student financial support",
            "stats": "Student aid"
        },
        {
            "title": "Subsidies Analysis", 
            "href": "/factbook/subsidies", 
            "icon": "fas fa-hand-holding-usd", 
            "description": "Government subsidies, grants, and external funding sources",
            "stats": "External funding"
        },
        {
            "title": "Debt Collection", 
            "href": "/factbook/debt-collection", 
            "icon": "fas fa-file-invoice-dollar", 
            "description": "Accounts receivable, payment trends, and collection analytics",
            "stats": "Collections data"
        }
    ]

    def create_section_card(section, accessible=True, tier_required=2):
        """Create a card for each factbook section"""
        if accessible:
            card_style = {
                'border': f'2px solid {USC_COLORS["secondary_green"]}',
                'borderRadius': '10px',
                'height': '100%',
                'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                'cursor': 'pointer'
            }
            card_class = "factbook-card-accessible"
            button_props = {"color": "success", "href": section["href"], "size": "sm"}
            button_text = "View Data"
            icon_color = USC_COLORS["secondary_green"]
        else:
            card_style = {
                'border': f'2px solid {USC_COLORS["medium_gray"]}',
                'borderRadius': '10px',
                'height': '100%',
                'backgroundColor': '#f8f9fa',
                'opacity': '0.7'
            }
            card_class = "factbook-card-locked"
            button_props = {"color": "outline-secondary", "disabled": True, "size": "sm"}
            button_text = f"Tier {tier_required} Required"
            icon_color = USC_COLORS["medium_gray"]

        return dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(
                        className=f"{section['icon']} fa-2x mb-3",
                        style={'color': icon_color}
                    ),
                    html.H5(section["title"], 
                            className="card-title fw-bold mb-2",
                            style={'color': USC_COLORS["primary_green"] if accessible else USC_COLORS["dark_gray"]}),
                    html.P(section["description"], 
                           className="card-text small mb-3",
                           style={'color': '#666', 'lineHeight': '1.4'}),
                    html.P(section["stats"], 
                           className="card-text small fw-bold mb-3",
                           style={'color': USC_COLORS["accent_yellow"] if accessible else USC_COLORS["medium_gray"]}),
                    dbc.Button(button_text, **button_props, className="w-100"),
                    
                    # Lock overlay for inaccessible sections
                    html.Div([
                        html.I(className="fas fa-lock fa-lg",
                               style={'color': USC_COLORS["medium_gray"]})
                    ], className="position-absolute top-0 end-0 m-2") if not accessible else html.Div()
                ], className="text-center position-relative")
            ])
        ], style=card_style, className=f"{card_class} h-100")

    # Create the page layout
    return html.Div([
        # Hero Section
        html.Section([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H1([
                                "USC ",
                                html.Span("Factbook", style={
                                    'background': f'linear-gradient(45deg, {USC_COLORS["accent_yellow"]}, #FFEB3B)',
                                    'WebkitBackgroundClip': 'text',
                                    'WebkitTextFillColor': 'transparent'
                                })
                            ], className="display-4 fw-bold mb-3"),
                            html.P([
                                "Comprehensive institutional data and analytics powered by the ",
                                html.Strong("Department of Institutional Research", 
                                          style={'color': USC_COLORS["accent_yellow"]})
                            ], className="lead mb-4", style={'fontSize': '1.2rem'}),
                            
                            # Quick Stats
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.H3("3,110", className="fw-bold mb-0"),
                                        html.Small("Total Students")
                                    ], className="text-center")
                                ], md=3),
                                dbc.Col([
                                    html.Div([
                                        html.H3("5", className="fw-bold mb-0"),
                                        html.Small("Academic Divisions")
                                    ], className="text-center")
                                ], md=3),
                                dbc.Col([
                                    html.Div([
                                        html.H3("250+", className="fw-bold mb-0"),
                                        html.Small("Faculty & Staff")
                                    ], className="text-center")
                                ], md=3),
                                dbc.Col([
                                    html.Div([
                                        html.H3(f"Tier {user_tier}", className="fw-bold mb-0"),
                                        html.Small("Your Access Level")
                                    ], className="text-center")
                                ], md=3)
                            ], className="text-white mb-4") if user_authenticated else html.Div()
                            
                        ], className="text-center text-white")
                    ], md=10, lg=8)
                ], justify="center")
            ])
        ], style={
            'background': f'linear-gradient(135deg, {USC_COLORS["primary_green"]} 0%, {USC_COLORS["secondary_green"]} 100%)',
            'padding': '60px 0',
            'marginBottom': '50px'
        }),

        # Main Content
        dbc.Container([
            # Access Level Indicator
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                f"You currently have " if user_authenticated else "Please sign in for access to factbook data. ",
                html.Strong(f"Tier {user_tier}" if user_authenticated else "Public"),
                f" access" if user_authenticated else "",
                " - " if user_authenticated else ". ",
                "Contact ir@usc.edu.tt for access upgrades." if user_authenticated else "Tier 2+ required for detailed data."
            ], color="info" if user_authenticated else "warning", className="mb-5"),

            # Introduction Section
            dbc.Row([
                dbc.Col([
                    html.H2("About the USC Factbook", 
                            className="fw-bold mb-4", 
                            style={'color': USC_COLORS['primary_green']}),
                    html.P([
                        "This University Factbook is a comprehensive report providing a three-year data trend for key ",
                        "performance metrics related to graduation, finances, enrollment, and spiritual development at ",
                        "the University of the Southern Caribbean."
                    ], className="lead mb-3"),
                    html.P([
                        "The report is organized to include information from the Office of the President and the five ",
                        "divisions of the university, covering program offerings, teaching loads, graduation data, ",
                        "undergraduate and graduate student enrollment, faculty and staff demographics, financial ",
                        "statements and spiritual development activities."
                    ], className="mb-4"),
                    
                    # Access Tier Explanation
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6("Tier 2: Limited Access", className="fw-bold text-success"),
                                    html.P("Academic and operational data", className="mb-0 small")
                                ])
                            ], color="success", outline=True)
                        ], md=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6("Tier 3: Complete Access", className="fw-bold text-warning"),
                                    html.P("Full financial and budget data", className="mb-0 small")
                                ])
                            ], color="warning", outline=True)
                        ], md=6)
                    ], className="mb-5")
                ], md=12)
            ]),

            # Tier 2 Sections - Academic & Operational Data
            html.Div([
                html.Div([
                    html.H2([
                        html.I(className="fas fa-chart-bar me-3"),
                        "Academic & Operational Data"
                    ], className="fw-bold mb-2", style={'color': USC_COLORS['primary_green']}),
                    html.P("Student analytics, enrollment trends, faculty data, and operational metrics", 
                           className="text-muted mb-4"),
                    dbc.Badge("Tier 2 Access Required", color="success", className="mb-4")
                ]),
                
                dbc.Row([
                    dbc.Col([
                        create_section_card(section, accessible=(user_tier >= 2), tier_required=2)
                    ], width=12, md=6, lg=4, className="mb-4")
                    for section in tier_2_sections
                ])
            ], className="mb-5"),

            html.Hr(className="my-5", style={'borderColor': USC_COLORS['medium_gray'], 'borderWidth': '2px'}),

            # Tier 3 Sections - Financial Data
            html.Div([
                html.Div([
                    html.H2([
                        html.I(className="fas fa-dollar-sign me-3"),
                        "Financial & Budget Data"
                    ], className="fw-bold mb-2", style={'color': USC_COLORS['primary_green']}),
                    html.P("Budget analysis, revenue streams, financial statements, and fiscal analytics", 
                           className="text-muted mb-4"),
                    dbc.Badge("Tier 3 Access Required", color="warning", className="mb-4")
                ]),
                
                dbc.Row([
                    dbc.Col([
                        create_section_card(section, accessible=(user_tier >= 3), tier_required=3)
                    ], width=12, md=6, lg=4, className="mb-4")
                    for section in tier_3_sections
                ])
            ], className="mb-5"),

            html.Hr(className="my-5"),

            # Additional Resources
            dbc.Row([
                dbc.Col([
                    html.H3("Need Help?", className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.I(className="fas fa-key fa-2x mb-3", style={'color': USC_COLORS['secondary_green']}),
                                    html.H5("Request Access Upgrade", className="fw-bold mb-3"),
                                    html.P("Need higher tier access? Submit a request with justification.", className="mb-3"),
                                    dbc.Button("Request Access", href="/profile", color="success", size="sm")
                                ], className="text-center")
                            ])
                        ], md=4, className="mb-3"),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.I(className="fas fa-file-alt fa-2x mb-3", style={'color': USC_COLORS['accent_yellow']}),
                                    html.H5("Custom Reports", className="fw-bold mb-3"),
                                    html.P("Need specific analysis? Request a custom report from our team.", className="mb-3"),
                                    dbc.Button("Request Report", href="/request-report", color="warning", size="sm")
                                ], className="text-center")
                            ])
                        ], md=4, className="mb-3"),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.I(className="fas fa-envelope fa-2x mb-3", style={'color': USC_COLORS['primary_green']}),
                                    html.H5("Contact IR Team", className="fw-bold mb-3"),
                                    html.P("Questions about data or need assistance? Contact us directly.", className="mb-3"),
                                    dbc.Button("Contact Us", href="/contact", color="primary", size="sm")
                                ], className="text-center")
                            ])
                        ], md=4, className="mb-3")
                    ])
                ], width=12)
            ])
        ])
    ])