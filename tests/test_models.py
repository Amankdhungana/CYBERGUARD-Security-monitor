import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.user import User
from extensions import db

class TestUserModel(unittest.TestCase):
    """Test User model - authentication, roles, and account lockout"""
    
    def setUp(self):
        """Setup test environment - isolates database to memory safely"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        # Crucial Fix: Force the active SQLAlchemy engine to drop its disk bind and connect to memory
        with app.app_context():
            db.engine.dispose()  # Disconnects from company.db hard file
            db.create_all()      # Builds fresh tables in RAM only
    
    def tearDown(self):
        """Cleanup after tests - safely cleans the in-memory data cache"""
        with app.app_context():
            db.session.remove()
            db.drop_all()       # Drops memory tables only
            db.engine.dispose() # Clears memory engine footprints cleanly
    
    def test_user_creation(self):
        """Verify user can be created and saved to database"""
        with app.app_context():
            user = User(
                employee_id='EMP999',
                full_name='Test User',
                username='testuser',
                email='test@test.com',
                department='IT',
                role='employee',
                account_status='active'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            saved_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.full_name, 'Test User')
            self.assertEqual(saved_user.role, 'employee')
    
    def test_password_hashing(self):
        """Verify password hashing and verification works"""
        with app.app_context():
            user = User(
                employee_id='EMP998',
                full_name='Password Test',
                username='passtest',
                email='pass@test.com',
                department='IT',
                role='employee'
            )
            user.set_password('secret123')
            self.assertTrue(user.check_password('secret123'))
            self.assertFalse(user.check_password('wrongpass'))
    
    def test_is_admin(self):
        """Verify role-based access control works"""
        with app.app_context():
            admin = User(
                employee_id='EMP997',
                full_name='Admin User',
                username='adminuser',
                email='admin@test.com',
                department='IT',
                role='admin'
            )
            employee = User(
                employee_id='EMP996',
                full_name='Regular User',
                username='reguser',
                email='reg@test.com',
                department='IT',
                role='employee'
            )
            self.assertTrue(admin.is_admin())
            self.assertFalse(employee.is_admin())
            self.assertTrue(employee.is_employee())
    
    def test_failed_login_tracking(self):
        """Verify failed login attempts are tracked and can be reset"""
        with app.app_context():
            user = User(
                employee_id='EMP995',
                full_name='Login Test',
                username='logintest',
                email='login@test.com',
                department='IT',
                role='employee'
            )
            user.set_password('pass123')
            db.session.add(user)
            db.session.commit()
            
            self.assertEqual(user.failed_login_attempts, 0)
            user.increment_failed_attempts()
            self.assertEqual(user.failed_login_attempts, 1)
            user.reset_failed_attempts()
            self.assertEqual(user.failed_login_attempts, 0)
    
    def test_account_lockout(self):
        """Verify account locks after 5 failed attempts"""
        with app.app_context():
            user = User(
                employee_id='EMP994',
                full_name='Lock Test',
                username='locktest',
                email='lock@test.com',
                department='IT',
                role='employee'
            )
            user.set_password('pass123')
            db.session.add(user)
            db.session.commit()
            
            for _ in range(5):
                user.increment_failed_attempts()
            self.assertTrue(user.is_locked())
            user.reset_failed_attempts()
            self.assertFalse(user.is_locked())

if __name__ == '__main__':
    unittest.main()
    