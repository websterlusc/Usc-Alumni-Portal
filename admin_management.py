"""
Admin Management Functions for USC IR Portal
Complete user management, password reset, and access control
"""

import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, callback, dash_table, ctx
import pandas as pd
from datetime import datetime, timedelta
from auth_database import db
import secrets

# USC Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA'
}

class AdminManager:
    """Admin management functionality"""
    
    def __init__(self):
        self.db = db
    
    def get_all_users(self):
        """Get all users for admin management"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, full_name, department, access_tier, 
                       is_active, is_approved, created_at, last_login
                FROM users 
                ORDER BY created_at DESC
            ''')
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'email': row[1],
                    'full_name': row[2],
                    'department': row[3] or 'Not specified',
                    'access_tier': row[4],
                    'is_active': row[5],
                    'is_approved': row[6],
                    'created_at': row[7],
                    'last_login': row[8] or 'Never'
                })
            
            conn.close()
            return users
            
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def update_user_access(self, user_id: int, new_tier: int, admin_id: int):
        """Update user access tier"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET access_tier = ? WHERE id = ?
            ''', (new_tier, user_id))
            
            # Log the action
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (admin_id, 'access_tier_changed', 
                  f'{{"user_id": {user_id}, "new_tier": {new_tier}}}', 
                  datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating user access: {e}")
            return False
    
    def reset_user_password(self, user_id: int, admin_id: int):
        """Reset user password and generate temporary password"""
        try:
            import sqlite3
            temp_password = secrets.token_urlsafe(12)  # Generate random password
            password_hash = self.db._hash_password(temp_password)
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET password_hash = ?, password_reset_required = 1 
                WHERE id = ?
            ''', (password_hash, user_id))
            
            # Log the action
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (admin_id, 'password_reset', 
                  f'{{"user_id": {user_id}, "admin_id": {admin_id}}}', 
                  datetime.now()))
            
            conn.commit()
            conn.close()
            
            return temp_password
            
        except Exception as e:
            print(f"Error resetting password: {e}")
            return None
    
    def toggle_user_status(self, user_id: int, admin_id: int):
        """Toggle user active/inactive status"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get current status
            cursor.execute('SELECT is_active FROM users WHERE id = ?', (user_id,))
            current_status = cursor.fetchone()[0]
            new_status = not current_status
            
            cursor.execute('''
                UPDATE users SET is_active = ? WHERE id = ?
            ''', (new_status, user_id))
            
            # Log the action
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (admin_id, 'user_status_changed', 
                  f'{{"user_id": {user_id}, "new_status": {new_status}}}', 
                  datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error toggling user status: {e}")
            return False
    
    def delete_user(self, user_id: int, admin_id: int):
        """Delete user account (soft delete by deactivating)"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Soft delete - deactivate and mark as deleted
            cursor.execute('''
                UPDATE users SET is_active = 0, is_approved = 0 WHERE id = ?
            ''', (user_id,))
            
            # Log the action
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (admin_id, 'user_deleted', 
                  f'{{"user_id": {user_id}, "admin_id": {admin_id}}}', 
                  datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

# Initialize admin manager
admin_manager = AdminManager()

def create_user_management_table():
    """Create interactive user management table"""
    users = admin_manager.get_all_users()
    
    if not users:
        return dbc.Alert("No users found", color="info")
    
    # Convert to DataFrame for table
    df = pd.DataFrame(users)
    
    # Create action buttons for each user
    user_cards = []
    for user in users:
        # Status badge
        if user['is_active'] and user['is_approved']:
            status_badge = dbc.Badge("Active", color="success")
        elif user['is_approved'] and not user['is_active']:
            status_badge = dbc.Badge("Inactive", color="warning")
        elif not user['is_approved']:
            status_badge = dbc.Badge("Pending", color="info")
        else:
            status_badge = dbc.Badge("Disabled", color="danger")
        
        # Tier badge
        tier_colors = {1: "secondary", 2: "info", 3: "warning", 4: "danger"}
        tier_badge = dbc.Badge(f"Tier {user['access_tier']}", 
                              color=tier_colors.get(user['access_tier'], "secondary"))
        
        card = dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        html.H5(user['full_name'], className="mb-0"),
                        html.Small(user['email'], className="text-muted")
                    ], width=6),
                    dbc.Col([
                        status_badge, " ", tier_badge
                    ], width=6, className="text-end")
                ])
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.P([html.Strong("Department: "), user['department']]),
                        html.P([html.Strong("Created: "), user['created_at'][:10]]),
                        html.P([html.Strong("Last Login: "), str(user['last_login'])[:10] if user['last_login'] != 'Never' else 'Never'])
                    ], width=8),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Edit", size="sm", color="primary", 
                                      id=f"edit-user-{user['id']}"),
                            dbc.Button("Reset PW", size="sm", color="warning",
                                      id=f"reset-pw-{user['id']}"),
                            dbc.Button("Toggle", size="sm", color="secondary",
                                      id=f"toggle-{user['id']}"),
                            dbc.Button("Delete", size="sm", color="danger",
                                      id=f"delete-{user['id']}")
                        ], vertical=True, className="w-100")
                    ], width=4)
                ])
            ])
        ], className="mb-3")
        
        user_cards.append(card)
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H4("User Management"),
                html.P(f"Total Users: {len(users)} | Active: {sum(1 for u in users if u['is_active'])}")
            ])
        ]),
        html.Div(user_cards),
        
        # Modals for user actions
        create_edit_user_modal(),
        create_password_reset_modal(),
        create_delete_confirmation_modal()
    ])

