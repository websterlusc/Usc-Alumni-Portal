#!/usr/bin/env python3
"""
USC IR Portal - Database Fix Script
Fixes the database schema mismatch issue
"""

import sqlite3
import bcrypt
import os
from datetime import datetime

DATABASE_PATH = 'usc_ir.db'

def fix_database_schema():
    """Fix the database schema by recreating tables with correct columns"""
    
    print("🔧 Fixing USC IR Database Schema...")
    
    # Backup existing database if it exists
    if os.path.exists(DATABASE_PATH):
        backup_name = f'usc_ir_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        print(f"📦 Creating backup: {backup_name}")
        
        # Simple backup by copying
        import shutil
        shutil.copy2(DATABASE_PATH, backup_name)
        
        # Remove the problematic database
        os.remove(DATABASE_PATH)
        print("🗑️  Removed old database file")
    
    # Create fresh database with correct schema
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("🗄️  Creating new database tables...")
    
    # Users table with ALL required columns
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            access_tier INTEGER DEFAULT 2,
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            department TEXT,
            position TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP NULL,
            created_by INTEGER REFERENCES users(id)
        )
    ''')
    
    # User sessions table
    cursor.execute('''
        CREATE TABLE user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            session_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Access requests table
    cursor.execute('''
        CREATE TABLE access_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            current_tier INTEGER NOT NULL,
            requested_tier INTEGER NOT NULL,
            justification TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by INTEGER REFERENCES users(id),
            reviewed_at TIMESTAMP,
            admin_notes TEXT,
            priority TEXT DEFAULT 'normal'
        )
    ''')
    
    # Password reset requests table
    cursor.execute('''
        CREATE TABLE password_reset_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            reset_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_at TIMESTAMP,
            ip_address TEXT
        )
    ''')
    
    # Audit log table
    cursor.execute('''
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id INTEGER,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            severity TEXT DEFAULT 'info'
        )
    ''')
    
    # System settings table
    cursor.execute('''
        CREATE TABLE system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            updated_by INTEGER REFERENCES users(id),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ Database tables created successfully")
    
    # Create indexes for performance
    print("📊 Creating database indexes...")
    
    indexes = [
        'CREATE INDEX idx_users_email ON users(email)',
        'CREATE INDEX idx_users_username ON users(username)',
        'CREATE INDEX idx_users_active ON users(is_active)',
        'CREATE INDEX idx_users_tier ON users(access_tier)',
        'CREATE INDEX idx_sessions_token ON user_sessions(session_token)',
        'CREATE INDEX idx_sessions_expires ON user_sessions(expires_at)',
        'CREATE INDEX idx_sessions_user ON user_sessions(user_id)',
        'CREATE INDEX idx_access_requests_user ON access_requests(user_id)',
        'CREATE INDEX idx_access_requests_status ON access_requests(status)',
        'CREATE INDEX idx_audit_user ON audit_log(user_id)',
        'CREATE INDEX idx_audit_timestamp ON audit_log(timestamp)',
        'CREATE INDEX idx_audit_action ON audit_log(action)'
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print("✅ Database indexes created")
    
    # Create initial admin user
    print("👤 Creating initial admin account...")
    
    admin_password = bcrypt.hashpw('admin123!USC'.encode('utf-8'), bcrypt.gensalt())
    
    cursor.execute('''
        INSERT INTO users (
            username, email, password_hash, full_name, 
            access_tier, is_admin, department, position
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'ir_admin',
        'ir@usc.edu.tt', 
        admin_password,
        'IR Administrator',
        3,  # Tier 3 - Financial access
        True,
        'Institutional Research',
        'Administrator'
    ))
    
    # Add default system settings
    print("⚙️  Adding system settings...")
    
    default_settings = [
        ('app_name', 'USC Institutional Research Portal', 'Application name'),
        ('app_version', '2.0.0', 'Application version'),
        ('session_timeout_hours', '8', 'Session timeout in hours'),
        ('max_login_attempts', '5', 'Maximum failed login attempts'),
        ('lockout_duration_minutes', '30', 'Account lockout duration'),
        ('password_min_length', '8', 'Minimum password length'),
        ('maintenance_mode', 'false', 'System maintenance mode'),
        ('admin_email', 'ir@usc.edu.tt', 'System administrator email'),
    ]
    
    for setting_key, setting_value, description in default_settings:
        cursor.execute('''
            INSERT INTO system_settings (setting_key, setting_value, description, updated_by)
            VALUES (?, ?, ?, ?)
        ''', (setting_key, setting_value, description, 1))
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print("✅ System settings configured")
    print("\n" + "="*60)
    print("🎉 Database fix completed successfully!")
    print("\n📊 Database Summary:")
    print("   - Users table: Created with all required columns")
    print("   - Sessions table: Created for authentication")
    print("   - Access requests: Created for tier management") 
    print("   - Audit log: Created for security tracking")
    print("   - System settings: Created with defaults")
    print("\n🔑 Admin Account Created:")
    print("   Email: ir@usc.edu.tt")
    print("   Password: admin123!USC")
    print("   Access: Tier 3 (Full Financial Access)")
    print("\n⚠️  IMPORTANT: Change the admin password after first login!")
    print("=" * 60)

if __name__ == '__main__':
    fix_database_schema()