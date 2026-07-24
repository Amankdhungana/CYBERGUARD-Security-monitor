import os
from flask import Flask, render_template, request, flash
from datetime import datetime


from extensions import db, login_manager


os.makedirs('database', exist_ok=True) # Create the 'database' directory if it doesn't exist to store the SQLite database file and ensure that the application has a designated location for its database files
os.makedirs('logs', exist_ok=True)

def create_app(config_name='default'): # Create and configure the Flask application instance based on the specified configuration name
    app = Flask(__name__)
    
    from config import config
    app.config.from_object(config[config_name])
    
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.employee_login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Import models here
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.employee import employee_bp
    from routes.admin import admin_bp
    from routes.files import files_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(files_bp, url_prefix='/files')
    
    @app.route('/') # Home route that logs the page view activity and renders the home page template
    def home():
        from utils.logger import log_activity
        log_activity(
            user='anonymous',
            action='page_view',
            event_type='page_view',
            ip_address=request.remote_addr,
            status='success',
            endpoint='/',
            details='Home page viewed'
        )
        return render_template('home.html')
    
    @app.route('/about') # About route that logs the page view activity and renders the about page template
    def about():
        from utils.logger import log_activity
        log_activity(
            user='anonymous',
            action='page_view',
            event_type='page_view',
            ip_address=request.remote_addr,
            status='success',
            endpoint='/about',
            details='About page viewed'
        )
        return render_template('about.html')
    
    @app.route('/services') # Services route that logs the page view activity and renders the services page template
    def services():
        from utils.logger import log_activity
        log_activity(
            user='anonymous',
            action='page_view',
            event_type='page_view',
            ip_address=request.remote_addr,
            status='success',
            endpoint='/services',
            details='Services page viewed'
        )
        return render_template('services.html')
    
    @app.route('/contact', methods=['GET', 'POST']) # Contact route that handles both GET and POST requests, logging the page view activity and form submission activity for auditing purposes
    def contact():
        from utils.logger import log_activity
        
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
        return render_template('contact.html')
    
    @app.errorhandler(403) # Error handler for 403 Forbidden errors, logging the unauthorized access attempt and rendering a custom 403 error page
    def forbidden(error):
        from utils.logger import log_security_event
        log_security_event(
            event_type='unauthorized_access',
            source_ip=request.remote_addr,
            target_endpoint=request.path,
            description=f'Unauthorized access attempt to {request.path}'
        )
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404) # Error handler for 404 Not Found errors, rendering a custom 404 error page
    def not_found(error):
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
    print("="*50)
    print("🔑 Login Credentials:")
    print("   Admin:    john.smith / Admin@123")
    print("   Employee: Any employee / Employee@123")
    print("="*50)
    print("⚠️  Press CTRL+C to stop the server")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
