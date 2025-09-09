"""
Enhanced Database Schema for USC IR Portal Authentication System
Supports 4-tier access control with comprehensive user management
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

class AuthDatabase:
    """Enhanced database manager for authentication and user management"""
    
    def __init__(self, db_path: str = "usc_ir.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced users table with 4-tier access
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE,
                password_hash TEXT,
                full_name TEXT NOT NULL,
                department TEXT,
                role TEXT DEFAULT 'employee',
                access_tier INTEGER DEFAULT 1,  -- 1=public, 2=factbook, 3=financial, 4=admin
                is_active BOOLEAN DEFAULT TRUE,
                is_approved BOOLEAN DEFAULT FALSE,
                google_id TEXT,
                profile_picture TEXT,
                phone TEXT,
                employee_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                password_reset_required BOOLEAN DEFAULT FALSE,
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                created_by INTEGER REFERENCES users(id),
                notes TEXT
            )
        ''')
        
        # User sessions with enhanced security
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Access requests for tier upgrades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                current_tier INTEGER NOT NULL,
                requested_tier INTEGER NOT NULL,
                justification TEXT NOT NULL,
                business_need TEXT,
                supervisor_email TEXT,
                status TEXT DEFAULT 'pending',  -- pending, approved, denied, cancelled
                priority TEXT DEFAULT 'normal', -- low, normal, high, urgent
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by INTEGER REFERENCES users(id),
                reviewed_at TIMESTAMP,
                admin_notes TEXT,
                expires_at TIMESTAMP,
                auto_approve BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Password reset tokens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                ip_address TEXT,
                is_used BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Audit log for security and compliance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                action TEXT NOT NULL,  -- login, logout, access_granted, access_denied, etc.
                resource TEXT,  -- what was accessed
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                details TEXT,  -- JSON for additional details
                session_id TEXT
            )
        ''')
        
        # Email notifications queue
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                email_type TEXT,  -- welcome, approval, reset_password, etc.
                status TEXT DEFAULT 'pending',  -- pending, sent, failed
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                related_user_id INTEGER REFERENCES users(id),
                related_request_id INTEGER REFERENCES access_requests(id)
            )
        ''')
        
        # System settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                description TEXT,
                updated_by INTEGER REFERENCES users(id),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_access_tier ON users(access_tier)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)')
        
        # Insert default system settings
        default_settings = [
            ('session_timeout_hours', '8', 'Default session timeout in hours'),
            ('max_login_attempts', '5', 'Maximum login attempts before lockout'),
            ('lockout_duration_minutes', '30', 'Lockout duration in minutes'),
            ('auto_approve_usc_emails', 'true', 'Auto-approve users with @usc.edu.tt emails for tier 2'),
            ('require_supervisor_approval', 'true', 'Require supervisor approval for tier 3+ access'),
            ('password_reset_expiry_hours', '24', 'Password reset token expiry in hours'),
            ('allow_self_registration', 'true', 'Allow users to self-register')
        ]
        
        for key, value, desc in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', (key, value, desc))
        
        # Create default admin user if none exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE access_tier = 4')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # Create default admin
            admin_password_hash = self._hash_password("admin123")  # Change this!
            cursor.execute('''
                INSERT INTO users (
                    email, username, password_hash, full_name, 
                    access_tier, is_active, is_approved, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'admin@usc.edu.tt', 'admin', admin_password_hash, 
                'System Administrator', 4, True, True, datetime.now()
            ))
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                            password.encode('utf-8'),
                                            salt.encode('utf-8'),
                                            100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_hex = stored_hash.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256',
                                                password.encode('utf-8'),
                                                salt.encode('utf-8'),
                                                100000)
            return password_hash.hex() == hash_hex
        except:
            return False
    
    def create_user(self, email: str, password: str, full_name: str, 
                   department: str = None, access_tier: int = 1) -> Dict[str, Any]:
        """Create a new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return {"success": False, "message": "User already exists"}
            
            # Auto-approve USC emails for tier 2
            is_usc_email = email.endswith('@usc.edu.tt')
            if is_usc_email and access_tier <= 2:
                is_approved = True
                access_tier = max(access_tier, 2)  # USC emails get at least tier 2
            else:
                is_approved = False
            
            # Generate username from email
            username = email.split('@')[0]
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (
                    email, username, password_hash, full_name, department,
                    access_tier, is_active, is_approved, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, username, password_hash, full_name, department,
                  access_tier, True, is_approved, datetime.now()))
            
            user_id = cursor.lastrowid
            
            # Log the registration
            self._log_action(cursor, user_id, 'user_registered', 
                           details={"tier": access_tier, "auto_approved": is_approved})
            
            conn.commit()
            conn.close()
            
            return {
                "success": True, 
                "message": "User created successfully",
                "user_id": user_id,
                "auto_approved": is_approved
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error creating user: {str(e)}"}
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user
            cursor.execute('''
                SELECT id, email, password_hash, full_name, access_tier, 
                       is_active, is_approved, login_attempts, locked_until
                FROM users WHERE email = ?
            ''', (email,))
            
            user_row = cursor.fetchone()
            
            if not user_row:
                self._log_action(cursor, None, 'login_failed', 
                               details={"reason": "user_not_found", "email": email})
                conn.close()
                return {"success": False, "message": "Invalid credentials"}
            
            user_id, email, password_hash, full_name, access_tier, is_active, is_approved, login_attempts, locked_until = user_row
            
            # Check if account is locked
            if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
                conn.close()
                return {"success": False, "message": "Account temporarily locked. Try again later."}
            
            # Check if account is active
            if not is_active:
                conn.close()
                return {"success": False, "message": "Account is disabled"}
            
            # Check if account is approved
            if not is_approved:
                conn.close()
                return {"success": False, "message": "Account pending approval"}
            
            # Verify password
            if not self._verify_password(password, password_hash):
                # Increment login attempts
                login_attempts += 1
                max_attempts = 5  # Could be from settings
                
                if login_attempts >= max_attempts:
                    # Lock account for 30 minutes
                    locked_until = datetime.now() + timedelta(minutes=30)
                    cursor.execute('''
                        UPDATE users SET login_attempts = ?, locked_until = ?
                        WHERE id = ?
                    ''', (login_attempts, locked_until, user_id))
                else:
                    cursor.execute('''
                        UPDATE users SET login_attempts = ?
                        WHERE id = ?
                    ''', (login_attempts, user_id))
                
                self._log_action(cursor, user_id, 'login_failed', 
                               details={"reason": "invalid_password", "attempts": login_attempts})
                conn.commit()
                conn.close()
                return {"success": False, "message": "Invalid credentials"}
            
            # Successful login - reset attempts
            cursor.execute('''
                UPDATE users SET login_attempts = 0, locked_until = NULL, last_login = ?
                WHERE id = ?
            ''', (datetime.now(), user_id))
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=8)
            
            cursor.execute('''
                INSERT INTO user_sessions (session_token, user_id, expires_at)
                VALUES (?, ?, ?)
            ''', (session_token, user_id, expires_at))
            
            self._log_action(cursor, user_id, 'login_success')
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "access_tier": access_tier
                },
                "session_token": session_token
            }
            
        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    def _log_action(self, cursor, user_id: int, action: str, 
                   resource: str = None, details: Dict = None):
        """Log user action for audit trail"""
        cursor.execute('''
            INSERT INTO audit_log (user_id, action, resource, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, action, resource, json.dumps(details) if details else None, datetime.now()))
    
    def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user from valid session token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.email, u.full_name, u.access_tier, u.is_active, u.is_approved
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.expires_at > ? AND s.is_active = 1
            ''', (session_token, datetime.now()))
            
            user_row = cursor.fetchone()
            conn.close()
            
            if user_row:
                return {
                    "id": user_row[0],
                    "email": user_row[1],
                    "full_name": user_row[2],
                    "access_tier": user_row[3],
                    "is_active": user_row[4],
                    "is_approved": user_row[5]
                }
            
            return None
            
        except Exception as e:
            print(f"Session validation error: {e}")
            return None
    
    def request_access_upgrade(self, user_id: int, requested_tier: int, 
                              justification: str, business_need: str = None) -> Dict[str, Any]:
        """Request access tier upgrade"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current tier
            cursor.execute('SELECT access_tier FROM users WHERE id = ?', (user_id,))
            current_tier = cursor.fetchone()[0]
            
            if requested_tier <= current_tier:
                return {"success": False, "message": "Cannot request lower or same tier"}
            
            # Check for existing pending request
            cursor.execute('''
                SELECT id FROM access_requests 
                WHERE user_id = ? AND status = 'pending'
            ''', (user_id,))
            
            if cursor.fetchone():
                return {"success": False, "message": "You have a pending request"}
            
            # Create request
            cursor.execute('''
                INSERT INTO access_requests (
                    user_id, current_tier, requested_tier, justification, 
                    business_need, requested_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, current_tier, requested_tier, justification, 
                  business_need, datetime.now()))
            
            request_id = cursor.lastrowid
            
            self._log_action(cursor, user_id, 'access_request_submitted',
                           details={"request_id": request_id, "tier": requested_tier})
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Access request submitted", "request_id": request_id}
            
        except Exception as e:
            return {"success": False, "message": f"Error submitting request: {str(e)}"}
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending access requests for admin review"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ar.id, ar.user_id, u.email, u.full_name, ar.current_tier,
                       ar.requested_tier, ar.justification, ar.business_need,
                       ar.requested_at, ar.priority
                FROM access_requests ar
                JOIN users u ON ar.user_id = u.id
                WHERE ar.status = 'pending'
                ORDER BY ar.priority DESC, ar.requested_at ASC
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
                    "business_need": row[7],
                    "requested_at": row[8],
                    "priority": row[9]
                })
            
            conn.close()
            return requests
            
        except Exception as e:
            print(f"Error getting requests: {e}")
            return []
    
    def approve_access_request(self, request_id: int, admin_user_id: int, 
                             admin_notes: str = None) -> Dict[str, Any]:
        """Approve access request and upgrade user tier"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get request details
            cursor.execute('''
                SELECT user_id, requested_tier FROM access_requests 
                WHERE id = ? AND status = 'pending'
            ''', (request_id,))
            
            request_row = cursor.fetchone()
            if not request_row:
                return {"success": False, "message": "Request not found or already processed"}
            
            user_id, requested_tier = request_row
            
            # Update user access tier
            cursor.execute('''
                UPDATE users SET access_tier = ? WHERE id = ?
            ''', (requested_tier, user_id))
            
            # Update request status
            cursor.execute('''
                UPDATE access_requests 
                SET status = 'approved', reviewed_by = ?, reviewed_at = ?, admin_notes = ?
                WHERE id = ?
            ''', (admin_user_id, datetime.now(), admin_notes, request_id))
            
            # Log the approval
            self._log_action(cursor, admin_user_id, 'access_request_approved',
                           details={"request_id": request_id, "user_id": user_id, "tier": requested_tier})
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Access request approved"}
            
        except Exception as e:
            return {"success": False, "message": f"Error approving request: {str(e)}"}

# Initialize database instance
db = AuthDatabase()
