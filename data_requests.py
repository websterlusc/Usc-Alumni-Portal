"""
Data Requests Module for USC Institutional Research Portal
Complete standalone module with database, UI, and callback functions
"""

import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import dash
from dash import html, dcc, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc

# USC Brand Colors - import from your main app if needed
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA'
}


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def init_data_requests_database():
    """Initialize data requests table with proper migration handling"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Check if table exists and get its columns
        cursor.execute("PRAGMA table_info(data_requests)")
        existing_columns = [column[1] for column in cursor.fetchall()]

        if not existing_columns:
            # Create new table if it doesn't exist
            cursor.execute('''
                CREATE TABLE data_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    requester_name TEXT NOT NULL,
                    requester_email TEXT NOT NULL,
                    organization TEXT,
                    position TEXT,
                    category TEXT NOT NULL,
                    priority TEXT DEFAULT 'standard',
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    file_formats TEXT NOT NULL,
                    deadline_date TEXT,
                    additional_notes TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_to INTEGER,
                    completed_at TIMESTAMP,
                    admin_notes TEXT,
                    FOREIGN KEY (assigned_to) REFERENCES users (id)
                )
            ''')
            print("✅ Created new data_requests table")
        else:
            # Handle migration - drop and recreate table
            print("🔄 Migrating data_requests table...")
            cursor.execute('DROP TABLE IF EXISTS data_requests')
            cursor.execute('''
                CREATE TABLE data_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    requester_name TEXT NOT NULL,
                    requester_email TEXT NOT NULL,
                    organization TEXT,
                    position TEXT,
                    category TEXT NOT NULL,
                    priority TEXT DEFAULT 'standard',
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    file_formats TEXT NOT NULL,
                    deadline_date TEXT,
                    additional_notes TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_to INTEGER,
                    completed_at TIMESTAMP,
                    admin_notes TEXT,
                    FOREIGN KEY (assigned_to) REFERENCES users (id)
                )
            ''')
            print("✅ Migrated data_requests table successfully")

        conn.commit()

    except Exception as e:
        print(f"❌ Error with data_requests table: {str(e)}")
    finally:
        conn.close()


def save_data_request(data):
    """Save data request to database"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO data_requests (
                requester_name, requester_email, organization, position,
                category, priority, title, description, purpose, file_formats,
                deadline_date, additional_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], data['email'], data['organization'], data['position'],
            data['category'], data['priority'], data['title'], data['description'],
            data['purpose'], data['formats'], data['deadline'], data['notes']
        ))

        request_id = cursor.lastrowid
        conn.commit()

        # Send email notification
        send_request_emails(data, request_id)

        return {"success": True, "id": request_id}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def send_request_emails(data, request_id):
    """Send email notifications"""
    try:
        smtp_user = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')

        if not smtp_user or not smtp_password:
            print(f"Request #{request_id} saved - email disabled (no SMTP config)")
            return True

        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = 'ir@usc.edu.tt'
        msg['Reply-To'] = data['email']
        msg['Subject'] = f"New Data Request #{request_id}: {data['title']}"

        body = f"""New Data Request #{request_id}

From: {data['name']} ({data['email']})
Organization: {data['organization'] or 'Not specified'}
Category: {data['category']}
Title: {data['title']}

Description:
{data['description']}

Purpose:
{data['purpose']}

Check the admin dashboard to manage this request.
"""

        msg.attach(MIMEText(body, 'plain'))

        # Try SSL port 465 instead of 587
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, 'ir@usc.edu.tt', msg.as_string())
        server.quit()

        print(f"Email sent for request #{request_id}")
        return True

    except Exception as e:
        print(f"Email error: {str(e)}")
        return True
