"""
This module defines the routes and functions related to user data visualization.
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import User, Device, DeviceData
from datetime import datetime

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

def get_device_data(device_id, request_timestamp=None):
    """
    Retrieve data for a specific device and request_timestamp belonging to the current user.

    Args:
        device_id (int): The ID of the device.
        request_timestamp (str): The request timestamp string.

    Returns:
        dict: A dictionary containing sensor data arrays and timestamps.
    """
    try:
        # Ensure the device belongs to the current user
        device = Device.query.filter_by(id=device_id, user_id=current_user.id).first()
        if not device:
            logger.warning(f"Device ID {device_id} not found for user {current_user.id}")
            return {}

        # Build the query for data points
        query = DeviceData.query.filter_by(device_id=device_id)
        if request_timestamp:
            query = query.filter_by(request_timestamp=request_timestamp)
        data_points = query.order_by(DeviceData.time).all()

        if not data_points:
            logger.warning(f"No data points found for device ID {device_id} and request_timestamp {request_timestamp}")
            return {}

        # Prepare data structure
        data_dict = {
            'timestamps': [],
            'ax1': [], 'ay1': [], 'az1': [], 'gx1': [], 'gy1': [], 'gz1': [],
            'ax2': [], 'ay2': [], 'az2': [], 'gx2': [], 'gy2': [], 'gz2': [],
            'ax3': [], 'ay3': [], 'az3': [], 'gx3': [], 'gy3': [], 'gz3': []
        }

        for data_point in data_points:
            # Convert data_point.time from float to datetime
            timestamp_str = datetime.fromtimestamp(data_point.time).strftime('%Y-%m-%d %H:%M:%S')
            data_dict['timestamps'].append(timestamp_str)
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

        # Get the selected device ID and request timestamp from the query parameters
        selected_device_id = request.args.get('device_id', type=int)
        selected_request_timestamp = request.args.get('request_timestamp')

        # Initialize data
        device_data = {}
        request_timestamps = []

        if selected_device_id:
            # Get the list of unique request_timestamps for the selected device
            request_timestamps_query = (
                db.session.query(DeviceData.request_timestamp)
                .filter_by(device_id=selected_device_id)
                .distinct()
                .order_by(DeviceData.request_timestamp)
                .all()
            )
            # Extract unique request_timestamps
            request_timestamps = [rt[0] for rt in request_timestamps_query]

            # Retrieve data for the selected device and request_timestamp
            data_dict = get_device_data(selected_device_id, selected_request_timestamp)
            if data_dict:
                # Store data for the selected device
                device_data[selected_device_id] = data_dict
            else:
                flash("No data available for the selected device and session.", category='error')
                return redirect(url_for('data_view.user_data', device_id=selected_device_id))

        return render_template(
            "user_data.html",
            devices=devices,
            selected_device_id=selected_device_id,
            request_timestamps=request_timestamps,
            selected_request_timestamp=selected_request_timestamp,
            device_data=device_data,
            user=current_user,
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        flash("An error occurred while loading your devices.", category='error')
        return redirect(url_for('views.home'))

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        flash("An unexpected error occurred.", category='error')
        return redirect(url_for('views.home'))
