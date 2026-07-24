from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from datetime import datetime
from app import db
from models.user import User
from utils.logger import log_activity, log_security_event
from utils.ip_tracker import get_client_ip

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/employee-login', methods=['GET', 'POST']) # Route for employee login, handling both GET and POST requests for the login form
def employee_login():
    if request.method == 'GET':
        return render_template('employee_login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('User-Agent', '')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password): # Check if the user exists and the password is correct
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
            
            if user.is_locked():
                flash('Account locked due to too many failed attempts. Contact administrator.', 'danger')
                log_security_event(
                    event_type='account_locked',
                    source_ip=ip_address,
                    target_endpoint='/auth/employee-login',
                    description=f'Account {username} locked due to 5 failed login attempts'
                )
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
    
    if user and user.role == 'employee': # Log unauthorized admin access attempt by an employee
        log_security_event(
            event_type='employee_admin_access_attempt',
            source_ip=ip_address,
            target_endpoint='/auth/admin-login',
            description=f'Employee {username} attempted to access admin portal'
        )
        
        log_activity(
            user=username,
            action='unauthorized_admin_access_attempt',
            event_type='unauthorized_access',
            ip_address=ip_address,
            status='failed',
            endpoint='/auth/admin-login',
            details='Employee attempted admin login'
        )
        
        flash('Unauthorized access attempt logged', 'danger')
        return render_template('admin_login.html')
    
    if user and user.check_password(password) and user.role == 'admin': # Check if the user exists, the password is correct, and the role is admin
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
        
        flash(f'Welcome Admin {user.full_name}!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    else: # Handle failed admin login attempts, incrementing failed attempts and logging the event
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
            
            if user.is_locked():
                flash('Admin account locked due to too many failed attempts. Contact administrator.', 'danger')
                log_security_event(
                    event_type='admin_account_locked',
                    source_ip=ip_address,
                    target_endpoint='/auth/admin-login',
                    description=f'Admin account {username} locked due to 5 failed login attempts'
                )
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
        
        flash('Invalid admin credentials', 'danger')
        return render_template('admin_login.html')

@auth_bp.route('/logout') #   Route to log out the current user, clearing their session and redirecting them to the home page
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
        logout_user()
        flash('You have been logged out.', 'info')
    
    return redirect(url_for('home'))
