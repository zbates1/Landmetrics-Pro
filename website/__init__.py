import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import MetaData
from werkzeug.security import generate_password_hash
from .config import Config
from .admin_views import MyAdminIndexView

# Set naming conventions to avoid naming convention errors
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Basic authentication setup
    basic_auth = BasicAuth(app)
    app.config['BASIC_AUTH_USERNAME'] = 'admin'
    app.config['BASIC_AUTH_PASSWORD'] = 'secret'
    app.config['BASIC_AUTH_FORCE'] = False

    # Setup admin interface with custom index view that requires basic authentication
    admin = Admin(app, index_view=MyAdminIndexView(basic_auth), name='MySite Admin', template_mode='bootstrap3')

    # Register blueprints
    register_blueprints(app)

    # Configure login manager
    configure_login_manager(app)

    # Set up logging
    setup_logging(app)

    # Initialize Migrate and Limiter within the application context
    with app.app_context():
        migrate = Migrate(app,db,render_as_batch=True)
        limiter = Limiter(app, default_limits=["100 per minute"])

    # Create database tables if they don't exist
    create_database(app)

    return app

def register_blueprints(app):
    from .views import views
    from .auth import auth
    from .user_data import data_view
    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(data_view)

def configure_login_manager(app):
    login_manager.login_view = 'auth.login'
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

def setup_admin_interface(admin):
    from .models import User, Device, DeviceData, Patient
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Device, db.session))
    admin.add_view(ModelView(DeviceData, db.session))
    admin.add_view(ModelView(Patient, db.session))

def create_database(app):
    with app.app_context():
        db.create_all()

def setup_logging(app):
    logging.basicConfig(level=logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
