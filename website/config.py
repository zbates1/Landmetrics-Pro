import os

class Config:

    # This ensures python-dotenv is loaded before the app is created and the env variables are loaded. Putting this in main.py or __init__.py doesn't work.
    from dotenv import load_dotenv
    load_dotenv()  # This method will load the environment variables from .env file


    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # I am not sure why the app in __init__ is using this key, and I will probably need to understand this for production
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL