"""
Dash Callbacks for Posts/Announcements System
Fixed version with consistent naming and proper error handling
"""

from dash import Input, Output, State, callback, ALL, ctx, no_update, html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# Import posts system modules
from posts_system import (
    create_post, get_active_posts, get_post_by_id,
    update_post, delete_post, add_comment, get_post_comments,
    cleanup_expired_posts
)

USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA'
}


# ============================================================================
# CALLBACK 0: TOGGLE POST CREATION FORM
# ============================================================================

# Add this callback to app.py (after all your other callbacks)

@callback(
    Output('post-form-collapse', 'is_open'),
    Output('create-new-post-btn', 'children'),
    Input('create-new-post-btn', 'n_clicks'),
    Input('cancel-post-btn', 'n_clicks'),
    Input('submit-post-btn', 'n_clicks'),
    State('post-form-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_post_form(create_clicks, cancel_clicks, submit_clicks, is_open):
    """Toggle the post creation form visibility"""


    print(f"🔍 Button clicked! Trigger: {ctx.triggered_id}, is_open: {is_open}")

    if not ctx.triggered_id:
        return no_update, no_update

    # Open form when create button clicked
    if ctx.triggered_id == 'create-new-post-btn':
        if is_open:
            return False, [html.I(className="fas fa-plus me-2"), "Create New Post"]
        else:
            return True, [html.I(className="fas fa-times me-2"), "Cancel"]

    # Close form when cancel or submit clicked
    if ctx.triggered_id in ['cancel-post-btn', 'submit-post-btn']:
        return False, [html.I(className="fas fa-plus me-2"), "Create New Post"]

    return no_update, no_update

# ============================================================================
# CALLBACK 1: TOGGLE CUSTOM DATE PICKER
# ============================================================================

@callback(
    Output('custom-date-container', 'style'),
    Input('post-duration-dropdown', 'value'),
    prevent_initial_call=True
)
def toggle_custom_date_picker(duration_value):
    """Show/hide custom date picker based on duration selection"""
    if duration_value == 'custom':
        return {'display': 'block'}
    return {'display': 'none'}


# ============================================================================
# CALLBACK 2: SUBMIT NEW POST
# ============================================================================

@callback(
    Output('admin-alerts', 'children', allow_duplicate=True),
    Output('post-title-input', 'value'),
    Output('post-content-input', 'value'),
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
def submit_new_post(n_clicks, title, content, tier, category, duration,
                    custom_date, options, user_session):
    """Handle post creation submission"""

    if not n_clicks:
        return no_update, no_update, no_update, no_update

    # Validation
    if not title or not content:
        return dbc.Alert("Title and content are required", color="danger", dismissable=True), no_update, no_update, no_update

    if not user_session or user_session.get('access_tier', 0) < 4:
        return dbc.Alert("Admin access required", color="danger", dismissable=True), no_update, no_update, no_update

    # Sanitize inputs
    import html as html_module
    title_clean = html_module.escape(title.strip())
    content_clean = html_module.escape(content.strip())

    # Calculate expiration date
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
            return (
                dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    f"Post created successfully!"
                ], color="success", dismissable=True),
                '',  # Clear title
                '',  # Clear content
                {'timestamp': datetime.now().isoformat(), 'action': 'post_created'}  # Trigger refresh
            )
        else:
            return dbc.Alert("Error creating post", color="danger", dismissable=True), no_update, no_update, no_update

    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True), no_update, no_update, no_update


# ============================================================================
# CALLBACK 3: DELETE POST CONFIRMATION
# ============================================================================