def create_edit_user_modal():
    """Create modal for editing user details"""
    return dbc.Modal([
        dbc.ModalHeader("Edit User"),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Label("Full Name", width=3),
                    dbc.Col([
                        dbc.Input(id="edit-fullname", type="text")
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Email", width=3),
                    dbc.Col([
                        dbc.Input(id="edit-email", type="email", disabled=True)
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Department", width=3),
                    dbc.Col([
                        dbc.Input(id="edit-department", type="text")
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Access Tier", width=3),
                    dbc.Col([
                        dcc.Dropdown(
                            id="edit-access-tier",
                            options=[
                                {'label': 'Tier 1 - Public Access', 'value': 1},
                                {'label': 'Tier 2 - Factbook Access', 'value': 2},
                                {'label': 'Tier 3 - Financial Access', 'value': 3},
                                {'label': 'Tier 4 - Admin Access', 'value': 4}
                            ]
                        )
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Status", width=3),
                    dbc.Col([
                        dbc.Checklist(
                            id="edit-user-status",
                            options=[
                                {'label': 'Account Active', 'value': 'active'},
                                {'label': 'Account Approved', 'value': 'approved'}
                            ],
                            value=['active', 'approved']
                        )
                    ], width=9)
                ])
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Save Changes", id="save-user-changes", color="primary"),
            dbc.Button("Cancel", id="cancel-edit", color="secondary")
        ]),
        html.Div(id="edit-user-alerts")
    ], id="edit-user-modal", is_open=False, size="lg")

def create_password_reset_modal():
    """Create modal for password reset confirmation"""
    return dbc.Modal([
        dbc.ModalHeader("Reset User Password"),
        dbc.ModalBody([
            dbc.Alert([
                html.H5("Are you sure?", className="alert-heading"),
                html.P("This will generate a new temporary password for the user. The old password will no longer work."),
                html.Hr(),
                html.P("The temporary password will be displayed once and should be shared securely with the user.", className="mb-0")
            ], color="warning"),
            html.Div(id="temp-password-display", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("Reset Password", id="confirm-password-reset", color="warning"),
            dbc.Button("Cancel", id="cancel-password-reset", color="secondary")
        ])
    ], id="password-reset-modal", is_open=False)

def create_delete_confirmation_modal():
    """Create modal for user deletion confirmation"""
    return dbc.Modal([
        dbc.ModalHeader("Delete User Account"),
        dbc.ModalBody([
            dbc.Alert([
                html.H5("Warning: Account Deletion", className="alert-heading"),
                html.P("This action will permanently deactivate the user account. This action cannot be undone."),
                html.Hr(),
                html.P("The user will lose access to all systems and data.", className="mb-0")
            ], color="danger"),
            html.P(id="delete-user-details", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("Delete Account", id="confirm-delete-user", color="danger"),
            dbc.Button("Cancel", id="cancel-delete-user", color="secondary")
        ])
    ], id="delete-user-modal", is_open=False)

def create_add_user_form():
    """Create form for adding new users"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Add New User", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Full Name *", className="fw-bold"),
                        dbc.Input(
                            id="new-user-fullname",
                            type="text",
                            placeholder="Enter full name",
                            className="mb-3"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Email Address *", className="fw-bold"),
                        dbc.Input(
                            id="new-user-email",
                            type="email",
                            placeholder="user@usc.edu.tt",
                            className="mb-3"
                        )
                    ], width=6)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Department", className="fw-bold"),
                        dbc.Input(
                            id="new-user-department",
                            type="text",
                            placeholder="Department/Unit",
                            className="mb-3"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Initial Access Tier", className="fw-bold"),
                        dcc.Dropdown(
                            id="new-user-tier",
                            options=[
                                {'label': 'Tier 1 - Public Access', 'value': 1},
                                {'label': 'Tier 2 - Factbook Access', 'value': 2},
                                {'label': 'Tier 3 - Financial Access', 'value': 3},
                                {'label': 'Tier 4 - Admin Access', 'value': 4}
                            ],
                            value=2,
                            className="mb-3"
                        )
                    ], width=6)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Temporary Password *", className="fw-bold"),
                        dbc.Input(
                            id="new-user-password",
                            type="password",
                            placeholder="Enter temporary password",
                            className="mb-3"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Checklist(
                            id="new-user-options",
                            options=[
                                {'label': 'Account Active', 'value': 'active'},
                                {'label': 'Pre-approved', 'value': 'approved'},
                                {'label': 'Require Password Change', 'value': 'reset_required'}
                            ],
                            value=['active', 'approved', 'reset_required'],
                            className="mt-4"
                        )
                    ], width=6)
                ]),
                html.Div(id="add-user-alerts", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Create User Account",
                            id="create-user-btn",
                            color="success",
                            size="lg",
                            className="w-100",
                            style={'background-color': USC_COLORS['primary_green']}
                        )
                    ])
                ])
            ])
        ])
    ], className="mb-4")

# Callback functions for admin management
def create_admin_callbacks():
    """Create all admin management callbacks"""
    
    from dash import callback, Input, Output, State, ctx, no_update
    
    # Edit user modal callbacks
    @callback(
        [Output('edit-user-modal', 'is_open'),
         Output('edit-fullname', 'value'),
         Output('edit-email', 'value'),
         Output('edit-department', 'value'),
         Output('edit-access-tier', 'value'),
         Output('edit-user-status', 'value')],
        [Input(f'edit-user-{i}', 'n_clicks') for i in range(1, 100)],  # Support up to 100 users
        prevent_initial_call=True
    )
    def open_edit_user_modal(*args):
        """Open edit user modal with current user data"""
        if not any(args):
            return no_update, no_update, no_update, no_update, no_update, no_update
        
        # Extract user ID from triggered button
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        user_id = int(button_id.split('-')[-1])
        
        # Get user data
        users = admin_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)
        
        if user:
            status_values = []
            if user['is_active']:
                status_values.append('active')
            if user['is_approved']:
                status_values.append('approved')
            
            return (True, user['full_name'], user['email'], 
                   user['department'], user['access_tier'], status_values)
        
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    # Password reset callbacks
    @callback(
        [Output('password-reset-modal', 'is_open'),
         Output('temp-password-display', 'children')],
        [Input(f'reset-pw-{i}', 'n_clicks') for i in range(1, 100)],
        [Input('confirm-password-reset', 'n_clicks'),
         Input('cancel-password-reset', 'n_clicks')],
        State('user-session', 'data'),
        prevent_initial_call=True
    )
    def handle_password_reset(*args):
        """Handle password reset process"""
        session_data = args[-1]  # Last argument is session_data
        
        if ctx.triggered_id and 'reset-pw-' in ctx.triggered_id:
            # Open modal
            return True, ""
        elif ctx.triggered_id == 'confirm-password-reset':
            # Extract user ID and reset password
            button_id = [key for key in ctx.inputs_list[0] if ctx.inputs_list[0][key]['value']][0]
            user_id = int(button_id.split('-')[-1])
            
            admin_id = session_data.get('user_id') if session_data else None
            temp_password = admin_manager.reset_user_password(user_id, admin_id)
            
            if temp_password:
                display = dbc.Alert([
                    html.H5("Password Reset Successful!", className="alert-heading"),
                    html.P(f"Temporary Password: {temp_password}"),
                    html.Hr(),
                    html.P("Share this password securely with the user. They will be required to change it on first login.")
                ], color="success")
                return True, display
            else:
                display = dbc.Alert("Error resetting password", color="danger")
                return True, display
        elif ctx.triggered_id == 'cancel-password-reset':
            return False, ""
        
        return no_update, no_update
    
    # Add new user callback
    @callback(
        [Output('add-user-alerts', 'children'),
         Output('new-user-fullname', 'value'),
         Output('new-user-email', 'value'),
         Output('new-user-department', 'value'),
         Output('new-user-password', 'value')],
        Input('create-user-btn', 'n_clicks'),
        [State('new-user-fullname', 'value'),
         State('new-user-email', 'value'),
         State('new-user-department', 'value'),
         State('new-user-tier', 'value'),
         State('new-user-password', 'value'),
         State('new-user-options', 'value'),
         State('user-session', 'data')],
        prevent_initial_call=True
    )
    def create_new_user(n_clicks, fullname, email, department, tier, password, options, session_data):
        """Create new user account"""
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update
        
        # Validation
        errors = []
        if not fullname or len(fullname.strip()) < 2:
            errors.append("Full name is required")
        if not email or '@' not in email:
            errors.append("Valid email is required")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        if errors:
            alert = dbc.Alert([
                html.H5("Please fix the following errors:", className="alert-heading"),
                html.Ul([html.Li(error) for error in errors])
            ], color="danger")
            return alert, no_update, no_update, no_update, no_update
        
        # Create user
        result = db.create_user(
            email=email,
            password=password,
            full_name=fullname.strip(),
            department=department.strip() if department else None,
            access_tier=tier
        )
        
        if result['success']:
            # Update user status based on options
            if options:
                import sqlite3
                conn = sqlite3.connect(db.db_path)
                cursor = conn.cursor()
                
                is_active = 'active' in options
                is_approved = 'approved' in options
                reset_required = 'reset_required' in options
                
                cursor.execute('''
                    UPDATE users 
                    SET is_active = ?, is_approved = ?, password_reset_required = ?
                    WHERE id = ?
                ''', (is_active, is_approved, reset_required, result['user_id']))
                
                conn.commit()
                conn.close()
            
            alert = dbc.Alert([
                html.H5("User Created Successfully!", className="alert-heading"),
                html.P(f"User ID: {result['user_id']}"),
                html.P(f"Access Tier: {tier}")
            ], color="success")
            
            return alert, "", "", "", ""
        
        else:
            alert = dbc.Alert(f"Error: {result['message']}", color="danger")
            return alert, no_update, no_update, no_update, no_update

# Initialize admin callbacks
create_admin_callbacks()

# Export admin components
__all__ = [
    'admin_manager', 'create_user_management_table', 'create_add_user_form',
    'create_edit_user_modal', 'create_password_reset_modal', 'create_delete_confirmation_modal'
]