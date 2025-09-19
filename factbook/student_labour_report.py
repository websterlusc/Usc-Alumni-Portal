"""
Student Labour Report - Using Universal Callback System
Clean, efficient implementation that automatically registers callbacks
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from universal_factbook_loader import load_factbook_section
from callback_registry import register_section_callbacks

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

def create_universal_controls(section_key: str):
    """Create universal filter controls that work with any section"""
    # Get initial data to populate filters
    section_data = load_factbook_section(section_key)
    available_years = section_data.get('available_years', [])

    # Extract years from data if not in standard format
    if not available_years and section_data.get('success'):
        sheets = section_data.get('sheets', {})
        year_set = set()

        for sheet_info in sheets.values():
            df = sheet_info['data']
            if len(df) > 0:
                # Check first column for year-like values
                first_col_values = df.iloc[:, 0].astype(str)
                for val in first_col_values:
                    if '20' in val and len(val) > 4:
                        year_set.add(val)

                # Check column names for year patterns
                for col in df.columns:
                    col_str = str(col)
                    if '20' in col_str and ('-' in col_str or '/' in col_str):
                        year_set.add(col_str)

        available_years = sorted(list(year_set))

    return dbc.Card([
        dbc.CardHeader([
            html.H6([
                html.I(className="fas fa-sliders-h me-2"),
                "Universal Controls"
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
                value=available_years,  # All years selected by default
                multi=True,
                className="mb-3"
            ),

            # Category Filter (for sections that have categories)
            html.Label("Categories:", className="fw-bold mb-2"),
            dcc.Dropdown(
                id=f'{section_key}-category-filter',
                options=[],  # Will be populated by callback
                value=[],
                multi=True,
                className="mb-3"
            ),

            # Refresh Button
            dbc.Button([
                html.I(className="fas fa-sync-alt me-2"),
                "Refresh Data"
            ], id=f"{section_key}-refresh-btn", color="success", size="sm", className="w-100 mb-2"),

            # Data Status
            html.Small([
                html.I(className="fas fa-info-circle me-1"),
                f"Loaded: {len(available_years)} years available"
            ], className="text-muted")
        ])
    ])

def create_student_labour_layout():
    """Create student labour layout using universal callback system"""

    section_key = 'student-labour'

    # Register callbacks for this section
    register_section_callbacks(section_key)

    # Get data status
    section_data = load_factbook_section(section_key)
    data_status = "success" if section_data.get('success') else "error"

    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1([
                    html.I(className="fas fa-users-cog me-3"),
                    "Student Labour Report"
                ], className="mb-4", style={"color": USC_COLORS["primary_green"]}),

                # Data Status Alert
                dbc.Alert([
                    html.I(className=f"fas fa-{'check-circle' if data_status == 'success' else 'exclamation-triangle'} me-2"),
                    html.Strong("Data Status: "),
                    "Successfully loaded from Excel file" if data_status == "success" else f"Error: {section_data.get('error', 'Unknown error')}",
                    html.Br(),
                    html.Strong("Available Years: "),
                    ", ".join(section_data.get('available_years', [])) if section_data.get('available_years') else "Years will be detected from data",
                    html.Br(),
                    html.Small("Data updates automatically when Excel file is modified", className="text-muted")
                ], color="success" if data_status == "success" else "warning", className="mb-4")
            ])
        ]),

        # Main Chart Section
        dbc.Row([
            # Controls Sidebar
            dbc.Col([
                create_universal_controls(section_key),

                # Additional Controls for Chart 2
                dbc.Card([
                    dbc.CardHeader([
                        html.H6("Secondary Chart", className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                    ], style={'backgroundColor': USC_COLORS["secondary_green"]}),
                    dbc.CardBody([
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

                        html.Label("Chart 2 Type:", className="fw-bold mb-2"),
                        dcc.RadioItems(
                            id=f'{section_key}-chart-type-2',
                            options=[
                                {'label': ' Bar Chart', 'value': 'bar'},
                                {'label': ' Line Chart', 'value': 'line'}
                            ],
                            value='line',
                            className="mb-3"
                        )
                    ])
                ], className="mt-3"),

                # Chart 3 Controls
                dbc.Card([
                    dbc.CardHeader([
                        html.H6("Monthly/Detail Chart", className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                    ], style={'backgroundColor': USC_COLORS["dark_gray"]}),
                    dbc.CardBody([
                        html.Label("Chart 3 Type:", className="fw-bold mb-2"),
                        dcc.RadioItems(
                            id=f'{section_key}-chart-type-3',
                            options=[
                                {'label': ' Line Trends', 'value': 'line'},
                                {'label': ' Monthly Bars', 'value': 'bar'}
                            ],
                            value='line',
                            className="mb-3"
                        )
                    ])
                ], className="mt-3")
            ], width=3),

            # Charts Content
            dbc.Col([
                # Primary Chart
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-chart-bar me-2"),
                            "Primary Analysis"
                        ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                    ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                    dbc.CardBody([
                        dcc.Graph(id=f'{section_key}-chart-1')
                    ])
                ], className="mb-4"),

                # Secondary Charts Row
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H6([
                                    html.I(className="fas fa-chart-line me-2"),
                                    "Secondary Analysis"
                                ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                            ], style={'backgroundColor': USC_COLORS["secondary_green"]}),
                            dbc.CardBody([
                                dcc.Graph(id=f'{section_key}-chart-2')
                            ])
                        ])
                    ], width=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H6([
                                    html.I(className="fas fa-calendar-alt me-2"),
                                    "Detailed Breakdown"
                                ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                            ], style={'backgroundColor': USC_COLORS["dark_gray"]}),
                            dbc.CardBody([
                                dcc.Graph(id=f'{section_key}-chart-3')
                            ])
                        ])
                    ], width=6)
                ])
            ], width=9)
        ]),

        # Information Footer
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.I(className="fas fa-lightbulb me-2"),
                    html.Strong("Universal System: "),
                    "This report uses the universal callback system. The same architecture powers all factbook sections. ",
                    "Charts automatically adapt to your Excel file structure. When you update the Excel file, ",
                    "refresh the data to see changes immediately.",
                    html.Br(), html.Br(),
                    html.Strong("How it works: "),
                    "The system automatically detects employment data, expense data, and monthly trends from any sheet structure. ",
                    "Filter controls dynamically populate based on available data. All 19+ factbook sections use this same system."
                ], color="info", className="mt-4")
            ])
        ])
    ], fluid=True)

# Main functions for compatibility
def create_factbook_student_labour_page():
    """Create the student labour page for the factbook"""
    return create_student_labour_layout()

# Create layout
layout = create_student_labour_layout()