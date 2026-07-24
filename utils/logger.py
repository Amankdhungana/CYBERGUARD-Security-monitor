from datetime import datetime
from extensions import db
from models.activity_log import ActivityLog
from models.security_event import SecurityEvent
from models.behavior_log import BehaviorLog
from flask import request, session, has_request_context
import uuid

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_user_info():
    from flask_login import current_user
    
    user_info = {
        'user': 'anonymous',
        'username': None,
        'full_name': None,
        'role': None,
        'employee_id': None
    }
    
    if current_user and current_user.is_authenticated:
        user_info['user'] = current_user.username
        user_info['username'] = current_user.username
        user_info['full_name'] = current_user.full_name
        user_info['role'] = current_user.role
        user_info['employee_id'] = current_user.employee_id
    
    return user_info

def log_activity(user, action, event_type, ip_address, 
                 status='success', details=None, endpoint=None, page_accessed=None):
    try:
        user_info = get_user_info()
        page = page_accessed or endpoint
        
        log_entry = ActivityLog(
            user=user or user_info.get('user', 'anonymous'),
            username=user_info.get('username'),
            full_name=user_info.get('full_name'),
            role=user_info.get('role'),
            employee_id=user_info.get('employee_id'),
            action=action,
            event_type=event_type,
            status=status,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            endpoint=page,
            details=details,
            session_id=get_session_id()
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Failed to log activity: {e}")
        db.session.rollback()
        return False

def log_security_event(event_type, source_ip, target_endpoint, 
                       description, user=None, severity='high'):
    try:
        user_info = get_user_info()
        
        event = SecurityEvent(
            user=user or user_info.get('user'),
            username=user_info.get('username'),
            role=user_info.get('role'),
            event_type=event_type,
            severity=severity,
            description=description,
            timestamp=datetime.utcnow(),
            source_ip=source_ip,
            target_endpoint=target_endpoint,
            session_id=get_session_id()
        )
        
        db.session.add(event)
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Failed to log security event: {e}")
        db.session.rollback()
        return False

def log_behavior(employee_id, username, behavior_type, activity, 
                 ip_address=None, page_accessed=None, details=None, risk_level='low'):
    try:
        user_info = get_user_info()
        
        behavior = BehaviorLog(
            employee_id=employee_id or user_info.get('employee_id'),
            username=username or user_info.get('username'),
            full_name=user_info.get('full_name'),
            department=user_info.get('department'),
            role=user_info.get('role'),
            behavior_type=behavior_type,
            activity=activity,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            page_accessed=page_accessed,
            session_id=get_session_id(),
            risk_level=risk_level,
            details=details
        )
        
        db.session.add(behavior)
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Failed to log behavior: {e}")
        db.session.rollback()
        return False

def log_file_access(user, filename, action, ip_address, details=None):
    log_activity(
        user=user,
        action=f'file_{action}',
        event_type='file_access',
        ip_address=ip_address,
        status='success',
        details=f'File: {filename}, {details or ""}',
        endpoint=f'/files/{filename}'
    )
