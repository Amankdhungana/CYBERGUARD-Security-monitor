import unittest
import sys
import os

# Add parent directory to Python path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.user import User
from extensions import db

class TestUserModel(unittest.TestCase):
    """Test cases for User model - authentication, roles, and account security"""
    
    def setUp(self):
        """Setup runs before each test - creates in-memory test database"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Cleanup runs after each test - removes test database"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_creation(self):
        """Test that a user can be created and saved to database"""
        with app.app_context():
            # Create a test user
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
            
            # Retrieve and verify user
            saved_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.full_name, 'Test User')
            self.assertEqual(saved_user.role, 'employee')
            self.assertEqual(saved_user.employee_id, 'EMP999')
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed and verified"""
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
            
            # Correct password should pass
            self.assertTrue(user.check_password('secret123'))
            # Wrong password should fail
            self.assertFalse(user.check_password('wrongpass'))
            # Empty password should fail
            self.assertFalse(user.check_password(''))
    
    def test_is_admin(self):
        """Test that role-based access control works correctly"""
        with app.app_context():
            # Create admin user
            admin = User(
                employee_id='EMP997',
                full_name='Admin User',
                username='adminuser',
                email='admin@test.com',
                department='IT',
                role='admin'
            )
            # Create regular employee
            employee = User(
                employee_id='EMP996',
                full_name='Regular User',
                username='reguser',
                email='reg@test.com',
                department='IT',
                role='employee'
            )
            
            # Verify role checks
            self.assertTrue(admin.is_admin())
            self.assertFalse(employee.is_admin())
            self.assertTrue(employee.is_employee())
            self.assertFalse(admin.is_employee())
    
    def test_failed_login_tracking(self):
        """Test that failed login attempts are tracked and can be reset"""
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
            
            # Initially zero attempts
            self.assertEqual(user.failed_login_attempts, 0)
            
            # Increment attempts and verify
            user.increment_failed_attempts()
            self.assertEqual(user.failed_login_attempts, 1)
            user.increment_failed_attempts()
            user.increment_failed_attempts()
            self.assertEqual(user.failed_login_attempts, 3)
            
            # Reset attempts
            user.reset_failed_attempts()
            self.assertEqual(user.failed_login_attempts, 0)
    
    def test_account_lockout(self):
        """Test that account locks after 5 failed login attempts"""
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
            
            # 5 failed attempts should lock account
            for _ in range(5):
                user.increment_failed_attempts()
            self.assertTrue(user.is_locked())
            
            # Resetting attempts unlocks account
            user.reset_failed_attempts()
            self.assertFalse(user.is_locked())

if __name__ == '__main__':
    unittest.main()
    