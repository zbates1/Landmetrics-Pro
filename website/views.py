import logging
from flask import Blueprint, render_template, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from .models import Device, DeviceData
from . import db, csrf
import json
from datetime import datetime
import random

views = Blueprint('views', __name__)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


@views.route('/', methods=['GET', 'POST'])
def home():
    # tag: delete -> This stuff below could prolly get deleted cuz it is just needed for the Notes db -- deleted
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    # Access DATABASE_URL from current_app.config
    DATABASE_URL = current_app.config.get('DATABASE_URL', '')

    return render_template("home.html", csrf=csrf, user=current_user, DATABASE_URL=DATABASE_URL)

# Taking data from the Arduino ESP32
@views.route('/api/data', methods=['POST'])
@csrf.exempt  # only if you're exempting this route from CSRF checks
def receive_data():
    """
    Receive JSON data for a device, create DeviceData entries for each data point.
    Expected JSON structure (example):
    {
      "device_name": "ABCD1234",     # The device's serial_number
      "timestamps": [float, float, ...],
      "ax1": [float, float, ...],
      "ay1": [...],
      "az1": [...],
      "ox1": [...],
      "oy1": [...],
      "oz1": [...],
      "ow1": [...],
      "ax2": [...],
      "ay2": [...],
      "az2": [...],
      "ox2": [...],
      "oy2": [...],
      "oz2": [...],
      "ow2": [...]
    }
    (All arrays must be the same length.)
    """
    data = request.get_json()
    if not data:
        logger.error("No JSON data received")
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    device_serial_number = data.get('device_name')  # Serial number of the device
    timestamps = data.get('timestamps')            # Array of 'time' values

    # Create a request_timestamp for each data point, but use the current time and the same value for each data point in the same API call
    request_timestamps = [datetime.utcnow() for _ in range(len(timestamps or []))]

    # Define the sensor fields matching your new schema (acceleration + orientation)
    sensor_variables = [
        'ax1', 'ay1', 'az1', 'ox1', 'oy1', 'oz1', 'ow1',
        'ax2', 'ay2', 'az2', 'ox2', 'oy2', 'oz2', 'ow2'
    ]

    # Check that device_name and timestamps exist
    if not device_serial_number or not timestamps:
        logger.error("Missing device_name or timestamps in the received JSON")
        return jsonify({"status": "error", "message": "Missing device_name or timestamps"}), 400

    # Gather all sensor arrays from the JSON payload
    sensor_data = {}
    for var in sensor_variables:
        sensor_data[var] = data.get(var)
        if sensor_data[var] is None:
            logger.error(f"Missing data for {var}")
            return jsonify({"status": "error", "message": f"Missing data for {var}"}), 400

    # Check all arrays have the same length
    data_length = len(timestamps)
    for var in sensor_variables:
        if len(sensor_data[var]) != data_length:
            logger.error("Mismatch in lengths of data arrays")
            return jsonify({"status": "error", "message": "Mismatch in lengths of data arrays"}), 400

    # Find the device in the database via the serial_number
    device = Device.query.filter_by(serial_number=device_serial_number).first()
    if not device:
        logger.error(f"Device with serial_number {device_serial_number} not found in the database")
        return jsonify({"status": "error", "message": "Device not found"}), 404

    # Prepare the DeviceData objects
    new_data_entries = []
    for i in range(data_length):
        new_entry = DeviceData(
            device_id=device.id,
            # The device might not have a 'patient_id' here, so leave it None or handle logic as needed
            patient_id=None,
            # A single request_timestamp used repeatedly, or adapt as needed
            request_timestamp=request_timestamps[i],
            time=timestamps[i],

            ax1=sensor_data['ax1'][i],
            ay1=sensor_data['ay1'][i],
            az1=sensor_data['az1'][i],

            ox1=sensor_data['ox1'][i],
            oy1=sensor_data['oy1'][i],
            oz1=sensor_data['oz1'][i],
            ow1=sensor_data['ow1'][i],

            ax2=sensor_data['ax2'][i],
            ay2=sensor_data['ay2'][i],
            az2=sensor_data['az2'][i],

            ox2=sensor_data['ox2'][i],
            oy2=sensor_data['oy2'][i],
            oz2=sensor_data['oz2'][i],
            ow2=sensor_data['ow2'][i],

            # If you wanted to pass something like test_name from the JSON, you could do:
            # test_name=data.get('test_name') or something
        )
        new_data_entries.append(new_entry)

    # Insert into DB
    try:
        db.session.bulk_save_objects(new_data_entries)
        db.session.commit()
        logger.info(f"Saved {len(new_data_entries)} data points for Device with serial_number {device_serial_number}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error when saving data: {str(e)}")
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

    return jsonify({"status": "success", "message": f"{len(new_data_entries)} data points received and saved"}), 200
