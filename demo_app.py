#!/usr/bin/env python3
"""
USC Institutional Research Portal - Demo Version
Quick deployment version with minimal dependencies
"""

import os
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Expose Flask server for Gunicorn

# USC Brand Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F5F5F5'
}

# Sample data for demo
enrollment_data = pd.DataFrame({
    'Academic Year': ['2021-2022', '2022-2023', '2023-2024', '2024-2025'],
    'Total Students': [3410, 3130, 2778, 3110]
})

graduation_data = pd.DataFrame({
    'Program': ['Business', 'Education', 'Sciences', 'Theology', 'Social Sciences'],
    'Graduates': [45, 32, 28, 15, 23]
})

employment_data = pd.DataFrame({
    'Year': ['2021-2022', '2022-2023', '2023-2024'],
    'Academic Employment': [28, 36, 39],
    'Non-Academic Employment': [22, 108, 116]
})

def create_navbar():
    """Create navigation bar"""
    return dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Img(
                        src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiMxQjVFMjAiLz4KPHR2eHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5VU0M8L3RleHQ+Cjwvc3ZnPgo=",
                        height="40px",
                        className="me-2"
                    ),
                    dbc.NavbarBrand("USC Institutional Research Portal", 
                                  style={'color': USC_COLORS['white'], 'fontWeight': 'bold'})
                ], width="auto"),
                dbc.Col([
                    dbc.Badge("Demo Version", color="warning", className="ms-2")
                ], width="auto")
            ], align="center", className="w-100 justify-content-between")
        ], fluid=True)
    ], color=USC_COLORS['primary_green'], dark=True, className="mb-4")

def create_overview_cards():
    """Create overview cards with key metrics"""
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-user-graduate fa-3x text-primary mb-3"),
                        html.H3("3,110", className="text-primary mb-1"),
                        html.P("Current Enrollment", className="card-text mb-2"),
                        html.Small("Academic Year 2024-2025", className="text-muted")
                    ], className="text-center")
                ])
            ], className="h-100 shadow-sm")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-briefcase fa-3x text-success mb-3"),
                        html.H3("155", className="text-success mb-1"),
                        html.P("Student Employees", className="card-text mb-2"),
                        html.Small("Academic & Non-Academic", className="text-muted")
                    ], className="text-center")
                ])
            ], className="h-100 shadow-sm")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-graduation-cap fa-3x text-info mb-3"),
                        html.H3("143", className="text-info mb-1"),
                        html.P("Expected Graduates", className="card-text mb-2"),
                        html.Small("May 2025 Cohort", className="text-muted")
                    ], className="text-center")
                ])
            ], className="h-100 shadow-sm")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-3x text-warning mb-3"),
                        html.H3("$18.5M", className="text-warning mb-1"),
                        html.P("Annual Revenue", className="card-text mb-2"),
                        html.Small("Fiscal Year 2024", className="text-muted")
                    ], className="text-center")
                ])
            ], className="h-100 shadow-sm")
        ], md=3)
    ], className="mb-4")
    
    return cards

def create_enrollment_chart():
    """Create enrollment trend chart"""
    fig = px.line(enrollment_data, 
                  x='Academic Year', 
                  y='Total Students',
                  title='USC Enrollment Trends (2021-2025)',
                  color_discrete_sequence=[USC_COLORS['primary_green']])
    
    fig.update_layout(
        template="plotly_white",
        height=400,
        xaxis_title="Academic Year",
        yaxis_title="Number of Students"
    )
    
    fig.add_annotation(
        x='2024-2025',
        y=3110,
        text="Current: 3,110<br>+12% from 2023",
        showarrow=True,
        arrowhead=2,
        arrowcolor=USC_COLORS['primary_green']
    )
    
    return dcc.Graph(figure=fig)

def create_graduation_chart():
    """Create graduation by program chart"""
    fig = px.bar(graduation_data,
                 x='Program',
                 y='Graduates',
                 title='Expected Graduates by Program (May 2025)',
                 color_discrete_sequence=[USC_COLORS['secondary_green']])
    
    fig.update_layout(
        template="plotly_white",
        height=400,
        xaxis_title="Academic Program",
        yaxis_title="Number of Graduates"
    )
    
    return dcc.Graph(figure=fig)

def create_employment_chart():
    """Create student employment chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Academic Employment',
        x=employment_data['Year'],
        y=employment_data['Academic Employment'],
        marker_color=USC_COLORS['primary_green']
    ))
    
    fig.add_trace(go.Bar(
        name='Non-Academic Employment',
        x=employment_data['Year'],
        y=employment_data['Non-Academic Employment'],
        marker_color=USC_COLORS['secondary_green']
    ))
    
    fig.update_layout(
        title='Student Employment Trends',
        xaxis_title='Academic Year',
        yaxis_title='Number of Students',
        barmode='stack',
        template="plotly_white",
        height=400
    )
    
    return dcc.Graph(figure=fig)

def create_navigation_tabs():
    """Create navigation tabs for different sections"""
    return dbc.Tabs([
        dbc.Tab(label="Overview", tab_id="overview", active_tab_style={"backgroundColor": USC_COLORS['primary_green']}),
        dbc.Tab(label="Enrollment", tab_id="enrollment"),
        dbc.Tab(label="Graduation", tab_id="graduation"),
        dbc.Tab(label="Employment", tab_id="employment"),
        dbc.Tab(label="Financial", tab_id="financial")
    ], id="navigation-tabs", active_tab="overview", className="mb-4")

# App layout
app.layout = html.Div([
    create_navbar(),
    
    dbc.Container([
        # Header
        html.Div([
            html.H1("University of the Southern Caribbean", 
                   className="display-4 fw-bold text-center mb-2",
                   style={'color': USC_COLORS['primary_green']}),
            html.H2("Institutional Research Portal", 
                   className="text-center text-muted mb-4"),
            html.Hr()
        ]),
        
        # Navigation tabs
        create_navigation_tabs(),
        
        # Dynamic content area
        html.Div(id="tab-content")
        
    ], fluid=True),
    
    # Footer
    html.Footer([
        dbc.Container([
            html.Hr(),
            html.P("© 2025 University of the Southern Caribbean | Department of Institutional Research",
                  className="text-center text-muted"),
            html.P("Demo Version - For demonstration purposes only",
                  className="text-center text-muted small")
        ])
    ], className="mt-5")
])

# Callback for tab content
@callback(
    Output('tab-content', 'children'),
    Input('navigation-tabs', 'active_tab')
)
def update_tab_content(active_tab):
    if active_tab == "overview":
        return html.Div([
            create_overview_cards(),
            dbc.Row([
                dbc.Col([
                    create_enrollment_chart()
                ], md=6),
                dbc.Col([
                    create_graduation_chart()
                ], md=6)
            ])
        ])
    
    elif active_tab == "enrollment":
        return html.Div([
            html.H3("Enrollment Analytics", className="mb-4"),
            dbc.Row([
                dbc.Col([
                    create_enrollment_chart()
                ], md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Enrollment Summary"),
                        dbc.CardBody([
                            html.P(f"Current Total: {enrollment_data.iloc[-1]['Total Students']:,} students"),
                            html.P(f"YoY Change: +{((3110-2778)/2778)*100:.1f}%"),
                            html.P("Peak Enrollment: 3,410 (2021-2022)"),
                            html.P("Lowest Enrollment: 2,778 (2023-2024)"),
                            html.Hr(),
                            html.H6("Key Insights:"),
                            html.Ul([
                                html.Li("Strong recovery in 2024-2025"),
                                html.Li("12% increase from previous year"),
                                html.Li("Approaching pre-pandemic levels")
                            ])
                        ])
                    ])
                ], md=4)
            ])
        ])
    
    elif active_tab == "graduation":
        return html.Div([
            html.H3("Graduation Statistics", className="mb-4"),
            dbc.Row([
                dbc.Col([
                    create_graduation_chart()
                ], md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Graduation Highlights"),
                        dbc.CardBody([
                            html.P("Total Expected Graduates: 143"),
                            html.P("Graduation Rate: 85%"),
                            html.P("Top Program: Business (45 graduates)"),
                            html.Hr(),
                            html.H6("Program Distribution:"),
                            html.Ul([
                                html.Li("Business: 31.5%"),
                                html.Li("Education: 22.4%"),
                                html.Li("Sciences: 19.6%"),
                                html.Li("Theology: 10.5%"),
                                html.Li("Social Sciences: 16.1%")
                            ])
                        ])
                    ])
                ], md=4)
            ])
        ])
    
    elif active_tab == "employment":
        return html.Div([
            html.H3("Student Employment", className="mb-4"),
            dbc.Row([
                dbc.Col([
                    create_employment_chart()
                ], md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Employment Statistics"),
                        dbc.CardBody([
                            html.P("Total Student Employees: 155"),
                            html.P("Academic Positions: 39"),
                            html.P("Non-Academic Positions: 116"),
                            html.P("Employment Growth: +18% YoY"),
                            html.Hr(),
                            html.H6("Employment Benefits:"),
                            html.Ul([
                                html.Li("Tuition assistance"),
                                html.Li("Professional development"),
                                html.Li("Work-study programs"),
                                html.Li("Career preparation")
                            ])
                        ])
                    ])
                ], md=4)
            ])
        ])
    
    elif active_tab == "financial":
        return html.Div([
            html.H3("Financial Overview", className="mb-4"),
            dbc.Alert([
                html.H4("🔒 Restricted Access", className="alert-heading"),
                html.P("Financial data requires Tier 3 access level."),
                html.Hr(),
                html.P("Please contact the Institutional Research office for access to detailed financial reports."),
                dbc.Button("Request Access", color="primary", className="mt-2")
            ], color="warning")
        ])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print("🎓 Starting USC IR Portal Demo...")
    print(f"📍 Running on port: {port}")
    app.run_server(debug=False, host='0.0.0.0', port=port)
