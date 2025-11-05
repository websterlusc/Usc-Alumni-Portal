"""
USC Institutional Research Portal - Updated Navigation Component
Modified to redirect factbook to external web app
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

def create_auth_section(user_data=None):
    """Create authentication section of navbar"""
    if user_data and user_data.get('authenticated'):
        # User is logged in
        user_menu_items = [
            dbc.DropdownMenuItem("Profile", href="/profile"),
            dbc.DropdownMenuItem(divider=True),
        ]

        # Add admin link for tier 3 users
        if user_data.get('access_tier', 1) >= 3:
            user_menu_items.extend([
                dbc.DropdownMenuItem("Admin Dashboard", href="/admin"),
                dbc.DropdownMenuItem(divider=True),
            ])

        user_menu_items.append(dbc.DropdownMenuItem("Logout", href="/logout"))

        return dbc.DropdownMenu(
            user_menu_items,
            label=f"👤 {user_data.get('email', 'User')}",
            nav=True,
            toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none',
                          'background': 'transparent'}
        )
    else:
        # User not logged in
        return dbc.Nav([
            dbc.NavItem(dbc.NavLink(
                "Login", href="/login",
                style={'color': '#1B5E20', 'fontWeight': '600'}
            ))
        ])

def create_modern_navbar(user_data=None):
    """Updated navbar with external factbook redirect"""
    user_access_tier = user_data.get('access_tier', 1) if user_data else 1

    # Dynamic services menu
    services_items = [
        dbc.DropdownMenuItem("Request Report", href="/request-report"),
        dbc.DropdownMenuItem(divider=True) if user_access_tier >= 2 else None,
        dbc.DropdownMenuItem("Help", href="/help"),
        dbc.DropdownMenuItem("Contact IR", href="/contact")
    ]
    services_items = [item for item in services_items if item is not None]

    return dbc.Navbar(
        dbc.Container([
            # Brand
            dbc.NavbarBrand([
                html.Img(src="assets/usc-logo.png", height="45", className="me-3"),
                html.Div([
                    html.Div("Institutional Research", style={
                        'fontSize': '1.2rem', 'fontWeight': '700',
                        'color': '#FDD835', 'lineHeight': '1.1'
                    }),
                    html.Div("University of the Southern Caribbean", style={
                        'fontSize': '0.8rem', 'color': '#FFFFFF',
                        'lineHeight': '1.1'
                    })
                ])
            ], href="/"),

            # Spacer
            html.Div(style={'flex': '1'}),

            # Right-aligned navigation
            dbc.Nav([
                dbc.NavItem(dbc.NavLink(
                    "Home", href="/",
                    style={'color': '#1B5E20', 'fontWeight': '600'}
                )),
                dbc.DropdownMenu([
                    dbc.DropdownMenuItem("About USC", href="/about-usc"),
                    dbc.DropdownMenuItem("Vision & Mission", href="/vision-mission"),
                    dbc.DropdownMenuItem("Governance", href="/governance"),
                    dbc.DropdownMenuItem("Contact", href="/contact")
                ],
                    label="About USC", nav=True,
                    toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none',
                                  'background': 'transparent'}
                ),

                # News link
                dbc.NavItem(dbc.NavLink(
                    [html.I(className="fas fa-newspaper me-1"), "News"],
                    href="/news",
                    style={'color': '#1B5E20', 'fontWeight': '600'}
                )),

                # UPDATED: External factbook link with target="_blank"
                dbc.NavItem(html.A(
                    [html.I(className="fas fa-chart-bar me-1"), "Factbook"],
                    href="https://your-factbook-app.herokuapp.com",  # ⚠️ REPLACE WITH YOUR ACTUAL FACTBOOK URL
                    target="_blank",
                    rel="noopener noreferrer",
                    className="nav-link",
                    style={'color': '#1B5E20', 'fontWeight': '600', 'textDecoration': 'none'}
                )),

                dbc.DropdownMenu(
                    services_items,
                    label="Services", nav=True,
                    toggle_style={'color': '#1B5E20', 'fontWeight': '600', 'border': 'none',
                                  'background': 'transparent'}
                ),

                # Authentication section
                create_auth_section(user_data)
            ])
        ], fluid=True, style={'display': 'flex', 'alignItems': 'center'}),
        color="white",
        className="shadow-sm sticky-top",
        style={'borderBottom': '3px solid #1B5E20', 'minHeight': '75px'}
    )

# Backup of original navbar for reference
def create_navbar_original(user=None):
    """Original navbar implementation - keep for reference"""
    nav_items = []

    nav_items.append(
        dbc.NavItem(dbc.NavLink("Home", href="/", active="exact", className="text-white fw-bold"))
    )

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

    # Original internal factbook link
    nav_items.append(
        dbc.NavItem(dbc.NavLink("Factbook", href="/factbook", className="text-white fw-bold"))
    )

    nav_items.append(
        dbc.NavItem(dbc.NavLink("Request Reports", href="/request-reports", className="text-white fw-bold"))
    )

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

    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.Img(src="/assets/usc-logo.png", height="40", className="me-2"),
                "USC Institutional Research"
            ], href="/", className="text-white fw-bold"),
            dbc.Nav(nav_items + [user_section], className="ms-auto", navbar=True)
        ], fluid=True),
        color=USC_COLORS['primary_green'],
        dark=True,
        className="shadow-sm"
    )