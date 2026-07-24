import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add the parent directory to the system path to allow imports from the app package

from app import app, db
from models.user import User
from datetime import datetime

def seed_database(): # Seed the database with initial user data
    with app.app_context():
        if User.query.count() > 0:
            print("Database already seeded")
            return
        
        users = [
            User(
                employee_id='EMP001',
                full_name='John Smith',
                username='john.smith',
                email='john.smith@replicatedcompany.com',
                department='Engineering',
                role='admin',
                account_status='active',
                created_at=datetime.now()
            ),
            User(
                employee_id='EMP002',
                full_name='Sarah Johnson',
                username='sarah.johnson',
                email='sarah.johnson@replicatedcompany.com',
                department='Sales',
                role='employee',
                account_status='active',
                created_at=datetime.now()
            ),
            User(
                employee_id='EMP003',
                full_name='Michael Chen',
                username='michael.chen',
                email='michael.chen@replicatedcompany.com',
                department='Engineering',
                role='employee',
                account_status='active',
                created_at=datetime.now()
            ),
            User(
                employee_id='EMP004',
                full_name='Emily Rodriguez',
                username='emily.rodriguez',
                email='emily.rodriguez@replicatedcompany.com',
                department='Marketing',
                role='employee',
                account_status='active',
                created_at=datetime.now()
            ),
            User(
                employee_id='EMP005',
                full_name='David Kim',
                username='david.kim',
                email='david.kim@replicatedcompany.com',
                department='Support',
                role='employee',
                account_status='active',
                created_at=datetime.now()
            ),
            User(
                employee_id='EMP006',
                full_name='Lisa Thompson',
                username='lisa.thompson',
                email='lisa.thompson@replicatedcompany.com',
                department='HR',
                role='employee',
                account_status='active',
                created_at=datetime.now()
            )
        ]
        
        passwords = { # Define passwords for the seeded users
            'john.smith': 'Admin@123',
            'sarah.johnson': 'Employee@123',
            'michael.chen': 'Employee@123',
            'emily.rodriguez': 'Employee@123',
            'david.kim': 'Employee@123',
            'lisa.thompson': 'Employee@123'
        }
        
        for user in users:
            user.set_password(passwords[user.username])
            db.session.add(user)
        
        db.session.commit() # Commit the changes to the database
        print(f"Database seeded with {len(users)} users")
        print("\nLogin Credentials:")
        print("Admin: john.smith / Admin@123")
        print("Employees: Any employee username / Employee@123")

if __name__ == '__main__':
    seed_database()
    