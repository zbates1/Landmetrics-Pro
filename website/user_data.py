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


@data_view.route('/new_test', methods=['GET'])
@login_required
def new_test():
    patient_id = request.args.get('patient_id', type=int)
    # Logic to initiate a new test for this patient
    return "New test page placeholder"


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
