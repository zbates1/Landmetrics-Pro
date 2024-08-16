# user_data.py
# This script will collect the data from the SQL database and pass it to the html

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User
from . import db   ## means from __init__.py import db

# imports for database connection
import psycopg2
import os

# Collect data from the database
# Get database connection URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL', 'postgres://username:password@hostname:port/databasename') # -> IMPORTANT: HOW DO YOU SETUP THESE ENV VARIABLES? 

def connect_to_database():
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(DATABASE_URL)

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute a query
        cur.execute("SELECT * FROM your_table_name")

        # Retrieve query results
        records = cur.fetchall()

        print(records)

        # Clean up
        cur.close()
        conn.close()

    except Exception as e:
        print("An error occurred:", e)

# Set up the blueprint for html
data_view = Blueprint('data_view', __name__)


@data_view.route('/user_data', methods=['GET', 'POST'])
def user_data():

    connect_to_database()

    sample_array_1 = [1, 2, 3, 4, 5]
    sample_array_2 = [6, 7, 8, 9, 10]

    return render_template("user_data.html", 
                           sample_array_1=sample_array_1, 
                           sample_array_2=sample_array_2,
                           user=current_user,
                           first_name=current_user.first_name)