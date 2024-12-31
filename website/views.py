import logging
from flask import Blueprint, render_template, request, flash, jsonify, current_app, abort
from flask_login import login_required, current_user
from .models import Device, DeviceData, Patient
from . import db, csrf
import json
from datetime import datetime
import random
from functools import wraps
import os
from dotenv import load_dotenv


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


# ==========================
# API ROUTES LOAD API KEY
# ==========================

load_dotenv()  # Load environment variables from .env file if present
API_SECRET_KEY = os.environ.get('API_SECRET_KEY', 'YOUR_SUPER_SECRET_KEY')

def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if not provided_key or provided_key != API_SECRET_KEY:
            abort(403, description="Forbidden: invalid API key")
        return func(*args, **kwargs)
    return wrapper

# Taking data from the Arduino ESP32
@views.route('/api/data', methods=['POST'])
@csrf.exempt  # Only if intentionally exempt from CSRF checks
@require_api_key
# @limiter.limit("10/minute")  # e.g., override to 10 requests/min for this route -> tag: not working as I don't know how to import limiter from __init__.py, but it should apply the default rate limit to every route
def receive_data():
    """
    Receive JSON data for a device and a patient,
    create DeviceData entries for each data point.
    
    Now *requires* a valid 'test_name' chosen from:
      - "Depth Jump Test"
      - "3 Jump Test"
      - "Vertical Jump Test"

    Expected JSON structure (example):
    {
      "device_name": "ABCD1234",  # The device's serial_number
      "patient_id": 123,          # ID of the patient in the DB
      "test_name": "Depth Jump Test",
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

    # Required fields
    device_serial_number = data.get('device_name')
    patient_id_val = data.get('patient_id')
    test_name_val = data.get('test_name')
    timestamps = data.get('timestamps')

    # Validate 'device_name' or 'timestamps'
    if not device_serial_number or not timestamps:
        logger.error("Missing 'device_name' or 'timestamps' in the JSON")
        return jsonify({"status": "error", "message": "Missing 'device_name' or 'timestamps'"}), 400

    # Validate 'patient_id'
    if not patient_id_val:
        logger.error("Missing 'patient_id' in the JSON")
        return jsonify({"status": "error", "message": "Missing 'patient_id'"}), 400

    # Validate 'test_name'
    allowed_test_names = [
        "Depth Jump Test",
        "3 Jump Test",
        "Vertical Jump Test"
    ]
    if not test_name_val:
        logger.error("Missing 'test_name' in the JSON")
        return jsonify({"status": "error", "message": "Missing 'test_name'"}), 400
    if test_name_val not in allowed_test_names:
        logger.error(f"Invalid 'test_name' provided: {test_name_val}")
        return jsonify({"status": "error", "message": f"Invalid 'test_name'. Must be one of: {allowed_test_names}"}), 400

    # Retrieve Device and Patient from the DB
    device = Device.query.filter_by(serial_number=device_serial_number).first()
    if not device:
        logger.error(f"Device with serial_number {device_serial_number} not found.")
        return jsonify({"status": "error", "message": "Device not found"}), 404

    from .models import Patient  # Ensure Patient is imported if in a different module
    patient = Patient.query.filter_by(id=patient_id_val).first()
    if not patient:
        logger.error(f"Patient with id {patient_id_val} not found.")
        return jsonify({"status": "error", "message": "Patient not found"}), 404

    # Prepare sensor fields
    sensor_variables = [
        'ax1', 'ay1', 'az1', 'ox1', 'oy1', 'oz1', 'ow1',
        'ax2', 'ay2', 'az2', 'ox2', 'oy2', 'oz2', 'ow2'
    ]

    # Gather sensor arrays
    sensor_data = {}
    for var in sensor_variables:
        sensor_data[var] = data.get(var)
        if sensor_data[var] is None:
            logger.error(f"Missing data for {var}")
            return jsonify({"status": "error", "message": f"Missing data for {var}"}), 400

    # Check all arrays match length of 'timestamps'
    data_length = len(timestamps)
    for var in sensor_variables:
        if len(sensor_data[var]) != data_length:
            logger.error("Mismatch in lengths of data arrays")
            return jsonify({"status": "error", "message": "Mismatch in lengths of data arrays"}), 400

    # Create a request_timestamp for each data point
    # request_timestamps = [datetime.utcnow() for _ in range(data_length)]
    request_timestamps = [datetime.utcnow().replace(microsecond=0) for _ in range(data_length)]


    new_data_entries = []
    for i in range(data_length):
        new_entry = DeviceData(
            device_id=device.id,
            patient_id=patient.id,
            test_name=test_name_val,            # set the test_name
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
            ow2=sensor_data['ow2'][i]
        )
        new_data_entries.append(new_entry)

    try:
        db.session.bulk_save_objects(new_data_entries)
        db.session.commit()
        logger.info(f"Saved {len(new_data_entries)} data points for Device({device_serial_number}), "
                    f"Patient({patient_id_val}), Test({test_name_val}).")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error when saving data: {str(e)}")
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

    return jsonify({
        "status": "success",
        "message": f"{len(new_data_entries)} data points received "
                   f"and saved for device {device_serial_number}, "
                   f"patient {patient_id_val}, "
                   f"test_name '{test_name_val}'."
    }), 200
