"""
Posts UI Components - FIXED VERSION
Fixed news page layout to be centered instead of full-width
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
# FIXED: NEWS PAGE WITH CENTERED LAYOUT
# ============================================================================

def create_news_page(posts: List[Dict], user_data: Optional[Dict] = None) -> html.Div:
    """Full news page with all posts - FIXED: Centered layout"""

    if not posts:
        return dbc.Container([
            html.H1("News & Announcements", className="text-center my-5"),
            dbc.Alert("No posts available", color="info", className="text-center")
        ])

    # Separate pinned and regular
    pinned = [p for p in posts if p.get('is_pinned')]
    regular = [p for p in posts if not p.get('is_pinned')]

    return html.Div([
        # Hero Section - Keep full width for visual impact
        html.Section([
            dbc.Container([
                html.H1("News & Announcements", className="display-4 fw-bold mb-3 text-center",
                       style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),
                html.P("Official updates from Institutional Research",
                      className="lead text-muted text-center",
                      style={'fontFamily': 'Roboto, sans-serif'})
            ])
        ], className="py-5", style={'backgroundColor': USC_COLORS['light_gray']}),

        # FIXED: Content Container - Removed fluid=True for centered layout
        dbc.Container([
            # Pinned posts
            html.Div([
                html.H3([
                    html.I(className="fas fa-thumbtack me-2",
                          style={'color': USC_COLORS['accent_yellow']}),
                    "Pinned Posts"
                ], className="mb-4", style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),
                html.Div([create_full_post_card(p) for p in pinned])
            ], className="mb-5") if pinned else html.Div(),

            # Regular posts
            html.H3("Recent Posts", className="mb-4",
                   style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),
            html.Div([create_full_post_card(p) for p in regular])
        ], className="py-4")  # FIXED: Removed fluid=True, content now respects Bootstrap's max-width
    ])


def create_full_post_card(post: Dict) -> dbc.Card:
    """Full post card for news page with improved typography"""

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
                    ], className="text-muted", style={'fontFamily': 'Roboto, sans-serif'})
                ], className="text-end")
            ], className="mb-3"),

            # Title
            html.H4(post['title'], className="fw-bold mb-3",
                   style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),

            # Content
            html.P(post['content'], style={
                'whiteSpace': 'pre-wrap',
                'fontFamily': 'Roboto, sans-serif',
                'lineHeight': '1.6'
            }, className="mb-3"),

            # Footer
            html.Hr(),
            html.Small([
                html.I(className="fas fa-user-circle me-2"),
                html.Span(post.get('author_name', 'Admin'), className="fw-bold me-3"),
                html.I(className="far fa-calendar me-2"),
                date_str
            ], className="text-muted", style={'fontFamily': 'Roboto, sans-serif'})
        ])
    ], className="mb-4 shadow-sm")


# ============================================================================
# NEWS FEED SECTION FOR HOMEPAGE (unchanged but added font)
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
            ], className="text-center mb-4",
               style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),

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
                    ], href="/news", color="primary", outline=True, size="lg",
                    style={'fontFamily': 'Roboto, sans-serif'})
                ], className="text-center")
            ])
        ], fluid=True)
    ], className="py-5", style={'backgroundColor': USC_COLORS['light_gray']})


def create_news_card(post: Dict) -> dbc.Card:
    """Individual news card for homepage with improved typography"""

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
                   style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),

            # Excerpt
            html.P(
                post['content'][:120] + "..." if len(post['content']) > 120 else post['content'],
                className="card-text text-muted mb-3",
                style={'fontFamily': 'Roboto, sans-serif', 'lineHeight': '1.5'}
            ),

            # Footer
            html.Div([
                html.Small([
                    html.I(className="far fa-calendar me-2"),
                    date_str
                ], className="text-muted", style={'fontFamily': 'Roboto, sans-serif'}),
                dbc.Button(
                    "Read More →",
                    id={'type': 'view-post', 'post_id': post['id']},
                    color="link",
                    size="sm",
                    className="p-0 float-end",
                    style={'fontFamily': 'Roboto, sans-serif'}
                )
            ])
        ])
    ], className="h-100 shadow-sm")


# ============================================================================
# POSTS MANAGEMENT TAB (unchanged but added font)
# ============================================================================
def create_posts_management_tab(posts: List[Dict]) -> html.Div:
    """Posts management with SIMPLE delete buttons"""

    # Statistics cards (your existing code)
    total_posts = len(posts)
    active_posts = len([p for p in posts if p.get('status') == 'published'])
    pinned_posts = len([p for p in posts if p.get('is_pinned', False)])
    total_views = sum([p.get('view_count', 0) for p in posts])

    return html.Div([
        # Page Title
        html.H2("Posts Management", className="mb-4",
                style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),

        # Statistics Row (your existing code)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-newspaper fa-2x mb-2",
                               style={'color': USC_COLORS['accent_yellow']}),
                        html.H3(total_posts, className="mb-0", style={'fontFamily': 'Roboto, sans-serif'}),
                        html.P("Total Posts", className="text-muted mb-0", style={'fontFamily': 'Roboto, sans-serif'})
                    ], className="text-center")
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-check-circle fa-2x mb-2",
                               style={'color': USC_COLORS['secondary_green']}),
                        html.H3(active_posts, className="mb-0", style={'fontFamily': 'Roboto, sans-serif'}),
                        html.P("Active", className="text-muted mb-0", style={'fontFamily': 'Roboto, sans-serif'})
                    ], className="text-center")
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-thumbtack fa-2x mb-2",
                               style={'color': USC_COLORS['accent_yellow']}),
                        html.H3(pinned_posts, className="mb-0", style={'fontFamily': 'Roboto, sans-serif'}),
                        html.P("Pinned", className="text-muted mb-0", style={'fontFamily': 'Roboto, sans-serif'})
                    ], className="text-center")
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-eye fa-2x mb-2",
                               style={'color': USC_COLORS['secondary_green']}),
                        html.H3(total_views, className="mb-0", style={'fontFamily': 'Roboto, sans-serif'}),
                        html.P("Total Views", className="text-muted mb-0", style={'fontFamily': 'Roboto, sans-serif'})
                    ], className="text-center")
                ])
            ], width=3)
        ], className="mb-4"),

        # Create Post Button
        dbc.Button([
            html.I(className="fas fa-plus me-2"),
            "Create New Post"
        ], id="create-new-post-btn", color="primary", size="lg", className="mb-3",
            style={'fontFamily': 'Roboto, sans-serif'}),

        # Collapsible Form (add your create_post_form() here)
        dbc.Collapse([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Create New Post", className="mb-3",
                            style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),

                    dbc.Input(id="post-title-input", placeholder="Post Title", className="mb-3"),
                    dbc.Textarea(id="post-content-input", placeholder="Post Content", rows=6, className="mb-3"),

                    dcc.Dropdown(
                        id="post-tier-dropdown",
                        options=[
                            {'label': 'Tier 1 - Public', 'value': 1},
                            {'label': 'Tier 2 - Limited', 'value': 2},
                            {'label': 'Tier 3 - Complete', 'value': 3},
                            {'label': 'Tier 4 - Admin', 'value': 4}
                        ],
                        value=1,
                        placeholder="Select Access Level",
                        className="mb-3"
                    ),

                    dcc.Dropdown(
                        id="post-category-dropdown",
                        options=[
                            {'label': 'Announcement', 'value': 'announcement'},
                            {'label': 'News', 'value': 'news'},
                            {'label': 'Event', 'value': 'event'}
                        ],
                        value='announcement',
                        placeholder="Select Category",
                        className="mb-3"
                    ),

                    dcc.Dropdown(
                        id="post-duration-dropdown",
                        options=[
                            {'label': 'Permanent', 'value': 'permanent'},
                            {'label': '7 Days', 'value': '7'},
                            {'label': '30 Days', 'value': '30'}
                        ],
                        value='permanent',
                        placeholder="Select Duration",
                        className="mb-3"
                    ),

                    dbc.Checklist(
                        id="post-options-checklist",
                        options=[
                            {'label': 'Pin to Top', 'value': 'pinned'},
                            {'label': 'Enable Comments', 'value': 'comments'}
                        ],
                        value=[],
                        className="mb-3"
                    ),

                    html.Div(id="post-expiration-date", style={'display': 'none'}),
                    html.Div(id="custom-date-container", style={'display': 'none'}),

                    dbc.ButtonGroup([
                        dbc.Button("Publish Post", id="submit-post-btn", color="success"),
                        dbc.Button("Cancel", id="cancel-post-btn", color="secondary", outline=True)
                    ])
                ])
            ])
        ], id="post-form-collapse", is_open=False, className="mb-4"),

        # ✅ SIMPLE POSTS LIST WITH DELETE BUTTONS
        html.H4("All Posts", className="mt-4 mb-3",
                style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),

        html.Div([
            create_simple_posts_list_with_delete(posts)
        ])
    ])


def create_simple_posts_list_with_delete(posts):
    """Simple posts list with inline delete buttons"""

    if not posts:
        return dbc.Alert("No posts yet. Create your first post!", color="info",
                         style={'fontFamily': 'Roboto, sans-serif'})

    post_items = []
    for post in posts:

        # Format date
        from datetime import datetime
        try:
            created_date = datetime.fromisoformat(post['created_at']).strftime("%b %d, %Y")
        except:
            created_date = "Unknown"

        post_item = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    # Post info column
                    dbc.Col([
                        html.H5(post.get('title', 'Untitled'), className="mb-2",
                                style={'color': USC_COLORS['primary_green'], 'fontFamily': 'Roboto, sans-serif'}),
                        html.P(
                            (post.get('content', '')[:120] + "..."
                             if len(post.get('content', '')) > 120
                             else post.get('content', '')),
                            className="text-muted mb-2",
                            style={'fontFamily': 'Roboto, sans-serif'}
                        ),
                        html.Div([
                            dbc.Badge(f"Tier {post.get('min_access_tier', 1)}",
                                      color="info", className="me-2"),
                            dbc.Badge(post.get('category', 'announcement').title(),
                                      color="secondary", className="me-2"),
                            dbc.Badge("Pinned", color="warning", className="me-2") if post.get(
                                'is_pinned') else html.Span(),
                            html.Small(f"Created: {created_date}", className="text-muted")
                        ])
                    ], width=8),

                    # Action buttons column
                    dbc.Col([
                        html.Div([
                            # ✅ SIMPLE DELETE BUTTON
                            dbc.Button([
                                html.I(className="fas fa-trash me-2"),
                                "Delete"
                            ],
                                id={'type': 'simple-delete-post', 'post_id': post['id']},
                                color="danger",
                                size="sm",
                                outline=True,
                                className="mb-2 w-100",
                                style={'fontFamily': 'Roboto, sans-serif'}),

                            # Edit button (optional)
                            dbc.Button([
                                html.I(className="fas fa-edit me-2"),
                                "Edit"
                            ],
                                color="primary",
                                size="sm",
                                outline=True,
                                className="w-100",
                                style={'fontFamily': 'Roboto, sans-serif'},
                                disabled=True)  # Disable for now
                        ])
                    ], width=4)
                ])
            ])
        ], className="mb-3 shadow-sm")

        post_items.append(post_item)

    return html.Div(post_items)