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

# Import databases from models.py
from .models import User, Device, DeviceData

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


def get_device_data(device_id):
    # Ensure the device belongs to the current user
    device = Device.query.filter_by(id=device_id, user_id=current_user.id).first()
    if not device:
        return [], [], []

    data_points = DeviceData.query.filter_by(device_id=device_id).order_by(DeviceData.timestamp).all()
    sample_array_1 = [data_point.value1 for data_point in data_points]
    sample_array_2 = [data_point.value2 for data_point in data_points]
    labels = [data_point.timestamp.strftime('%Y-%m-%d %H:%M:%S') for data_point in data_points]
    
    return sample_array_1, sample_array_2, labels

# Set up the blueprint for html
data_view = Blueprint('data_view', __name__)


@data_view.route('/user_data', methods=['GET', 'POST'])
@login_required
def user_data():
    # Get the list of devices for the current user
    devices = Device.query.filter_by(user_id=current_user.id).all()

    # Get the selected device ID from the query parameters
    selected_device_id = request.args.get('device_id', type=int)

    # If a device is selected, retrieve its data
    if selected_device_id:
        # Fetch data for the selected device
        # Replace this with your actual data fetching logic
        sample_array_1, sample_array_2, labels = get_device_data(selected_device_id)
    else:
        # Default data or message
        sample_array_1 = []
        sample_array_2 = []

    return render_template(
        "user_data.html",
        devices=devices,
        selected_device_id=selected_device_id,
        sample_array_1=sample_array_1,
        sample_array_2=sample_array_2,
        labels=labels,
        user=current_user,
        first_name=current_user.first_name,
)


def get_device_data(device_id):
    # Implement logic to fetch data for the device
    # For demonstration purposes, we'll return dummy data
    # In practice, fetch data from your database or data source
    sample_array_1 = [1, 2, 3, 4, 5]
    sample_array_2 = [6, 7, 8, 9, 10]
    return sample_array_1, sample_array_2
