from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect  # Import CSRFProtect
from os import path
from flask_login import LoginManager

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash

from flask_mail import Mail

from .config import Config # this is to setup the config.py for env variables

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL'] # This is needed, and doesn't get set in the previous line
    print("Database Path:", app.config['SQLALCHEMY_DATABASE_URI'])

    csrf = CSRFProtect(app)
    csrf.init_app(app)

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .user_data import data_view # Zane Addition

    # Register Blueprints, Views and Auth (the two files containing the routes)
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(data_view, url_prefix='/') # Zane Addition

    from .models import User, Note, Device
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Admin setup
    admin = Admin(app)
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Device, db.session))

    # Configuration for Flask-Mail
    # app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # For Gmail
    # app.config['MAIL_PORT'] = 587  # For TLS
    # app.config['MAIL_USE_TLS'] = True
    # app.config['MAIL_USE_SSL'] = False  # Use either TLS or SSL
    # app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Your email address
    # app.config['MAIL_PASSWORD'] = 'your_email_password'  # Your email password
    # app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

    # Configuration for Flask-Mail
    app.config['MAIL_SERVER'] = app.config['MAIL_SERVER']
    app.config['MAIL_PORT'] = app.config['MAIL_PORT']
    app.config['MAIL_USE_TLS'] = app.config['MAIL_USE_TLS']
    app.config['MAIL_USE_SSL'] = app.config['MAIL_USE_SSL']
    app.config['MAIL_USERNAME'] = app.config['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = app.config['MAIL_PASSWORD']
    app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_DEFAULT_SENDER']

    mail = Mail(app)


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
