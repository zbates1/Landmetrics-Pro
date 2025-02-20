"""
This module defines the routes and functions related to user data visualization,
incorporating patient selection and updated schema changes.
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from . import db
from .models import User, Device, DeviceData, Patient, PatientNotes
from datetime import datetime
import json
import paho.mqtt.client as mqtt
import queue
import psycopg2


from flask_wtf.csrf import generate_csrf

# Use your new function from db_utils
try:
    from .db_utils import find_patient_data_by_id_and_timestamp
except ImportError:
    from website.db_utils import find_patient_data_by_id_and_timestamp  # Absolute import for script execution


# Initialize the blueprint
data_view = Blueprint('data_view', __name__)

# Set up logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

################################
# MQTT Functions -> it seems like the MQTT functions are mostly not used by me and could be modules, except the handle_incoming_data
################################

# ----------------------------------------------------------------------------
# HiveMQ Cloud broker details
BROKER_URL = "6b53960d5ee44dbf8e50b63d29b4bfa1.s1.eu.hivemq.cloud"
BROKER_PORT = 8883  # Secure TLS port
USERNAME = "Landmetrics"  # Replace if needed
PASSWORD = "TestTest1"    # Replace if needed

# Configure the device you're targeting (if only handling one device for now)
currentDevice = "device1"

# ----------------------------------------------------------------------------
# DONT THINK I NEED THIS THIS BECAUSE OF SQLALCHEMY -> I DO ACTUALLY NEED THIS

# PostgreSQL connection details
# Make sure these match your actual DB credentials / host / port:
# db_conn = psycopg2.connect(
#     dbname="your_database",
#     user="your_username",
#     password="your_password",
#     host="your_host",
#     port="your_port"
# )

# db_cursor = db_conn.cursor()

# ----------------------------------------------------------------------------
# Queue to store incoming MQTT messages
message_queue = queue.Queue()

# Dictionary to store data and statuses for multiple devices
device_data = {}
device_status = {}

# ----------------------------------------------------------------------------
# MQTT callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to HiveMQ!")
        # Subscribe to the data topic for the given device
        topic = f"device/{currentDevice}/data"
        client.subscribe(topic)
        print(f"Subscribed to: {topic}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode()
        message_queue.put((msg.topic, payload_str))  # Add (topic, payload) to queue
    except Exception as e:
        print(f"Error processing message payload: {e}")

# ----------------------------------------------------------------------------
# Worker function: processes messages from the queue
def process_messages():
    while True:
        try:
            topic, payload_str = message_queue.get(timeout=1)
            topic_parts = topic.split('/')
            # Expect something like ["device", "<device_id>", "data"]
            if len(topic_parts) == 3 and topic_parts[2] == "data":
                handle_incoming_data(payload_str)
        except queue.Empty:
            continue

# ----------------------------------------------------------------------------
def handle_incoming_data(payload_str):
    """
    Parse incoming JSON data and insert into the database,
    following the validation logic of your existing HTTP endpoint.

    NEEDS TO BE CHANGED TO CSV!!!!!!!!!!!!!!!!!!!!!!!!
    """

    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError:
        print("Invalid JSON payload received.")
        return

    # Required fields
    device_serial_number = data.get('device_name')
    patient_id_val       = data.get('patient_id')
    test_name_val        = data.get('test_name')
    timestamps           = data.get('timestamps')

    # Validate required fields
    if not device_serial_number or not timestamps:
        print("Missing 'device_name' or 'timestamps' in the JSON")
        return

    if not patient_id_val:
        print("Missing 'patient_id' in the JSON")
        return

    # Validate 'test_name'
    allowed_test_names = [
        "Depth Jump Test",
        "3 Jump Test",
        "Vertical Jump Test"
    ]
    if not test_name_val:
        print("Missing 'test_name' in the JSON")
        return
    if test_name_val not in allowed_test_names:
        print(f"Invalid 'test_name' provided: {test_name_val}")
        return

    # Gather sensor arrays
    sensor_variables = [
        'ax1', 'ay1', 'az1', 'ox1', 'oy1', 'oz1', 'ow1',
        'ax2', 'ay2', 'az2', 'ox2', 'oy2', 'oz2', 'ow2'
    ]
    sensor_data = {}
    for var in sensor_variables:
        sensor_data[var] = data.get(var)
        if sensor_data[var] is None:
            print(f"Missing data for {var}")
            return

    # Verify lengths match
    data_length = len(timestamps)
    for var in sensor_variables:
        if len(sensor_data[var]) != data_length:
            print("Mismatch in lengths of data arrays.")
            return

    # Insert each data point into the DB
    # (Adapt column names / table name to your actual schema)
    # The original code used "DeviceData(...)" from SQLAlchemy; here we’ll do direct inserts.
    try:
        for i in range(data_length):
            # Insert row
            # request_timestamp (UTC) like in your original code
            request_timestamp = datetime.utcnow().replace(microsecond=0) # THIS SHOULD BE MOVED OUTSIDE THE FOR LOOP SO THERE IS ONE FOR EVERY TEST

            insert_sql = """
                INSERT INTO device_data (
                    device_name,
                    patient_id,
                    test_name,
                    request_timestamp,
                    time,
                    ax1, ay1, az1,
                    ox1, oy1, oz1, ow1,
                    ax2, ay2, az2,
                    ox2, oy2, oz2, ow2
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s
                )
            """

            db_cursor.execute(
                insert_sql,
                (
                    device_serial_number,
                    patient_id_val,
                    test_name_val,
                    request_timestamp,
                    timestamps[i],
                    sensor_data['ax1'][i],
                    sensor_data['ay1'][i],
                    sensor_data['az1'][i],
                    sensor_data['ox1'][i],
                    sensor_data['oy1'][i],
                    sensor_data['oz1'][i],
                    sensor_data['ow1'][i],
                    sensor_data['ax2'][i],
                    sensor_data['ay2'][i],
                    sensor_data['az2'][i],
                    sensor_data['ox2'][i],
                    sensor_data['oy2'][i],
                    sensor_data['oz2'][i],
                    sensor_data['ow2'][i]
                )
            )

        db_conn.commit()
        print(f"Saved {data_length} data points for device={device_serial_number}, "
              f"patient={patient_id_val}, test={test_name_val}.")
    except Exception as e:
        db_conn.rollback()
        print(f"Database error when saving data: {e}")

# ----------------------------------------------------------------------------
# Start the background thread for processing MQTT messages
threading.Thread(target=process_messages, daemon=True).start()

# ----------------------------------------------------------------------------
# Initialize MQTT client
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_URL, BROKER_PORT)
client.loop_start()

# ----------------------------------------------------------------------------


def build_data_dict(data_points):
    """
    Given a list of DeviceData points, build a dictionary with
    timestamps and sensor arrays for Chart.js or other visualization.
    """
    if not data_points:
        return {}

    data_dict = {
        'timestamps': [],
        'request_timestamp': [],
        'test_name': [],
        'ax1': [], 'ay1': [], 'az1': [], 'ox1': [], 'oy1': [], 'oz1': [], 'ow1': [],
        'ax2': [], 'ay2': [], 'az2': [], 'ox2': [], 'oy2': [], 'oz2': [], 'ow2': []
    }

    for dp in data_points:
        # Convert dp.time (float) to a readable string
        timestamp_str = datetime.fromtimestamp(dp.time).strftime('%Y-%m-%d %H:%M:%S')
        data_dict['timestamps'].append(timestamp_str)
        data_dict['request_timestamp'].append(dp.request_timestamp)
        data_dict['test_name'].append(dp.test_name)
        data_dict['ax1'].append(dp.ax1)
        data_dict['ay1'].append(dp.ay1)
        data_dict['az1'].append(dp.az1)
        data_dict['ox1'].append(dp.ox1)
        data_dict['oy1'].append(dp.oy1)
        data_dict['oz1'].append(dp.oz1)
        data_dict['ow1'].append(dp.ow1)
        data_dict['ax2'].append(dp.ax2)
        data_dict['ay2'].append(dp.ay2)
        data_dict['az2'].append(dp.az2)
        data_dict['ox2'].append(dp.ox2)
        data_dict['oy2'].append(dp.oy2)
        data_dict['oz2'].append(dp.oz2)
        data_dict['ow2'].append(dp.ow2)

    return data_dict


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
    return "View tests page placeholder"


################################
# MQTT ROUTES
################################

@data_view.route('/new_test', methods=['GET'])
@login_required
def new_test():
    patient_id = request.args.get('patient_id', type=int)
    # Logic to initiate a new test for this patient
    return "New test page placeholder"

@data_view.route("/stream_data")
def stream_data():
    # Return the latest data for the current device
    return jsonify([device_data.get(currentDevice, "No data available")])

@data_view.route("/get_device_status", methods=["GET"])
def get_device_status():
    # Return the latest status for the current device
    return jsonify(device_status.get(currentDevice, "No status available"))

@data_view.route("/start_test", methods=["POST"])
def start_test():
    # Publish "start" command to the MQTT control topic
    topic = f"device/{currentDevice}/control"
    client.publish(topic, "start")
    return jsonify({"status": "success", "message": "Start command sent."})

@data_view.route("/stop_test", methods=["POST"])
def stop_test():
    # Publish "stop" command to the MQTT control topic
    topic = f"device/{currentDevice}/control"
    client.publish(topic, "stop")
    return jsonify({"status": "success", "message": "Stop command sent."})


################################
# MQTT ROUTES
################################

@data_view.route('/user_data', methods=['GET', 'POST'])
@login_required
def user_data():
    """
    Main route for visualizing patient data.
    """
    try:
        # Get all patients for the current user
        patients = Patient.query.filter_by(user_id=current_user.id).all()

        # Initialize notes to an empty list
        notes = []

        # Get the currently selected patient
        selected_patient_id = request.args.get('patient_id', type=int)
        current_patient_name = None
        if selected_patient_id:
            patient = Patient.query.filter_by(
                id=selected_patient_id,
                user_id=current_user.id
            ).first()

            # Load existing notes (descending by date_created)
            notes = PatientNotes.query.filter_by(patient_id=selected_patient_id)\
                                      .order_by(PatientNotes.date_created.desc())\
                                      .all()

            if not patient:
                flash("Selected patient not found or does not belong to you.", category='error')
                return redirect(url_for('data_view.user_data'))
            current_patient_name = patient.name

        # ===============================
        # Handle POST => Add Patient Note
        # ===============================
        if request.method == 'POST' and request.form.get('note'):
            note_data = request.form.get('note')
            new_note = PatientNotes(
                note=note_data,
                user_id=current_user.id,
                patient_id=selected_patient_id
            )
            db.session.add(new_note)
            db.session.commit()

            # Return JSON to let our JavaScript add the new note without refreshing
            # IMPORTANT: Include "id" in the returned JSON
            return jsonify({
                'status': 'success',
                'message': 'Note added successfully',
                'new_note': {
                    'id': new_note.id,  # <--- ADD THIS LINE
                    'date_created': new_note.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                    'note': new_note.note
                }
            })

        # (Optional) Device logic you already have
        devices_query = Device.query.filter_by(user_id=current_user.id).all()
        devices = [{'id': dev.id, 'name': dev.name} for dev in devices_query]

        selected_device_id = request.args.get('device_id', type=int)
        selected_request_timestamp = request.args.get('request_timestamp')

        device_data = {}
        request_timestamps = []

        # If a patient is selected, gather timestamps + data
        if selected_patient_id:
            # Distinct timestamps
            request_timestamps_query = (
                db.session.query(DeviceData.request_timestamp)
                .filter_by(patient_id=selected_patient_id)
                .distinct()
                .order_by(DeviceData.request_timestamp)
                .all()
            )
            request_timestamps = [
                rt[0].strftime('%Y-%m-%d %H:%M:%S')
                for rt in request_timestamps_query
                if rt[0]
            ]

            # Get DeviceData for the selected request_timestamp (if any)
            data_points = None
            if selected_request_timestamp:
                data_points = find_patient_data_by_id_and_timestamp(
                    selected_patient_id,
                    selected_request_timestamp
                )

            # Build a data dict from data_points
            data_dict = build_data_dict(data_points) if data_points else {}

            if data_dict:
                # Key by patient_id (or device_id) as needed
                device_data[selected_patient_id] = data_dict
            else:
                # If no data returned, flash an error if request_timestamp was specified
                if selected_request_timestamp:
                    flash("No data available for the selected patient and session.", category='error')
                device_data[selected_patient_id] = {}

        # Normal GET => Render template
        return render_template(
            "user_data2.html",
            devices=devices,
            selected_device_id=selected_device_id,
            request_timestamps=request_timestamps,
            selected_request_timestamp=selected_request_timestamp,
            device_data=device_data,
            user=current_user,
            patients=patients,
            selected_patient_id=selected_patient_id if selected_patient_id else None,
            current_patient_name=current_patient_name,
            csrf=generate_csrf(),  # for the add_patient endpoint if needed
            notes=notes
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        flash("An error occurred while loading your data.", category='error')
        return redirect(url_for('views.home'))

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        flash("An unexpected error occurred.", category='error')
        return redirect(url_for('views.home'))

@data_view.route('/delete_note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    """
    Deletes the note with the given note_id if it belongs to the current user.
    Returns JSON with success/failure message.
    """
    # Find the note in the database
    note_to_delete = PatientNotes.query.filter_by(id=note_id, user_id=current_user.id).first()
    if not note_to_delete:
        return jsonify({'status': 'error', 'message': 'Note not found or not yours.'}), 404
    
    # If found, delete it
    db.session.delete(note_to_delete)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Note deleted successfully.'}), 200
