from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from datetime import datetime
from replicated_company.app import db
from replicated_company.models.user import User
from replicated_company.utils.logger import log_activity, log_security_event, log_behavior
from replicated_company.utils.ip_tracker import get_client_ip
import sqlite3
import os

# TRACK BRUTE FORCE ALERTS - prevents duplicates
bruteforce_alert_tracker = {}

def create_bruteforce_alert(username, ip_address):
    """Create ONLY ONE brute force alert per attack"""
    alert_key = f"bruteforce_{username}"
    
    # Check if alert already exists
    db_path = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'database/company.db'
    ))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    
    cursor.execute('''
        SELECT COUNT(*) FROM security_events 
        WHERE event_type = 'bruteforce_attack_detected' AND resolved = 0
    ''')
    exists = cursor.fetchone()[0]
    conn.close()
    
    if exists > 0:
        return False
    
    # Create alert
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO security_events 
        (event_type, severity, source_ip, target_endpoint, description, timestamp, resolved)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        'bruteforce_attack_detected',
        'high',
        ip_address,
        '/auth/admin-login',
        f'🔴 Brute Force Attack detected on admin {username}. Account locked after 5 failed attempts. Attacker IP: {ip_address}',
        datetime.now().isoformat(),
        0
    ))
    conn.commit()
    conn.close()
    print(f"✅ Brute Force alert created for {username}")
    return True

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/employee-login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'GET':
        return render_template('employee_login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('User-Agent', '')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        if user.account_status != 'active':
            log_activity(
                user=username,
                action='login_failed',
                event_type='login',
                ip_address=ip_address,
                status='failed',
                endpoint='/auth/employee-login',
                details='Account locked or disabled'
            )
            flash('Your account is locked. Please contact administrator.', 'danger')
            return render_template('employee_login.html')
        
        login_user(user, remember=True)
        user.update_last_login()
        user.reset_failed_attempts()
        
        log_activity(
            user=username,
            action='login_success',
            event_type='login',
            ip_address=ip_address,
            status='success',
            endpoint='/auth/employee-login',
            details=f'User agent: {user_agent}'
        )
        
        log_behavior(
            employee_id=user.employee_id,
            username=user.username,
            behavior_type='login',
            activity=f'User {user.username} logged in successfully',
            page_accessed='/auth/employee-login',
            risk_level='low',
            ip_address=ip_address
        )
        
        flash(f'Welcome back, {user.full_name}!', 'success')
        
        if user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('employee.employee_dashboard'))
    else:
        if user:
            user.increment_failed_attempts()
            
            log_activity(
                user=username,
                action='login_failed',
                event_type='login',
                ip_address=ip_address,
                status='failed',
                endpoint='/auth/employee-login',
                details=f'Failed attempt {user.failed_login_attempts} of 5'
            )
            
            log_behavior(
                employee_id=user.employee_id,
                username=user.username,
                behavior_type='login_failed',
                activity=f'Failed login attempt for {user.username}',
                page_accessed='/auth/employee-login',
                risk_level='medium',
                ip_address=ip_address
            )
            
            if user.is_locked():
                flash('Account locked due to too many failed attempts. Contact administrator.', 'danger')
                # Only create ONE alert
                create_bruteforce_alert(username, ip_address)
        else:
            log_activity(
                user=username or 'unknown',
                action='login_failed',
                event_type='login',
                ip_address=ip_address,
                status='failed',
                endpoint='/auth/employee-login',
                details=f'Non-existent username: {username}'
            )
            
            log_behavior(
                employee_id=None,
                username=username or 'unknown',
                behavior_type='login_failed',
                activity=f'Failed login attempt with non-existent user: {username}',
                page_accessed='/auth/employee-login',
                risk_level='low',
                ip_address=ip_address
            )
        
        flash('Invalid username or password', 'danger')
        return render_template('employee_login.html')

@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('User-Agent', '')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.role == 'employee':
        log_activity(
            user=username,
            action='unauthorized_admin_access_attempt',
            event_type='unauthorized_access',
            ip_address=ip_address,
            status='failed',
            endpoint='/auth/admin-login',
            details='Employee attempted admin login'
        )
        
        log_behavior(
            employee_id=user.employee_id,
            username=user.username,
            behavior_type='unauthorized_access',
            activity=f'Employee {user.username} attempted to access admin portal',
            page_accessed='/auth/admin-login',
            risk_level='high',
            ip_address=ip_address
        )
        
        flash('Unauthorized access attempt logged', 'danger')
        return render_template('admin_login.html')
    
    if user and user.check_password(password) and user.role == 'admin':
        login_user(user, remember=True)
        user.update_last_login()
        user.reset_failed_attempts()
        
        log_activity(
            user=username,
            action='admin_login_success',
            event_type='login',
            ip_address=ip_address,
            status='success',
            endpoint='/auth/admin-login',
            details=f'Admin login from user agent: {user_agent}'
        )
        
        log_behavior(
            employee_id=user.employee_id,
            username=user.username,
            behavior_type='admin_login',
            activity=f'Admin {user.username} logged in',
            page_accessed='/auth/admin-login',
            risk_level='low',
            ip_address=ip_address
        )
        
        flash(f'Welcome Admin {user.full_name}!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    else:
        if user and user.role == 'admin':
            user.increment_failed_attempts()
            
            log_activity(
                user=username,
                action='admin_login_failed',
                event_type='login',
                ip_address=ip_address,
                status='failed',
                endpoint='/auth/admin-login',
                details=f'Failed admin attempt {user.failed_login_attempts} of 5'
            )
            
            log_behavior(
                employee_id=user.employee_id,
                username=user.username,
                behavior_type='admin_login_failed',
                activity=f'Failed admin login attempt for {user.username}',
                page_accessed='/auth/admin-login',
                risk_level='medium',
                ip_address=ip_address
            )
            
            if user.is_locked():
                flash('Admin account locked due to too many failed attempts. Contact administrator.', 'danger')
                # Only create ONE alert
                create_bruteforce_alert(username, ip_address)
        else:
            log_activity(
                user=username or 'unknown',
                action='admin_login_failed',
                event_type='login',
                ip_address=ip_address,
                status='failed',
                endpoint='/auth/admin-login',
                details=f'Failed admin login attempt'
            )
            
            log_behavior(
                employee_id=None,
                username=username or 'unknown',
                behavior_type='admin_login_failed',
                activity=f'Failed admin login attempt with user: {username}',
                page_accessed='/auth/admin-login',
                risk_level='low',
                ip_address=ip_address
            )
        
        flash('Invalid admin credentials', 'danger')
        return render_template('admin_login.html')

@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        log_activity(
            user=current_user.username,
            action='logout',
            event_type='logout',
            ip_address=get_client_ip(request),
            status='success',
            endpoint='/auth/logout',
            details='User logged out successfully'
        )
        
        log_behavior(
            employee_id=current_user.employee_id,
            username=current_user.username,
            behavior_type='logout',
            activity=f'User {current_user.username} logged out',
            page_accessed='/auth/logout',
            risk_level='low',
            ip_address=get_client_ip(request)
        )
        
        logout_user()
        flash('You have been logged out.', 'info')
    
    return redirect(url_for('home'))
