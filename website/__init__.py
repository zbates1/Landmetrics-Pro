from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .config import Config # this is to setup the config.py for env variables

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    # app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs' # now handled by the import above and this line below
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .user_data import data_view # Zane Addition

    # Register Blueprints, Views and Auth (the two files containing the routes)
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(data_view, url_prefix='/') # Zane Addition

    from .models import User, Note
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Admin setup
    admin = Admin(app)
    admin.add_view(ModelView(User, db.session))

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
