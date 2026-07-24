from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for
from flask_login import login_required, current_user
from models.user import User
from models.activity_log import ActivityLog
from models.security_event import SecurityEvent
from models.behavior_log import BehaviorLog
from utils.logger import log_activity, log_security_event, log_behavior
from utils.ip_tracker import get_client_ip
from app import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__) # Blueprint for admin routes, providing a modular structure for the admin section of the application

@admin_bp.route('/dashboard') # Admin dashboard route that displays key statistics and recent logs/events
def admin_dashboard():
    if not current_user.is_authenticated:
        log_security_event(
            event_type='unauthorized_admin_access',
            source_ip=get_client_ip(request),
            target_endpoint='/admin/dashboard',
            severity='high',
            description=f'Anonymous user accessed admin dashboard from IP {get_client_ip(request)}'
        )
        
        log_activity(
            user='anonymous',
            action='unauthorized_admin_dashboard_access',
            event_type='unauthorized_access',
            ip_address=get_client_ip(request),
            status='success',
            endpoint='/admin/dashboard',
            details='Anonymous user accessed admin dashboard without authentication'
        )
        
        log_behavior(
            employee_id=None,
            username='anonymous',
            behavior_type='critical_security_event',
            activity='Anonymous user accessed admin dashboard without authentication',
            page_accessed='/admin/dashboard',
            risk_level='high',
            ip_address=get_client_ip(request)
        )
    
    total_users = User.query.count()
    active_users = User.query.filter_by(account_status='active').count()
    admin_count = User.query.filter_by(role='admin').count()
    employee_count = User.query.filter_by(role='employee').count()
    
    recent_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    recent_security_events = SecurityEvent.query.filter_by(resolved=False).order_by(SecurityEvent.timestamp.desc()).limit(10).all()
    
    high_severity_events = SecurityEvent.query.filter(SecurityEvent.severity == 'high', SecurityEvent.resolved == False).count()
    
    stats = { # Compile key statistics for the admin dashboard
        'total_users': total_users,
        'active_users': active_users,
        'admin_count': admin_count,
        'employee_count': employee_count,
        'high_severity_events': high_severity_events,
        'recent_logs': recent_logs,
        'recent_security_events': recent_security_events
    }
    
    users = User.query.all()
    
    return render_template('admin_dashboard.html', stats=stats, users=users)

@admin_bp.route('/users') # Admin route to manage users, displaying a list of all users in the system
def manage_users():
    if not current_user.is_authenticated:
        log_security_event(
            event_type='unauthorized_admin_access',
            source_ip=get_client_ip(request),
            target_endpoint='/admin/users',
            severity='high',
            description=f'Anonymous user accessed /admin/users from IP {get_client_ip(request)}'
        )
        
        log_activity(
            user='anonymous',
            action='unauthorized_admin_users_access',
            event_type='unauthorized_access',
            ip_address=get_client_ip(request),
            status='success',
            endpoint='/admin/users',
            details='Anonymous user accessed admin users page without authentication'
        )
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/logs') # Admin route to view activity logs, displaying a paginated list of recent activity logs in the system
def view_logs():
    if not current_user.is_authenticated:
        log_security_event(
            event_type='unauthorized_admin_access',
            source_ip=get_client_ip(request),
            target_endpoint='/admin/logs',
            severity='high',
            description=f'Anonymous user accessed /admin/logs from IP {get_client_ip(request)}'
        )
        
        log_activity(
            user='anonymous',
            action='unauthorized_admin_logs_access',
            event_type='unauthorized_access',
            ip_address=get_client_ip(request),
            status='success',
            endpoint='/admin/logs',
            details='Anonymous user accessed admin logs page without authentication'
        )
    
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(page=page, per_page=20)
    return render_template('admin_logs.html', logs=logs)

@admin_bp.route('/security-events') # Admin route to view security events, displaying a list of recent security events in the system
def view_security_events():
    if not current_user.is_authenticated:
        log_security_event(
            event_type='unauthorized_admin_access',
            source_ip=get_client_ip(request),
            target_endpoint='/admin/security-events',
            severity='high',
            description=f'Anonymous user accessed /admin/security-events from IP {get_client_ip(request)}'
        )
        
        log_activity(
            user='anonymous',
            action='unauthorized_admin_security_events_access',
            event_type='unauthorized_access',
            ip_address=get_client_ip(request),
            status='success',
            endpoint='/admin/security-events',
            details='Anonymous user accessed admin security events page without authentication'
        )
    
    events = SecurityEvent.query.order_by(SecurityEvent.timestamp.desc()).all()
    return render_template('admin_security_events.html', events=events)

@admin_bp.route('/behavior-logs') # Admin route to view behavior logs, displaying a list of recent behavior logs in the system
def view_behavior_logs():
    if not current_user.is_authenticated:
        log_security_event(
            event_type='unauthorized_admin_access',
            source_ip=get_client_ip(request),
            target_endpoint='/admin/behavior-logs',
            severity='high',
            description=f'Anonymous user accessed /admin/behavior-logs from IP {get_client_ip(request)}'
        )
        
        log_activity(
            user='anonymous',
            action='unauthorized_admin_behavior_logs_access',
            event_type='unauthorized_access',
            ip_address=get_client_ip(request),
            status='success',
            endpoint='/admin/behavior-logs',
            details='Anonymous user accessed admin behavior logs page without authentication'
        )
    
    logs = BehaviorLog.query.order_by(BehaviorLog.timestamp.desc()).limit(100).all()
    return render_template('admin_behavior_logs.html', logs=logs)
