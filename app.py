import os
import time
import threading
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, flash
from extensions import db, login_manager

os.makedirs('database', exist_ok=True)
os.makedirs('logs', exist_ok=True)


def ensure_unique_ddos_index():
    """
    Creates a partial unique index so SQLite guarantees only
    ONE UNRESOLVED 'ddos_attack_detected' row can ever exist.
    Once resolved (resolved=1), a NEW alert can be created.
    """
    try:
        conn = sqlite3.connect('database/company.db')
        
        # Drop old index if exists
        conn.execute('DROP INDEX IF EXISTS idx_one_ddos_alert')
        
        # Create new index - only blocks UNRESOLVED alerts
        conn.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_one_ddos_alert
            ON security_events(event_type)
            WHERE event_type = 'ddos_attack_detected' AND resolved = 0
        ''')
        conn.commit()
        conn.close()
        print("✅ Unique index created: only one UNRESOLVED DDoS alert allowed")
    except Exception as e:
        print(f"⚠️ Could not create unique index: {e}")


def ddos_monitor():
    while True:
        try:
            conn = sqlite3.connect('database/company.db')
            cursor = conn.cursor()

            one_minute_ago = (datetime.now() - timedelta(minutes=1)).isoformat()
            cursor.execute('''
                SELECT ip_address, COUNT(*) as count 
                FROM activity_logs 
                WHERE timestamp > ?
                GROUP BY ip_address 
                HAVING COUNT(*) > 30
                LIMIT 1
            ''', (one_minute_ago,))

            attack = cursor.fetchone()

            if attack:
                ip, count = attack
                try:
                    cursor.execute('''
                        INSERT INTO security_events 
                        (event_type, severity, source_ip, target_endpoint, description, timestamp, resolved)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        'ddos_attack_detected',
                        'high',
                        ip,
                        '/',
                        f'DDoS attack from IP {ip}. {count} requests.',
                        datetime.now().isoformat(),
                        0  # UNRESOLVED
                    ))
                    conn.commit()
                    print("✅ DDoS alert created")
                except sqlite3.IntegrityError:
                    # Unresolved alert already exists - this is expected
                    pass

            conn.close()

        except Exception as e:
            print(f"⚠️ ddos_monitor error: {e}")

        time.sleep(60)


def create_app(config_name='default'):
    app = Flask(__name__)
    from config import config
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.employee_login'
    login_manager.login_message = 'Please log in to access this page.'

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.employee import employee_bp
    from routes.admin import admin_bp
    from routes.files import files_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(files_bp, url_prefix='/files')

    @app.route('/')
    def home():
        from utils.logger import log_activity, log_behavior
        log_activity(
            user='anonymous',
            action='page_view',
            event_type='page_view',
            ip_address=request.remote_addr,
            status='success',
            endpoint='/',
            details='Home page viewed'
        )
        log_behavior(
            employee_id=None,
            username='anonymous',
            behavior_type='page_view',
            activity='Home page viewed',
            page_accessed='/',
            risk_level='low',
            ip_address=request.remote_addr
        )
        return render_template('home.html')

    @app.route('/about')
    def about():
        from utils.logger import log_activity, log_behavior
        log_activity(
            user='anonymous',
            action='page_view',
            event_type='page_view',
            ip_address=request.remote_addr,
            status='success',
            endpoint='/about',
            details='About page viewed'
        )
        log_behavior(
            employee_id=None,
            username='anonymous',
            behavior_type='page_view',
            activity='About page viewed',
            page_accessed='/about',
            risk_level='low',
            ip_address=request.remote_addr
        )
        return render_template('about.html')

    @app.route('/services')
    def services():
        from utils.logger import log_activity, log_behavior
        log_activity(
            user='anonymous',
            action='page_view',
            event_type='page_view',
            ip_address=request.remote_addr,
            status='success',
            endpoint='/services',
            details='Services page viewed'
        )
        log_behavior(
            employee_id=None,
            username='anonymous',
            behavior_type='page_view',
            activity='Services page viewed',
            page_accessed='/services',
            risk_level='low',
            ip_address=request.remote_addr
        )
        return render_template('services.html')

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        from utils.logger import log_activity, log_behavior

        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')

            log_activity(
                user='anonymous',
                action='contact_form_submission',
                event_type='form_submission',
                ip_address=request.remote_addr,
                status='success',
                endpoint='/contact',
                details=f'Contact form from {name} ({email}) - Subject: {subject}'
            )
            log_behavior(
                employee_id=None,
                username='anonymous',
                behavior_type='form_submission',
                activity=f'Contact form submission from {name}',
                page_accessed='/contact',
                risk_level='low',
                ip_address=request.remote_addr
            )
            flash('Your message has been sent. We\'ll get back to you soon!', 'success')
            return render_template('contact.html')

        log_activity(
            user='anonymous',
            action='page_view',
            event_type='page_view',
            ip_address=request.remote_addr,
            status='success',
            endpoint='/contact',
            details='Contact page viewed'
        )
        log_behavior(
            employee_id=None,
            username='anonymous',
            behavior_type='page_view',
            activity='Contact page viewed',
            page_accessed='/contact',
            risk_level='low',
            ip_address=request.remote_addr
        )
        return render_template('contact.html')

    @app.errorhandler(403)
    def forbidden(error):
        from utils.logger import log_security_event, log_behavior
        log_security_event(
            event_type='unauthorized_access',
            source_ip=request.remote_addr,
            target_endpoint=request.path,
            description=f'Unauthorized access attempt to {request.path}'
        )
        log_behavior(
            employee_id=None,
            username='anonymous',
            behavior_type='unauthorized_access',
            activity=f'Unauthorized access attempt to {request.path}',
            page_accessed=request.path,
            risk_level='high',
            ip_address=request.remote_addr
        )
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    return app


app = create_app('development')

# Make sure the DB-level guard against duplicate DDoS alerts exists
ensure_unique_ddos_index()

thread = threading.Thread(target=ddos_monitor, daemon=True)
thread.start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from database.seed_data import seed_database
        seed_database()

    print("\n" + "=" * 50)
    print("🚀 Server Running")
    print("📍 http://localhost:5001")
    print("=" * 50)
    print("🛡️ Only ONE UNRESOLVED DDoS alert allowed")
    print("   Resolve it to allow a NEW alert")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
