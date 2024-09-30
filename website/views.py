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
@csrf.exempt
def receive_data():
    data = request.get_json()

    # Check if the JSON payload is received
    if not data:
        logger.error("No JSON data received")
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    device_serial_number = data.get('device_name')
    timestamps = data.get('timestamps')

    # List of all sensor variables
    sensor_variables = [
        'Ax1', 'Ay1', 'Az1', 'Gx1', 'Gy1', 'Gz1',
        'Ax2', 'Ay2', 'Az2', 'Gx2', 'Gy2', 'Gz2',
        'Ax3', 'Ay3', 'Az3', 'Gx3', 'Gy3', 'Gz3'
    ]

    # Ensure all required data is present
    if not device_serial_number or not timestamps:
        logger.error("Missing device_name or timestamps in the received JSON")
        return jsonify({"status": "error", "message": "Missing device_name or timestamps"}), 400

    sensor_data = {}
    for var in sensor_variables:
        sensor_data[var] = data.get(var)
        if sensor_data[var] is None:
            logger.error(f"Missing data for {var}")
            return jsonify({"status": "error", "message": f"Missing data for {var}"}), 400

    # Check that all arrays are the same length
    data_length = len(timestamps)
    if any(len(sensor_data[var]) != data_length for var in sensor_variables):
        logger.error("Mismatch in lengths of data arrays")
        return jsonify({"status": "error", "message": "Mismatch in lengths of data arrays"}), 400

    # Find the device in the database
    device = Device.query.filter_by(serial_number=device_serial_number).first()
    if not device:
        logger.error(f"Device with serial_number {device_serial_number} not found in the database")
        return jsonify({"status": "error", "message": "Device not found"}), 404

    # Prepare data entries
    new_data_entries = []
    for i in range(data_length):
        new_data = DeviceData(
            device_id=device.id,
            time=timestamps[i],
            # request_timestamp=datetime.utcnow(),
            # replace request_timestamp with random string, 15 characters
            request_timestamp=''.join([str(random.randint(0, 9)) for _ in range(15)]),
            ax1=sensor_data['Ax1'][i], ay1=sensor_data['Ay1'][i], az1=sensor_data['Az1'][i],
            gx1=sensor_data['Gx1'][i], gy1=sensor_data['Gy1'][i], gz1=sensor_data['Gz1'][i],
            ax2=sensor_data['Ax2'][i], ay2=sensor_data['Ay2'][i], az2=sensor_data['Az2'][i],
            gx2=sensor_data['Gx2'][i], gy2=sensor_data['Gy2'][i], gz2=sensor_data['Gz2'][i],
            ax3=sensor_data['Ax3'][i], ay3=sensor_data['Ay3'][i], az3=sensor_data['Az3'][i],
            gx3=sensor_data['Gx3'][i], gy3=sensor_data['Gy3'][i], gz3=sensor_data['Gz3'][i]
        )
        new_data_entries.append(new_data)

    # Bulk insert all data entries
    try:
        db.session.bulk_save_objects(new_data_entries)
        db.session.commit()
        logger.info(f"Saved {len(new_data_entries)} data points for Device with serial_number {device_serial_number}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error when saving data: {str(e)}")
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

    return jsonify({"status": "success", "message": f"{len(new_data_entries)} data points received and saved"}), 200