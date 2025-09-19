"""
Universal Callback Registry System
Automatically registers callbacks for any factbook section
One system handles all 19+ reports without individual callback definitions
"""

from dash import html, dcc, Input, Output, callback, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from typing import Dict, List, Any
import pandas as pd

# Import the universal loader
from universal_factbook_loader import load_factbook_section

class UniversalCallbackRegistry:
    """
    Registers callbacks dynamically for any factbook section
    No need to define individual callbacks for each report
    """
    
    def __init__(self, app):
        self.app = app
        self.registered_sections = set()
    
    def register_section_callbacks(self, section_key: str):
        """Register all callbacks for a specific section"""
        if section_key in self.registered_sections:
            return  # Already registered
        
        # Register universal chart callback
        @self.app.callback(
            Output(f'{section_key}-chart-1', 'figure'),
            [Input(f'{section_key}-view-mode', 'value'),
             Input(f'{section_key}-chart-type', 'value'),
             Input(f'{section_key}-years-filter', 'value'),
             Input(f'{section_key}-category-filter', 'value'),
             Input(f'{section_key}-refresh-btn', 'n_clicks')],
            prevent_initial_call=False
        )
        def update_chart_1(view_mode, chart_type, years, categories, refresh_clicks):
            return self._universal_chart_callback(section_key, 'chart-1', view_mode, chart_type, years, categories, refresh_clicks)
        
        # Register second chart callback
        @self.app.callback(
            Output(f'{section_key}-chart-2', 'figure'),
            [Input(f'{section_key}-view-mode-2', 'value'),
             Input(f'{section_key}-chart-type-2', 'value'),
             Input(f'{section_key}-years-filter', 'value'),
             Input(f'{section_key}-refresh-btn', 'n_clicks')],
            prevent_initial_call=False
        )
        def update_chart_2(view_mode, chart_type, years, refresh_clicks):
            return self._universal_chart_callback(section_key, 'chart-2', view_mode, chart_type, years, None, refresh_clicks)
        
        # Register third chart callback
        @self.app.callback(
            Output(f'{section_key}-chart-3', 'figure'),
            [Input(f'{section_key}-chart-type-3', 'value'),
             Input(f'{section_key}-years-filter', 'value'),
             Input(f'{section_key}-refresh-btn', 'n_clicks')],
            prevent_initial_call=False
        )
        def update_chart_3(chart_type, years, refresh_clicks):
            return self._universal_chart_callback(section_key, 'chart-3', 'numbers', chart_type, years, None, refresh_clicks)
        
        # Register filter refresh callback
        @self.app.callback(
            [Output(f'{section_key}-years-filter', 'options'),
             Output(f'{section_key}-category-filter', 'options')],
            [Input(f'{section_key}-refresh-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def refresh_filters(refresh_clicks):
            return self._refresh_filter_options(section_key)
        
        self.registered_sections.add(section_key)
        print(f"Registered callbacks for section: {section_key}")
    
    def _universal_chart_callback(self, section_key: str, chart_id: str, view_mode: str, 
                                 chart_type: str, years: List[str], categories: List[str], 
                                 refresh_clicks: int):
        """Universal callback that works for any section and chart"""
        try:
            print(f"Universal callback triggered: {section_key}-{chart_id}, view={view_mode}, type={chart_type}")
            
            # Load data with force reload if refresh clicked
            force_reload = refresh_clicks and refresh_clicks > 0
            section_data = load_factbook_section(section_key, force_reload=force_reload)
            
            if not section_data.get('success'):
                return self._create_error_chart(f"Could not load {section_key} data: {section_data.get('error', 'Unknown error')}")
            
            # Create chart based on the chart_id
            if chart_id == 'chart-1':
                return self._create_primary_chart(section_data, view_mode, chart_type, years, categories)
            elif chart_id == 'chart-2':
                return self._create_secondary_chart(section_data, view_mode, chart_type, years)
            elif chart_id == 'chart-3':
                return self._create_tertiary_chart(section_data, chart_type, years)
            else:
                return self._create_error_chart("Unknown chart type")
                
        except Exception as e:
            print(f"Error in universal callback for {section_key}-{chart_id}: {e}")
            return self._create_error_chart(f"Error: {str(e)}")
    
    def _create_primary_chart(self, section_data: Dict, view_mode: str, chart_type: str, 
                             years: List[str], categories: List[str]):
        """Create the main chart for any section"""
        sheets = section_data.get('sheets', {})
        
        # Find the best sheet for visualization
        best_sheet = self._find_best_sheet(sheets)
        if not best_sheet:
            return self._create_error_chart("No suitable data found for visualization")
        
        df = best_sheet['data']
        numeric_cols = best_sheet['analysis']['numeric_columns']
        
        if not numeric_cols:
            return self._create_error_chart("No numeric data found")
        
        # Filter data by years if specified
        if years:
            df = self._filter_by_years(df, years)
        
        if df.empty:
            return self._create_error_chart("No data for selected years")
        
        # Create chart based on type
        fig = go.Figure()
        
        if chart_type == 'bar':
            fig = self._create_bar_chart(df, numeric_cols[0], view_mode)
        elif chart_type == 'line':
            fig = self._create_line_chart(df, numeric_cols[0])
        elif chart_type == 'pie':
            fig = self._create_pie_chart(df, numeric_cols[0])
        else:
            fig = self._create_bar_chart(df, numeric_cols[0], view_mode)
        
        self._apply_usc_styling(fig, f"Primary Analysis - {numeric_cols[0]}")
        return fig
    
    def _create_secondary_chart(self, section_data: Dict, view_mode: str, chart_type: str, years: List[str]):
        """Create secondary chart for comparison"""
        sheets = section_data.get('sheets', {})
        best_sheet = self._find_best_sheet(sheets)
        
        if not best_sheet:
            return self._create_error_chart("No data available")
        
        df = best_sheet['data']
        numeric_cols = best_sheet['analysis']['numeric_columns']
        
        # Use second numeric column if available, otherwise first
        col_to_use = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
        
        if years:
            df = self._filter_by_years(df, years)
        
        fig = go.Figure()
        
        if chart_type == 'line':
            fig = self._create_line_chart(df, col_to_use)
        else:
            fig = self._create_bar_chart(df, col_to_use, view_mode)
        
        self._apply_usc_styling(fig, f"Secondary Analysis - {col_to_use}")
        return fig
    
    def _create_tertiary_chart(self, section_data: Dict, chart_type: str, years: List[str]):
        """Create third chart (usually monthly or detailed breakdown)"""
        sheets = section_data.get('sheets', {})
        
        # Look for monthly or detailed data
        monthly_sheet = None
        for sheet_name, sheet_info in sheets.items():
            df = sheet_info['data']
            if len(df) > 0:
                first_col = df.iloc[:, 0].astype(str).str.lower()
                if any('month' in val or any(month in val for month in ['jan', 'feb', 'mar']) for val in first_col):
                    monthly_sheet = sheet_info
                    break
        
        if not monthly_sheet:
            monthly_sheet = self._find_best_sheet(sheets)
        
        if not monthly_sheet:
            return self._create_error_chart("No monthly data available")
        
        df = monthly_sheet['data']
        numeric_cols = monthly_sheet['analysis']['numeric_columns']
        
        if not numeric_cols:
            return self._create_error_chart("No numeric data for monthly chart")
        
        fig = go.Figure()
        
        # Create monthly trend chart
        if chart_type == 'line':
            fig = self._create_trend_chart(df, numeric_cols)
        else:
            fig = self._create_monthly_bar_chart(df, numeric_cols, years)
        
        self._apply_usc_styling(fig, "Monthly/Detailed Analysis")
        return fig
    
    def _find_best_sheet(self, sheets: Dict) -> Dict:
        """Find the sheet with the most useful data"""
        best_sheet = None
        max_numeric_cols = 0
        
        for sheet_info in sheets.values():
            numeric_count = len(sheet_info['analysis']['numeric_columns'])
            if numeric_count > max_numeric_cols:
                max_numeric_cols = numeric_count
                best_sheet = sheet_info
        
        return best_sheet
    
    def _filter_by_years(self, df: pd.DataFrame, years: List[str]) -> pd.DataFrame:
        """Filter DataFrame by year values"""
        if not years:
            return df
        
        # Try to filter by first column (usually contains years)
        first_col = df.iloc[:, 0].astype(str)
        mask = first_col.str.contains('|'.join(years), case=False, na=False)
        
        return df[mask] if mask.any() else df
    
    def _create_bar_chart(self, df: pd.DataFrame, col: str, view_mode: str):
        """Create bar chart"""
        fig = go.Figure()
        
        x_values = df.iloc[:, 0].astype(str)  # First column as x-axis
        y_values = df[col]
        
        if view_mode == 'percentage' and y_values.sum() > 0:
            y_values = (y_values / y_values.sum() * 100).round(1)
            text_values = [f"{val}%" for val in y_values]
        else:
            text_values = [f"{val:,.0f}" if pd.notnull(val) else "0" for val in y_values]
        
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            text=text_values,
            textposition='outside',
            marker_color='#1B5E20'
        ))
        
        return fig
    
    def _create_line_chart(self, df: pd.DataFrame, col: str):
        """Create line chart"""
        fig = go.Figure()
        
        x_values = df.iloc[:, 0].astype(str)
        y_values = df[col]
        
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            line=dict(color='#1B5E20', width=3),
            marker=dict(size=8, color='#1B5E20')
        ))
        
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, col: str):
        """Create pie chart"""
        fig = go.Figure()
        
        labels = df.iloc[:, 0].astype(str)
        values = df[col]
        
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            textinfo='label+percent+value',
            marker=dict(colors=['#1B5E20', '#4CAF50', '#FDD835', '#28A745'])
        ))
        
        return fig
    
    def _create_trend_chart(self, df: pd.DataFrame, numeric_cols: List[str]):
        """Create multi-line trend chart"""
        fig = go.Figure()
        colors = ['#1B5E20', '#4CAF50', '#FDD835']
        
        x_values = df.iloc[:, 0].astype(str)
        
        for i, col in enumerate(numeric_cols[:3]):  # Max 3 lines
            fig.add_trace(go.Scatter(
                x=x_values,
                y=df[col],
                mode='lines+markers',
                name=str(col),
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=6)
            ))
        
        return fig
    
    def _create_monthly_bar_chart(self, df: pd.DataFrame, numeric_cols: List[str], years: List[str]):
        """Create monthly bar chart"""
        fig = go.Figure()
        colors = ['#1B5E20', '#4CAF50', '#FDD835']
        
        x_values = df.iloc[:, 0].astype(str)
        
        # Show up to 3 year columns
        year_cols = [col for col in numeric_cols if any(year in str(col) for year in years)] if years else numeric_cols[:3]
        
        for i, col in enumerate(year_cols):
            fig.add_trace(go.Bar(
                x=x_values,
                y=df[col],
                name=str(col),
                marker_color=colors[i % len(colors)]
            ))
        
        fig.update_layout(barmode='group')
        return fig
    
    def _apply_usc_styling(self, fig, title: str):
        """Apply consistent USC styling to any chart"""
        fig.update_layout(
            title=dict(text=title, font=dict(size=16, color='black')),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(title_font=dict(color='black'), tickfont=dict(color='black'))
        fig.update_yaxes(title_font=dict(color='black'), tickfont=dict(color='black'))
    
    def _create_error_chart(self, message: str):
        """Create error chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=500, title="Error")
        return fig
    
    def _refresh_filter_options(self, section_key: str):
        """Refresh filter options for a section"""
        try:
            section_data = load_factbook_section(section_key, force_reload=True)
            
            # Extract years
            available_years = section_data.get('available_years', [])
            if not available_years and section_data.get('success'):
                sheets = section_data.get('sheets', {})
                year_set = set()
                
                for sheet_info in sheets.values():
                    df = sheet_info['data']
                    if len(df) > 0:
                        # Check first column for years
                        first_col_values = df.iloc[:, 0].astype(str)
                        for val in first_col_values:
                            if '20' in val and len(val) > 4:
                                year_set.add(val)
                
                available_years = sorted(list(year_set))
            
            year_options = [{'label': year, 'value': year} for year in available_years]
            
            # Extract categories (first few unique values from first text column)
            category_options = []
            if section_data.get('success'):
                sheets = section_data.get('sheets', {})
                for sheet_info in sheets.values():
                    df = sheet_info['data']
                    text_cols = sheet_info['analysis']['text_columns']
                    if text_cols:
                        unique_values = df[text_cols[0]].unique()[:10]  # Max 10 categories
                        category_options = [{'label': str(val), 'value': str(val)} for val in unique_values if pd.notnull(val)]
                        break
            
            return year_options, category_options
            
        except Exception as e:
            print(f"Error refreshing filters for {section_key}: {e}")
            return [], []


# Global registry instance
callback_registry = None

def initialize_callback_registry(app):
    """Initialize the callback registry with the main app"""
    global callback_registry
    callback_registry = UniversalCallbackRegistry(app)
    return callback_registry

def register_section_callbacks(section_key: str):
    """Register callbacks for a specific section"""
    if callback_registry:
        callback_registry.register_section_callbacks(section_key)