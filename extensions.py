from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create ONE instance of SQLAlchemy
db = SQLAlchemy()
login_manager = LoginManager()