@callback(
    Output('delete-post-modal', 'is_open'),
    Output('delete-post-id-store', 'data'),
    Input({'type': 'delete-post', 'post_id': ALL}, 'n_clicks'),
    Input('cancel-delete-post', 'n_clicks'),
    Input('confirm-delete-post', 'n_clicks'),
    State('delete-post-id-store', 'data'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def handle_delete_post_modal(delete_clicks, cancel_click, confirm_click, stored_post_id, user_session):
    """Handle post deletion confirmation modal"""

    if not ctx.triggered_id:
        return no_update, no_update

    # Check admin access
    if not user_session or user_session.get('access_tier', 0) < 4:
        return False, None

    # Open modal with post ID
    if isinstance(ctx.triggered_id, dict) and ctx.triggered_id['type'] == 'delete-post':
        post_id = ctx.triggered_id['post_id']
        return True, post_id

    # Cancel deletion
    if ctx.triggered_id == 'cancel-delete-post':
        return False, None

    # Confirm deletion
    if ctx.triggered_id == 'confirm-delete-post' and stored_post_id:
        success = delete_post(stored_post_id, soft_delete=True)
        return False, None

    return no_update, no_update


# ============================================================================
# CALLBACK 4: REFRESH POSTS TABLE AFTER DELETE
# ============================================================================

@callback(
    Output('admin-alerts', 'children', allow_duplicate=True),
    Input('confirm-delete-post', 'n_clicks'),
    State('delete-post-id-store', 'data'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def delete_post_and_notify(n_clicks, post_id, user_session):
    """Delete post and show notification"""

    if not n_clicks or not post_id:
        return no_update

    if not user_session or user_session.get('access_tier', 0) < 4:
        return dbc.Alert("Unauthorized", color="danger", dismissable=True)

    success = delete_post(post_id, soft_delete=True)

    if success:
        return dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "Post deleted successfully"
        ], color="success", dismissable=True)
    else:
        return dbc.Alert("Failed to delete post", color="danger", dismissable=True)


# ============================================================================
# CALLBACK 5: SUBMIT COMMENT
# ============================================================================

@callback(
    Output({'type': 'comment-input', 'post_id': ALL}, 'value'),
    Output('admin-alerts', 'children', allow_duplicate=True),
    Input({'type': 'submit-comment', 'post_id': ALL}, 'n_clicks'),
    State({'type': 'comment-input', 'post_id': ALL}, 'value'),
    State({'type': 'comment-input', 'post_id': ALL}, 'id'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def submit_comment(submit_clicks, comment_texts, comment_ids, user_session):
    """Handle comment submission"""

    if not ctx.triggered_id or not user_session:
        return no_update, no_update

    # Get the post_id from triggered button
    post_id = ctx.triggered_id['post_id']

    # Find the matching comment text by post_id
    comment_text = None
    for i, comment_id in enumerate(comment_ids):
        if comment_id['post_id'] == post_id:
            comment_text = comment_texts[i]
            break

    if not comment_text or not comment_text.strip():
        return no_update, dbc.Alert("Comment cannot be empty", color="warning", dismissable=True)

    # Add comment
    try:
        comment_id = add_comment(
            post_id=post_id,
            user_id=user_session['id'],
            content=comment_text.strip()
        )

        if comment_id:
            # Clear all comment inputs
            return [''] * len(comment_texts), dbc.Alert("Comment posted!", color="success", duration=3000, dismissable=True)
        else:
            return no_update, dbc.Alert("Failed to post comment", color="danger", dismissable=True)

    except Exception as e:
        return no_update, dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True)


# ============================================================================
# CALLBACK 6: DELETE COMMENT
# ============================================================================

@callback(
    Output('admin-alerts', 'children', allow_duplicate=True),
    Input({'type': 'delete-comment', 'comment_id': ALL}, 'n_clicks'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def delete_comment_handler(delete_clicks, user_session):
    """Handle comment deletion"""

    if not ctx.triggered_id or not user_session:
        return no_update

    comment_id = ctx.triggered_id['comment_id']
    user_id = user_session['id']
    is_admin = user_session.get('access_tier', 1) >= 4

    try:
        from posts_system import delete_comment
        success = delete_comment(comment_id, user_id, is_admin)

        if success:
            return dbc.Alert("Comment deleted", color="success", duration=3000, dismissable=True)
        else:
            return dbc.Alert("Failed to delete comment", color="danger", dismissable=True)
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True)


# ============================================================================
# CALLBACK 7: AUTO-CLEANUP EXPIRED POSTS (RUNS HOURLY)
# ============================================================================

@callback(
    Output('cleanup-status-dummy', 'data'),
    Input('cleanup-interval', 'n_intervals'),
    prevent_initial_call=True
)
def auto_cleanup_expired_posts(n_intervals):
    """
    Automatically archive expired posts
    Runs every hour based on interval component
    """
    try:
        archived_count = cleanup_expired_posts()
        return {
            'last_cleanup': datetime.now().isoformat(),
            'archived_count': archived_count
        }
    except Exception as e:
        print(f"Error in auto cleanup: {str(e)}")
        return {'error': str(e)}


# ============================================================================
# CALLBACK 8: PREVIEW POST (OPTIONAL)
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
    """Generate live preview of the post"""

    if not n_clicks or not title or not content:
        return dbc.Alert("Fill in title and content to preview", color="info")

    # Create preview card
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
            dbc.Badge("PREVIEW", color="info", className="mb-2"),
            dbc.Badge(
                (category or 'announcement').replace('_', ' ').title(),
                color=category_colors.get(category, 'primary'),
                className="ms-2 mb-2"
            ),
            dbc.Badge("Pinned", color="warning", className="ms-2 mb-2") if is_pinned else html.Span(),
            html.H4(title, className="fw-bold mt-2 mb-3", style={'color': USC_COLORS['primary_green']}),
            html.P(content, style={'whiteSpace': 'pre-wrap'}),
            html.Hr(),
            html.Small([
                html.I(className="fas fa-user me-2"),
                "You • Just now"
            ], className="text-muted")
        ])
    ], className="shadow-sm", style={'backgroundColor': USC_COLORS['light_gray']})


