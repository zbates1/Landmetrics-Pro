import logging
from flask import Blueprint, render_template, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from .models import Device, DeviceData
from . import db, csrf
import json
from datetime import datetime

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
@csrf.exempt  # Exempt the route from CSRF protection
def receive_data():
    data = request.get_json()

    # Check if the JSON payload is received
    if not data:
        logger.error("No JSON data received")
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    # Extract data from the request
    device_serial_number = data.get('device_name')  # Assuming device_name from the Arduino payload
    time_sent = data.get('time')  # The time column from your dataset

    # Ax1, Ay1, Az1, Gx1, Gy1, Gz1 for three sets of readings
    ax1, ay1, az1 = data.get('Ax1'), data.get('Ay1'), data.get('Az1')
    gx1, gy1, gz1 = data.get('Gx1'), data.get('Gy1'), data.get('Gz1')

    ax2, ay2, az2 = data.get('Ax2'), data.get('Ay2'), data.get('Az2')
    gx2, gy2, gz2 = data.get('Gx2'), data.get('Gy2'), data.get('Gz2')

    ax3, ay3, az3 = data.get('Ax3'), data.get('Ay3'), data.get('Az3')
    gx3, gy3, gz3 = data.get('Gx3'), data.get('Gy3'), data.get('Gz3')
    
    logger.info(f"Extracted data - device_serial_number: {device_serial_number}, time_sent: {time_sent}")
    logger.info(f"Ax1: {ax1}, Ay1: {ay1}, Az1: {az1}, Gx1: {gx1}, Gy1: {gy1}, Gz1: {gz1}")
    logger.info(f"Ax2: {ax2}, Ay2: {ay2}, Az2: {az2}, Gx2: {gx2}, Gy2: {gy2}, Gz2: {gz2}")
    logger.info(f"Ax3: {ax3}, Ay3: {ay3}, Az3: {az3}, Gx3: {gx3}, Gy3: {gy3}, Gz3: {gz3}")

    # Validate that all required fields are present
    required_fields = [
        device_serial_number, time_sent,
        ax1, ay1, az1, gx1, gy1, gz1,
        ax2, ay2, az2, gx2, gy2, gz2,
        ax3, ay3, az3, gx3, gy3, gz3
    ]

    if any(field is None for field in required_fields):
        logger.error("Missing data fields in the received JSON")
        return jsonify({"status": "error", "message": "Missing data fields"}), 400

    # Find the device in the database
    device = Device.query.filter_by(serial_number=device_serial_number).first()
    if not device:
        logger.error(f"Device with serial_number {device_serial_number} not found in the database")
        return jsonify({"status": "error", "message": "Device not found"}), 404

    # Create a new DeviceData entry
    new_data = DeviceData(
        device_id=device.id,
        time=time_sent,
        request_timestamp=datetime.utcnow(),
        ax1=ax1, ay1=ay1, az1=az1, gx1=gx1, gy1=gy1, gz1=gz1,
        ax2=ax2, ay2=ay2, az2=az2, gx2=gx2, gy2=gy2, gz2=gz2,
        ax3=ax3, ay3=ay3, az3=az3, gx3=gx3, gy3=gy3, gz3=gz3
    )

    try:
        db.session.add(new_data)
        db.session.commit()
        logger.info(f"Data saved for Device with serial_number {device_serial_number}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error when saving data for Device with serial_number {device_serial_number}: {str(e)}")
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

    return jsonify({"status": "success", "message": "Data received and saved"}), 200