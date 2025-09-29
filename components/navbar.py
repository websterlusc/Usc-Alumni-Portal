"""
USC Institutional Research Portal - Navigation Component
Right-aligned navbar with simplified factbook link
"""

from dash import html
import dash_bootstrap_components as dbc

USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F5F5F5',
    'dark_gray': '#424242',
    'text_gray': '#666666'
}

def create_navbar(user=None):
    """Create right-aligned navigation bar with simplified structure"""

    nav_items = []

    # Home link
    nav_items.append(
        dbc.NavItem(dbc.NavLink("Home", href="/", active="exact", className="text-white fw-bold"))
    )

    # Facts About USC section
    facts_menu = [
        dbc.DropdownMenuItem("About USC", href="/about-usc"),
        dbc.DropdownMenuItem("Vision, Mission & Motto", href="/vision-mission-motto"),
        dbc.DropdownMenuItem("Governance Structure", href="/governance"),
        dbc.DropdownMenuItem("USC History", href="/usc-history"),
        dbc.DropdownMenuItem("Campus Information", href="/campus-info"),
        dbc.DropdownMenuItem("Contact Information", href="/contact")
    ]

    nav_items.append(
        dbc.DropdownMenu(
            facts_menu,
            nav=True,
            in_navbar=True,
            label="Facts About USC",
            toggle_style={"color": "white", "border": "none", "background": "transparent"}
        )
    )

    # Student Services section
    services_menu = [
        dbc.DropdownMenuItem("Admissions", href="/admissions"),
        dbc.DropdownMenuItem("Academic Programs", href="/programs"),
        dbc.DropdownMenuItem("Academic Calendar", href="/calendar"),
        dbc.DropdownMenuItem("Student Life", href="/student-life"),
        dbc.DropdownMenuItem("Student Support", href="/student-support")
    ]

    nav_items.append(
        dbc.DropdownMenu(
            services_menu,
            nav=True,
            in_navbar=True,
            label="Student Services",
            toggle_style={"color": "white", "border": "none", "background": "transparent"}
        )
    )

    # Single Factbook link
    nav_items.append(
        dbc.NavItem(dbc.NavLink("Factbook", href="/factbook", className="text-white fw-bold"))
    )

    # Request Reports link
    nav_items.append(
        dbc.NavItem(dbc.NavLink("Request Reports", href="/request-reports", className="text-white fw-bold"))
    )

    # User section
    if user:
        user_menu = [
            dbc.DropdownMenuItem("View Profile", href="/profile"),
            dbc.DropdownMenuItem("Account Settings", href="/account-settings"),
            dbc.DropdownMenuItem("Login History", href="/login-history"),
            dbc.DropdownMenuItem(divider=True)
        ]

        if user.get('is_admin'):
            user_menu.extend([
                dbc.DropdownMenuItem("Admin Dashboard", href="/admin"),
                dbc.DropdownMenuItem("User Management", href="/user-management"),
                dbc.DropdownMenuItem(divider=True)
            ])

        user_menu.append(dbc.DropdownMenuItem("Logout", href="/logout"))

        user_section = dbc.Nav([
            dbc.DropdownMenu(
                user_menu,
                nav=True,
                in_navbar=True,
                label=user['email'],
                toggle_style={"color": "white", "border": "none", "background": "transparent"}
            )
        ])
    else:
        user_section = dbc.Nav([
            dbc.NavItem(dbc.NavLink("Login", href="/login", className="text-white fw-bold"))
        ])
    dbc.NavItem(dbc.NavLink(
        "News & Announcements",
        href="/news",
        style={'color': '#1B5E20', 'fontWeight': '600'}
    ))
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-university me-3", style={'fontSize': '2rem', 'color': 'white'}),
                        dbc.NavbarBrand("USC Institutional Research", className="text-white fw-bold", style={'fontSize': '1.3rem'})
                    ], className="d-flex align-items-center")
                ], width="auto"),
                dbc.Col([
                    html.Div([
                        dbc.Nav(nav_items, navbar=True, className="me-3"),
                        user_section
                    ], className="d-flex align-items-center")
                ], className="d-flex justify-content-end")
            ], align="center", className="w-100")
        ], fluid=True),
        color=USC_COLORS['primary_green'],
        dark=True,
        className="mb-4",
        style={
            'background': f'linear-gradient(135deg, {USC_COLORS["primary_green"]}, {USC_COLORS["secondary_green"]})',
            'padding': '0.8rem 0',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
        }
    )

def create_footer():
    """Create footer for all pages"""
    return html.Footer([
        dbc.Container([
            html.Hr(style={'borderColor': USC_COLORS['light_gray']}),
            dbc.Row([
                dbc.Col([
                    html.H5("USC Institutional Research", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                    html.P("Providing comprehensive data, analytics, and insights to support evidence-based decision making at the University of the Southern Caribbean.")
                ], width=4),
                dbc.Col([
                    html.H6("Quick Links", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                    html.Ul([
                        html.Li(html.A("USC Main Website", href="https://www.usc.edu.tt", target="_blank", className="text-decoration-none")),
                        html.Li(html.A("USC eLearn", href="https://elearn.usc.edu.tt", target="_blank", className="text-decoration-none")),
                        html.Li(html.A("USC Aerion Portal", href="https://aerion.usc.edu.tt", target="_blank", className="text-decoration-none")),
                        html.Li(html.A("Request Reports", href="/request-reports", className="text-decoration-none"))
                    ], className="list-unstyled")
                ], width=3),
                dbc.Col([
                    html.H6("Contact Information", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                    html.P([
                        html.Strong("Director: "), "Nordian C. Swaby Robinson", html.Br(),
                        html.Strong("Email: "), html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt", className="text-decoration-none"), html.Br(),
                        html.Strong("Phone: "), "868-645-3265 ext. 2150"
                    ], className="mb-0")
                ], width=3),
                dbc.Col([
                    html.H6("Development Team", className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),
                    html.P([
                        html.Strong("Web Developer: "), "Liam Webster", html.Br(),
                        html.Strong("Email: "), html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt", className="text-decoration-none"), html.Br(),
                        html.Strong("Phone: "), "868-645-3265 ext. 1014"
                    ], className="mb-0")
                ], width=2)
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.Hr(style={'borderColor': USC_COLORS['light_gray']}),
                    html.P([
                        "© 2025 University of the Southern Caribbean - Institutional Research Department | ",
                        html.A("Privacy Policy", href="/privacy", className="text-muted text-decoration-none"), " | ",
                        html.A("Terms of Use", href="/terms", className="text-muted text-decoration-none")
                    ], className="text-center text-muted mb-0")
                ])
            ])
        ], fluid=True)
    ], className="mt-5 py-4", style={'backgroundColor': USC_COLORS['light_gray']})