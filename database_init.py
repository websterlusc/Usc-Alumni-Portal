#!/usr/bin/env python3
"""
USC Institutional Research Portal - Database Initialization
Creates and configures the SQLite database with initial data
"""

import sqlite3
import bcrypt
import secrets
from datetime import datetime, timedelta
import os

# Configuration
DATABASE_PATH = 'usc_ir.db'
DEFAULT_ADMIN_EMAIL = 'ir@usc.edu.tt'
DEFAULT_ADMIN_PASSWORD = 'admin123!USC'


class DatabaseInitializer:
    """Initialize and configure the USC IR database"""

    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()

    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create all required database tables"""
        cursor = self.connect()

        print("🗄️  Creating database tables...")

        # Users table with comprehensive fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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

        # User sessions with enhanced tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
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

        # Access requests with detailed tracking
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
                admin_notes TEXT,
                priority TEXT DEFAULT 'normal'
            )
        ''')

        # Password reset requests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_requests (
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

        # Audit log for sensitive operations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
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

        # System settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                description TEXT,
                updated_by INTEGER REFERENCES users(id),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Data file metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                access_tier INTEGER DEFAULT 2,
                uploaded_by INTEGER REFERENCES users(id),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                description TEXT
            )
        ''')

        # User activity tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                activity_type TEXT NOT NULL,
                page_accessed TEXT,
                data_accessed TEXT,
                duration_seconds INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT
            )
        ''')

        self.conn.commit()
        print("✅ Database tables created successfully")

    def create_indexes(self):
        """Create database indexes for performance"""
        cursor = self.connect()

        print("📊 Creating database indexes...")

        # User-related indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_tier ON users(access_tier)')

        # Session indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)')

        # Access request indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_requests_user ON access_requests(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_requests_status ON access_requests(status)')

        # Audit log indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)')

        self.conn.commit()
        print("✅ Database indexes created successfully")

    def create_initial_admin(self):
        """Create the initial administrator account"""
        cursor = self.connect()

        print("👤 Creating initial admin account...")

        # Check if admin already exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', (DEFAULT_ADMIN_EMAIL,))
        if cursor.fetchone()[0] > 0:
            print("ℹ️  Admin account already exists")
            return

        # Hash the default password
        password_hash = bcrypt.hashpw(DEFAULT_ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())

        # Create admin user
        cursor.execute('''
            INSERT INTO users (
                username, email, password_hash, full_name, 
                access_tier, is_admin, department, position
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'ir_admin',
            DEFAULT_ADMIN_EMAIL,
            password_hash,
            'IR Administrator',
            3,  # Tier 3 - Financial access
            True,
            'Institutional Research',
            'Administrator'
        ))

        self.conn.commit()
        print(f"✅ Admin account created: {DEFAULT_ADMIN_EMAIL}")
        print(f"🔑 Default password: {DEFAULT_ADMIN_PASSWORD}")
        print("⚠️  IMPORTANT: Change this password after first login!")

    def create_sample_users(self):
        """Create sample users for testing"""
        cursor = self.connect()

        print("👥 Creating sample test users...")

        sample_users = [
            {
                'username': 'factbook_user',
                'email': 'factbook@usc.edu.tt',
                'password': 'factbook123',
                'full_name': 'Factbook Test User',
                'access_tier': 2,
                'department': 'Academic Affairs',
                'position': 'Data Analyst'
            },
            {
                'username': 'financial_user',
                'email': 'finance@usc.edu.tt',
                'password': 'finance123',
                'full_name': 'Financial Test User',
                'access_tier': 3,
                'department': 'Finance',
                'position': 'Financial Analyst'
            },
            {
                'username': 'public_user',
                'email': 'public@usc.edu.tt',
                'password': 'public123',
                'full_name': 'Public Test User',
                'access_tier': 1,
                'department': 'General',
                'position': 'Guest User'
            }
        ]

        for user_data in sample_users:
            # Check if user already exists
            cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', (user_data['email'],))
            if cursor.fetchone()[0] > 0:
                continue

            # Hash password
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())

            # Create user
            cursor.execute('''
                INSERT INTO users (
                    username, email, password_hash, full_name,
                    access_tier, department, position, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data['full_name'],
                user_data['access_tier'],
                user_data['department'],
                user_data['position'],
                1  # Created by admin (ID 1)
            ))

        self.conn.commit()
        print("✅ Sample users created")
        print("   - factbook@usc.edu.tt / factbook123 (Tier 2)")
        print("   - finance@usc.edu.tt / finance123 (Tier 3)")
        print("   - public@usc.edu.tt / public123 (Tier 1)")

    def insert_system_settings(self):
        """Insert default system settings"""
        cursor = self.connect()

        print("⚙️  Inserting system settings...")

        default_settings = [
            ('app_name', 'USC Institutional Research Portal', 'Application name'),
            ('app_version', '2.0.0', 'Application version'),
            ('session_timeout_hours', '8', 'Session timeout in hours'),
            ('max_login_attempts', '5', 'Maximum failed login attempts'),
            ('lockout_duration_minutes', '30', 'Account lockout duration'),
            ('password_min_length', '8', 'Minimum password length'),
            ('require_password_change', 'true', 'Require password change on first login'),
            ('enable_audit_logging', 'true', 'Enable audit logging'),
            ('maintenance_mode', 'false', 'System maintenance mode'),
            ('allow_user_registration', 'false', 'Allow public user registration'),
            ('admin_email', DEFAULT_ADMIN_EMAIL, 'System administrator email'),
            ('backup_interval_hours', '24', 'Database backup interval'),
            ('data_retention_days', '365', 'Data retention period'),
            ('max_file_size_mb', '50', 'Maximum file upload size'),
            ('enable_email_notifications', 'false', 'Enable email notifications')
        ]

        for setting_key, setting_value, description in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO system_settings 
                (setting_key, setting_value, description, updated_by)
                VALUES (?, ?, ?, ?)
            ''', (setting_key, setting_value, description, 1))

        self.conn.commit()
        print("✅ System settings configured")

    def log_audit_event(self, user_id, action, details=None):
        """Log an audit event"""
        cursor = self.connect()

        cursor.execute('''
            INSERT INTO audit_log (user_id, action, details, severity)
            VALUES (?, ?, ?, ?)
        ''', (user_id, action, details, 'info'))

        self.conn.commit()

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        cursor = self.connect()

        print("🧹 Cleaning up expired sessions...")

        cursor.execute('''
            DELETE FROM user_sessions 
            WHERE expires_at < datetime('now') OR is_active = FALSE
        ''')

        deleted_count = cursor.rowcount
        self.conn.commit()

        if deleted_count > 0:
            print(f"✅ Cleaned up {deleted_count} expired sessions")
        else:
            print("ℹ️  No expired sessions to clean")

    def get_database_stats(self):
        """Get database statistics"""
        cursor = self.connect()

        stats = {}

        # Count records in each table
        tables = [
            'users', 'user_sessions', 'access_requests',
            'audit_log', 'system_settings', 'data_files'
        ]

        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            stats[table] = cursor.fetchone()[0]

        return stats

    def validate_database(self):
        """Validate database integrity"""
        cursor = self.connect()

        print("🔍 Validating database integrity...")

        issues = []

        # Check for admin user
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
        if cursor.fetchone()[0] == 0:
            issues.append("No admin users found")

        # Check for orphaned sessions
        cursor.execute('''
            SELECT COUNT(*) FROM user_sessions s 
            WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = s.user_id)
        ''')
        orphaned_sessions = cursor.fetchone()[0]
        if orphaned_sessions > 0:
            issues.append(f"{orphaned_sessions} orphaned sessions found")

        # Check for orphaned access requests
        cursor.execute('''
            SELECT COUNT(*) FROM access_requests r 
            WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = r.user_id)
        ''')
        orphaned_requests = cursor.fetchone()[0]
        if orphaned_requests > 0:
            issues.append(f"{orphaned_requests} orphaned access requests found")

        if issues:
            print("⚠️  Database validation issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Database validation passed")
            return True

    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'usc_ir_backup_{timestamp}.db'

        print(f"💾 Creating database backup: {backup_path}")

        try:
            # Create backup using sqlite3 backup API
            backup_conn = sqlite3.connect(backup_path)
            self.conn.backup(backup_conn)
            backup_conn.close()
            print("✅ Database backup created successfully")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None

    def initialize_complete_database(self, include_samples=True):
        """Complete database initialization process"""
        print("🚀 Starting USC IR Database Initialization...")
        print("=" * 60)

        try:
            # Create tables
            self.create_tables()

            # Create indexes
            self.create_indexes()

            # Create initial admin
            self.create_initial_admin()

            # Create sample users if requested
            if include_samples:
                self.create_sample_users()

            # Insert system settings
            self.insert_system_settings()

            # Clean up any existing expired sessions
            self.cleanup_expired_sessions()

            # Validate database
            self.validate_database()

            # Get and display statistics
            stats = self.get_database_stats()
            print("\n📊 Database Statistics:")
            for table, count in stats.items():
                print(f"   {table}: {count} records")

            # Log initialization
            self.log_audit_event(1, 'database_initialized', 'Complete database setup completed')

            print("\n" + "=" * 60)
            print("🎉 Database initialization completed successfully!")
            print("\n📝 Next Steps:")
            print("   1. Change the default admin password after first login")
            print("   2. Create additional user accounts as needed")
            print("   3. Configure system settings via admin panel")
            print("   4. Upload your Excel data files to the data/ folder")
            print("   5. Test authentication and access controls")
            print("\n🔑 Login Credentials:")
            print(f"   Admin: {DEFAULT_ADMIN_EMAIL} / {DEFAULT_ADMIN_PASSWORD}")
            if include_samples:
                print("   Test Users: factbook@usc.edu.tt, finance@usc.edu.tt, public@usc.edu.tt")
                print("   (All test passwords: [username]123)")

        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise

        finally:
            self.disconnect()


def main():
    """Main initialization function"""
    import argparse

    parser = argparse.ArgumentParser(description='Initialize USC IR Database')
    parser.add_argument('--no-samples', action='store_true',
                        help='Skip creation of sample test users')
    parser.add_argument('--database', default=DATABASE_PATH,
                        help='Database file path')
    parser.add_argument('--backup', action='store_true',
                        help='Create backup before initialization')

    args = parser.parse_args()

    # Initialize database
    db_init = DatabaseInitializer(args.database)

    # Create backup if existing database and backup requested
    if args.backup and os.path.exists(args.database):
        db_init.connect()
        db_init.backup_database()
        db_init.disconnect()

    # Run complete initialization
    db_init.initialize_complete_database(include_samples=not args.no_samples)


if __name__ == '__main__':
    main()