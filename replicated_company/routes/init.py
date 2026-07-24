from replicated_company.routes.auth import auth_bp
from replicated_company.routes.employee import employee_bp
from replicated_company.routes.admin import admin_bp
from replicated_company.routes.files import files_bp

__all__ = ['auth_bp', 'employee_bp', 'admin_bp', 'files_bp']
