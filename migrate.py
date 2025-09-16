import sqlite3


def update_database_for_4_tiers():
    """Update existing database to support 4-tier system"""
    conn = sqlite3.connect('usc_ir.db')
    cursor = conn.cursor()

    try:
        # Update existing demo users to new tier system
        tier_updates = [
            ('admin@usc.edu.tt', 4),  # Admin tier
            ('nrobinson@usc.edu.tt', 4),  # Admin tier
            ('websterl@usc.edu.tt', 4),  # Admin tier
            ('employee@usc.edu.tt', 3),  # Complete access
            ('demo@usc.edu.tt', 2),  # Limited access
            ('student@usc.edu.tt', 1)  # Basic access
        ]

        for email, new_tier in tier_updates:
            cursor.execute('UPDATE users SET access_tier = ? WHERE email = ?', (new_tier, email))

        conn.commit()
        print("✅ Database updated to 4-tier system")

    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    update_database_for_4_tiers()