#!/usr/bin/env python3
"""
USC Institutional Research Portal - Production Ready
Fixed for Render deployment
"""

import os
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from flask import Flask
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Import your existing components and pages
from components.navbar import create_navbar
from components.home_page import create_homepage
from components.admin_dashboard import create_admin_dashboard_page

# ... import other components as needed

# Configuration
DATABASE = 'usc_ir.db'
SECRET_KEY = os.getenv('SECRET_KEY', 'usc-ir-secret-key-production-2025')
IS_PRODUCTION = os.environ.get('RENDER') is not None


def init_database():
    """Initialize database with error handling for production"""
    try:
        if os.path.exists(DATABASE):
            print("✅ Database already exists")
            return True

        print("🔧 Creating production database...")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Users table with all required columns
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                access_tier INTEGER DEFAULT 2,
                is_admin BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                department TEXT,
                position TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP NULL,
                created_by INTEGER REFERENCES users(id)
            )
        ''')

        # User sessions table
        cursor.execute('''
            CREATE TABLE user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                user_email TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Access requests table
        cursor.execute('''
            CREATE TABLE access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                requested_tier INTEGER NOT NULL,
                current_tier INTEGER DEFAULT 1,
                justification TEXT,
                status TEXT DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by INTEGER,
                reviewed_at TIMESTAMP,
                approved_until TIMESTAMP,
                notes TEXT,
                request_type TEXT DEFAULT 'tier_upgrade',
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (reviewed_by) REFERENCES users (id)
            )
        ''')

        # Create default admin user for production
        admin_password = "admin123!USC"
        admin_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, access_tier, is_admin, department, position)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
        'admin', 'ir@usc.edu.tt', admin_hash, 'IR Administrator', 3, True, 'Institutional Research', 'Administrator'))

        conn.commit()
        conn.close()
        print("✅ Database created successfully")
        return True

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # In production, try to continue without database for basic functionality
        if IS_PRODUCTION:
            print("⚠️ Continuing in read-only mode...")
            return False
        else:
            raise e


def create_app():
    """Create and configure the Dash application"""

    # Initialize database
    db_ready = init_database()

    # Flask server
    server = Flask(__name__)
    server.secret_key = SECRET_KEY

    # Dash app
    app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
        ],
        title="USC Institutional Research",
        suppress_callback_exceptions=True
    )

    # App layout
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='session-store', storage_type='session'),
        html.Div(id='page-content')
    ])

    # Import and setup your existing callbacks here
    # from callbacks.auth_callbacks import setup_auth_callbacks
    # from callbacks.page_callbacks import setup_page_callbacks
    # setup_auth_callbacks(app)
    # setup_page_callbacks(app)

    # Basic page routing callback
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')],
        prevent_initial_call=False
    )
    def display_page(pathname):
        """Basic page routing - replace with your existing routing logic"""
        try:
            if pathname == '/' or pathname is None:
                return create_homepage(user=None)  # Adjust based on your function signature
            elif pathname == '/admin':
                return create_admin_dashboard_page()
            else:
                return html.Div([
                    html.H2("404 - Page Not Found"),
                    html.P(f"The page '{pathname}' was not found."),
                    dcc.Link("Return to Home", href="/")
                ])
        except Exception as e:
            return html.Div([
                html.H2("Application Error"),
                html.P(f"An error occurred: {str(e)}"),
                dcc.Link("Return to Home", href="/")
            ])

    # Add any Flask routes here
    @server.route('/health')
    def health_check():
        """Health check endpoint for Render"""
        return {'status': 'healthy', 'database': db_ready}

    return app


# Create the app instance
app = create_app()

# CRITICAL: Expose the Flask server for Gunicorn
server = app.server

# Only for local development
if __name__ == '__main__':
    print("🎓 Starting USC Institutional Research Portal...")
    print("✅ Application initialized")

    if not IS_PRODUCTION:
        print("📍 Development mode - Access the portal at: http://localhost:8050")
        print("🔑 Default admin login: ir@usc.edu.tt / admin123!USC")
        app.run_server(debug=True, host='0.0.0.0', port=8050)
    else:
        print("🚀 Production mode - Ready for Gunicorn")