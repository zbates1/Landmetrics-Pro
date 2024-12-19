"""
This module defines the routes and functions related to user data visualization,
incorporating patient selection and updated schema changes.
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import User, Device, DeviceData, Patient
from datetime import datetime
import json

from flask_wtf.csrf import generate_csrf

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
    Updated to reflect the changed DeviceData schema.
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
            # Note: request_timestamp should be a datetime if stored as a DateTime.
            # If you're passing it as a string from the template, you may need to convert it.
            # If it's stored as a DateTime, parse the string into a datetime object.
            # Otherwise, if it's stored as-is, adjust accordingly.
            # Assuming request_timestamp is a string and matches the database format:
            try:
                rt_dt = datetime.strptime(request_timestamp, '%Y-%m-%d %H:%M:%S')
                query = query.filter_by(request_timestamp=rt_dt)
            except ValueError:
                logger.warning(f"Invalid request_timestamp format: {request_timestamp}")
                return {}

        data_points = query.order_by(DeviceData.time).all()

        if not data_points:
            logger.warning(f"No data points found for device ID {device_id} and request_timestamp {request_timestamp}")
            return {}

        # Prepare data structure based on the updated DeviceData fields
        data_dict = {
            'timestamps': [],
            'ax1': [], 'ay1': [], 'az1': [], 'ox1': [], 'oy1': [], 'oz1': [], 'ow1': [],
            'ax2': [], 'ay2': [], 'az2': [], 'ox2': [], 'oy2': [], 'oz2': [], 'ow2': []
        }

        for data_point in data_points:
            # Convert data_point.time from float to datetime string
            timestamp_str = datetime.fromtimestamp(data_point.time).strftime('%Y-%m-%d %H:%M:%S')
            data_dict['timestamps'].append(timestamp_str)
            data_dict['ax1'].append(data_point.ax1)
            data_dict['ay1'].append(data_point.ay1)
            data_dict['az1'].append(data_point.az1)
            data_dict['ox1'].append(data_point.ox1)
            data_dict['oy1'].append(data_point.oy1)
            data_dict['oz1'].append(data_point.oz1)
            data_dict['ow1'].append(data_point.ow1)
            data_dict['ax2'].append(data_point.ax2)
            data_dict['ay2'].append(data_point.ay2)
            data_dict['az2'].append(data_point.az2)
            data_dict['ox2'].append(data_point.ox2)
            data_dict['oy2'].append(data_point.oy2)
            data_dict['oz2'].append(data_point.oz2)
            data_dict['ow2'].append(data_point.ow2)

        return data_dict

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        flash("An error occurred while retrieving device data.", category='error')
        return {}

@data_view.route('/add_patient', methods=['POST'])
@login_required
def add_patient():
    """
    Handle AJAX requests to add a new patient.
    Expects form data: name, date_of_birth, gender, injury
    Returns JSON { success: bool, patient_id: int }
    """
    name = request.form.get('name')
    dob = request.form.get('date_of_birth')
    gender = request.form.get('gender')
    injury = request.form.get('injury')

    if not name or not dob or not gender:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    try:
        # Convert dob to a date object
        date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format'}), 400

    new_patient = Patient(
        name=name,
        date_of_birth=date_of_birth,
        gender=gender,
        injury=injury,
        user_id=current_user.id
    )

    try:
        db.session.add(new_patient)
        db.session.commit()
        return jsonify({'success': True, 'patient_id': new_patient.id})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
@data_view.route('/view_tests', methods=['GET'])
@login_required
def view_tests():
    patient_id = request.args.get('patient_id', type=int)
    # Logic to display past health tests for this patient
    # e.g., tests = HealthTest.query.filter_by(patient_id=patient_id).all()
    # return render_template('view_tests.html', tests=tests, patient_id=patient_id)
    return "View tests page placeholder"

@data_view.route('/new_test', methods=['GET'])
@login_required
def new_test():
    patient_id = request.args.get('patient_id', type=int)
    # Logic to initiate a new test for this patient
    # return render_template('new_test.html', patient_id=patient_id)
    return "New test page placeholder"



@data_view.route('/user_data', methods=['GET'])
@login_required
def user_data():
    try:
        # Get all patients for the current user
        patients = Patient.query.filter_by(user_id=current_user.id).all()

        # Get selected_patient_id from query params
        selected_patient_id = request.args.get('patient_id', type=int)
        current_patient_name = None

        # If patient is selected, fetch their name
        if selected_patient_id:
            patient = Patient.query.filter_by(id=selected_patient_id, user_id=current_user.id).first()
            if not patient:
                flash("Selected patient not found or does not belong to you.", category='error')
                return redirect(url_for('data_view.user_data'))
            current_patient_name = patient.name

        # Get the list of devices for the current user
        devices_query = Device.query.filter_by(user_id=current_user.id).all()
        devices = [{'id': device.id, 'name': device.name} for device in devices_query]

        # Get the selected device ID and request timestamp from the query parameters
        selected_device_id = request.args.get('device_id', type=int)
        selected_request_timestamp = request.args.get('request_timestamp')

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
            request_timestamps = [rt[0].strftime('%Y-%m-%d %H:%M:%S') for rt in request_timestamps_query if rt[0]]

            # Retrieve data for the selected device and request_timestamp
            data_dict = get_device_data(selected_device_id, selected_request_timestamp)
            if data_dict:
                device_data[selected_device_id] = data_dict
            else:
                # If no data, redirect but keep the same device_id for user convenience
                flash("No data available for the selected device and session.", category='error')
                return redirect(url_for('data_view.user_data', device_id=selected_device_id, patient_id=selected_patient_id))

        return render_template(
            "user_data.html",
            devices=devices,
            selected_device_id=selected_device_id,
            request_timestamps=request_timestamps,
            selected_request_timestamp=selected_request_timestamp,
            device_data=device_data,
            user=current_user,
            patients=patients,
            selected_patient_id=selected_patient_id if selected_patient_id is not None else None,
            current_patient_name=current_patient_name,
            csrf=generate_csrf() # THIS MAY NOT BE FUNCTIONAL FOR THE ADD PATIENT BUTTON, NOT SURE SINCE ADD_PATIENT ENDPOINT ONLY USES JSONIFY RETURNS
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        flash("An error occurred while loading your data.", category='error')
        return redirect(url_for('views.home'))

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        flash("An unexpected error occurred.", category='error')
        return redirect(url_for('views.home'))
