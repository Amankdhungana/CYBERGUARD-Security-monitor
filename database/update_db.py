import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db

def update_database(): # Update the database schema to include new tables and modifications
    with app.app_context():
        # Create new tables
        db.create_all()
        print("✅ Database updated with new tables!")
        print("   - activity_logs (enhanced)")
        print("   - security_events (enhanced)")
        print("   - behavior_logs (new)")

if __name__ == '__main__':
    update_database()
    