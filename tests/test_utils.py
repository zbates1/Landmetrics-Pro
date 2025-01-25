# test_utils.py

import pytest
from datetime import datetime
from werkzeug.security import check_password_hash
from website import create_app, db
from website.models import User, Device, DeviceData, Patient
from website.db_utils import (
    add_user,
    add_device,
    add_device_data,
    list_users,
    list_devices_for_user,
    list_all_devices,
    find_user_by_email,
    find_patient_by_id,
    find_patient_by_name,
    list_all_patients,
    find_tests_by_patient_id,
    find_data_by_patient_id,
    find_unique_request_timestamps_by_patient_id,
    find_patient_data_by_id_and_timestamp
)

@pytest.fixture
def app():
    """Provide a Flask app configured for testing, 
    and create/destroy an in-memory database around each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # In-memory DB
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_client(app):
    """Flask test client for sending requests if needed."""
    return app.test_client()

# ------------------------------------------------------------------------------
# Example Tests for db_utils.py
# ------------------------------------------------------------------------------

def test_add_user(app, capsys):
    """Test that add_user creates a User in the DB and prints expected output."""
    with app.app_context():
        # Verify no users in DB initially
        assert User.query.count() == 0, f'There are {User.query.count()} users in DB, instead of 0, as expected.'
        
        add_user("test_user@example.com", "password123", "TestUser")
        captured = capsys.readouterr()
        
        # Check console output
        # assert "User test_user@example.com added successfully!" in captured.out, f''
        
        # Verify user in DB
        user = User.query.filter_by(email="test_user@example.com").first()
        assert user is not None, f'User with email "test_user@example.com" not found in DB.'
        assert user.first_name == "TestUser", f'User with email "test_user@example.com" has name {user.first_name} instead of "TestUser".'
        # Check that the password is hashed
        assert user.password != "password123", f'User with email "test_user@example.com" has password {user.password} instead of "password123".'
        assert check_password_hash(user.password, "password123"), f'User with email "test_user@example.com" password is not hashed.'


def test_add_device(app, capsys):
    """Test that add_device creates a Device and prints expected output."""
    with app.app_context():
        # Create a user first
        user = User(email="owner@example.com", password="secret", first_name="Owner")
        db.session.add(user)
        db.session.commit()

        # Add a device under that user
        add_device("MyDevice", "Sensor", "SN-0001", user.id)
        captured = capsys.readouterr()
        
        # Check console output
        assert "Device MyDevice added successfully for User owner@example.com!" in captured.out

        # Verify device in DB
        device = Device.query.filter_by(serial_number="SN-0001").first()
        assert device is not None
        assert device.name == "MyDevice"
        assert device.owner.email == "owner@example.com"


def test_add_device_data(app, capsys):
    """Test that add_device_data creates a DeviceData entry when device exists."""
    with app.app_context():
        # Create user and device
        user = User(email="sensor@example.com", password="pwd", first_name="SensorUser")
        device = Device(name="Sensor1", type="TestType", serial_number="SN-XYZ", user_id=1)
        db.session.add(user)
        db.session.add(device)
        db.session.commit()

        # Add device data
        add_device_data(
            serial_number="SN-XYZ",
            time=123.45,
            ax1=0.1, ay1=0.1, az1=0.1, ox1=0.1, oy1=0.1, oz1=0.1, ow1=0.1,
            ax2=0.2, ay2=0.2, az2=0.2, ox2=0.2, oy2=0.2, oz2=0.2, ow2=0.2,
            test_name="JumpTest"
        )
        captured = capsys.readouterr()
        
        # Check console output
        assert "Data for Device SN-XYZ added successfully!" in captured.out

        # Verify DeviceData in DB
        dev_data = DeviceData.query.first()
        assert dev_data is not None
        assert dev_data.device_id == device.id
        assert dev_data.time == 123.45
        assert dev_data.test_name == "JumpTest"

def test_list_users(app, capsys):
    """Test that list_users prints out all users in the console."""
    with app.app_context():
        # Create a couple users
        user1 = User(email="user1@example.com", password="pwd", first_name="User1")
        user2 = User(email="user2@example.com", password="pwd", first_name="User2")
        db.session.add_all([user1, user2])
        db.session.commit()

        list_users()
        captured = capsys.readouterr()
        
        # Verify console output has user details
        assert "user1@example.com" in captured.out
        assert "user2@example.com" in captured.out


def test_list_devices_for_user(app, capsys):
    """Test that list_devices_for_user prints devices belonging to a user."""
    with app.app_context():
        user = User(email="deviceowner@example.com", password="pwd", first_name="Owner")
        db.session.add(user)
        db.session.commit()

        # Add devices for this user
        dev1 = Device(name="DevA", type="Sensor", serial_number="A1", user_id=user.id)
        dev2 = Device(name="DevB", type="Sensor", serial_number="B2", user_id=user.id)
        db.session.add_all([dev1, dev2])
        db.session.commit()

        list_devices_for_user(user.id)
        captured = capsys.readouterr()
        
        # Verify console output
        assert "DevA" in captured.out
        assert "DevB" in captured.out
        assert "Owner" in captured.out  # Should mention the user's first_name


def test_list_all_devices(app, capsys):
    """Test that list_all_devices prints all devices in the DB."""
    with app.app_context():
        user = User(email="alist@example.com", password="pwd", first_name="ListAll")
        db.session.add(user)
        db.session.commit()

        dev1 = Device(name="DevA", type="Sensor", serial_number="A1", user_id=user.id)
        dev2 = Device(name="DevB", type="Monitor", serial_number="B2", user_id=user.id)
        db.session.add_all([dev1, dev2])
        db.session.commit()

        list_all_devices()
        captured = capsys.readouterr()
        # Verify console output has device names/types, and user email
        assert "DevA" in captured.out
        assert "Sensor" in captured.out
        assert "DevB" in captured.out
        assert "Monitor" in captured.out
        assert "alist@example.com" in captured.out


def test_find_user_by_email(app, capsys):
    """Test that find_user_by_email prints details of the matching user."""
    with app.app_context():
        user = User(email="search@example.com", password="pwd", first_name="Searcher")
        db.session.add(user)
        db.session.commit()

        find_user_by_email("search@example.com")
        captured = capsys.readouterr()
        assert "User found: Searcher" in captured.out

        # Non-existing email
        find_user_by_email("notfound@example.com")
        captured = capsys.readouterr()
        assert "No user found with email notfound@example.com" in captured.out


def test_find_patient_by_id(app, capsys):
    """Test that find_patient_by_id prints patient details if found."""
    with app.app_context():
        user = User(email="provider@example.com", password="pwd")
        db.session.add(user)
        db.session.commit()

        patient = Patient(name="Test Patient", date_of_birth=datetime(1990, 1, 1), gender="Other", user_id=user.id)
        db.session.add(patient)
        db.session.commit()

        find_patient_by_id(patient.id)
        captured = capsys.readouterr()
        assert "Test Patient" in captured.out
        assert "provider@example.com" in captured.out


def test_find_patient_by_name(app, capsys):
    """Test that find_patient_by_name prints patients whose name matches."""
    with app.app_context():
        user = User(email="provider2@example.com", password="pwd")
        db.session.add(user)
        db.session.commit()

        # Add multiple patients
        p1 = Patient(name="Alice Wonderland", date_of_birth=datetime(1990, 1, 1), gender="Female", user_id=user.id)
        p2 = Patient(name="Alicia Keys", date_of_birth=datetime(1980, 2, 2), gender="Female", user_id=user.id)
        p3 = Patient(name="Bob Marley", date_of_birth=datetime(1975, 3, 3), gender="Male", user_id=user.id)
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        find_patient_by_name("Alic")
        captured = capsys.readouterr()
        
        # We should see both Alice and Alicia
        assert "Alice Wonderland" in captured.out
        assert "Alicia Keys" in captured.out
        # Should NOT see Bob
        assert "Bob Marley" not in captured.out


def test_list_all_patients(app, capsys):
    """Test that list_all_patients prints out all patients in the DB."""
    with app.app_context():
        user = User(email="doc@example.com", password="pwd")
        db.session.add(user)
        db.session.commit()

        p1 = Patient(name="PatientOne", date_of_birth=datetime(1990, 1, 1), gender="Female", user_id=user.id)
        p2 = Patient(name="PatientTwo", date_of_birth=datetime(1991, 2, 2), gender="Male", user_id=user.id)
        db.session.add_all([p1, p2])
        db.session.commit()

        list_all_patients()
        captured = capsys.readouterr()
        assert "PatientOne" in captured.out
        assert "PatientTwo" in captured.out


def test_find_tests_by_patient_id(app, capsys):
    """Test that find_tests_by_patient_id prints all DeviceData (tests) for a patient."""
    with app.app_context():
        user = User(email="tester@example.com", password="pwd")
        db.session.add(user)
        db.session.commit()

        patient = Patient(name="Testy McTestface", date_of_birth=datetime(1995, 4, 4), gender="Unknown", user_id=user.id)
        db.session.add(patient)
        db.session.commit()

        device = Device(name="TesterDevice", type="Sensor", serial_number="TD-01", user_id=user.id)
        db.session.add(device)
        db.session.commit()

        # Add 2 data points (both with test_name set)
        d1 = DeviceData(device_id=device.id, patient_id=patient.id, test_name="JumpTest1", time=1.1)
        d2 = DeviceData(device_id=device.id, patient_id=patient.id, test_name="JumpTest2", time=2.2)
        db.session.add_all([d1, d2])
        db.session.commit()

        find_tests_by_patient_id(patient.id)
        captured = capsys.readouterr()
        assert "JumpTest1" in captured.out
        assert "JumpTest2" in captured.out


def test_find_data_by_patient_id(app, capsys):
    """Test that find_data_by_patient_id prints all DeviceData for a patient."""
    with app.app_context():
        user = User(email="tester2@example.com", password="pwd")
        db.session.add(user)
        db.session.commit()

        patient = Patient(name="Data Searcher", date_of_birth=datetime(2000, 5, 5), gender="Female", user_id=user.id)
        db.session.add(patient)
        db.session.commit()

        device = Device(name="DataDevice", type="Sensor", serial_number="DD-01", user_id=user.id)
        db.session.add(device)
        db.session.commit()

        d1 = DeviceData(device_id=device.id, patient_id=patient.id, test_name="DataTest1", time=1.1)
        db.session.add(d1)
        db.session.commit()

        find_data_by_patient_id(patient.id)
        captured = capsys.readouterr()
        assert "Data points for patient Data Searcher" in captured.out
        assert "DeviceData ID: 1, Request Timestamp:" in captured.out


def test_find_unique_request_timestamps_by_patient_id(app, capsys):
    """Test that find_unique_request_timestamps_by_patient_id prints unique timestamps."""
    with app.app_context():
        user = User(email="ts_user@example.com", password="pwd")
        db.session.add(user)
        db.session.commit()

        patient = Patient(name="TimestampCheck", date_of_birth=datetime(1999, 9, 9), gender="Non-binary", user_id=user.id)
        db.session.add(patient)
        db.session.commit()

        device = Device(name="TSDevice", type="Sensor", serial_number="TS-01", user_id=user.id)
        db.session.add(device)
        db.session.commit()

        # Add multiple data points with duplicates
        tstamp = datetime(2025, 1, 1, 12, 0, 0)
        d1 = DeviceData(device_id=device.id, patient_id=patient.id, request_timestamp=tstamp, time=1.0)
        d2 = DeviceData(device_id=device.id, patient_id=patient.id, request_timestamp=tstamp, time=2.0)
        d3 = DeviceData(device_id=device.id, patient_id=patient.id, request_timestamp=tstamp.replace(minute=1), time=3.0)
        db.session.add_all([d1, d2, d3])
        db.session.commit()

        find_unique_request_timestamps_by_patient_id(patient.id)
        captured = capsys.readouterr()

        # We expect 2 unique timestamps printed
        assert "Found 2 unique timestamp(s)." in captured.out
        assert "2025-01-01 12:00:00" in captured.out
        assert "2025-01-01 12:01:00" in captured.out


def test_find_patient_data_by_id_and_timestamp(app, capsys):
    """Test that find_patient_data_by_id_and_timestamp prints matching data points."""
    with app.app_context():
        user = User(email="searchts@example.com", password="pwd")
        db.session.add(user)
        db.session.commit()

        patient = Patient(name="TimestampSearch", date_of_birth=datetime(1992, 3, 3), gender="F", user_id=user.id)
        db.session.add(patient)
        db.session.commit()

        device = Device(name="FinderDevice", type="Sensor", serial_number="FD-01", user_id=user.id)
        db.session.add(device)
        db.session.commit()

        tstamp = datetime(2030, 5, 5, 10, 30, 0)
        d1 = DeviceData(
            device_id=device.id,
            patient_id=patient.id,
            request_timestamp=tstamp,
            time=10.5
        )
        db.session.add(d1)
        db.session.commit()

        # Now call the function
        find_patient_data_by_id_and_timestamp(patient.id, "2030-05-05 10:30:00")
        captured = capsys.readouterr()

        # Check console output
        assert "Querying for patient_id=1 and request_timestamp=2030-05-05 10:30:00" in captured.out
        # Confirm the record is found
        assert "Length of data_points for patient TimestampSearch (ID: 1) and request_timestamp 2030-05-05 10:30:00: 1" in captured.out

        # Try a timestamp that doesn't match
        find_patient_data_by_id_and_timestamp(patient.id, "2030-05-05 10:31:00")
        captured = capsys.readouterr()
        assert "No data points found for patient TimestampSearch" in captured.out
