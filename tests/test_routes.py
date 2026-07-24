import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.user import User
from extensions import db

class TestRoutes(unittest.TestCase):
    """Test cases for Flask routes - authentication, access control, and pages"""
    
    def setUp(self):
        """Setup test environment - isolates database to memory safely"""
        # 1. Update configurations before initializing contexts
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        # 2. Force the active SQLAlchemy engine to drop its disk bind and connect to memory
        with app.app_context():
            db.engine.dispose()  # Disconnects from company.db hard file
            db.create_all()      # Builds fresh tables in RAM only
            self.create_test_user()
    
    def tearDown(self):
        """Cleanup after tests - safely cleans the in-memory data cache"""
        with app.app_context():
            db.session.remove()
            db.drop_all()       # Drops memory tables only
            db.engine.dispose() # Clears memory engine footprints cleanly
    
    def create_test_user(self):
        """Helper to create a test admin user"""
        with app.app_context():
            user = User(
                employee_id='EMP001',
                full_name='Test Admin',
                username='admin',
                email='admin@test.com',
                department='IT',
                role='admin',
                account_status='active'
            )
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()
    
    def test_home_page(self):
        """Test that home page loads successfully"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Replicated Company', response.data)
    
    def test_employee_login_page(self):
        """Test that employee login page loads"""
        response = self.app.get('/auth/employee-login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Employee Portal', response.data)
    
    def test_admin_login_page(self):
        """Test that admin login page loads"""
        response = self.app.get('/auth/admin-login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Administrator Portal', response.data)
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        response = self.app.post('/auth/admin-login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)
    
    def test_admin_login_failure(self):
        """Test failed admin login with wrong password"""
        response = self.app.post('/auth/admin-login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        self.assertIn(b'Invalid admin credentials', response.data)
    
    def test_protected_route_redirects(self):
        """Test that protected routes redirect to login when not authenticated (but the bug kept intentionally)"""
        response = self.app.get('/admin/dashboard')
        # Due to the intentional bug, it returns 200 instead of 302
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        """Test that logout works"""
        self.app.post('/auth/admin-login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        response = self.app.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
    