def get_all_data_requests():
    """Get all data requests for admin"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT dr.*, u.full_name as assigned_name
            FROM data_requests dr
            LEFT JOIN users u ON dr.assigned_to = u.id
            ORDER BY dr.created_at DESC
        ''')
        return cursor.fetchall()
    finally:
        conn.close()


def update_request_status(request_id, status, admin_id, notes=None):
    """Update request status"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        if status == 'completed':
            cursor.execute('''
                UPDATE data_requests 
                SET status = ?, assigned_to = ?, admin_notes = ?, completed_at = ?
                WHERE id = ?
            ''', (status, admin_id, notes, datetime.now(), request_id))
        else:
            cursor.execute('''
                UPDATE data_requests 
                SET status = ?, assigned_to = ?, admin_notes = ?
                WHERE id = ?
            ''', (status, admin_id, notes, request_id))

        conn.commit()
        return {"success": True, "message": f"Request marked as {status}"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
    finally:
        conn.close()


def get_request_stats():
    """Get request statistics for admin dashboard"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        stats = {}

        # Total requests
        cursor.execute('SELECT COUNT(*) FROM data_requests')
        stats['total'] = cursor.fetchone()[0]

        # By status
        cursor.execute('SELECT status, COUNT(*) FROM data_requests GROUP BY status')
        stats['by_status'] = dict(cursor.fetchall())

        # Recent (last 30 days)
        cursor.execute('''
            SELECT COUNT(*) FROM data_requests 
            WHERE created_at > datetime('now', '-30 days')
        ''')
        stats['recent'] = cursor.fetchone()[0]

        return stats
    finally:
        conn.close()


# ============================================================================
# UI COMPONENTS
# ============================================================================

def create_data_request_page():
    """Public data request form"""
    return dbc.Container([
        html.H1("Data Request Service", className="text-center display-4 mb-4",
                style={'color': USC_COLORS['primary_green']}),

        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "Request custom data reports from the USC Institutional Research team. "
                    "No login required. Typical response: 5-10 business days."
                ], color="info", className="mb-4")
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id="data-request-alerts"),

                        dbc.Form([
                            # Contact Information
                            html.H5("Contact Information", className="mb-3",
                                    style={'color': USC_COLORS['primary_green']}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Full Name *"),
                                    dbc.Input(id="dr-name", placeholder="Enter your full name", className="mb-3")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Email Address *"),
                                    dbc.Input(id="dr-email", type="email",
                                              placeholder="your.email@example.com", className="mb-3")
                                ], md=6)
                            ]),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Organization/Department"),
                                    dbc.Input(id="dr-org", placeholder="USC Department, External Org, etc.",
                                              className="mb-3")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Position/Title"),
                                    dbc.Input(id="dr-position", placeholder="Your role or position",
                                              className="mb-3")
                                ], md=6)
                            ]),

                            html.Hr(),

                            # Request Details
                            html.H5("Request Details", className="mb-3",
                                    style={'color': USC_COLORS['primary_green']}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Category *"),
                                    dbc.Select(
                                        id="dr-category",
                                        options=[
                                            {"label": "Select category...", "value": ""},
                                            {"label": "Enrollment & Registration", "value": "enrollment"},
                                            {"label": "Graduation & Completion", "value": "graduation"},
                                            {"label": "Student Demographics", "value": "demographics"},
                                            {"label": "Faculty & Staff Data", "value": "faculty"},
                                            {"label": "Financial Reports", "value": "financial"},
                                            {"label": "Academic Programs", "value": "programs"},
                                            {"label": "Student Success", "value": "success"},
                                            {"label": "Historical Trends", "value": "historical"},
                                            {"label": "Custom Analysis", "value": "custom"},
                                            {"label": "Other", "value": "other"}
                                        ],
                                        className="mb-3"
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Priority"),
                                    dbc.Select(
                                        id="dr-priority",
                                        options=[
                                            {"label": "Standard (5-10 days)", "value": "standard"},
                                            {"label": "High (2-5 days)", "value": "high"},
                                            {"label": "Urgent (1-2 days)", "value": "urgent"}
                                        ],
                                        value="standard",
                                        className="mb-3"
                                    )
                                ], md=6)
                            ]),

                            dbc.Label("Request Title *"),
                            dbc.Input(id="dr-title", placeholder="Brief title for your request", className="mb-3"),

                            dbc.Label("Detailed Description *"),
                            dbc.Textarea(
                                id="dr-description",
                                placeholder="Describe the specific data you need, time periods, populations, level of detail, etc.",
                                rows=5,
                                className="mb-3"
                            ),

                            dbc.Label("Purpose/Justification *"),
                            dbc.Textarea(
                                id="dr-purpose",
                                placeholder="How will this data be used? (research, planning, accreditation, etc.)",
                                rows=3,
                                className="mb-3"
                            ),

                            html.Hr(),

                            # Delivery Preferences
                            html.H5("Delivery Preferences", className="mb-3",
                                    style={'color': USC_COLORS['primary_green']}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("File Formats *"),
                                    dbc.Checklist(
                                        id="dr-formats",
                                        options=[
                                            {"label": "Excel (.xlsx)", "value": "excel"},
                                            {"label": "CSV (.csv)", "value": "csv"},
                                            {"label": "PDF Report", "value": "pdf"},
                                            {"label": "PowerPoint (.pptx)", "value": "powerpoint"},
                                            {"label": "Word Document (.docx)", "value": "word"}
                                        ],
                                        value=["excel"],
                                        className="mb-3"
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Required By Date"),
                                    dbc.Input(id="dr-deadline", type="date", className="mb-3"),
                                    html.Small("Leave blank for standard processing", className="text-muted")
                                ], md=6)
                            ]),

                            dbc.Label("Additional Notes"),
                            dbc.Textarea(
                                id="dr-notes",
                                placeholder="Any additional requirements or questions...",
                                rows=3,
                                className="mb-4"
                            ),

                            # Agreement
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6("Data Use Agreement"),
                                    html.P([
                                        "By submitting this request, I agree to use the data only for the stated purpose, ",
                                        "maintain confidentiality, and acknowledge USC IR as the source."
                                    ], className="small"),
                                    dbc.Checklist(
                                        id="dr-agreement",
                                        options=[{"label": "I agree to these terms", "value": "agreed"}]
                                    )
                                ])
                            ], color="light", className="mb-4"),

                            # Submit Button
                            dbc.Button(
                                [html.I(className="fas fa-paper-plane me-2"), "Submit Request"],
                                id="dr-submit-btn",
                                color="success",
                                size="lg",
                                className="w-100"
                            )
                        ])
                    ])
                ], className="shadow")
            ], lg=8, className="mx-auto")
        ])
    ], className="py-5")


def create_admin_data_requests_tab():
    """Admin data requests management tab"""
    return html.Div([
        # Stats Overview
        html.Div(id="data-requests-stats"),

        html.Hr(),

        # Filters
        dbc.Row([
            dbc.Col([
                dbc.Input(id="dr-admin-search", placeholder="Search requests...", className="mb-3")
            ], md=4),
            dbc.Col([
                dbc.Select(
                    id="dr-admin-status-filter",
                    options=[
                        {"label": "All Status", "value": "all"},
                        {"label": "Pending", "value": "pending"},
                        {"label": "In Progress", "value": "in_progress"},
                        {"label": "Completed", "value": "completed"},
                        {"label": "Denied", "value": "denied"}
                    ],
                    value="all",
                    className="mb-3"
                )
            ], md=3),
            dbc.Col([
                dbc.Button("Refresh", id="dr-admin-refresh", color="outline-primary", className="w-100 mb-3")
            ], md=2)
        ]),

        # Requests List
        html.Div(id="data-requests-list")
    ])


def render_data_requests_stats():
    """Render data requests statistics"""
    stats = get_request_stats()

    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(str(stats.get('by_status', {}).get('pending', 0)), className="text-warning"),
                    html.P("Pending", className="mb-0")
                ])
            ])
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(str(stats.get('by_status', {}).get('in_progress', 0)), className="text-primary"),
                    html.P("In Progress", className="mb-0")
                ])
            ])
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(str(stats.get('by_status', {}).get('completed', 0)), className="text-success"),
                    html.P("Completed", className="mb-0")
                ])
            ])
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(str(stats.get('recent', 0)), className="text-info"),
                    html.P("Last 30 Days", className="mb-0")
                ])
            ])
        ], md=3)
    ], className="mb-4")


def render_data_requests_list():
    """Render list of data requests for admin"""
    requests = get_all_data_requests()

    if not requests:
        return dbc.Alert("No data requests found", color="info")

    cards = []
    for req in requests:
        (req_id, name, email, org, position, category, priority, title,
         description, purpose, formats, deadline, notes, status, created_at,
         assigned_to, completed_at, admin_notes, assigned_name) = req

        # Status badge
        status_colors = {
            'pending': 'warning',
            'in_progress': 'primary',
            'completed': 'success',
            'denied': 'danger'
        }

        status_badge = dbc.Badge(
            status.replace('_', ' ').title(),
            color=status_colors.get(status, 'secondary')
        )

        # Priority badge
        priority_colors = {'standard': 'secondary', 'high': 'warning', 'urgent': 'danger'}
        priority_badge = dbc.Badge(priority.title(), color=priority_colors.get(priority, 'secondary'))

        card = dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        html.H5(f"#{req_id}: {title}", className="mb-1"),
                        html.P(f"by {name} ({email})", className="text-muted small mb-0")
                    ], md=8),
                    dbc.Col([
                        html.Div([status_badge, " ", priority_badge], className="text-end")
                    ], md=4)
                ])
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.P([
                            html.Strong("Category: "), category.replace('_', ' ').title(), html.Br(),
                            html.Strong("Organization: "), org or 'Not specified', html.Br(),
                            html.Strong("Created: "), created_at[:10] if created_at else 'N/A', html.Br(),
                            html.Strong("Deadline: "), deadline or 'Not specified'
                        ], className="small"),

                        html.Details([
                            html.Summary("View Description", className="fw-bold text-primary"),
                            html.P(description, className="mt-2 small")
                        ], className="mt-2")
                    ], md=8),
                    dbc.Col([
                        html.P([
                            html.Strong("Formats: "), html.Br(), formats
                        ], className="small mb-3"),

                        dbc.ButtonGroup([
                            dbc.Button("Assign to Me",
                                       id={"type": "assign-request", "id": req_id},
                                       color="outline-primary", size="sm"),
                            dbc.DropdownMenu([
                                dbc.DropdownMenuItem("Mark In Progress",
                                                     id={"type": "status-progress", "id": req_id}),
                                dbc.DropdownMenuItem("Mark Completed",
                                                     id={"type": "status-completed", "id": req_id}),
                                dbc.DropdownMenuItem("Mark Denied",
                                                     id={"type": "status-denied", "id": req_id})
                            ], label="Actions", color="primary", size="sm")
                        ], vertical=True)
                    ], md=4)
                ])
            ])
        ], className="mb-3")

        cards.append(card)

    return html.Div([
        html.H4(f"Data Requests ({len(requests)})", className="mb-3"),
        html.Div(cards)
    ])


# ============================================================================
# CALLBACKS
# ============================================================================

# Data request form submission
@callback(
    [Output('data-request-alerts', 'children'),
     Output('dr-name', 'value'),
     Output('dr-email', 'value'),
     Output('dr-org', 'value'),
     Output('dr-position', 'value'),
     Output('dr-category', 'value'),
     Output('dr-priority', 'value'),
     Output('dr-title', 'value'),
     Output('dr-description', 'value'),
     Output('dr-purpose', 'value'),
     Output('dr-formats', 'value'),
     Output('dr-deadline', 'value'),
     Output('dr-notes', 'value'),
     Output('dr-agreement', 'value')],
    Input('dr-submit-btn', 'n_clicks'),
    [State('dr-name', 'value'),
     State('dr-email', 'value'),
     State('dr-org', 'value'),
     State('dr-position', 'value'),
     State('dr-category', 'value'),
     State('dr-priority', 'value'),
     State('dr-title', 'value'),
     State('dr-description', 'value'),
     State('dr-purpose', 'value'),
     State('dr-formats', 'value'),
     State('dr-deadline', 'value'),
     State('dr-notes', 'value'),
     State('dr-agreement', 'value')],
    prevent_initial_call=True
)
def handle_data_request_submission(n_clicks, name, email, org, position, category, priority,
                                   title, description, purpose, formats, deadline, notes, agreement):
    if not n_clicks:
        return [dash.no_update] * 14

    # Validation
    errors = []
    if not name or not name.strip():
        errors.append("Full name is required")
    if not email or '@' not in email:
        errors.append("Valid email is required")
    if not category:
        errors.append("Category is required")
    if not title or not title.strip():
        errors.append("Title is required")
    if not description or len(description.strip()) < 20:
        errors.append("Description must be at least 20 characters")
    if not purpose or len(purpose.strip()) < 20:
        errors.append("Purpose must be at least 20 characters")
    if not formats:
        errors.append("At least one file format is required")
    if not agreement or 'agreed' not in agreement:
        errors.append("You must agree to the terms")

    if errors:
        alert = dbc.Alert([
            html.H6("Please fix these errors:"),
            html.Ul([html.Li(error) for error in errors])
        ], color="danger", dismissable=True)
        return [alert] + [dash.no_update] * 13

    # Save request
    data = {
        'name': name.strip(),
        'email': email.strip().lower(),
        'organization': org.strip() if org else None,
        'position': position.strip() if position else None,
        'category': category,
        'priority': priority,
        'title': title.strip(),
        'description': description.strip(),
        'purpose': purpose.strip(),
        'formats': ', '.join(formats),
        'deadline': deadline,
        'notes': notes.strip() if notes else None
    }

    result = save_data_request(data)

    if result['success']:
        alert = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            f"Request submitted successfully! Request ID: #{result['id']}"
        ], color="success", dismissable=True)
        # Clear form
        return [alert, "", "", "", "", "", "standard", "", "", "", ["excel"], "", "", []]
    else:
        alert = dbc.Alert(f"Error: {result['error']}", color="danger")
        return [alert] + [dash.no_update] * 13


# Admin data requests callbacks
@callback(
    Output('data-requests-stats', 'children'),
    Input('dr-admin-refresh', 'n_clicks'),
    prevent_initial_call=False
)
def update_data_requests_stats(n_clicks):
    return render_data_requests_stats()


@callback(
    Output('data-requests-list', 'children'),
    [Input('dr-admin-refresh', 'n_clicks'),
     Input('dr-admin-search', 'value'),
     Input('dr-admin-status-filter', 'value')],
    prevent_initial_call=False
)
def update_data_requests_list(n_clicks, search, status_filter):
    return render_data_requests_list()


# Request status management
@callback(
    [Output('admin-alerts', 'children', allow_duplicate=True),
     Output('data-requests-list', 'children', allow_duplicate=True)],
    [Input({"type": "assign-request", "id": ALL}, 'n_clicks'),
     Input({"type": "status-progress", "id": ALL}, 'n_clicks'),
     Input({"type": "status-completed", "id": ALL}, 'n_clicks'),
     Input({"type": "status-denied", "id": ALL}, 'n_clicks')],
    State('user-session', 'data'),
    prevent_initial_call=True
)
def handle_request_status_updates(assign_clicks, progress_clicks, completed_clicks, denied_clicks, user_session):
    ctx = dash.callback_context
    if not ctx.triggered or not user_session.get('authenticated'):
        return dash.no_update, dash.no_update

    admin_id = user_session.get('id')
    triggered = ctx.triggered[0]

    # Parse the component ID
    import json
    component_id = json.loads(triggered['prop_id'].split('.')[0])
    request_id = component_id['id']
    action_type = component_id['type']

    if action_type == "assign-request":
        result = update_request_status(request_id, 'in_progress', admin_id, 'Assigned to admin')
    elif action_type == "status-progress":
        result = update_request_status(request_id, 'in_progress', admin_id)
    elif action_type == "status-completed":
        result = update_request_status(request_id, 'completed', admin_id, 'Completed by admin')
    elif action_type == "status-denied":
        result = update_request_status(request_id, 'denied', admin_id, 'Denied by admin')
    else:
        return dash.no_update, dash.no_update

    alert = dbc.Alert(result["message"],
                      color="success" if result["success"] else "danger",
                      dismissable=True)

    return alert, render_data_requests_list()