import sqlite3
import os

def init_database():
    db_path = 'database/company.db'
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table 
    cursor.execute('''
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
    
    # Create activity_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            username TEXT,
            full_name TEXT,
            role TEXT,
            employee_id TEXT,
            action TEXT NOT NULL,
            event_type TEXT NOT NULL,
            status TEXT DEFAULT 'success',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT NOT NULL,
            endpoint TEXT,
            http_method TEXT,
            user_agent TEXT,
            details TEXT,
            session_id TEXT
        )
    ''')
    
    # Create security_events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            severity TEXT DEFAULT 'low',
            description TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_ip TEXT NOT NULL,
            target_endpoint TEXT,
            resolved BOOLEAN DEFAULT 0,
            session_id TEXT,
            user_agent TEXT
        )
    ''')
    
    # Create behavior_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS behavior_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            username TEXT NOT NULL,
            full_name TEXT,
            department TEXT,
            role TEXT,
            behavior_type TEXT NOT NULL,
            activity TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            page_accessed TEXT,
            session_id TEXT,
            user_agent TEXT,
            risk_level TEXT DEFAULT 'low',
            details TEXT,
            day_of_week INTEGER,
            hour_of_day INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")

if __name__ == '__main__':
    init_database()
