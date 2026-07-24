from datetime import datetime
from replicated_company.extensions import db

class ActivityLog(db.Model): # Define the ActivityLog model to represent activity logs in the database
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    
    user = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50))
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20))
    employee_id = db.Column(db.String(20))
    
    
    action = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='success')
    
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True) # Index the timestamp column for faster queries based on time
    
    
    ip_address = db.Column(db.String(45), nullable=False) # Store IPv4 and IPv6 addresses
    endpoint = db.Column(db.String(200))
    http_method = db.Column(db.String(10))
    user_agent = db.Column(db.String(500))
    
    
    details = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    
    def to_dict(self): # Convert the ActivityLog object to a dictionary for easy serialization
        return {
            'id': self.id,
            'user': self.user,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'employee_id': self.employee_id,
            'action': self.action,
            'event_type': self.event_type,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'endpoint': self.endpoint,
            'http_method': self.http_method,
            'user_agent': self.user_agent,
            'details': self.details,
            'session_id': self.session_id
        }
    
    def __repr__(self):
        return f'<ActivityLog {self.user} - {self.action} at {self.timestamp}>'
    