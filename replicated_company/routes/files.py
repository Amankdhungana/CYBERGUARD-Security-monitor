"""
File Routes - Document management and file access
"""
from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from replicated_company.utils.logger import log_activity, log_behavior
from replicated_company.utils.ip_tracker import get_client_ip

files_bp = Blueprint('files', __name__)

# Company file structure with role-based access
company_files = {
    'public': [
        {'name': 'Company_Policy_2024.pdf', 'size': '2.3 MB', 'type': 'PDF', 'path': '/files/policy.pdf'},
        {'name': 'Employee_Handbook.pdf', 'size': '5.1 MB', 'type': 'PDF', 'path': '/files/handbook.pdf'},
        {'name': 'Security_Guidelines.docx', 'size': '1.8 MB', 'type': 'DOCX', 'path': '/files/security.docx'}
    ],
    'internal': [
        {'name': 'Q4_Financial_Report.xlsx', 'size': '3.2 MB', 'type': 'XLSX', 'path': '/files/financial.xlsx'},
        {'name': 'Project_Roadmap_2024.pptx', 'size': '4.7 MB', 'type': 'PPTX', 'path': '/files/roadmap.pptx'},
        {'name': 'Internal_Memo_Q1.pdf', 'size': '0.9 MB', 'type': 'PDF', 'path': '/files/memo.pdf'}
    ],
    'confidential': [
        {'name': 'Client_Data_List.xlsx', 'size': '1.5 MB', 'type': 'XLSX', 'path': '/files/client_data.xlsx'},
        {'name': 'Strategic_Plan_2025.docx', 'size': '2.1 MB', 'type': 'DOCX', 'path': '/files/strategic.docx'},
        {'name': 'Employee_Reviews_Q4.pdf', 'size': '3.4 MB', 'type': 'PDF', 'path': '/files/reviews.pdf'}
    ]
}

@files_bp.route('/')
@login_required
def list_files():
    """List available files based on user role"""
    log_activity(
        user=current_user.username,
        action='file_list_view',
        event_type='file_access',
        ip_address=get_client_ip(request),
        status='success',
        endpoint='/files/',
        details=f'User viewed file list'
    )
    
    log_behavior(
        employee_id=current_user.employee_id,
        username=current_user.username,
        behavior_type='file_list_view',
        activity=f'User {current_user.username} viewed file list',
        page_accessed='/files/',
        risk_level='low',
        ip_address=get_client_ip(request)
    )
    
    # Determine accessible files based on role
    accessible_files = {}
    
    if current_user.is_admin():
        accessible_files = company_files
    elif current_user.is_employee():
        accessible_files = {
            'public': company_files['public'],
            'internal': company_files['internal']
        }
    
    return render_template('files.html', files=accessible_files, role=current_user.role)

@files_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    """Download file with access control"""
    ip_address = get_client_ip(request)
    
    file_access_allowed = False
    file_info = None
    
    # Check if user has access to this file
    for category, files in company_files.items():
        for file in files:
            if filename in file['name']:
                file_info = file
                if current_user.is_admin():
                    file_access_allowed = True
                elif current_user.is_employee() and category in ['public', 'internal']:
                    file_access_allowed = True
                break
    
    # Block unauthorized access
    if not file_access_allowed:
        log_activity(
            user=current_user.username,
            action='unauthorized_file_access',
            event_type='unauthorized_access',
            ip_address=ip_address,
            status='failed',
            endpoint=f'/files/download/{filename}',
            details=f'Unauthorized access attempt to {filename}'
        )
        
        log_behavior(
            employee_id=current_user.employee_id,
            username=current_user.username,
            behavior_type='unauthorized_file_access',
            activity=f'Unauthorized file access attempt: {filename}',
            page_accessed=f'/files/download/{filename}',
            risk_level='high',
            ip_address=ip_address
        )
        abort(403)
    
    # Log successful download
    log_activity(
        user=current_user.username,
        action='file_download',
        event_type='file_access',
        ip_address=ip_address,
        status='success',
        endpoint=f'/files/download/{filename}',
        details=f'Downloaded: {filename}'
    )
    
    log_behavior(
        employee_id=current_user.employee_id,
        username=current_user.username,
        behavior_type='file_download',
        activity=f'User {current_user.username} downloaded file: {filename}',
        page_accessed=f'/files/download/{filename}',
        risk_level='low',
        ip_address=ip_address
    )
    
    return f"Simulated file download: {filename}"
