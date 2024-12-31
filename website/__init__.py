# website/__init__.py

"""
Initialize the Flask application and its extensions.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import MetaData # needed to make migrations work
from werkzeug.security import generate_password_hash
from .config import Config  # Base configuration class


# I am going to set some naming conventions to get passed this annoying naming convention error:
convention = {
"ix": 'ix_%(column_0_label)s',
"uq": "uq_%(table_name)s_%(column_0_name)s",
"ck": "ck_%(table_name)s_%(constraint_name)s",
"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
"pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

# Initialize extensions
# db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
admin = Admin()

def create_app(config_class):
    """
    Application factory function.

    Args:
        config_class (object): The configuration class to use. Function called in main.py

    Returns:
        Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # tag: if this doesn't work for Heroku, I will probably need to implement one of my old solutions like this: 
    # Version 2 Solution
    # app.config['DATABASE_URL'] = Config.uri
    # app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']

    # Set up logging
    setup_logging(app)

    # Initialize extensions
    initialize_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Configure login manager
    configure_login_manager()

    # Set up Flask-Admin
    setup_admin_interface()

    # Create database tables
    create_database(app)

    return app

def initialize_extensions(app):
    """
    Initialize Flask extensions.

    Args:
        app (Flask): The Flask app instance.
    """
    
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    migrate = Migrate(app,db,render_as_batch=True)
    limiter = Limiter(app, default_limits=["100 per minute"])

def register_blueprints(app):
    """
    Register Flask blueprints.

    Args:
        app (Flask): The Flask app instance.
    """
    from .views import views
    from .auth import auth
    from .user_data import data_view  # Zane Addition

    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(data_view)

def configure_login_manager():
    """
    Configure the Flask-Login manager.
    """
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        """
        Load user by ID.

        Args:
            user_id (str): User ID.

        Returns:
            User instance or None.
        """
        from .models import User
        return User.query.get(int(user_id))

def setup_admin_interface():
    """
    Set up the Flask-Admin interface.
    """
    from .models import User, Device, DeviceData, Patient

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Device, db.session))
    admin.add_view(ModelView(DeviceData, db.session))
    admin.add_view(ModelView(Patient, db.session))

def create_database(app):
    """
    Create database tables.

    Args:
        app (Flask): The Flask app instance.
    """
    with app.app_context():
        try:
            db.create_all()
            app.logger.info(f"Database initialized at {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            app.logger.error(f"Error creating database: {e}")

def setup_logging(app):
    """
    Set up application logging.

    Args:
        app (Flask): The Flask app instance.
    """
    logging.basicConfig(level=logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
