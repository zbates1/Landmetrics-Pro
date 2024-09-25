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
        tuple: Seven lists containing ax_array, ay_array, az_array, gx_array, gy_array, gz_array, and labels.
    """
    try:
        # Ensure the device belongs to the current user
        device = Device.query.filter_by(id=device_id, user_id=current_user.id).first()
        if not device:
            logger.warning(f"Device ID {device_id} not found for user {current_user.id}")
            return [], [], [], [], [], [], []

        # Retrieve data points for the device
        data_points = (
            DeviceData.query
            .filter_by(device_id=device_id)
            .order_by(DeviceData.timestamp)
            .all()
        )

        # Extract data arrays
        ax_array = [data_point.ax for data_point in data_points]
        ay_array = [data_point.ay for data_point in data_points]
        az_array = [data_point.az for data_point in data_points]
        gx_array = [data_point.gx for data_point in data_points]
        gy_array = [data_point.gy for data_point in data_points]
        gz_array = [data_point.gz for data_point in data_points]
        labels = [data_point.timestamp.strftime('%Y-%m-%d %H:%M:%S') for data_point in data_points]

        logger.info(f"Retrieved {len(data_points)} data points for device ID {device_id}")
        return ax_array, ay_array, az_array, gx_array, gy_array, gz_array, labels

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        flash("An error occurred while retrieving device data.", category='error')
        return [], [], [], [], [], [], []

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
            ax_array, ay_array, az_array, gx_array, gy_array, gz_array, labels = get_device_data(selected_device_id)
        else:
            # Default data when no device is selected
            ax_array, ay_array, az_array, gx_array, gy_array, gz_array, labels = [], [], [], [], [], [], []

        return render_template(
            "user_data.html",
            devices=devices,
            selected_device_id=selected_device_id,
            ax_array=ax_array,
            ay_array=ay_array,
            az_array=az_array,
            gx_array=gx_array,
            gy_array=gy_array,
            gz_array=gz_array,
            labels=labels,
            user=current_user,
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        flash("An error occurred while loading your devices.", category='error')
        return redirect(url_for('views.home'))

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        flash("An unexpected error occurred.", category='error')
        return redirect(url_for('views.home'))
