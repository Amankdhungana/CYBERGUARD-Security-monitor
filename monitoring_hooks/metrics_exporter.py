from models.user import User
from models.activity_log import ActivityLog
from models.security_event import SecurityEvent
from app import db
from datetime import datetime, timedelta

class MetricsExporter: # A utility class to export system metrics for monitoring purposes
    @staticmethod
    def get_system_metrics():
        return {
            'total_users': User.query.count(),
            'active_sessions': db.session.query(ActivityLog.user).filter(
                ActivityLog.action == 'login_success',
                ActivityLog.timestamp >= datetime.utcnow() - timedelta(hours=2)
            ).distinct().count(),
            'failed_logins_last_hour': ActivityLog.query.filter(
                ActivityLog.action.in_(['login_failed', 'failed_login']),
                ActivityLog.timestamp >= datetime.utcnow() - timedelta(hours=1)
            ).count(),
            'security_events_today': SecurityEvent.query.filter(
                SecurityEvent.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0)
            ).count(),
            'high_severity_events': SecurityEvent.query.filter_by(severity='high', resolved=False).count()
        }
    
    @staticmethod # Export the collected metrics in a structured format for monitoring tools
    def export_for_monitoring():
        metrics = MetricsExporter.get_system_metrics()
        metrics['timestamp'] = datetime.utcnow().isoformat()
        return metrics
    