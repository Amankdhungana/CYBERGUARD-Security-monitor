import socket
from functools import wraps
from flask import request

def get_client_ip(request): # Function to retrieve the client's IP address from the request headers, considering possible proxy headers for accurate identification
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    
    return ip

def track_ip_behavior(threshold=100): # Decorator to monitor and log IP behavior based on request volume, useful for detecting potential abuse or suspicious activity
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = get_client_ip(request)
            
            from models.activity_log import ActivityLog
            from app import db
            
            recent_requests = ActivityLog.query.filter_by(
                ip_address=ip
            ).filter(
                ActivityLog.timestamp >= db.func.datetime('now', '-5 minutes')
            ).count()
            
            if recent_requests > threshold: # Log a security event if the number of requests from the same IP exceeds the defined threshold within a 5-minute window, indicating potential suspicious behavior
                from utils.logger import log_security_event
                log_security_event(
                    event_type='suspicious_behavior',
                    source_ip=ip,
                    target_endpoint=request.path,
                    severity='high',
                    description=f'High request volume detected: {recent_requests} requests in 5 minutes',
                    recommendation='Consider rate limiting or blocking this IP'
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
