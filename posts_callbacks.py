"""
Posts System Callbacks - COMPLETE REBUILD
Clean, working callbacks that match the new UI
"""

from dash import Input, Output, State, callback, ALL, ctx, no_update, html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import dash as dash
from posts_system import (
    create_post, get_active_posts, get_post_by_id,
    update_post, delete_post, cleanup_expired_posts
)

USC_COLORS = {
    'primary_green': '#1B5E20',
    'accent_yellow': '#FDD835',
    'light_gray': '#F8F9FA'
}


# ============================================================================
# CALLBACK 1: TOGGLE POST FORM
# ============================================================================

@callback(
    Output('post-form-collapse', 'is_open'),
    Output('create-new-post-btn', 'children'),
    Input('create-new-post-btn', 'n_clicks'),
    State('post-form-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_post_form(n_clicks, is_open):
    """Open/close the post creation form"""

    print(f"🔘 CREATE POST BUTTON CLICKED")
    print(f"   n_clicks: {n_clicks}")
    print(f"   Current state (is_open): {is_open}")

    if n_clicks:
        if is_open:
            # Close form
            print("   → Closing form")
            return False, [html.I(className="fas fa-plus me-2"), "Create New Post"]
        else:
            # Open form
            print("   → Opening form")
            return True, [html.I(className="fas fa-times me-2"), "Cancel"]

    return no_update, no_update


# ============================================================================
# CALLBACK 2: TOGGLE CUSTOM DATE PICKER
# ============================================================================

@callback(
    Output('custom-date-container', 'style'),
    Input('post-duration-dropdown', 'value'),
    prevent_initial_call=True
)
def toggle_custom_date(duration):
    """Show/hide custom date picker"""
    if duration == 'custom':
        return {'display': 'block'}
    return {'display': 'none'}


# ============================================================================
# CALLBACK 3: CANCEL BUTTON - CLOSE FORM
# ============================================================================

@callback(
    Output('post-form-collapse', 'is_open', allow_duplicate=True),
    Output('create-new-post-btn', 'children', allow_duplicate=True),
    Input('cancel-post-btn', 'n_clicks'),
    prevent_initial_call=True
)
def cancel_post_form(n_clicks):
    """Close form when cancel clicked"""
    if n_clicks:
        print("❌ CANCEL clicked - closing form")
        return False, [html.I(className="fas fa-plus me-2"), "Create New Post"]
    return no_update, no_update


# ============================================================================
# CALLBACK 4: SUBMIT POST
# ============================================================================

@callback(
    Output('admin-alerts', 'children', allow_duplicate=True),
    Output('post-title-input', 'value'),
    Output('post-content-input', 'value'),
    Output('post-form-collapse', 'is_open', allow_duplicate=True),
    Output('create-new-post-btn', 'children', allow_duplicate=True),
    Output('posts-refresh-trigger', 'data'),
    Input('submit-post-btn', 'n_clicks'),
    State('post-title-input', 'value'),
    State('post-content-input', 'value'),
    State('post-tier-dropdown', 'value'),
    State('post-category-dropdown', 'value'),
    State('post-duration-dropdown', 'value'),
    State('post-expiration-date', 'value'),
    State('post-options-checklist', 'value'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def submit_post(n_clicks, title, content, tier, category, duration, custom_date, options, user_session):
    """Handle post submission"""

    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update, no_update

    print("📤 SUBMIT POST clicked")
    print(f"   Title: {title}")
    print(f"   Content length: {len(content) if content else 0}")

    # Validation
    if not title or not content:
        return (
            dbc.Alert("Title and content are required!", color="danger", dismissable=True),
            no_update, no_update, no_update, no_update, no_update
        )

    if not user_session or user_session.get('access_tier', 0) < 4:
        return (
            dbc.Alert("Admin access required", color="danger", dismissable=True),
            no_update, no_update, no_update, no_update, no_update
        )

    # Sanitize
    import html as html_escape
    title_clean = html_escape.escape(title.strip())
    content_clean = html_escape.escape(content.strip())

    # Calculate expiration
    is_permanent = (duration == 'permanent')
    expires_at = None

    if not is_permanent:
        if duration == 'custom' and custom_date:
            expires_at = f"{custom_date}T23:59:59"
        elif duration in ['7', '30', '90']:
            days = int(duration)
            exp_date = datetime.now() + timedelta(days=days)
            expires_at = exp_date.isoformat()

    # Parse options
    comments_enabled = 'comments' in (options or [])
    is_pinned = 'pinned' in (options or [])

    # Create post
    try:
        post_id = create_post(
            title=title_clean,
            content=content_clean,
            author_id=user_session['id'],
            min_access_tier=tier or 1,
            comments_enabled=comments_enabled,
            is_permanent=is_permanent,
            expires_at=expires_at,
            category=category or 'announcement',
            is_pinned=is_pinned
        )

        if post_id:
            print(f"✅ Post created successfully! ID: {post_id}")
            return (
                dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    "Post published successfully!"
                ], color="success", dismissable=True),
                '',  # Clear title
                '',  # Clear content
                False,  # Close form
                [html.I(className="fas fa-plus me-2"), "Create New Post"],  # Reset button
                {'timestamp': datetime.now().isoformat()}  # Trigger refresh
            )
        else:
            return (
                dbc.Alert("Failed to create post", color="danger", dismissable=True),
                no_update, no_update, no_update, no_update, no_update
            )

    except Exception as e:
        print(f"❌ Error creating post: {e}")
        return (
            dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True),
            no_update, no_update, no_update, no_update, no_update
        )


# ============================================================================
# CALLBACK 5: PREVIEW POST
# ============================================================================

@callback(
    Output('post-preview-container', 'children'),
    Input('preview-post-btn', 'n_clicks'),
    State('post-title-input', 'value'),
    State('post-content-input', 'value'),
    State('post-category-dropdown', 'value'),
    State('post-options-checklist', 'value'),
    prevent_initial_call=True
)
def preview_post(n_clicks, title, content, category, options):
    """Show preview of post"""

    if not n_clicks or not title or not content:
        return html.Div()

    category_colors = {
        'announcement': 'primary',
        'news': 'info',
        'event': 'success',
        'policy': 'warning',
        'data_release': 'secondary'
    }

    is_pinned = 'pinned' in (options or [])

    return dbc.Card([
        dbc.CardBody([
            dbc.Badge("PREVIEW", color="warning", className="mb-2"),
            dbc.Badge(
                (category or 'announcement').replace('_', ' ').title(),
                color=category_colors.get(category, 'primary'),
                className="ms-2 mb-2"
            ),
            dbc.Badge("Pinned", color="warning", className="ms-2 mb-2") if is_pinned else html.Span(),
            html.H4(title, className="fw-bold mt-3 mb-3",
                   style={'color': USC_COLORS['primary_green']}),
            html.P(content, style={'whiteSpace': 'pre-wrap'}),
            html.Hr(),
            html.Small([
                html.I(className="fas fa-user me-2"),
                "You • Just now"
            ], className="text-muted")
        ])
    ], className="mt-3", style={'backgroundColor': USC_COLORS['light_gray']})


# ============================================================================
# CALLBACK 6: DELETE POST
# ============================================================================

@callback(
    Output('delete-post-modal', 'is_open'),
    Output('delete-post-id-store', 'data'),
    Input({'type': 'delete-post', 'post_id': ALL}, 'n_clicks'),
    Input('cancel-delete-post', 'n_clicks'),
    Input('confirm-delete-post', 'n_clicks'),
    State('delete-post-id-store', 'data'),
    prevent_initial_call=True
)
def handle_delete_modal(delete_clicks, cancel, confirm, stored_id):
    """Handle delete confirmation modal"""

    if not ctx.triggered_id:
        return no_update, no_update

    # Open modal
    if isinstance(ctx.triggered_id, dict) and ctx.triggered_id['type'] == 'delete-post':
        post_id = ctx.triggered_id['post_id']
        print(f"🗑️ Delete requested for post ID: {post_id}")
        return True, post_id

    # Cancel
    if ctx.triggered_id == 'cancel-delete-post':
        return False, None

    # Confirm delete
    if ctx.triggered_id == 'confirm-delete-post' and stored_id:
        print(f"✅ Confirming delete for post ID: {stored_id}")
        delete_post(stored_id, soft_delete=True)
        return False, None

    return no_update, no_update


# ============================================================================
# CALLBACK 7: DELETE CONFIRMATION ALERT
# ============================================================================

@callback(
    Output('admin-alerts', 'children', allow_duplicate=True),
    Output('posts-refresh-trigger', 'data', allow_duplicate=True),
    Input({'type': 'simple-delete-post', 'post_id': ALL}, 'n_clicks'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def simple_delete_post(n_clicks_list, user_session):
    """Simple delete post without confirmation modal"""

    if not any(n_clicks_list) or not user_session or user_session.get('access_tier', 0) < 4:
        return dash.no_update, dash.no_update

    # Find which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    import json
    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    post_id = button_id['post_id']

    # Delete the post
    from posts_system import delete_post
    success = delete_post(post_id, soft_delete=True)

    if success:
        alert = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            f"Post deleted successfully!"
        ], color="success", dismissable=True, duration=3000)

        # Trigger refresh
        return alert, datetime.now().timestamp()
    else:
        alert = dbc.Alert([
            html.I(className="fas fa-exclamation-circle me-2"),
            "Failed to delete post"
        ], color="danger", dismissable=True)

        return alert, dash.no_update

def show_delete_alert(n_clicks, post_id):
    """Show alert after deletion"""

    if n_clicks and post_id:
        return dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "Post deleted successfully"
        ], color="success", dismissable=True)

    return no_update


# ============================================================================
# CALLBACK 8: AUTO CLEANUP EXPIRED POSTS
# ============================================================================

@callback(
    Output('cleanup-status-dummy', 'data'),
    Input('cleanup-interval', 'n_intervals'),
    prevent_initial_call=True
)
def auto_cleanup(n_intervals):
    """Run automatic cleanup every hour"""
    try:
        count = cleanup_expired_posts()
        if count > 0:
            print(f"🧹 Archived {count} expired posts")
        return {'last_run': datetime.now().isoformat(), 'count': count}
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
        return {'error': str(e)}


def register_callbacks(dash_app):
    """Explicitly register all callbacks with the app"""
    # All your @callback decorators automatically register
    # when this module is imported with the app in scope
    pass

# Auto-register when imported
print("✅ Posts callbacks registered successfully")