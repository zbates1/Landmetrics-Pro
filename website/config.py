import os
from dotenv import load_dotenv
import psycopg2


load_dotenv()  # Load environment variables from .env file if present

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    # Common configurations can go here


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    # Add any other development-specific configurations


class ProductionConfig(Config): # tag: set up ENV variables in Heroku GUI or in Procfile
    DEBUG = False
    DATABASE_URL = os.environ['DATABASE_URL']
    # Fix for SQLAlchemy error with Heroku Postgres
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    # Add any other production-specific configurations

    uri = os.getenv("DATABASE_URL")  # or other relevant config var
    if os.getenv('FLASK_ENV ') == 'production':
        print('====Production mode environment variable detected=====')
        conn = psycopg2.connect(uri, sslmode='require')
