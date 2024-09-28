"""
This module defines the routes and functions related to user data visualization.
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
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
        dict: A dictionary containing sensor data arrays and timestamps.
    """
    try:
        # Ensure the device belongs to the current user
        device = Device.query.filter_by(id=device_id, user_id=current_user.id).first()
        if not device:
            logger.warning(f"Device ID {device_id} not found for user {current_user.id}")
            return {}

        # Retrieve data points for the device
        data_points = (
            DeviceData.query
            .filter_by(device_id=device_id)
            .order_by(DeviceData.timestamp)
            .all()
        )
        if not data_points:
            logger.warning(f"No data points found for device ID {device_id}")
            return {}


        # Prepare data structure
        data_dict = {
            'timestamps': [],
            'ax1': [], 'ay1': [], 'az1': [], 'gx1': [], 'gy1': [], 'gz1': [],
            'ax2': [], 'ay2': [], 'az2': [], 'gx2': [], 'gy2': [], 'gz2': [],
            'ax3': [], 'ay3': [], 'az3': [], 'gx3': [], 'gy3': [], 'gz3': []
        }

        for data_point in data_points:
            data_dict['timestamps'].append(data_point.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            data_dict['ax1'].append(data_point.ax1)
            data_dict['ay1'].append(data_point.ay1)
            data_dict['az1'].append(data_point.az1)
            data_dict['gx1'].append(data_point.gx1)
            data_dict['gy1'].append(data_point.gy1)
            data_dict['gz1'].append(data_point.gz1)
            data_dict['ax2'].append(data_point.ax2)
            data_dict['ay2'].append(data_point.ay2)
            data_dict['az2'].append(data_point.az2)
            data_dict['gx2'].append(data_point.gx2)
            data_dict['gy2'].append(data_point.gy2)
            data_dict['gz2'].append(data_point.gz2)
            data_dict['ax3'].append(data_point.ax3)
            data_dict['ay3'].append(data_point.ay3)
            data_dict['az3'].append(data_point.az3)
            data_dict['gx3'].append(data_point.gx3)
            data_dict['gy3'].append(data_point.gy3)
            data_dict['gz3'].append(data_point.gz3)

        return data_dict

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        flash("An error occurred while retrieving device data.", category='error')
        return {}


@data_view.route('/user_data', methods=['GET'])
@login_required
def user_data():
    try:
        # Get the list of devices for the current user and serialize them
        devices_query = Device.query.filter_by(user_id=current_user.id).all()
        devices = [{'id': device.id, 'name': device.name} for device in devices_query]

        # Get the selected device ID from the query parameters
        selected_device_id = request.args.get('device_id', type=int)

        # Initialize data
        device_data = {}

        if selected_device_id:
            # Retrieve data for the selected device using the helper function
            data_dict = get_device_data(selected_device_id)
            if data_dict:
                # Store data for the selected device using an integer key
                device_data[selected_device_id] = data_dict
            else:
                logger.warning(f"Device ID {selected_device_id} not found or no data available.")
                flash("Selected device not found or no data available.", category='error')
                return redirect(url_for('data_view.user_data'))

        return render_template(
            "user_data.html",
            devices=devices,
            selected_device_id=selected_device_id,
            device_data=device_data,
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