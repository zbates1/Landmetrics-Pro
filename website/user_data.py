# user_data.py
"""
This module defines the routes and functions related to user data visualization.
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import User, Device, DeviceData

# Initialize the blueprint
data_view = Blueprint('data_view', __name__)

# Set up logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_device_data(device_id):
    """
    Retrieve data for a specific device belonging to the current user.

    Args:
        device_id (int): The ID of the device.

    Returns:
        tuple: Three lists containing sample_array_1, sample_array_2, and labels.
    """
    try:
        # Ensure the device belongs to the current user
        device = Device.query.filter_by(id=device_id, user_id=current_user.id).first()
        if not device:
            logger.warning(f"Device ID {device_id} not found for user {current_user.id}")
            return [], [], []

        # Retrieve data points for the device
        data_points = (
            DeviceData.query
            .filter_by(device_id=device_id)
            .order_by(DeviceData.timestamp)
            .all()
        )

        sample_array_1 = [data_point.value1 for data_point in data_points]
        sample_array_2 = [data_point.value2 for data_point in data_points]
        labels = [data_point.timestamp.strftime('%Y-%m-%d %H:%M:%S') for data_point in data_points]

        logger.info(f"Retrieved {len(data_points)} data points for device ID {device_id}")
        return sample_array_1, sample_array_2, labels

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        flash("An error occurred while retrieving device data.", category='error')
        return [], [], []

@data_view.route('/user_data', methods=['GET', 'POST'])
@login_required
def user_data():
    """
    Render the user data page where users can view data from their devices.

    Returns:
        Response: The rendered template for the user data page.
    """
    try:
        # Get the list of devices for the current user
        devices = Device.query.filter_by(user_id=current_user.id).all()

        # Get the selected device ID from the query parameters
        selected_device_id = request.args.get('device_id', type=int)

        # If a device is selected, retrieve its data
        if selected_device_id:
            sample_array_1, sample_array_2, labels = get_device_data(selected_device_id)
        else:
            # Default data when no device is selected
            sample_array_1, sample_array_2, labels = [], [], []

        return render_template(
            "user_data.html",
            devices=devices,
            selected_device_id=selected_device_id,
            sample_array_1=sample_array_1,
            sample_array_2=sample_array_2,
            labels=labels,
            user=current_user, # deleted first_name returned from User model
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        flash("An error occurred while loading your devices.", category='error')
        return redirect(url_for('views.home'))

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        flash("An unexpected error occurred.", category='error')
        return redirect(url_for('views.home'))
