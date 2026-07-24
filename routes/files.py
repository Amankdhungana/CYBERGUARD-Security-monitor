from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from utils.logger import log_activity
from utils.ip_tracker import get_client_ip

files_bp = Blueprint('files', __name__)

company_files = { # Simulated file storage structure with categories and file metadata, representing the files available in the company system
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
@login_required # Route to display the list of files accessible to the logged-in user, based on their role (admin or employee) and logging the activity for auditing purposes
def list_files():
    log_activity(
        user=current_user.username,
        action='file_list_view',
        event_type='file_access',
        ip_address=get_client_ip(request),
        status='success',
        endpoint='/files/',
        details=f'User viewed file list'
    )
    
    accessible_files = {}
    
    if current_user.is_admin():
        accessible_files = company_files
    elif current_user.is_employee():
        accessible_files = {
            'public': company_files['public'],
            'internal': company_files['internal']
        }
    
    return render_template('files.html', files=accessible_files, role=current_user.role)

@files_bp.route('/download/<filename>') # Route to handle file download requests, ensuring that only authorized users can access specific files based on their role and logging the activity for auditing purposes
@login_required
def download_file(filename):
    ip_address = get_client_ip(request)
    
    file_access_allowed = False
    file_info = None
    
    for category, files in company_files.items(): # Check if the requested file exists in the accessible categories based on user role
        for file in files:
            if filename in file['name']:
                file_info = file
                if current_user.is_admin():
                    file_access_allowed = True
                elif current_user.is_employee() and category in ['public', 'internal']:
                    file_access_allowed = True
                break
    
    if not file_access_allowed: # Log unauthorized file access attempt and abort with a 403 Forbidden response
        log_activity(
            user=current_user.username,
            action='unauthorized_file_access',
            event_type='unauthorized_access',
            ip_address=ip_address,
            status='failed',
            endpoint=f'/files/download/{filename}',
            details=f'Unauthorized access attempt to {filename}'
        )
        abort(403)
    
    log_activity( # Log the successful file download activity for auditing and tracking purposes
        user=current_user.username,
        action='file_download',
        event_type='file_access',
        ip_address=ip_address,
        status='success',
        endpoint=f'/files/download/{filename}',
        details=f'Downloaded: {filename}'
    )
    
    return f"Simulated file download: {filename}"
