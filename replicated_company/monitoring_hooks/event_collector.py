from replicated_company.models.activity_log import ActivityLog
from replicated_company.models.security_event import SecurityEvent
from replicated_company.app import db
from datetime import datetime, timedelta

class EventCollector: # A utility class to collect and query events from the database
    @staticmethod 
    def get_events_since(timestamp):
        return ActivityLog.query.filter(ActivityLog.timestamp >= timestamp).all()
    
    @staticmethod 
    def get_security_events(severity=None, resolved=False):
        query = SecurityEvent.query.filter_by(resolved=resolved)
        if severity:
            query = query.filter_by(severity=severity)
        return query.order_by(SecurityEvent.timestamp.desc()).all()
    
    @staticmethod # Get a list of IP addresses that have exceeded a certain number of failed login attempts within the last hour
    def get_user_behavior(user_id, days=7):
        cutoff = datetime.utcnow() - timedelta(days=days)
        return ActivityLog.query.filter(
            ActivityLog.user == user_id,
            ActivityLog.timestamp >= cutoff
        ).all()
    
    @staticmethod # Get a list of IP addresses that have exceeded a certain number of failed login attempts within the last hour
    def get_suspicious_ips(threshold=10):
        from sqlalchemy import func
        
        suspicious = db.session.query(
            ActivityLog.ip_address,
            func.count(ActivityLog.id).label('attempts')
        ).filter(
            ActivityLog.status == 'failed',
            ActivityLog.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).group_by(ActivityLog.ip_address).having(func.count(ActivityLog.id) >= threshold).all()
        
        return [{'ip': ip, 'failed_attempts': count} for ip, count in suspicious]
    