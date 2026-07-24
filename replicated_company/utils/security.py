import re
from functools import wraps
from flask import request, abort, session
from replicated_company.utils.ip_tracker import get_client_ip
from replicated_company.utils.logger import log_security_event

def sanitize_input(input_string): # Function to sanitize user input by removing potentially harmful characters and trimming whitespace, helping to prevent injection attacks and ensure safe handling of user-provided data
    if not input_string:
        return input_string
    
    input_string = re.sub(r'[<>\"\'()&]', '', input_string)
    input_string = input_string.strip()
    
    return input_string

def require_https(f): # Decorator to enforce HTTPS for specific routes, ensuring that sensitive data is transmitted securely over encrypted connections and preventing potential man-in-the-middle attacks or eavesdropping on unencrypted traffic
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure:
            abort(400, description="HTTPS required")
        return f(*args, **kwargs)
    return decorated_function

def validate_session(): # Function to validate the current user session by checking for IP address consistency, helping to detect potential session hijacking attempts and ensuring that the session is being used by the legitimate user
    if 'ip_address' in session:
        current_ip = get_client_ip(request)
        if session['ip_address'] != current_ip:
            log_security_event(
                event_type='session_hijack_attempt',
                source_ip=current_ip,
                target_endpoint=request.path,
                severity='critical',
                description=f'Session IP mismatch: expected {session["ip_address"]}, got {current_ip}',
                recommendation='Invalidate session and require re-authentication'
            )
            return False
    return True
