"""
Simplified Authentication Utils for USC IR Portal
Fixes import errors and integrates cleanly with existing app.py
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import json
import re

class SimpleAuthManager:
    """Simple authentication manager to avoid circular imports"""
    
    def __init__(self, db_path: str = "usc_ir.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize authentication tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT,
                access_tier INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT TRUE,
                is_approved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        # Simple sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Access requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                current_tier INTEGER NOT NULL,
                requested_tier INTEGER NOT NULL,
                justification TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by INTEGER REFERENCES users(id),
                reviewed_at TIMESTAMP,
                admin_notes TEXT
            )
        ''')
        
        # Create default admin if none exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE access_tier = 4')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            admin_password_hash = self._hash_password("admin123")
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, access_tier, is_active, is_approved)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin@usc.edu.tt', admin_password_hash, 'System Administrator', 4, True, True))
        
        conn.commit()
        conn.close()
        print("✅ Authentication database initialized")
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_hex = stored_hash.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return password_hash.hex() == hash_hex
        except:
            return False
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and create session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, password_hash, full_name, access_tier, is_active, is_approved
                FROM users WHERE email = ?
            ''', (email,))
            
            user_row = cursor.fetchone()
            
            if not user_row or not self._verify_password(password, user_row[2]):
                conn.close()
                return {"success": False, "message": "Invalid credentials"}
            
            user_id, email, _, full_name, access_tier, is_active, is_approved = user_row
            
            if not is_active:
                conn.close()
                return {"success": False, "message": "Account is disabled"}
            
            if not is_approved:
                conn.close()
                return {"success": False, "message": "Account pending approval"}
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=8)
            
            cursor.execute('''
                INSERT INTO user_sessions (session_token, user_id, expires_at)
                VALUES (?, ?, ?)
            ''', (session_token, user_id, expires_at))
            
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "session_token": session_token,
                "user": {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "access_tier": access_tier
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def create_user(self, email: str, password: str, full_name: str, department: str = None) -> Dict[str, Any]:
        """Create new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "message": "User already exists"}
            
            # Auto-approve USC emails
            is_usc_email = email.endswith('@usc.edu.tt')
            access_tier = 2 if is_usc_email else 1
            is_approved = is_usc_email
            
            password_hash = self._hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, department, access_tier, is_approved)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, full_name, department, access_tier, is_approved))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "auto_approved": is_approved}
            
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user from session token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.email, u.full_name, u.access_tier
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.expires_at > ?
            ''', (session_token, datetime.now()))
            
            user_row = cursor.fetchone()
            conn.close()
            
            if user_row:
                return {
                    "id": user_row[0],
                    "email": user_row[1],
                    "full_name": user_row[2],
                    "access_tier": user_row[3]
                }
            return None
            
        except:
            return None
    
    def get_user_access_tier(self, session_data: Dict = None) -> int:
        """Get user access tier"""
        if not session_data or 'session_token' not in session_data:
            return 1
        
        user = self.get_user_by_session(session_data['session_token'])
        return user['access_tier'] if user else 1
    
    def has_access(self, required_tier: int, session_data: Dict = None) -> bool:
        """Check if user has required access"""
        return self.get_user_access_tier(session_data) >= required_tier
    
    def get_pending_requests(self) -> list:
        """Get pending access requests"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ar.id, ar.user_id, u.email, u.full_name, ar.current_tier,
                       ar.requested_tier, ar.justification, ar.requested_at
                FROM access_requests ar
                JOIN users u ON ar.user_id = u.id
                WHERE ar.status = 'pending'
                ORDER BY ar.requested_at ASC
            ''')
            
            requests = []
            for row in cursor.fetchall():
                requests.append({
                    "id": row[0],
                    "user_id": row[1],
                    "email": row[2],
                    "full_name": row[3],
                    "current_tier": row[4],
                    "requested_tier": row[5],
                    "justification": row[6],
                    "requested_at": row[7]
                })
            
            conn.close()
            return requests
            
        except:
            return []
    
    def approve_request(self, request_id: int, admin_user_id: int) -> bool:
        """Approve access request"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get request details
            cursor.execute('SELECT user_id, requested_tier FROM access_requests WHERE id = ?', (request_id,))
            request_row = cursor.fetchone()
            
            if request_row:
                user_id, requested_tier = request_row
                
                # Update user tier
                cursor.execute('UPDATE users SET access_tier = ? WHERE id = ?', (requested_tier, user_id))
                
                # Update request status
                cursor.execute('''
                    UPDATE access_requests 
                    SET status = 'approved', reviewed_by = ?, reviewed_at = ?
                    WHERE id = ?
                ''', (admin_user_id, datetime.now(), request_id))
                
                conn.commit()
            
            conn.close()
            return True
            
        except:
            return False
    
    def request_access_upgrade(self, user_id: int, requested_tier: int, justification: str) -> Dict[str, Any]:
        """Request access upgrade"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current tier
            cursor.execute('SELECT access_tier FROM users WHERE id = ?', (user_id,))
            current_tier = cursor.fetchone()[0]
            
            # Check for existing pending request
            cursor.execute('SELECT id FROM access_requests WHERE user_id = ? AND status = "pending"', (user_id,))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "message": "You already have a pending request"}
            
            # Create request
            cursor.execute('''
                INSERT INTO access_requests (user_id, current_tier, requested_tier, justification)
                VALUES (?, ?, ?, ?)
            ''', (user_id, current_tier, requested_tier, justification))
            
            request_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {"success": True, "request_id": request_id}
            
        except Exception as e:
            return {"success": False, "message": str(e)}

# Create global auth manager instance
auth_manager = SimpleAuthManager()

def get_user_access_tier(session_data=None):
    """Get user access tier - for compatibility with existing code"""
    return auth_manager.get_user_access_tier(session_data)

def has_access(required_tier, session_data=None):
    """Check access - for compatibility with existing code"""
    return auth_manager.has_access(required_tier, session_data)
