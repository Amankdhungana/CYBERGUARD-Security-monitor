import sqlite3
import os
import requests

def get_company_connection(): # Establish a connection to the company's database
    # Step out of utils/, step out of monitoring_system/, then go into replicated_company/
    db_path = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        '../replicated_company/database/company.db'
    ))
    
    if os.path.exists(db_path):
        return sqlite3.connect(db_path)
    return None


def get_security_events(limit=50, severity=None): # Retrieve security events from the database, optionally filtered by severity
    conn = get_company_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    if severity and severity != "All":
        cursor.execute('''
            SELECT id, event_type, severity, source_ip, target_endpoint, description, timestamp, resolved
            FROM security_events 
            WHERE severity = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (severity.lower(), limit))
    else:
        cursor.execute('''
            SELECT id, event_type, severity, source_ip, target_endpoint, description, timestamp, resolved
            FROM security_events 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
    
    events = cursor.fetchall()
    conn.close()
    
    return [{
        'id': e[0],
        'event_type': e[1],
        'severity': e[2],
        'source_ip': e[3],
        'target_endpoint': e[4],
        'description': e[5],
        'timestamp': e[6] if e[6] else '',
        'resolved': bool(e[7]) if e[7] else False
    } for e in events]

def get_activity_logs(limit=100): # Retrieve activity logs from the database, limited to a specified number of entries
    conn = get_company_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user, action, event_type, status, timestamp, ip_address, endpoint, details
        FROM activity_logs 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    logs = cursor.fetchall()
    conn.close()
    
    return [{
        'user': l[0] if l[0] else 'anonymous',
        'action': l[1] if l[1] else '',
        'event_type': l[2] if l[2] else '',
        'status': l[3] if l[3] else 'success',
        'timestamp': l[4] if l[4] else '',
        'ip_address': l[5] if l[5] else '',
        'endpoint': l[6] if l[6] else '',
        'details': l[7] if l[7] else ''
    } for l in logs]

def get_attack_statistics(): # Retrieve various statistics about attacks from the database, including total attacks, high severity attacks, unresolved attacks, attack types, and top source IPs
    conn = get_company_connection()
    if not conn:
        return {}
    
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM security_events')
    total = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM security_events WHERE severity="high"')
    high = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM security_events WHERE resolved=0')
    unresolved = cursor.fetchone()[0] or 0
    
    cursor.execute('''
        SELECT event_type, COUNT(*) as count 
        FROM security_events 
        GROUP BY event_type 
        ORDER BY count DESC
    ''')
    attack_types = cursor.fetchall()
    
    cursor.execute('''
        SELECT source_ip, COUNT(*) as count 
        FROM security_events 
        GROUP BY source_ip 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    top_ips = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_attacks': total,
        'high_severity': high,
        'unresolved': unresolved,
        'attack_types': [{'name': a[0], 'count': a[1]} for a in attack_types],
        'top_ips': [{'ip': i[0], 'count': i[1]} for i in top_ips]
    }

def format_timestamp(ts): # Format the timestamp to a more readable format, returning only the date and time up to minutes
    if ts:
        return ts[:16]
    return 'N/A'

def get_severity_color(severity): 
    colors = {
        'high': '#ff4757',
        'medium': '#ffd93d',
        'low': '#00d4aa'
    }
    return colors.get(severity, '#8892b0')

def check_endpoint_security(endpoint): # Check if a specific endpoint is secure by sending a GET request and checking the response status code
    try:
        target = f"http://192.168.101.12:5001{endpoint}"
        response = requests.get(target, timeout=5, allow_redirects=False)
        if response.status_code in [302, 403, 401]:
            return True
        return False
    except:
        return False

def check_bruteforce_protection(): # Check if the brute force protection is working by attempting multiple failed login attempts and checking if the account gets locked
    try:
        target = "http://192.168.101.12:5001/auth/admin-login"
        locked = False
        for i in range(6):
            response = requests.post(
                target,
                data={'username': 'test_user', 'password': f'wrong{i}'},
                timeout=5
            )
            if "locked" in response.text.lower():
                locked = True
                break
        return locked
    except:
        return False

def check_ddos_protection(): # Check if the DDoS protection is working by sending a request to the server and checking if it responds successfully
    try:
        response = requests.get("http://192.168.101.12:5001/", timeout=3)
        return response.status_code == 200
    except:
        return False

def can_resolve_attack(event_type): # Check if a specific attack can be resolved by verifying if the underlying vulnerability has been fixed, returning a dictionary with a verification function and an error message if not
    verifiable_attacks = {
        'unauthorized_admin_access': {
            'verify': lambda: check_endpoint_security('/admin/dashboard'),
            'error': 'Admin dashboard is still accessible without authentication! Fix the bug first.'
        },
        'unauthorized_employee_access': {
            'verify': lambda: check_endpoint_security('/employee/dashboard'),
            'error': 'Employee dashboard is still accessible without authentication! Fix the bug first.'
        },
        'bruteforce': {
            'verify': check_bruteforce_protection,
            'error': 'Account lockout is not working! Implement account lockout first.'
        },
        'ddos': {
            'verify': check_ddos_protection,
            'error': 'Server is still unresponsive! The DDoS attack is still ongoing.'
        },
        'dos': {
            'verify': check_ddos_protection,
            'error': 'Server is still unresponsive! The DoS attack is still ongoing.'
        }
    }
    return verifiable_attacks.get(event_type)

def resolve_security_event(event_id): # Mark a specific security event as resolved in the database by updating its resolved status to 1
    conn = get_company_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    cursor.execute('UPDATE security_events SET resolved=1 WHERE id=?', (event_id,))
    conn.commit()
    conn.close()
    return True
