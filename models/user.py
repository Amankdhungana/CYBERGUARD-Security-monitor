from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class User(UserMixin, db.Model): # Define the User model to represent users in the database
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    account_status = db.Column(db.String(20), default='active')
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password): # Hash the password and store it in the database
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password): # Check if the provided password matches the stored password hash
        return check_password_hash(self.password_hash, password)
    
    def increment_failed_attempts(self): # Increment the failed login attempts counter and commit the change to the database
        self.failed_login_attempts += 1
        db.session.commit()
    
    def reset_failed_attempts(self): # Reset the failed login attempts counter to zero and commit the change to the database
        self.failed_login_attempts = 0
        db.session.commit()
    
    def is_locked(self): # Check if the account is locked based on the number of failed login attempts
        return self.failed_login_attempts >= 5
    
    def update_last_login(self): # Update the last login timestamp to the current time and commit the change to the database
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_id(self): # Return the unique identifier of the user for Flask-Login
        return str(self.id)
    
    def is_admin(self): # Check if the user has an admin role
        return self.role == 'admin'
    
    def is_employee(self): # Check if the user has an employee role
        return self.role == 'employee'
    
    def __repr__(self): # Return a string representation of the User object for debugging purposes
        return f'<User {self.username}>'
    