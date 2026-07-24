"""
Admin Routes - Admin dashboard and management pages
"""
from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from replicated_company.models.user import User
from replicated_company.models.activity_log import ActivityLog
from replicated_company.models.security_event import SecurityEvent
from replicated_company.models.behavior_log import BehaviorLog
from replicated_company.utils.logger import log_activity, log_security_event, log_behavior
from replicated_company.utils.ip_tracker import get_client_ip
from replicated_company.app import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard - shows system statistics and recent events"""
    if not current_user.is_admin():
        abort(403)
    
    log_activity(
        user=current_user.username,
        action='admin_page_view',
        event_type='page_view',
        ip_address=get_client_ip(request),
        status='success',
        endpoint='/admin/dashboard',
        details='Admin viewed dashboard'
    )
    
    log_behavior(
        employee_id=current_user.employee_id,
        username=current_user.username,
        behavior_type='admin_page_view',
        activity=f'Admin {current_user.username} viewed dashboard',
        page_accessed='/admin/dashboard',
        risk_level='low',
        ip_address=get_client_ip(request)
    )
    
    # Get statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(account_status='active').count()
    recent_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    recent_security_events = SecurityEvent.query.filter_by(resolved=False).order_by(SecurityEvent.timestamp.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'recent_logs': recent_logs,
        'recent_security_events': recent_security_events
    }
    
    users = User.query.all()
    return render_template('admin_dashboard.html', stats=stats, users=users)

@admin_bp.route('/users')
@login_required
def manage_users():
    """User management page - view all employees"""
    if not current_user.is_admin():
        abort(403)
    
    log_activity(
        user=current_user.username,
        action='admin_page_view',
        event_type='page_view',
        ip_address=get_client_ip(request),
        status='success',
        endpoint='/admin/users',
        details='Admin viewed user management'
    )
    
    log_behavior(
        employee_id=current_user.employee_id,
        username=current_user.username,
        behavior_type='admin_page_view',
        activity=f'Admin {current_user.username} viewed user management',
        page_accessed='/admin/users',
        risk_level='low',
        ip_address=get_client_ip(request)
    )
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/logs')
@login_required
def view_logs():
    """Activity logs page - view all user activities"""
    if not current_user.is_admin():
        abort(403)
    
    log_activity(
        user=current_user.username,
        action='admin_page_view',
        event_type='page_view',
        ip_address=get_client_ip(request),
        status='success',
        endpoint='/admin/logs',
        details='Admin viewed activity logs'
    )
    
    log_behavior(
        employee_id=current_user.employee_id,
        username=current_user.username,
        behavior_type='admin_page_view',
        activity=f'Admin {current_user.username} viewed activity logs',
        page_accessed='/admin/logs',
        risk_level='low',
        ip_address=get_client_ip(request)
    )
    
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin_logs.html', logs=logs)

@admin_bp.route('/security-events')
@login_required
def view_security_events():
    """Security events page - view all security incidents"""
    if not current_user.is_admin():
        abort(403)
    
    log_activity(
        user=current_user.username,
        action='admin_page_view',
        event_type='page_view',
        ip_address=get_client_ip(request),
        status='success',
        endpoint='/admin/security-events',
        details='Admin viewed security events'
    )
    
    log_behavior(
        employee_id=current_user.employee_id,
        username=current_user.username,
        behavior_type='admin_page_view',
        activity=f'Admin {current_user.username} viewed security events',
        page_accessed='/admin/security-events',
        risk_level='low',
        ip_address=get_client_ip(request)
    )
    
    events = SecurityEvent.query.order_by(SecurityEvent.timestamp.desc()).all()
    return render_template('admin_security_events.html', events=events)

@admin_bp.route('/behavior-logs')
@login_required
def view_behavior_logs():
    """Behavior logs page - view behavioral patterns"""
    if not current_user.is_admin():
        abort(403)
    
    log_activity(
        user=current_user.username,
        action='admin_page_view',
        event_type='page_view',
        ip_address=get_client_ip(request),
        status='success',
        endpoint='/admin/behavior-logs',
        details='Admin viewed behavior logs'
    )
    
    log_behavior(
        employee_id=current_user.employee_id,
        username=current_user.username,
        behavior_type='admin_page_view',
        activity=f'Admin {current_user.username} viewed behavior logs',
        page_accessed='/admin/behavior-logs',
        risk_level='low',
        ip_address=get_client_ip(request)
    )
    
    logs = BehaviorLog.query.order_by(BehaviorLog.timestamp.desc()).limit(100).all()
    return render_template('admin_behavior_logs.html', logs=logs)
