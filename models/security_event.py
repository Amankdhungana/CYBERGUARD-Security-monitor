from datetime import datetime
from extensions import db

class SecurityEvent(db.Model): # Define the SecurityEvent model to represent security events in the database
    __tablename__ = 'security_events'
    
    id = db.Column(db.Integer, primary_key=True)
    
    
    user = db.Column(db.String(100))
    username = db.Column(db.String(50))
    role = db.Column(db.String(20))
    
    
    event_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), default='low')  # ← ADD THIS
    description = db.Column(db.Text, nullable=False)
    
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    
    source_ip = db.Column(db.String(45), nullable=False) # Store IPv4 and IPv6 addresses
    target_endpoint = db.Column(db.String(200))
    
    
    resolved = db.Column(db.Boolean, default=False)
    
    
    session_id = db.Column(db.String(100))
    user_agent = db.Column(db.String(500))
    
    def to_dict(self): # Convert the SecurityEvent object to a dictionary for easy serialization
        return {
            'id': self.id,
            'user': self.user,
            'username': self.username,
            'role': self.role,
            'event_type': self.event_type,
            'severity': self.severity,  
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'source_ip': self.source_ip,
            'target_endpoint': self.target_endpoint,
            'resolved': self.resolved,
            'session_id': self.session_id,
            'user_agent': self.user_agent
        }
    
    def __repr__(self):
        return f'<SecurityEvent {self.event_type} at {self.timestamp}>'
    