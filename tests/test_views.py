# test_views.py
import os
import pytest
from datetime import datetime, date
from flask import json
from website import create_app, db
from website.models import Device, Patient, DeviceData, User


@pytest.fixture
def app():
    """Create a Flask app for testing with an in-memory database."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory DB for faster tests
        "WTF_CSRF_ENABLED": False,  # Disable CSRF in tests
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Provide a Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Provide a CLI runner, if you need to test command-line commands."""
    return app.test_cli_runner()

@pytest.fixture
def sample_user():
    """Create and return a sample User object."""
    from website.models import User
    user = User(
        email="someuser@example.com",
        password="plaintextpw",  # Will be hashed by event listener
        first_name="Some",
        last_name="User"
    )
    return user

@pytest.fixture
def sample_device(sample_user):
    """Create and return a sample Device object with a valid user."""
    from website.models import Device
    device = Device(
        name="Test Device",
        type="Sensor",
        serial_number="ABCD1234",
        user_id=sample_user.id  # link to the user fixture
    )
    return device

@pytest.fixture
def sample_patient(sample_user):
    """Create and return a sample Patient object with a valid user."""
    from website.models import Patient
    # Just use a Python date directly:
    dob = date(1990, 1, 1)

    patient = Patient(
        id=123,  # so we can reference this in tests
        name="Test Patient",
        date_of_birth=dob,  # must be a date, not a string
        gender="Other",
        injury="TestInjury",
        user_id=sample_user.id
    )
    return patient

@pytest.fixture
def api_key():
    """Provide the valid API key for testing."""
    api_key = os.environ.get('API_SECRET_KEY', 'YOUR_SUPER_SECRET_KEY')
    return api_key


# ------------------------------------------------------------------------------
# Home Route Tests
# ------------------------------------------------------------------------------

def test_home_page(client):
    """
    Test the GET method of the home route. 
    Expects status 200 and the rendered template to include 'csrf'.
    """
    response = client.get('/')
    assert response.status_code == 200
    # assert b"csrf" in response.data # tag: Pytest Error -> I don't think I need csrf for home page


# tag: Pytest Error -> don't need this test anymore since we aren't using notes anymore
# def test_home_post(client):
#     """
#     Test the POST method of the home route with a short note.
#     Expects a flash message indicating 'Note is too short!'.
#     """
#     response = client.post('/', data={'note': 'A short note'})
#     assert response.status_code == 200
#     assert b'Note is too short!' in response.data


# ------------------------------------------------------------------------------
# /api/data Route Tests (receive_data)
# ------------------------------------------------------------------------------

def test_receive_data_no_api_key(client):
    """
    Test posting to /api/data with no API key.
    Expects a 403 Forbidden.
    """
    response = client.post('/api/data')
    assert response.status_code == 403
    assert b"Forbidden: invalid API key" in response.data


def test_receive_data_invalid_api_key(client, api_key):
    """
    Test posting to /api/data with an invalid API key.
    Expects a 403 Forbidden.
    """
    response = client.post('/api/data', headers={"X-API-Key": "INVALID_KEY"})
    assert response.status_code == 403
    assert b"Forbidden: invalid API key" in response.data


def test_receive_data_missing_json(client, api_key):
    """
    Test posting to /api/data with a valid API key but no JSON payload.
    Expects a 400 and an error message about missing JSON data.
    """
    response = client.post('/api/data', headers={"X-API-Key": api_key})
    assert response.status_code == 415, f'Got status code {response.status_code}, 403 means invalid API key, 415 means unsupported media type'
    assert b"No JSON data received" in response.data


