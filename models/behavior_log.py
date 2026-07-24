from datetime import datetime
from extensions import db

class BehaviorLog(db.Model): # Define the BehaviorLog model to represent user behavior logs in the database
    __tablename__ = 'behavior_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    
    employee_id = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100))
    department = db.Column(db.String(50))
    role = db.Column(db.String(20))

    
    behavior_type = db.Column(db.String(50), nullable=False) # Type of behavior (e.g., login, logout, file access, etc.)
    activity = db.Column(db.Text)
    
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True) # Index the timestamp column for faster queries based on time
    
    
    ip_address = db.Column(db.String(45)) # Store IPv4 and IPv6 addresses
    page_accessed = db.Column(db.String(200))
    session_id = db.Column(db.String(100))
    user_agent = db.Column(db.String(500))
    
   
    details = db.Column(db.Text)
    
    def to_dict(self): # Convert the BehaviorLog object to a dictionary for easy serialization
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'username': self.username,
            'full_name': self.full_name,
            'department': self.department,
            'role': self.role,
            'behavior_type': self.behavior_type,
            'activity': self.activity,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'page_accessed': self.page_accessed,
            'session_id': self.session_id,
            'user_agent': self.user_agent,
            'details': self.details
        }
    
    def __repr__(self):
        return f'<BehaviorLog {self.username} - {self.behavior_type} at {self.timestamp}>'
    