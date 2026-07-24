import os
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, flash
from replicated_company.extensions import db, login_manager

os.makedirs('database', exist_ok=True)
os.makedirs('logs', exist_ok=True)

def create_alert(event_type, severity, source_ip, target_endpoint, description):
    try:
        db_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'database',
            'company.db'
        ))
                
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM security_events 
            WHERE event_type = ? AND resolved = 0
        ''', (event_type,))
        
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False
        
        cursor.execute('''
            INSERT INTO security_events 
            (event_type, severity, source_ip, target_endpoint, description, timestamp, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_type,
            severity,
            source_ip,
            target_endpoint,
            description,
            datetime.now().isoformat(),
            0
        ))
        conn.commit()
        conn.close()
        print(f"✅ Alert created: {event_type}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def monitor_attacks():
    """Single monitor for all attack types - runs every 20 seconds"""
    while True:
        try:
            conn = sqlite3.connect('database/company.db')
            cursor = conn.cursor()
            
            twenty_sec_ago = (datetime.now() - timedelta(seconds=20)).isoformat()
            
            # Get all IPs with high request counts
            cursor.execute('''
                SELECT ip_address, COUNT(*) as count 
                FROM activity_logs 
                WHERE timestamp > ?
                GROUP BY ip_address 
                HAVING COUNT(*) > 5
                ORDER BY count DESC
            ''', (twenty_sec_ago,))
            
            attacks = cursor.fetchall()
            conn.close()
            
            for ip, count in attacks:
                print(f"🔍 Found: {ip} - {count} requests in 20 seconds")
                
                # Classify attack type based on count
                if count > 20:
                    create_alert('ddos_attack_detected', 'high', ip, '/', f'🔴 DDoS Attack from {ip}. {count} requests.')
                elif count > 10:
                    create_alert('request_flood_detected', 'medium', ip, '/', f'🟡 Request Flood from {ip}. {count} requests.')
                elif count > 5:
                    create_alert('endpoint_scanner_detected', 'medium', ip, '/', f'🟡 Endpoint Scanner from {ip}. {count} requests.')
                    
        except Exception as e:
            print(f"⚠️ Monitor error: {e}")
        
        time.sleep(20)

def create_app(config_name='default'):
    app = Flask(__name__)
    from replicated_company.config import config
    app.config.from_object(config[config_name])
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.employee_login'
    login_manager.login_message = 'Please log in to access this page.'

    from replicated_company.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from replicated_company.routes.auth import auth_bp
    from replicated_company.routes.employee import employee_bp
    from replicated_company.routes.admin import admin_bp
    from replicated_company.routes.files import files_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(files_bp, url_prefix='/files')

    @app.route('/')
    def home():
        from replicated_company.utils.logger import log_activity, log_behavior
        log_activity('anonymous', 'page_view', 'page_view', request.remote_addr, 'success', 'Home page viewed', '/')
        log_behavior(None, 'anonymous', 'page_view', 'Home page viewed', request.remote_addr, '/', None, 'low')
        return render_template('home.html')

    @app.route('/about')
    def about():
        from replicated_company.utils.logger import log_activity, log_behavior
        log_activity('anonymous', 'page_view', 'page_view', request.remote_addr, 'success', 'About page viewed', '/about')
        log_behavior(None, 'anonymous', 'page_view', 'About page viewed', request.remote_addr, '/about', None, 'low')
        return render_template('about.html')

    @app.route('/services')
    def services():
        from replicated_company.utils.logger import log_activity, log_behavior
        log_activity('anonymous', 'page_view', 'page_view', request.remote_addr, 'success', 'Services page viewed', '/services')
        log_behavior(None, 'anonymous', 'page_view', 'Services page viewed', request.remote_addr, '/services', None, 'low')
        return render_template('services.html')

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        from replicated_company.utils.logger import log_activity, log_behavior
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            log_activity('anonymous', 'contact_form_submission', 'form_submission', request.remote_addr, 'success', f'Contact from {name}', '/contact')
            log_behavior(None, 'anonymous', 'form_submission', f'Contact form from {name}', request.remote_addr, '/contact', None, 'low')
            flash('Your message has been sent!', 'success')
            return render_template('contact.html')
        log_activity('anonymous', 'page_view', 'page_view', request.remote_addr, 'success', 'Contact page viewed', '/contact')
        log_behavior(None, 'anonymous', 'page_view', 'Contact page viewed', request.remote_addr, '/contact', None, 'low')
        return render_template('contact.html')

    @app.errorhandler(403)
    def forbidden(error):
        from replicated_company.utils.logger import log_security_event
        log_security_event('unauthorized_access', request.remote_addr, request.path, f'Unauthorized access to {request.path}')
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    return app

app = create_app('development')

# Start the single monitor
threading.Thread(target=monitor_attacks, daemon=True).start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from replicated_company.database.seed_data import seed_database
        seed_database()
    print("\n" + "="*50)
    print("🚀 Server Running on http://localhost:5001")
    print("📊 Monitor checks every 20 seconds")
    print("🔍 Attack thresholds: >5 = scanner, >10 = flood, >20 = DDoS")
    print("="*50)
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