# ============================================================================
# CALLBACK 9: VIEW POST DETAILS (MODAL)
# ============================================================================

@callback(
    Output('post-detail-modal', 'is_open'),
    Output('post-detail-content', 'children'),
    Input({'type': 'view-post', 'post_id': ALL}, 'n_clicks'),
    Input({'type': 'view-post-admin', 'post_id': ALL}, 'n_clicks'),
    Input('close-post-detail', 'n_clicks'),
    State('user-session', 'data'),
    prevent_initial_call=True
)
def view_post_detail(view_clicks, admin_view_clicks, close_click, user_session):
    """Display full post with comments in modal"""

    if not ctx.triggered_id:
        return no_update, no_update

    # Close modal
    if ctx.triggered_id == 'close-post-detail':
        return False, None

    # Get post ID from triggered button
    post_id = None
    if isinstance(ctx.triggered_id, dict):
        post_id = ctx.triggered_id['post_id']

    if not post_id:
        return no_update, no_update

    # Fetch post (increment view count)
    post = get_post_by_id(post_id, increment_views=True)

    if not post:
        return True, dbc.Alert("Post not found", color="danger")

    # Check user access
    user_tier = user_session.get('access_tier', 1) if user_session else 1
    if post['min_access_tier'] > user_tier:
        return True, dbc.Alert([
            html.I(className="fas fa-lock me-2"),
            f"This post requires Tier {post['min_access_tier']} access"
        ], color="warning")

    # Build post display
    from posts_ui import create_post_card_full

    # Get comments if enabled
    comments_html = html.Div()
    if post['comments_enabled']:
        comments = get_post_comments(post_id)
        from posts_ui import create_comments_section
        comments_html = create_comments_section(post_id, comments, user_session)

    # Build modal content
    content = html.Div([
        create_post_card_full(post, user_session),
        html.Hr(className="my-4"),
        comments_html
    ])

    return True, content



# ============================================================================
# DUMMY OUTPUTS (Required for some callbacks)
# ============================================================================

# Add this to your app.layout in app.py:
# dcc.Store(id='cleanup-status-dummy', storage_type='memory')
# dbc.Modal(id='post-detail-modal', size='xl', scrollable=True, children=[
#     dbc.ModalHeader("Post Details"),
#     dbc.ModalBody(id='post-detail-content'),
#     dbc.ModalFooter(dbc.Button("Close", id='close-post-detail'))
# ])


print("✅ Posts callbacks registered successfully")