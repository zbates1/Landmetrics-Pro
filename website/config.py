import os

class Config:

    # This ensures python-dotenv is loaded before the app is created and the env variables are loaded. Putting this in main.py or __init__.py doesn't work.
    from dotenv import load_dotenv
    load_dotenv()  # This method will load the environment variables from .env file


    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # I am not sure why the app in __init__ is using this key, and I will probably need to understand this for production
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Flask-Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
