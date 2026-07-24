from datetime import datetime
from extensions import db

class BehaviorLog(db.Model):
    __tablename__ = 'behavior_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    employee_id = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100))
    department = db.Column(db.String(50))
    role = db.Column(db.String(20))
    
    behavior_type = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    ip_address = db.Column(db.String(45))
    page_accessed = db.Column(db.String(200))
    session_id = db.Column(db.String(100))
    user_agent = db.Column(db.String(500))
    
    risk_level = db.Column(db.String(20), default='low')
    details = db.Column(db.Text)
    
    day_of_week = db.Column(db.Integer)
    hour_of_day = db.Column(db.Integer)
    
    def to_dict(self):
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
            'risk_level': self.risk_level,
            'details': self.details,
            'day_of_week': self.day_of_week,
            'hour_of_day': self.hour_of_day
        }
    
    def __repr__(self):
        return f'<BehaviorLog {self.username} - {self.behavior_type} at {self.timestamp}>'