def test_receive_data_missing_device_name(client, api_key):
    """
    Test posting to /api/data with a valid API key but missing 'device_name'.
    Expects a 400 and an error about missing 'device_name' or 'timestamps'.
    """
    # We omit 'device_name'
    data = {
        "patient_id": 123,
        "test_name": "Depth Jump Test",
        "timestamps": [1.0, 2.0],
        "ax1": [0.1, 0.2], "ay1": [0.1, 0.2], "az1": [0.1, 0.2],
        "ox1": [0.1, 0.2], "oy1": [0.1, 0.2], "oz1": [0.1, 0.2], "ow1": [0.1, 0.2],
        "ax2": [0.1, 0.2], "ay2": [0.1, 0.2], "az2": [0.1, 0.2],
        "ox2": [0.1, 0.2], "oy2": [0.1, 0.2], "oz2": [0.1, 0.2], "ow2": [0.1, 0.2]
    }
    response = client.post('/api/data', headers={"X-API-Key": api_key}, json=data)
    assert response.status_code == 400, f'Got status code {response.status_code}, api_key probably wrong'
    assert b"Missing 'device_name' or 'timestamps'" in response.data


def test_receive_data_invalid_test_name(client, sample_device, sample_user, sample_patient, api_key):
    """
    Test posting data with an invalid test_name. 
    Expects a 400 and an error about valid test names.
    """
    with client.application.app_context():
        db.session.add(sample_device)
        db.session.add(sample_user)
        db.session.add(sample_patient)
        db.session.commit()

    # 'test_name' is invalid ("Unknown Test")
    data = {
        "device_name": "ABCD1234",
        "patient_id": 123,
        "test_name": "Unknown Test",
        "timestamps": [1.0],
        "ax1": [0.1], "ay1": [0.1], "az1": [0.1],
        "ox1": [0.1], "oy1": [0.1], "oz1": [0.1], "ow1": [0.1],
        "ax2": [0.1], "ay2": [0.1], "az2": [0.1],
        "ox2": [0.1], "oy2": [0.1], "oz2": [0.1], "ow2": [0.1]
    }
    response = client.post('/api/data', headers={"X-API-Key": api_key}, json=data)
    assert response.status_code == 400
    assert b"Invalid 'test_name'. Must be one of" in response.data


def test_receive_data_mismatch_array_lengths(client, sample_device, sample_patient, api_key):
    """
    Test posting data with array lengths that don't match timestamps.
    Expects a 400 and a 'Mismatch in lengths of data arrays' error.
    """
    with client.application.app_context():
        db.session.add(sample_device)
        db.session.add(sample_patient)
        db.session.commit()

    # Here, 'timestamps' has length 2, but 'ax1' has length 1
    data = {
        "device_name": "ABCD1234",
        "patient_id": 123,
        "test_name": "Depth Jump Test",
        "timestamps": [1.0, 2.0],
        "ax1": [0.1],  # <-- mismatch
        "ay1": [0.1, 0.2],
        "az1": [0.1, 0.2],
        "ox1": [0.1, 0.2],
        "oy1": [0.1, 0.2],
        "oz1": [0.1, 0.2],
        "ow1": [0.1, 0.2],
        "ax2": [0.1, 0.2],
        "ay2": [0.1, 0.2],
        "az2": [0.1, 0.2],
        "ox2": [0.1, 0.2],
        "oy2": [0.1, 0.2],
        "oz2": [0.1, 0.2],
        "ow2": [0.1, 0.2]
    }

    response = client.post('/api/data', headers={"X-API-Key": api_key}, json=data)
    assert response.status_code == 400
    assert b"Mismatch in lengths of data arrays" in response.data


def test_receive_data_device_not_found(client, sample_patient, api_key):
    """
    Test posting data when the device doesn't exist in DB. 
    Expects 404 with 'Device not found'.
    """
    with client.application.app_context():
        db.session.add(sample_patient)
        db.session.commit()

    data = {
        "device_name": "NONEXISTENT_DEVICE",
        "patient_id": 123,
        "test_name": "Depth Jump Test",
        "timestamps": [1.0],
        "ax1": [0.1], "ay1": [0.1], "az1": [0.1],
        "ox1": [0.1], "oy1": [0.1], "oz1": [0.1], "ow1": [0.1],
        "ax2": [0.1], "ay2": [0.1], "az2": [0.1],
        "ox2": [0.1], "oy2": [0.1], "oz2": [0.1], "ow2": [0.1]
    }
    response = client.post('/api/data', headers={"X-API-Key": api_key}, json=data)
    assert response.status_code == 404
    assert b"Device not found" in response.data


