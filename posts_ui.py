"""
Posts UI Components - COMPLETE REBUILD
Clean, working version with proper formatting
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
# MAIN: POSTS MANAGEMENT TAB FOR ADMIN DASHBOARD
# ============================================================================

def create_posts_management_tab(posts: List[Dict]) -> html.Div:
    """Main posts management interface for admin dashboard"""

    print("=" * 60)
    print("🎨 CREATING POSTS MANAGEMENT TAB")
    print(f"   Posts count: {len(posts)}")
    print("=" * 60)

    # Statistics cards
    total_posts = len(posts)
    active_posts = len([p for p in posts if p.get('status') == 'published'])
    pinned_posts = len([p for p in posts if p.get('is_pinned', False)])
    total_views = sum([p.get('view_count', 0) for p in posts])

    return html.Div([
        # Page Title
        html.H2("Posts Management", className="mb-4",
               style={'color': USC_COLORS['primary_green']}),

        # Statistics Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-newspaper fa-2x mb-2",
                              style={'color': USC_COLORS['accent_yellow']}),
                        html.H3(total_posts, className="mb-0"),
                        html.P("Total Posts", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-check-circle fa-2x mb-2",
                              style={'color': USC_COLORS['secondary_green']}),
                        html.H3(active_posts, className="mb-0"),
                        html.P("Active", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-thumbtack fa-2x mb-2",
                              style={'color': USC_COLORS['accent_yellow']}),
                        html.H3(pinned_posts, className="mb-0"),
                        html.P("Pinned", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-eye fa-2x mb-2",
                              style={'color': USC_COLORS['primary_green']}),
                        html.H3(total_views, className="mb-0"),
                        html.P("Total Views", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], width=3)
        ], className="mb-4"),

        # Create Post Button
        dbc.Button([
            html.I(className="fas fa-plus me-2"),
            "Create New Post"
        ], id="create-new-post-btn", color="primary", size="lg", className="mb-3"),

        # Collapsible Form
        dbc.Collapse([
            dbc.Card([
                dbc.CardBody([
                    create_post_form()
                ])
            ], className="shadow")
        ], id="post-form-collapse", is_open=False, className="mb-4"),

        # Posts Table
        html.H4("All Posts", className="mt-4 mb-3", style={'color': USC_COLORS['primary_green']}),
        create_posts_table(posts) if posts else dbc.Alert("No posts yet. Create your first post!", color="info")
    ])


# ============================================================================
# POST CREATION FORM
# ============================================================================

def create_post_form() -> html.Div:
    """Post creation/editing form"""

    print("📝 Creating post form")

    return html.Div([
        html.H4("Create New Post", className="mb-4", style={'color': USC_COLORS['primary_green']}),

        # Title Input
        dbc.Row([
            dbc.Col([
                dbc.Label("Post Title *", className="fw-bold"),
                dbc.Input(
                    id="post-title-input",
                    type="text",
                    placeholder="Enter post title...",
                    className="mb-3"
                )
            ])
        ]),

        # Content Input
        dbc.Row([
            dbc.Col([
                dbc.Label("Content *", className="fw-bold"),
                dbc.Textarea(
                    id="post-content-input",
                    placeholder="Write your post content here...",
                    rows=8,
                    className="mb-3"
                )
            ])
        ]),

        # Settings Row
        dbc.Row([
            # Access Tier
            dbc.Col([
                dbc.Label("Who can view this post?", className="fw-bold"),
                dcc.Dropdown(
                    id="post-tier-dropdown",
                    options=[
                        {'label': 'Tier 1 - Everyone (Public)', 'value': 1},
                        {'label': 'Tier 2 - Limited Access', 'value': 2},
                        {'label': 'Tier 3 - Complete Access', 'value': 3},
                        {'label': 'Tier 4 - Admin Only', 'value': 4}
                    ],
                    value=1,
                    clearable=False,
                    className="mb-3"
                )
            ], md=6),

            # Category
            dbc.Col([
                dbc.Label("Category", className="fw-bold"),
                dcc.Dropdown(
                    id="post-category-dropdown",
                    options=[
                        {'label': '📢 Announcement', 'value': 'announcement'},
                        {'label': '📰 News', 'value': 'news'},
                        {'label': '📅 Event', 'value': 'event'},
                        {'label': '📋 Policy', 'value': 'policy'},
                        {'label': '📊 Data Release', 'value': 'data_release'}
                    ],
                    value='announcement',
                    clearable=False,
                    className="mb-3"
                )
            ], md=6)
        ]),

        # Duration Row
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
                    value='permanent',
                    clearable=False,
                    className="mb-3"
                )
            ], md=6),

            # Options
            dbc.Col([
                dbc.Label("Options", className="fw-bold"),
                dbc.Checklist(
                    id="post-options-checklist",
                    options=[
                        {'label': ' Enable Comments', 'value': 'comments'},
                        {'label': ' Pin to Top', 'value': 'pinned'}
                    ],
                    value=[],
                    className="mb-3"
                )
            ], md=6)
        ]),

        # Custom Date (Hidden by default)
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Expiration Date", className="fw-bold"),
                    dbc.Input(
                        id="post-expiration-date",
                        type="date",
                        className="mb-3"
                    )
                ], md=6)
            ])
        ], id="custom-date-container", style={'display': 'none'}),

        # Preview Container
        html.Div(id="post-preview-container", className="mb-3"),

        # Action Buttons
        dbc.ButtonGroup([
            dbc.Button([
                html.I(className="fas fa-check me-2"),
                "Publish Post"
            ], id="submit-post-btn", color="success", size="lg"),

            dbc.Button([
                html.I(className="fas fa-eye me-2"),
                "Preview"
            ], id="preview-post-btn", color="info", size="lg", outline=True),

            dbc.Button([
                html.I(className="fas fa-times me-2"),
                "Cancel"
            ], id="cancel-post-btn", color="secondary", size="lg", outline=True)
        ], className="w-100")
    ])


# ============================================================================
# POSTS TABLE
# ============================================================================

def create_posts_table(posts: List[Dict]) -> dbc.Table:
    """Create table showing all posts"""

    if not posts:
        return dbc.Alert("No posts found", color="info")

    # Table header
    header = html.Thead(html.Tr([
        html.Th("Status"),
        html.Th("Title"),
        html.Th("Category"),
        html.Th("Access"),
        html.Th("Views"),
        html.Th("Created"),
        html.Th("Actions", style={'textAlign': 'center'})
    ]))

    # Table rows
    rows = []
    for post in posts:
        # Status badge
        status = post.get('status', 'published')
        status_badge = dbc.Badge(
            status.title(),
            color='success' if status == 'published' else 'secondary'
        )

        if post.get('is_pinned'):
            status_badge = html.Span([
                status_badge,
                html.I(className="fas fa-thumbtack ms-2 text-warning")
            ])

        # Format date
        created_date = datetime.fromisoformat(post['created_at']).strftime("%b %d, %Y")

        # Action buttons
        actions = dbc.ButtonGroup([
            dbc.Button(
                html.I(className="fas fa-eye"),
                id={'type': 'view-post-admin', 'post_id': post['id']},
                color="info",
                size="sm",
                outline=True
            ),
            dbc.Button(
                html.I(className="fas fa-edit"),
                id={'type': 'edit-post', 'post_id': post['id']},
                color="primary",
                size="sm",
                outline=True
            ),
            dbc.Button(
                html.I(className="fas fa-trash"),
                id={'type': 'delete-post', 'post_id': post['id']},
                color="danger",
                size="sm",
                outline=True
            )
        ], size="sm")

        # Create row
        row = html.Tr([
            html.Td(status_badge),
            html.Td(post['title'][:50] + "..." if len(post['title']) > 50 else post['title']),
            html.Td(post.get('category', 'N/A').replace('_', ' ').title()),
            html.Td(f"Tier {post.get('min_access_tier', 1)}"),
            html.Td(post.get('view_count', 0)),
            html.Td(created_date),
            html.Td(actions, style={'textAlign': 'center'})
        ])
        rows.append(row)

    body = html.Tbody(rows)

    return dbc.Table(
        [header, body],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    )


# ============================================================================
# HOMEPAGE NEWS FEED
# ============================================================================

def create_news_feed_section(posts: List[Dict], user_data: Optional[Dict] = None) -> html.Div:
    """News feed for homepage - shows 3 most recent posts"""

    if not posts:
        return html.Div()

    # Take 3 most recent
    recent_posts = posts[:3]

    return html.Section([
        dbc.Container([
            # Header
            html.H2([
                html.I(className="fas fa-bullhorn me-3",
                      style={'color': USC_COLORS['accent_yellow']}),
                "Latest News & Announcements"
            ], className="text-center mb-4", style={'color': USC_COLORS['primary_green']}),

            # Posts Grid
            dbc.Row([
                dbc.Col([
                    create_news_card(post)
                ], width=12, md=4) for post in recent_posts
            ], className="g-4 mb-4"),

            # View All Button
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


def create_news_card(post: Dict) -> dbc.Card:
    """Individual news card for homepage"""

    # Category colors
    category_colors = {
        'announcement': 'primary',
        'news': 'info',
        'event': 'success',
        'policy': 'warning',
        'data_release': 'secondary'
    }

    category = post.get('category', 'announcement')
    created_at = datetime.fromisoformat(post['created_at'])
    date_str = created_at.strftime("%B %d, %Y")

    return dbc.Card([
        dbc.CardBody([
            # Category badge
            dbc.Badge(
                category.replace('_', ' ').title(),
                color=category_colors.get(category, 'primary'),
                className="mb-2"
            ),

            # Title
            html.H5(post['title'], className="card-title fw-bold mb-2",
                   style={'color': USC_COLORS['primary_green']}),

            # Excerpt
            html.P(
                post['content'][:120] + "..." if len(post['content']) > 120 else post['content'],
                className="card-text text-muted mb-3"
            ),

            # Footer
            html.Div([
                html.Small([
                    html.I(className="far fa-calendar me-2"),
                    date_str
                ], className="text-muted"),
                dbc.Button(
                    "Read More →",
                    id={'type': 'view-post', 'post_id': post['id']},
                    color="link",
                    size="sm",
                    className="p-0 float-end"
                )
            ])
        ])
    ], className="h-100 shadow-sm")


# ============================================================================
# NEWS PAGE
# ============================================================================

def create_news_page(posts: List[Dict], user_data: Optional[Dict] = None) -> html.Div:
    """Full news page with all posts"""

    if not posts:
        return dbc.Container([
            html.H1("News & Announcements", className="text-center my-5"),
            dbc.Alert("No posts available", color="info", className="text-center")
        ])

    # Separate pinned and regular
    pinned = [p for p in posts if p.get('is_pinned')]
    regular = [p for p in posts if not p.get('is_pinned')]

    return html.Div([
        # Hero
        html.Section([
            dbc.Container([
                html.H1("News & Announcements", className="display-4 fw-bold mb-3 text-center",
                       style={'color': USC_COLORS['primary_green']}),
                html.P("Official updates from Institutional Research",
                      className="lead text-muted text-center")
            ])
        ], className="py-5", style={'backgroundColor': USC_COLORS['light_gray']}),

        # Content
        dbc.Container([
            # Pinned posts
            html.Div([
                html.H3([
                    html.I(className="fas fa-thumbtack me-2",
                          style={'color': USC_COLORS['accent_yellow']}),
                    "Pinned Posts"
                ], className="mb-4", style={'color': USC_COLORS['primary_green']}),
                html.Div([create_full_post_card(p) for p in pinned])
            ], className="mb-5") if pinned else html.Div(),

            # Regular posts
            html.H3("Recent Posts", className="mb-4", style={'color': USC_COLORS['primary_green']}),
            html.Div([create_full_post_card(p) for p in regular])
        ], fluid=True, className="py-4")
    ])


def create_full_post_card(post: Dict) -> dbc.Card:
    """Full post card for news page"""

    created_at = datetime.fromisoformat(post['created_at'])
    date_str = created_at.strftime("%B %d, %Y at %I:%M %p")

    category_colors = {
        'announcement': 'primary',
        'news': 'info',
        'event': 'success',
        'policy': 'warning',
        'data_release': 'secondary'
    }

    return dbc.Card([
        dbc.CardBody([
            # Header
            dbc.Row([
                dbc.Col([
                    dbc.Badge(
                        post.get('category', 'announcement').replace('_', ' ').title(),
                        color=category_colors.get(post.get('category', 'announcement'), 'primary')
                    ),
                    dbc.Badge("Pinned", color="warning", className="ms-2") if post.get('is_pinned') else html.Span()
                ], width="auto"),
                dbc.Col([
                    html.Small([
                        html.I(className="fas fa-eye me-2"),
                        f"{post.get('view_count', 0)} views"
                    ], className="text-muted")
                ], className="text-end")
            ], className="mb-3"),

            # Title
            html.H4(post['title'], className="fw-bold mb-3",
                   style={'color': USC_COLORS['primary_green']}),

            # Content
            html.P(post['content'], style={'whiteSpace': 'pre-wrap'}, className="mb-3"),

            # Footer
            html.Hr(),
            html.Small([
                html.I(className="fas fa-user-circle me-2"),
                html.Span(post.get('author_name', 'Admin'), className="fw-bold me-3"),
                html.I(className="far fa-calendar me-2"),
                date_str
            ], className="text-muted")
        ])
    ], className="mb-4 shadow-sm")


print("✅ Posts UI module loaded successfully")