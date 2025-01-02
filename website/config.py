import os
from dotenv import load_dotenv
import psycopg2


load_dotenv()  # Load environment variables from .env file if present

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    # Common configurations can go here


class DevelopmentConfig(Config):
    print(f'Entering Landmetrics-Pro development configuration')
    API_SECRET_KEY = os.environ.get('API_SECRET_KEY', 'YOUR_SUPER_SECRET_KEY')
    DEBUG = True
    # DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    postgress_password = os.getenv('POSTGRESS_PASSWORD')
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:Karlevyzane1@localhost:5432/postgres')
    # GET BATABASE URL FROM ENVIRONMENT, IF IT EXISTS, OTHERWISE USE DEFAULT, DYNAMICALLY ADDING IN PASSWORD
    # DATABASE_URL = os.getenv('DATABASE_URL', f'postgresql+psycopg2://postgres:{postgress_password}@localhost:5432/postgres')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


class ProductionConfig(Config): # tag: set up ENV variables in Heroku GUI or in Procfile
    print(f'Entering Landmetrics-Pro production configuration')
    API_SECRET_KEY = os.environ.get('API_SECRET_KEY', 'YOUR_SUPER_SECRET_KEY')
    DEBUG = False
    if os.getenv('DATABASE_URL'):

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
    
    else:
        print(f'No Production-Level DATABASE_URL environment variable found in {os.getenv("FLASK_ENV")} mode')
