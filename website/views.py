import logging
from flask import Blueprint, render_template, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from .models import Device, DeviceData
from . import db
import json
from flask_wtf.csrf import generate_csrf
# from flask_wtf.csrf import CSRFProtect, csrf_exempt
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

views = Blueprint('views', __name__)
csrf = CSRFProtect()

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

    return render_template("home.html", csrf=generate_csrf, user=current_user, DATABASE_URL=DATABASE_URL)

# Taking data from the Arduino ESP32
@views.route('/api/data', methods=['POST'])
@csrf.exempt
def receive_data():
    data = request.get_json()
    if not data:
        logger.error("No JSON data received")
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    # Extract data from the request
    device_serial_number = data.get('deviceId')  # Renamed variable
    ax = data.get('ax')
    ay = data.get('ay')
    az = data.get('az')
    gx = data.get('gx')
    gy = data.get('gy')
    gz = data.get('gz')

    logger.info(f"Received data from device_serial_number: {device_serial_number}")

    # Validate that all required fields are present
    if not all([
        device_serial_number,
        ax is not None,
        ay is not None,
        az is not None,
        gx is not None,
        gy is not None,
        gz is not None
    ]):
        logger.error("Missing data fields in the received JSON")
        return jsonify({"status": "error", "message": "Missing data fields"}), 400

    # Find the device in the database
    device = Device.query.filter_by(serial_number=device_serial_number).first()
    if not device:
        logger.error(f"Device with serial_number {device_serial_number} not found in the database")
        return jsonify({"status": "error", "message": "Device not found"}), 404

    # Create a new DeviceData entry
    new_data = DeviceData(
        device_id=device.id,  # Use the primary key here
        timestamp=datetime.utcnow(),
        ax=ax,
        ay=ay,
        az=az,
        gx=gx,
        gy=gy,
        gz=gz
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