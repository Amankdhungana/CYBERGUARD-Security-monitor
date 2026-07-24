#!/usr/bin/env python3
import os
from app import app
from extensions import db

os.makedirs('database', exist_ok=True) # Create the 'database' directory if it doesn't exist to store the SQLite database file 
os.makedirs('logs', exist_ok=True)

if __name__ == '__main__': # Entry point for running the Flask application, ensuring that the database is created and seeded before starting the server
    with app.app_context():
        db.create_all()
        from database.seed_data import seed_database
        seed_database()
    
    print("\n" + "="*50)
    print("🚀 Server running on PORT 5001")
    print(f"   Local: http://localhost:5001")
    print("="*50)
    app.run(host='0.0.0.0', port=5001, debug=True)
