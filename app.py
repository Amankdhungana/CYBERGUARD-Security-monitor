"""
Main Flask Application - Entry point for the company system
"""
import os
from flask import Flask, render_template, request, flash
from datetime import datetime
from extensions import db, login_manager

# Create necessary directories
os.makedirs('database', exist_ok=True)
os.makedirs('logs', exist_ok=True)

def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.employee_login'
    login_manager.login_message = 'Please log in to access this page.'
    
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
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
        """Homepage - Company landing page"""
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
        """About page"""
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
        """Services page"""
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
        """Contact page with form submission"""
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
        """403 Forbidden handler"""
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
        """404 Not Found handler"""
        return render_template('errors/404.html'), 404
    
    return app

# Create app instance
app = create_app('development')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from database.seed_data import seed_database
        seed_database()
    
    print("\n" + "="*50)
    print("🚀 Replicated Company Limited Server Running")
    print("="*50)
    print(f"📍 Local:    http://localhost:5001")
    print(f"📍 Network:  http://192.168.101.2:5001")
    print("="*50)
    print("🔑 Login Credentials:")
    print("   Admin:    john.smith / Admin@123")
    print("   Employee: Any employee / Employee@123")
    print("="*50)
    print("⚠️  Press CTRL+C to stop the server")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
    