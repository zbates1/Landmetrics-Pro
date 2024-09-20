import os
import psycopg2

class Config:

    # This ensures python-dotenv is loaded before the app is created and the env variables are loaded. Putting this in main.py or __init__.py doesn't work.
    from dotenv import load_dotenv
    # not really necessary because we don't have an env file. Heroku defines our port and the database url.
    load_dotenv()  # This method will load the environment variables from .env file


    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # I am not sure why the app in __init__ is using this key, and I will probably need to understand this for production
    # tag: local deployment
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
   
    # tag: heroku deployment
    # For heroku, I think I need to change it to this: tag: developments link: https://devcenter.heroku.com/articles/connecting-heroku-postgres#heroku-postgres-ssl
    # DATABASE_URL = os.environ['DATABASE_URL']
    # conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    SQLALCHEMY_DATABASE_URI = DATABASE_URL