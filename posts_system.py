"""
Posts and Announcements System for USC Institutional Research Portal
Handles news posts, announcements, and comments with tier-based access control
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_posts_database():
    """Initialize posts and comments tables with proper schema"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    
    try:
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Access Control
                min_access_tier INTEGER DEFAULT 1,
                
                -- Post Configuration
                comments_enabled BOOLEAN DEFAULT FALSE,
                is_pinned BOOLEAN DEFAULT FALSE,
                
                -- Time-based visibility
                is_permanent BOOLEAN DEFAULT FALSE,
                expires_at TIMESTAMP NULL,
                
                -- Status and metadata
                status TEXT DEFAULT 'published',
                view_count INTEGER DEFAULT 0,
                category TEXT DEFAULT 'announcement',
                
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
        ''')
        
        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_approved BOOLEAN DEFAULT TRUE,
                is_flagged BOOLEAN DEFAULT FALSE,
                
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_tier ON posts(min_access_tier)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_expires ON posts(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_pinned ON posts(is_pinned)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_post ON post_comments(post_id)')
        
        conn.commit()
        print("✅ Posts system database initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing posts database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()


# ============================================================================
# POST MANAGEMENT - CREATE, READ, UPDATE, DELETE
# ============================================================================

def create_post(
    title: str,
    content: str,
    author_id: int,
    min_access_tier: int = 1,
    comments_enabled: bool = False,
    is_permanent: bool = False,
    expires_at: Optional[str] = None,
    category: str = 'announcement',
    is_pinned: bool = False
) -> Optional[int]:
    """
    Create a new post
    Returns: post_id if successful, None otherwise
    """
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO posts (
                title, content, author_id, min_access_tier,
                comments_enabled, is_permanent, expires_at, category, is_pinned
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, content, author_id, min_access_tier,
            comments_enabled, is_permanent, expires_at, category, is_pinned
        ))
        
        conn.commit()
        post_id = cursor.lastrowid
        print(f"✅ Post created successfully (ID: {post_id})")
        return post_id
        
    except Exception as e:
        print(f"❌ Error creating post: {str(e)}")
        conn.rollback()
        return None
    finally:
        conn.close()


def get_active_posts(user_tier: int = 1, include_expired: bool = False) -> List[Dict]:
    """
    Get all active posts visible to user's tier
    Automatically filters out expired posts unless include_expired=True
    """
    conn = sqlite3.connect('usc_ir.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        
        if include_expired:
            query = '''
                SELECT p.*, u.full_name as author_name, u.email as author_email
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                WHERE p.status = 'published' 
                AND p.min_access_tier <= ?
                ORDER BY p.is_pinned DESC, p.created_at DESC
            '''
            cursor.execute(query, (user_tier,))
        else:
            query = '''
                SELECT p.*, u.full_name as author_name, u.email as author_email
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                WHERE p.status = 'published' 
                AND p.min_access_tier <= ?
                AND (p.is_permanent = TRUE OR p.expires_at IS NULL OR p.expires_at > ?)
                ORDER BY p.is_pinned DESC, p.created_at DESC
            '''
            cursor.execute(query, (user_tier, now))
        
        posts = [dict(row) for row in cursor.fetchall()]
        return posts
        
    except Exception as e:
        print(f"❌ Error fetching posts: {str(e)}")
        return []
    finally:
        conn.close()


def get_post_by_id(post_id: int, increment_views: bool = False) -> Optional[Dict]:
    """Get single post by ID, optionally increment view count"""
    conn = sqlite3.connect('usc_ir.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Increment view count if requested
        if increment_views:
            cursor.execute('UPDATE posts SET view_count = view_count + 1 WHERE id = ?', (post_id,))
            conn.commit()
        
        cursor.execute('''
            SELECT p.*, u.full_name as author_name, u.email as author_email
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            WHERE p.id = ?
        ''', (post_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
        
    except Exception as e:
        print(f"❌ Error fetching post: {str(e)}")
        return None
    finally:
        conn.close()


def update_post(
    post_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    min_access_tier: Optional[int] = None,
    comments_enabled: Optional[bool] = None,
    is_permanent: Optional[bool] = None,
    expires_at: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    status: Optional[str] = None
) -> bool:
    """Update post fields (only non-None values are updated)"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    
    try:
        updates = []
        values = []
        
        if title is not None:
            updates.append("title = ?")
            values.append(title)
        if content is not None:
            updates.append("content = ?")
            values.append(content)
        if min_access_tier is not None:
            updates.append("min_access_tier = ?")
            values.append(min_access_tier)
        if comments_enabled is not None:
            updates.append("comments_enabled = ?")
            values.append(comments_enabled)
        if is_permanent is not None:
            updates.append("is_permanent = ?")
            values.append(is_permanent)
        if expires_at is not None:
            updates.append("expires_at = ?")
            values.append(expires_at)
        if is_pinned is not None:
            updates.append("is_pinned = ?")
            values.append(is_pinned)
        if status is not None:
            updates.append("status = ?")
            values.append(status)
        
        if not updates:
            return True  # Nothing to update
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(post_id)
        
        query = f"UPDATE posts SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"❌ Error updating post: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_post(post_id: int, soft_delete: bool = True) -> bool:
    """
    Delete post (soft delete sets status to 'archived', hard delete removes from DB)
    Soft delete is recommended to preserve history
    """
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    
    try:
        if soft_delete:
            cursor.execute('UPDATE posts SET status = ? WHERE id = ?', ('archived', post_id))
        else:
            cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"❌ Error deleting post: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()


# ============================================================================
# COMMENT MANAGEMENT
# ============================================================================

def add_comment(post_id: int, user_id: int, content: str) -> Optional[int]:
    """Add comment to a post"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    
    try:
        # Verify post exists and has comments enabled
        cursor.execute('SELECT comments_enabled FROM posts WHERE id = ?', (post_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            print("❌ Post not found or comments disabled")
            return None
        
        cursor.execute('''
            INSERT INTO post_comments (post_id, user_id, content)
            VALUES (?, ?, ?)
        ''', (post_id, user_id, content))
        
        conn.commit()
        return cursor.lastrowid
        
    except Exception as e:
        print(f"❌ Error adding comment: {str(e)}")
        conn.rollback()
        return None
    finally:
        conn.close()


def get_post_comments(post_id: int, approved_only: bool = True) -> List[Dict]:
    """Get all comments for a post"""
    conn = sqlite3.connect('usc_ir.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        if approved_only:
            query = '''
                SELECT c.*, u.full_name as commenter_name, u.email as commenter_email
                FROM post_comments c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.post_id = ? AND c.is_approved = TRUE AND c.is_flagged = FALSE
                ORDER BY c.created_at ASC
            '''
        else:
            query = '''
                SELECT c.*, u.full_name as commenter_name, u.email as commenter_email
                FROM post_comments c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.post_id = ?
                ORDER BY c.created_at ASC
            '''
        
        cursor.execute(query, (post_id,))
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"❌ Error fetching comments: {str(e)}")
        return []
    finally:
        conn.close()


def delete_comment(comment_id: int, user_id: int, is_admin: bool = False) -> bool:
    """Delete comment (user can delete own comments, admin can delete any)"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    
    try:
        if is_admin:
            cursor.execute('DELETE FROM post_comments WHERE id = ?', (comment_id,))
        else:
            cursor.execute('DELETE FROM post_comments WHERE id = ? AND user_id = ?', 
                         (comment_id, user_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"❌ Error deleting comment: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()


# ============================================================================
# ADMIN UTILITIES
# ============================================================================

def get_post_statistics() -> Dict:
    """Get overall statistics for admin dashboard"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM posts WHERE status = "published"')
        stats['total_active_posts'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM posts WHERE is_pinned = TRUE AND status = "published"')
        stats['pinned_posts'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM post_comments WHERE is_approved = TRUE')
        stats['total_comments'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(view_count) FROM posts')
        stats['total_views'] = cursor.fetchone()[0] or 0
        
        # Get posts expiring soon (within 7 days)
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM posts 
            WHERE expires_at IS NOT NULL 
            AND expires_at <= ? 
            AND status = "published"
        ''', (future_date,))
        stats['expiring_soon'] = cursor.fetchone()[0]
        
        return stats
        
    except Exception as e:
        print(f"❌ Error getting statistics: {str(e)}")
        return {}
    finally:
        conn.close()


def cleanup_expired_posts() -> int:
    """Archive expired posts (run as scheduled task)"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE posts 
            SET status = 'archived' 
            WHERE expires_at IS NOT NULL 
            AND expires_at <= ? 
            AND status = 'published'
            AND is_permanent = FALSE
        ''', (now,))
        
        conn.commit()
        archived_count = cursor.rowcount
        
        if archived_count > 0:
            print(f"✅ Archived {archived_count} expired posts")
        
        return archived_count
        
    except Exception as e:
        print(f"❌ Error cleaning up expired posts: {str(e)}")
        conn.rollback()
        return 0
    finally:
        conn.close()


# ============================================================================
# TESTING AND DEMO DATA
# ============================================================================

def create_demo_posts(admin_user_id: int = 1):
    """Create sample posts for testing"""
    demo_posts = [
        {
            'title': '🎓 Welcome to the New Academic Year!',
            'content': 'The Department of Institutional Research welcomes all students, faculty, and staff to AY 2024-2025. We look forward to supporting your data needs this year.',
            'min_access_tier': 1,
            'comments_enabled': True,
            'is_permanent': False,
            'expires_at': None,
            'category': 'announcement',
            'is_pinned': True
        },
        {
            'title': '📊 Q3 Enrollment Report Now Available',
            'content': 'The latest enrollment statistics for Quarter 3 are now available in the Factbook. Access requires Tier 2+ credentials.',
            'min_access_tier': 2,
            'comments_enabled': False,
            'is_permanent': False,
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'category': 'data_release',
            'is_pinned': False
        },
        {
            'title': '🔒 Financial Data Access Policy Update',
            'content': 'Please note: Financial data access now requires Tier 3 clearance. Contact ir@usc.edu.tt for upgrade requests.',
            'min_access_tier': 3,
            'comments_enabled': False,
            'is_permanent': True,
            'expires_at': None,
            'category': 'policy',
            'is_pinned': False
        }
    ]
    
    for post_data in demo_posts:
        post_data['author_id'] = admin_user_id
        create_post(**post_data)
    
    print("✅ Demo posts created successfully")


if __name__ == '__main__':
    # Initialize database when run directly
    init_posts_database()
    
    # Optional: Create demo posts
    # create_demo_posts(admin_user_id=1)
