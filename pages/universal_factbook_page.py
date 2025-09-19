from dash import html, dcc
import dash_bootstrap_components as dbc
from universal_factbook_loader import load_factbook_section
from callback_registry import register_section_callbacks

USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF'
}


def create_universal_factbook_page(section_key: str):
    """Create a factbook page for ANY section using the universal system"""

    # Register callbacks for this section (automatic)
    register_section_callbacks(section_key)

    # Get section data and metadata
    section_data = load_factbook_section(section_key)
    section_title = section_key.replace('-', ' ').title()

    # Determine appropriate icon based on section
    icon_map = {
        'enrollment': 'fas fa-users',
        'financial-data': 'fas fa-chart-line',
        'hr-data': 'fas fa-user-tie',
        'graduation': 'fas fa-graduation-cap',
        'student-labour': 'fas fa-users-cog',
        # Add more as needed
    }

    section_icon = icon_map.get(section_key, 'fas fa-chart-bar')

    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1([
                    html.I(className=f"{section_icon} me-3"),
                    f"{section_title} Report"
                ], className="mb-4", style={"color": USC_COLORS["primary_green"]}),

                # Data Status
                create_data_status_alert(section_data, section_key)
            ])
        ]),

        # Main Content - Three Chart Layout
        dbc.Row([
            # Controls Sidebar
            dbc.Col([
                create_universal_controls(section_key, section_data)
            ], width=3),

            # Charts Area
            dbc.Col([
                # Primary Chart (Full Width)
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-chart-bar me-2"),
                            "Primary Analysis"
                        ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                    ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                    dbc.CardBody([
                        dcc.Graph(id=f'{section_key}-chart-1', style={'height': '500px'})
                    ])
                ], className="mb-4"),

                # Secondary Charts Row
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H6("Secondary Analysis", className="mb-0",
                                        style={'color': USC_COLORS["accent_yellow"]})
                            ], style={'backgroundColor': USC_COLORS["secondary_green"]}),
                            dbc.CardBody([
                                dcc.Graph(id=f'{section_key}-chart-2', style={'height': '400px'})
                            ])
                        ])
                    ], width=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H6("Detailed View", className="mb-0",
                                        style={'color': USC_COLORS["accent_yellow"]})
                            ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                            dbc.CardBody([
                                dcc.Graph(id=f'{section_key}-chart-3', style={'height': '400px'})
                            ])
                        ])
                    ], width=6)
                ])
            ], width=9)
        ])
    ], fluid=True)


def create_data_status_alert(section_data, section_key):
    """Create data status alert"""
    if section_data.get('success'):
        sheets_count = len(section_data.get('sheets', {}))
        years_count = len(section_data.get('available_years', []))

        return dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            html.Strong("Data Loaded Successfully: "),
            f"{sheets_count} sheets, {years_count} years detected",
            html.Br(),
            html.Small("Charts update automatically when Excel file changes", className="text-muted")
        ], color="success", className="mb-4")
    else:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            html.Strong("Data Loading Error: "),
            section_data.get('error', 'Unknown error'),
            html.Br(),
            html.Small(f"Check that {section_key}.xlsx exists in the data folder", className="text-muted")
        ], color="warning", className="mb-4")


def create_universal_controls(section_key, section_data):
    """Create universal filter controls"""
    # Extract available years
    available_years = section_data.get('available_years', [])

    if not available_years and section_data.get('success'):
        sheets = section_data.get('sheets', {})
        year_set = set()

        for sheet_info in sheets.values():
            df = sheet_info['data']
            if len(df) > 0:
                first_col_values = df.iloc[:, 0].astype(str)
                for val in first_col_values:
                    if '20' in val and len(val) > 4:
                        year_set.add(val)

        available_years = sorted(list(year_set))

    return dbc.Card([
        dbc.CardHeader([
            html.H6([
                html.I(className="fas fa-sliders-h me-2"),
                "Controls"
            ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
        ], style={'backgroundColor': USC_COLORS["primary_green"]}),
        dbc.CardBody([
            # View Mode
            html.Label("View Mode:", className="fw-bold mb-2"),
            dcc.RadioItems(
                id=f'{section_key}-view-mode',
                options=[
                    {'label': ' Numbers', 'value': 'numbers'},
                    {'label': ' Percentage', 'value': 'percentage'}
                ],
                value='numbers',
                className="mb-3"
            ),

            # Chart Type
            html.Label("Chart Type:", className="fw-bold mb-2"),
            dcc.RadioItems(
                id=f'{section_key}-chart-type',
                options=[
                    {'label': ' Bar Chart', 'value': 'bar'},
                    {'label': ' Line Chart', 'value': 'line'},
                    {'label': ' Pie Chart', 'value': 'pie'}
                ],
                value='bar',
                className="mb-3"
            ),

            # Years Filter
            html.Label("Years:", className="fw-bold mb-2"),
            dcc.Dropdown(
                id=f'{section_key}-years-filter',
                options=[{'label': year, 'value': year} for year in available_years],
                value=available_years[-3:] if len(available_years) > 3 else available_years,
                multi=True,
                className="mb-3"
            ),

            # Category Filter
            html.Label("Categories:", className="fw-bold mb-2"),
            dcc.Dropdown(
                id=f'{section_key}-category-filter',
                options=[],
                value=[],
                multi=True,
                className="mb-3"
            ),

            # Secondary Chart Controls
            html.Hr(),
            html.Label("Chart 2 Type:", className="fw-bold mb-2"),
            dcc.RadioItems(
                id=f'{section_key}-chart-type-2',
                options=[
                    {'label': ' Bar', 'value': 'bar'},
                    {'label': ' Line', 'value': 'line'}
                ],
                value='line',
                className="mb-3"
            ),

            html.Label("Chart 2 View:", className="fw-bold mb-2"),
            dcc.RadioItems(
                id=f'{section_key}-view-mode-2',
                options=[
                    {'label': ' Numbers', 'value': 'numbers'},
                    {'label': ' Percentage', 'value': 'percentage'}
                ],
                value='numbers',
                className="mb-3"
            ),

            # Third Chart Controls
            html.Hr(),
            html.Label("Chart 3 Type:", className="fw-bold mb-2"),
            dcc.RadioItems(
                id=f'{section_key}-chart-type-3',
                options=[
                    {'label': ' Trend Lines', 'value': 'line'},
                    {'label': ' Grouped Bars', 'value': 'bar'}
                ],
                value='line',
                className="mb-3"
            ),

            # Refresh Button
            dbc.Button([
                html.I(className="fas fa-sync-alt me-2"),
                "Refresh Data"
            ], id=f"{section_key}-refresh-btn", color="success", size="sm", className="w-100 mt-3")
        ])
    ])