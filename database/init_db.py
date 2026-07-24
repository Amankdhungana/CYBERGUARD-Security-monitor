import sqlite3
import os

def init_database(): # Initialize the database and create necessary tables
    db_path = 'database/company.db'
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''         # Create users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            account_status TEXT DEFAULT 'active',
            last_login TIMESTAMP,
            failed_login_attempts INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''         # Create activity logs table
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            action TEXT NOT NULL,
            page_accessed TEXT,
            ip_address TEXT NOT NULL,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success',
            risk_level TEXT DEFAULT 'low',
            details TEXT
        )
    ''')
    
    cursor.execute('''         # Create security events table
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            target_endpoint TEXT,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            recommendation TEXT,
            resolved BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()
    