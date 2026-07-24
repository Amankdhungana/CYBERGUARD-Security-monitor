from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from utils.logger import log_activity
from utils.ip_tracker import get_client_ip

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/dashboard') # Route for employee dashboard, accessible only to authenticated employees
@login_required
def employee_dashboard(): # Render the employee dashboard with relevant data and logs, ensuring that only authenticated employees can access it
    if not current_user.is_employee():
        from flask import abort
        abort(403)
    
    log_activity(
        user=current_user.username,
        action='employee_page_view',
        event_type='page_view',
        ip_address=get_client_ip(request),
        status='success',
        endpoint='/employee/dashboard',
        details='Employee viewed dashboard'
    )
    
    employee_data = { # Compile relevant data for the employee dashboard, including recent activities, assigned tasks, and notices
        'employee': current_user,
        'recent_activities': [
            {'date': '2024-01-15', 'activity': 'Completed security training', 'status': 'completed'},
            {'date': '2024-01-14', 'activity': 'Updated project documentation', 'status': 'completed'},
            {'date': '2024-01-13', 'activity': 'Team meeting attendance', 'status': 'completed'}
        ],
        'assigned_tasks': [
            {'task': 'Review Q4 security report', 'priority': 'High', 'due_date': '2024-01-20'},
            {'task': 'Update password', 'priority': 'Medium', 'due_date': '2024-01-25'},
            {'task': 'Complete compliance checklist', 'priority': 'High', 'due_date': '2024-01-18'}
        ],
        'notices': [
            'Company security audit next week',
            'New VPN policy effective immediately',
            'Q1 cybersecurity training scheduled'
        ]
    }
    
    return render_template('employee_dashboard.html', data=employee_data)
