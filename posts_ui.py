"""
UI Components for Posts/Announcements System
Dash/Bootstrap components for displaying and managing posts
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from typing import List, Dict, Optional

USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA',
    'medium_gray': '#E9ECEF',
    'dark_gray': '#495057'
}


# ============================================================================
# HOMEPAGE NEWS FEED COMPONENT
# ============================================================================

def create_news_feed_section(posts: List[Dict], user_data: Optional[Dict] = None) -> html.Div:
    """
    Create news feed section for homepage
    Shows latest announcements/news with tier-based filtering
    """
    if not posts:
        return html.Div()  # Don't show section if no posts
    
    # Take only the 3 most recent posts for homepage
    recent_posts = posts[:3]
    
    post_cards = []
    for post in recent_posts:
        post_cards.append(create_post_card_compact(post, user_data))
    
    return html.Section([
        dbc.Container([
            # Section Header
            dbc.Row([
                dbc.Col([
                    html.H2([
                        html.I(className="fas fa-bullhorn me-3", 
                              style={'color': USC_COLORS['accent_yellow']}),
                        "Latest News & Announcements"
                    ], className="fw-bold mb-2", style={'color': USC_COLORS['primary_green']}),
                    html.P("Stay updated with the latest from Institutional Research",
                          className="text-muted mb-4")
                ])
            ]),
            
            # Posts Grid
            dbc.Row([
                dbc.Col(card, width=12, md=4) for card in post_cards
            ], className="g-4 mb-4"),
            
            # View All Link
            dbc.Row([
                dbc.Col([
                    dbc.Button([
                        "View All Announcements ",
                        html.I(className="fas fa-arrow-right ms-2")
                    ], href="/news", color="primary", outline=True, size="lg")
                ], className="text-center")
            ])
        ], fluid=True)
    ], className="py-5", style={'backgroundColor': USC_COLORS['light_gray']})


def create_post_card_compact(post: Dict, user_data: Optional[Dict] = None) -> dbc.Card:
    """Compact post card for homepage feed"""
    
    # Category badge styling
    category_colors = {
        'announcement': 'primary',
        'news': 'info',
        'event': 'success',
        'policy': 'warning',
        'data_release': 'secondary'
    }
    
    category = post.get('category', 'announcement')
    category_color = category_colors.get(category, 'primary')
    
    # Format date
    created_at = datetime.fromisoformat(post['created_at'])
    date_str = created_at.strftime("%B %d, %Y")
    
    # Check if pinned
    is_pinned = post.get('is_pinned', False)
    
    return dbc.Card([
        dbc.CardBody([
            # Pinned indicator
            html.Div([
                html.I(className="fas fa-thumbtack me-2"),
                html.Span("Pinned", className="fw-bold")
            ], className="text-warning mb-2 small") if is_pinned else html.Div(),
            
            # Category badge
            dbc.Badge(category.replace('_', ' ').title(), 
                     color=category_color, className="mb-2"),
            
            # Title
            html.H5(post['title'], className="card-title fw-bold mb-2",
                   style={'color': USC_COLORS['primary_green']}),
            
            # Excerpt (first 120 chars)
            html.P(post['content'][:120] + "..." if len(post['content']) > 120 else post['content'],
                  className="card-text text-muted small mb-3"),
            
            # Footer: Date and Read More
            html.Div([
                html.Span([
                    html.I(className="far fa-calendar me-2"),
                    date_str
                ], className="text-muted small"),
                dbc.Button("Read More →", 
                          id={'type': 'view-post', 'post_id': post['id']},
                          color="link", size="sm", className="p-0 ms-3")
            ], className="d-flex justify-content-between align-items-center")
        ])
    ], className="h-100 shadow-sm hover-shadow", 
       style={'transition': 'all 0.3s ease', 'border': 'none'})


# ============================================================================
# FULL NEWS PAGE
# ============================================================================

def create_news_page(posts: List[Dict], user_data: Optional[Dict] = None) -> html.Div:
    """Full news/announcements page with all posts (NO NAVBAR - add separately)"""

    user_tier = user_data.get('access_tier', 1) if user_data else 1

    # Separate pinned and regular posts
    pinned_posts = [p for p in posts if p.get('is_pinned', False)]
    regular_posts = [p for p in posts if not p.get('is_pinned', False)]

    return html.Div([
        # Hero Section (NO NAVBAR HERE - it's added in the route)
        html.Section([
            dbc.Container([
                html.H1([
                    html.I(className="fas fa-newspaper me-3"),
                    "News & Announcements"
                ], className="display-4 fw-bold mb-3",
                   style={'color': USC_COLORS['primary_green']}),
                html.P("Official updates from the Department of Institutional Research",
                      className="lead text-muted")
            ])
        ], className="py-5", style={'backgroundColor': USC_COLORS['light_gray']}),

        # Main Content
        dbc.Container([
            # Pinned Posts Section
            html.Div([
                html.H3([
                    html.I(className="fas fa-thumbtack me-2",
                          style={'color': USC_COLORS['accent_yellow']}),
                    "Pinned Announcements"
                ], className="fw-bold mb-4", style={'color': USC_COLORS['primary_green']}),
                html.Div([
                    create_post_card_full(post, user_data)
                    for post in pinned_posts
                ])
            ], className="mb-5") if pinned_posts else html.Div(),

            # Regular Posts
            html.H3("Recent Posts", className="fw-bold mb-4",
                   style={'color': USC_COLORS['primary_green']}),
            html.Div([
                create_post_card_full(post, user_data)
                for post in regular_posts
            ]) if regular_posts else dbc.Alert("No posts available", color="info")

        ], fluid=True, className="py-5")
    ])


def create_post_card_full(post: Dict, user_data: Optional[Dict] = None) -> dbc.Card:
    """Full-width post card for news page"""

    # Category badge
    category_colors = {
        'announcement': 'primary',
        'news': 'info',
        'event': 'success',
        'policy': 'warning',
        'data_release': 'secondary'
    }
    category = post.get('category', 'announcement')

    # Format dates
    created_at = datetime.fromisoformat(post['created_at'])
    date_str = created_at.strftime("%B %d, %Y at %I:%M %p")

    # Check expiration
    expires_at = post.get('expires_at')
    expiration_badge = None
    if expires_at and not post.get('is_permanent'):
        exp_date = datetime.fromisoformat(expires_at)
        if exp_date > datetime.now():
            days_left = (exp_date - datetime.now()).days
            if days_left <= 7:
                expiration_badge = dbc.Badge(
                    f"Expires in {days_left} days",
                    color="warning", className="ms-2"
                )

    # Comments count
    comments_count = post.get('comment_count', 0)
    comments_enabled = post.get('comments_enabled', False)

    return dbc.Card([
        dbc.CardBody([
            # Header row
            dbc.Row([
                dbc.Col([
                    # Category and pinned indicator
                    html.Div([
                        dbc.Badge(category.replace('_', ' ').title(),
                                 color=category_colors.get(category, 'primary')),
                        dbc.Badge("Pinned", color="warning", className="ms-2")
                            if post.get('is_pinned') else html.Span(),
                        expiration_badge if expiration_badge else html.Span()
                    ])
                ], width="auto"),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-eye me-2"),
                        f"{post.get('view_count', 0)} views"
                    ], className="text-muted small text-end")
                ])
            ], className="mb-3"),

            # Title
            html.H4(post['title'], className="card-title fw-bold mb-3",
                   style={'color': USC_COLORS['primary_green']}),

            # Content
            html.P(post['content'], className="card-text mb-3",
                  style={'whiteSpace': 'pre-wrap'}),

            # Footer
            html.Div([
                # Author and date
                html.Div([
                    html.I(className="fas fa-user-circle me-2"),
                    html.Span(post.get('author_name', 'Unknown'), className="fw-bold me-3"),
                    html.I(className="far fa-calendar me-2"),
                    html.Span(date_str, className="text-muted small")
                ], className="d-inline-block"),

                # Comments button
                dbc.Button([
                    html.I(className="fas fa-comments me-2"),
                    f"View Comments ({comments_count})" if comments_count > 0 else "No Comments"
                ], id={'type': 'view-comments', 'post_id': post['id']},
                   color="outline-primary", size="sm", className="float-end"
                ) if comments_enabled else html.Div()
            ])
        ])
    ], className="mb-4 shadow-sm", style={'border': 'none'})


# ============================================================================
# ADMIN POST CREATION/EDITING FORM
# ============================================================================

def create_admin_post_form(edit_mode: bool = False, post_data: Optional[Dict] = None) -> dbc.Form:
    """Admin form for creating/editing posts"""

    form_title = "Edit Post" if edit_mode else "Create New Post"
    button_text = "Update Post" if edit_mode else "Publish Post"

    # Default values
    defaults = post_data if post_data else {
        'title': '',
        'content': '',
        'min_access_tier': 1,
        'comments_enabled': False,
        'is_permanent': False,
        'expires_at': '',
        'category': 'announcement',
        'is_pinned': False
    }

    return dbc.Form([
        # Form Header
        html.H4(form_title, className="mb-4 fw-bold",
               style={'color': USC_COLORS['primary_green']}),

        # Title
        dbc.Row([
            dbc.Col([
                dbc.Label("Post Title *", className="fw-bold"),
                dbc.Input(
                    id="post-title-input",
                    type="text",
                    placeholder="Enter post title...",
                    value=defaults['title'],
                    required=True,
                    className="mb-3"
                )
            ])
        ]),

        # Content
        dbc.Row([
            dbc.Col([
                dbc.Label("Post Content *", className="fw-bold"),
                dbc.Textarea(
                    id="post-content-input",
                    placeholder="Write your announcement or news content here...",
                    value=defaults['content'],
                    rows=8,
                    required=True,
                    className="mb-3"
                )
            ])
        ]),

        # Settings Row 1: Access Control and Category
        dbc.Row([
            dbc.Col([
                dbc.Label("Minimum Access Tier *", className="fw-bold"),
                dcc.Dropdown(
                    id="post-tier-dropdown",
                    options=[
                        {'label': 'Tier 1 - Public (Everyone)', 'value': 1},
                        {'label': 'Tier 2 - Limited Access', 'value': 2},
                        {'label': 'Tier 3 - Complete Access', 'value': 3},
                        {'label': 'Tier 4 - Admin Only', 'value': 4}
                    ],
                    value=defaults['min_access_tier'],
                    clearable=False,
                    className="mb-3"
                ),
                html.Small("Who can view this post?", className="text-muted")
            ], md=6),

            dbc.Col([
                dbc.Label("Category *", className="fw-bold"),
                dcc.Dropdown(
                    id="post-category-dropdown",
                    options=[
                        {'label': '📢 Announcement', 'value': 'announcement'},
                        {'label': '📰 News', 'value': 'news'},
                        {'label': '📅 Event', 'value': 'event'},
                        {'label': '📋 Policy Update', 'value': 'policy'},
                        {'label': '📊 Data Release', 'value': 'data_release'}
                    ],
                    value=defaults['category'],
                    clearable=False,
                    className="mb-3"
                )
            ], md=6)
        ]),

        # Settings Row 2: Time and Display Options
        dbc.Row([
            dbc.Col([
                dbc.Label("Post Duration", className="fw-bold"),
                dcc.Dropdown(
                    id="post-duration-dropdown",
                    options=[
                        {'label': '📌 Permanent (No Expiration)', 'value': 'permanent'},
                        {'label': '📅 7 Days', 'value': '7'},
                        {'label': '📅 30 Days', 'value': '30'},
                        {'label': '📅 90 Days', 'value': '90'},
                        {'label': '🗓️ Custom Date', 'value': 'custom'}
                    ],
                    value='permanent' if defaults['is_permanent'] else '30',
                    clearable=False,
                    className="mb-3"
                ),

                # Custom date picker (hidden unless 'custom' selected)
                html.Div([
                    dbc.Label("Expiration Date", className="fw-bold mt-2"),
                    dbc.Input(
                        id="post-expiration-date",
                        type="date",
                        value=defaults['expires_at'][:10] if defaults.get('expires_at') else '',
                        className="mb-3"
                    )
                ], id="custom-date-container", style={'display': 'none'})
            ], md=6),

            dbc.Col([
                dbc.Label("Display Options", className="fw-bold"),
                dbc.Checklist(
                    id="post-options-checklist",
                    options=[
                        {'label': ' Enable Comments', 'value': 'comments'},
                        {'label': ' Pin to Top', 'value': 'pinned'}
                    ],
                    value=[
                        'comments' if defaults['comments_enabled'] else None,
                        'pinned' if defaults['is_pinned'] else None
                    ],
                    inline=False,
                    className="mb-3"
                )
            ], md=6)
        ]),

        # Preview Section
        html.Hr(className="my-4"),
        html.H5("Preview", className="fw-bold mb-3",
               style={'color': USC_COLORS['primary_green']}),
        html.Div(id="post-preview-container", className="mb-4"),

        # Action Buttons
        dbc.Row([
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-check me-2"),
                    button_text
                ], id="submit-post-btn", color="success", size="lg", className="me-3"),

                dbc.Button([
                    html.I(className="fas fa-eye me-2"),
                    "Preview"
                ], id="preview-post-btn", color="info", size="lg", outline=True, className="me-3"),

                dbc.Button("Cancel", id="cancel-post-btn", color="secondary",
                          size="lg", outline=True)
            ])
        ])
    ])


# ============================================================================
# ADMIN POST MANAGEMENT DASHBOARD
# ============================================================================

def create_posts_management_tab(posts: List[Dict]) -> html.Div:
    """Admin dashboard tab for managing all posts"""

    if not posts:
        return dbc.Alert([
            html.H5("No Posts Yet", className="alert-heading"),
            html.P("Create your first post to get started!"),
            dbc.Button("Create Post", id="create-first-post-btn", color="primary")
        ], color="info")

    # Statistics cards
    stats_cards = create_posts_statistics_cards(posts)

    # Posts table
    posts_table = create_posts_management_table(posts)

    return html.Div([
        # Stats Overview
        dbc.Row([
            dbc.Col(stats_cards, className="mb-4")
        ]),

        # Create New Post Button
        dbc.Row([
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Create New Post"
                ], id="create-new-post-btn", color="primary", size="lg", className="mb-4")
            ])
        ]),

        # ✅ ADD THIS: Collapsible form container
        dbc.Collapse([
            dbc.Card([
                dbc.CardBody([
                    create_admin_post_form(edit_mode=False)
                ])
            ], className="mb-4 shadow")
        ], id="post-form-collapse", is_open=False),

        # Posts Management Table
        dbc.Row([
            dbc.Col([
                html.H4("All Posts", className="fw-bold mb-3",
                       style={'color': USC_COLORS['primary_green']}),
                posts_table
            ])
        ])
    ])


def create_posts_statistics_cards(posts: List[Dict]) -> dbc.Row:
    """Create statistics cards for posts dashboard"""

    total_posts = len(posts)
    active_posts = len([p for p in posts if p['status'] == 'published'])
    pinned_posts = len([p for p in posts if p.get('is_pinned', False)])
    total_views = sum([p.get('view_count', 0) for p in posts])

    cards = [
        {
            'icon': 'fas fa-newspaper',
            'title': 'Total Posts',
            'value': total_posts,
            'color': 'primary'
        },
        {
            'icon': 'fas fa-check-circle',
            'title': 'Active Posts',
            'value': active_posts,
            'color': 'success'
        },
        {
            'icon': 'fas fa-thumbtack',
            'title': 'Pinned Posts',
            'value': pinned_posts,
            'color': 'warning'
        },
        {
            'icon': 'fas fa-eye',
            'title': 'Total Views',
            'value': total_views,
            'color': 'info'
        }
    ]

    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className=f"{card['icon']} fa-2x mb-2",
                              style={'color': USC_COLORS['accent_yellow']}),
                        html.H3(card['value'], className="fw-bold mb-0",
                               style={'color': USC_COLORS['primary_green']}),
                        html.P(card['title'], className="text-muted small mb-0")
                    ], className="text-center")
                ])
            ], className="shadow-sm h-100")
        ], width=12, md=3) for card in cards
    ])


def create_posts_management_table(posts: List[Dict]) -> dbc.Table:
    """Create table of all posts with management actions"""

    table_header = [
        html.Thead(html.Tr([
            html.Th("Status"),
            html.Th("Title"),
            html.Th("Category"),
            html.Th("Access Tier"),
            html.Th("Views"),
            html.Th("Created"),
            html.Th("Actions")
        ]))
    ]

    rows = []
    for post in posts:
        # Status badge
        status = post['status']
        status_badge = dbc.Badge(
            status.title(),
            color='success' if status == 'published' else 'secondary'
        )

        # Pinned indicator
        if post.get('is_pinned'):
            status_badge = html.Span([
                status_badge,
                html.I(className="fas fa-thumbtack ms-2 text-warning")
            ])

        # Format date
        created_date = datetime.fromisoformat(post['created_at']).strftime("%b %d, %Y")

        # Action buttons
        actions = dbc.ButtonGroup([
            dbc.Button(html.I(className="fas fa-eye"),
                      id={'type': 'view-post-admin', 'post_id': post['id']},
                      color="info", size="sm", outline=True),
            dbc.Button(html.I(className="fas fa-edit"),
                      id={'type': 'edit-post', 'post_id': post['id']},
                      color="primary", size="sm", outline=True),
            dbc.Button(html.I(className="fas fa-trash"),
                      id={'type': 'delete-post', 'post_id': post['id']},
                      color="danger", size="sm", outline=True)
        ], size="sm")

        rows.append(html.Tr([
            html.Td(status_badge),
            html.Td(post['title'][:50] + "..." if len(post['title']) > 50 else post['title']),
            html.Td(post.get('category', 'N/A').replace('_', ' ').title()),
            html.Td(f"Tier {post['min_access_tier']}"),
            html.Td(post.get('view_count', 0)),
            html.Td(created_date),
            html.Td(actions)
        ]))

    table_body = [html.Tbody(rows)]

    return dbc.Table(
        table_header + table_body,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-0"
    )


# ============================================================================
# COMMENT COMPONENTS
# ============================================================================

def create_comments_section(post_id: int, comments: List[Dict],
                           user_data: Optional[Dict] = None) -> html.Div:
    """Create comments section for a post"""

    if not user_data:
        return dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            "Please sign in to view and post comments."
        ], color="info")

    comment_items = []
    for comment in comments:
        comment_items.append(create_comment_card(comment, user_data))

    return html.Div([
        html.H5([
            html.I(className="fas fa-comments me-2"),
            f"Comments ({len(comments)})"
        ], className="fw-bold mb-3", style={'color': USC_COLORS['primary_green']}),

        # Add comment form
        dbc.Card([
            dbc.CardBody([
                dbc.Textarea(
                    id={'type': 'comment-input', 'post_id': post_id},
                    placeholder="Write a comment...",
                    rows=3,
                    className="mb-3"
                ),
                dbc.Button([
                    html.I(className="fas fa-paper-plane me-2"),
                    "Post Comment"
                ], id={'type': 'submit-comment', 'post_id': post_id},
                   color="primary", size="sm")
            ])
        ], className="mb-4"),

        # Comments list
        html.Div(comment_items if comment_items else
                dbc.Alert("No comments yet. Be the first to comment!", color="light"))
    ])


def create_comment_card(comment: Dict, user_data: Optional[Dict]) -> dbc.Card:
    """Create individual comment card"""

    # Format date
    created_at = datetime.fromisoformat(comment['created_at'])
    time_ago = format_time_ago(created_at)

    # Check if user can delete (own comment or admin)
    can_delete = (
        user_data and
        (user_data['id'] == comment['user_id'] or user_data.get('access_tier', 1) >= 4)
    )

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Strong(comment.get('commenter_name', 'Anonymous')),
                        html.Span(f" • {time_ago}", className="text-muted small ms-2")
                    ])
                ]),
                dbc.Col([
                    dbc.Button(html.I(className="fas fa-trash"),
                              id={'type': 'delete-comment', 'comment_id': comment['id']},
                              color="link", size="sm", className="text-danger p-0 float-end"
                    ) if can_delete else html.Div()
                ], width="auto")
            ], className="mb-2"),

            html.P(comment['content'], className="mb-0",
                  style={'whiteSpace': 'pre-wrap'})
        ])
    ], className="mb-3 shadow-sm", style={'border': 'none', 'backgroundColor': USC_COLORS['light_gray']})


def format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X time ago'"""
    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return dt.strftime("%b %d, %Y")


# ============================================================================
# MODAL DIALOGS
# ============================================================================

def create_post_modal() -> dbc.Modal:
    """Modal for creating/editing posts"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Create/Edit Post")),
        dbc.ModalBody(id="post-modal-body"),
        dbc.ModalFooter([
            dbc.Button("Close", id="close-post-modal", color="secondary")
        ])
    ], id="post-modal", size="xl", scrollable=True)


def create_delete_confirmation_modal() -> dbc.Modal:
    """Modal for confirming post deletion"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Confirm Deletion")),
        dbc.ModalBody([
            html.I(className="fas fa-exclamation-triangle fa-3x text-warning mb-3 d-block text-center"),
            html.H5("Are you sure you want to delete this post?", className="text-center"),
            html.P("This action cannot be undone. All comments will also be deleted.",
                  className="text-muted text-center")
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-delete-post", color="secondary"),
            dbc.Button("Delete Post", id="confirm-delete-post", color="danger")
        ])
    ], id="delete-post-modal", centered=True)