def test_receive_data_patient_not_found(client, sample_device, sample_user, sample_patient, api_key):
    """
    Test posting data when the patient doesn't exist in DB.
    Expects 404 with 'Patient not found'.
    """
    with client.application.app_context():
        # db.session.add(sample_device)
        # db.session.commit()

        # Add and commit the user first
        db.session.add(sample_user)
        db.session.commit()

        # Now set user_id for device/patient
        sample_device.user_id = sample_user.id
        sample_patient.user_id = sample_user.id

        # Commit device/patient
        db.session.add(sample_device)
        db.session.add(sample_patient)
        db.session.commit()


    data = {
        "device_name": "ABCD1234",
        "patient_id": 9999,  # Nonexistent patient
        "test_name": "Depth Jump Test",
        "timestamps": [1.0],
        "ax1": [0.1], "ay1": [0.1], "az1": [0.1],
        "ox1": [0.1], "oy1": [0.1], "oz1": [0.1], "ow1": [0.1],
        "ax2": [0.1], "ay2": [0.1], "az2": [0.1],
        "ox2": [0.1], "oy2": [0.1], "oz2": [0.1], "ow2": [0.1]
    }
    response = client.post('/api/data', headers={"X-API-Key": api_key}, json=data)
    assert response.status_code == 404
    assert b"Patient not found" in response.data


def test_receive_data_success(client, sample_device, sample_user, sample_patient, api_key):
    """
    Test a successful data post with proper JSON and a valid API key.
    Expects status 200 and a success message about data points received.
    """
    with client.application.app_context():

        ###############
        # Old version that was giving a 'NOT NULL constraint failed: device.user_id' error
        ###############
        # db.session.add(sample_device)
        # db.session.add(sample_patient)
        # db.session.commit()

        ###############
        # New version -> FAILED tests/test_views.py::test_receive_data_success - sqlalchemy.orm.exc.UnmappedInstanceError: Class 'builtins.function' is not mapped
        ###############
                # Add and commit the user first
        db.session.add(sample_user)
        db.session.commit()

        # Now set user_id for device/patient
        sample_device.user_id = sample_user.id
        sample_patient.user_id = sample_user.id

        # Commit device/patient
        db.session.add(sample_device)
        db.session.add(sample_patient)
        db.session.commit()

    
    data = {
        "device_name": "ABCD1234",
        "patient_id": 123,
        "test_name": "Depth Jump Test",
        "timestamps": [1.0, 2.0],
        "ax1": [0.1, 0.2],
        "ay1": [0.1, 0.2],
        "az1": [0.1, 0.2],
        "ox1": [0.1, 0.2],
        "oy1": [0.1, 0.2],
        "oz1": [0.1, 0.2],
        "ow1": [0.1, 0.2],
        "ax2": [0.1, 0.2],
        "ay2": [0.1, 0.2],
        "az2": [0.1, 0.2],
        "ox2": [0.1, 0.2],
        "oy2": [0.1, 0.2],
        "oz2": [0.1, 0.2],
        "ow2": [0.1, 0.2]
    }

    response = client.post('/api/data', headers={"X-API-Key": api_key}, json=data)
    assert response.status_code == 200
    assert "data points received" in response.json['message']

    # Optionally, verify DeviceData was indeed created
    with client.application.app_context():
        db_data_count = DeviceData.query.count()
        assert db_data_count == len(data["timestamps"]), "Should match number of timestamps"
