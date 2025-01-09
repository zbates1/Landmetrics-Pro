# test_models.py

import pytest
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from website import create_app, db
from website.models import (
    User,
    Patient,
    PatientNotes,
    Device,
    DeviceData
)


@pytest.fixture
def app():
    """
    Provide a Flask app configured for testing.
    Uses an in-memory database to avoid altering real data.
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_client(app):
    """Provide a test client for the Flask app if route testing is needed."""
    return app.test_client()


# ------------------------------------------------------------------------------
# User Model Tests
# ------------------------------------------------------------------------------

def test_create_user(app):
    """
    Test that a User can be created and saved to the DB, ensuring that:
    - The saved record is retrieved correctly.
    - Passwords are hashed.
    """
    with app.app_context():
        user = User(
            email="test@example.com",
            password="plaintext_password",
            first_name="John",
            last_name="Doe",
        )
        db.session.add(user)
        db.session.commit()

        saved_user = User.query.filter_by(email="test@example.com").first()

        assert saved_user is not None
        assert saved_user.email == "test@example.com"
        # Check that the password is indeed hashed.
        assert saved_user.password != "plaintext_password"
        assert check_password_hash(saved_user.password, "plaintext_password")


def test_create_duplicate_user_email(app):
    """
    Test that creating two Users with the same email 
    raises an IntegrityError due to the unique constraint.
    """
    with app.app_context():
        # First user
        user1 = User(
            email="duplicate@example.com",
            password="testpass",
            first_name="First",
            last_name="User",
        )
        db.session.add(user1)
        db.session.commit()

        # Second user with the same email
        user2 = User(
            email="duplicate@example.com",
            password="anotherpass",
            first_name="Second",
            last_name="User",
        )
        db.session.add(user2)
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_user_relationships(app):
    """
    Test that a User can have multiple Devices and Patients.
    Verifies the backref is functional and correct.
    """
    with app.app_context():
        user = User(
            email="doc@example.com",
            password="12345"
        )
        db.session.add(user)
        db.session.commit()

        # Create a device for this user
        device1 = Device(
            name="Device One",
            type="Sensor",
            serial_number="ABC123",
            user_id=user.id
        )
        # Create a patient for this user
        patient1 = Patient(
            name="Alice Smith",
            date_of_birth=date(1990, 1, 1),
            gender="Female",
            injury="ACL tear",
            user_id=user.id
        )

        db.session.add(device1)
        db.session.add(patient1)
        db.session.commit()

        assert len(user.devices) == 1
        assert user.devices[0].name == "Device One"
        assert len(user.patients) == 1
        assert user.patients[0].name == "Alice Smith"


# ------------------------------------------------------------------------------
# Patient Model Tests
# ------------------------------------------------------------------------------

def test_patient_creation(app):
    """
    Test creation of a Patient record and retrieval from the DB.
    Ensures required fields (date_of_birth, gender, user_id) are handled correctly.
    """
    with app.app_context():
        user = User(email="provider@example.com", password="test123")
        db.session.add(user)
        db.session.commit()

        patient = Patient(
            name="Bob Johnson",
            date_of_birth=date(1985, 5, 20),
            gender="Male",
            injury="Sprained ankle",
            user_id=user.id
        )
        db.session.add(patient)
        db.session.commit()

        saved_patient = Patient.query.filter_by(name="Bob Johnson").first()
        assert saved_patient is not None
        assert saved_patient.gender == "Male"


def test_patient_notes_relationship(app):
    """
    Test the relationship between a Patient and its PatientNotes.
    Multiple notes should be linkable to the same patient.
    """
    with app.app_context():
        user = User(email="nurse@example.com", password="abc123")
        db.session.add(user)
        db.session.commit()

        patient = Patient(
            name="Charlie Davis",
            date_of_birth=date(2000, 1, 1),
            gender="Other",
            user_id=user.id
        )
        db.session.add(patient)
        db.session.commit()

        note1 = PatientNotes(
            note="First note about Charlie.",
            patient_id=patient.id,
            user_id=user.id
        )
        note2 = PatientNotes(
            note="Second note about Charlie.",
            patient_id=patient.id,
            user_id=user.id
        )
        db.session.add_all([note1, note2])
        db.session.commit()

        notes = PatientNotes.query.filter_by(patient_id=patient.id).all()
        assert len(notes) == 2
        assert notes[0].note == "First note about Charlie."
        assert notes[1].note == "Second note about Charlie."


# ------------------------------------------------------------------------------
# Device Model Tests
# ------------------------------------------------------------------------------

def test_device_creation(app):
    """
    Test that a Device can be created and retrieved by its unique serial number.
    """
    with app.app_context():
        user = User(email="deviceowner@example.com", password="pass")
        db.session.add(user)
        db.session.commit()

        device = Device(
            name="Test Device",
            type="Sensor",
            serial_number="XYZ123",
            user_id=user.id
        )
        db.session.add(device)
        db.session.commit()

        saved_device = Device.query.filter_by(serial_number="XYZ123").first()
        assert saved_device is not None
        assert saved_device.name == "Test Device"


def test_device_duplicate_serial_number(app):
    """
    Test that creating two Devices with the same serial_number 
    raises an IntegrityError (unique constraint on serial_number).
    """
    with app.app_context():
        user = User(email="owner@example.com", password="pass")
        db.session.add(user)
        db.session.commit()

        device1 = Device(
            name="Device A",
            type="Sensor",
            serial_number="DUPLICATE_SN",
            user_id=user.id
        )
        db.session.add(device1)
        db.session.commit()

        device2 = Device(
            name="Device B",
            type="Sensor",
            serial_number="DUPLICATE_SN",
            user_id=user.id
        )
        db.session.add(device2)
        with pytest.raises(IntegrityError):
            db.session.commit()


# ------------------------------------------------------------------------------
# DeviceData Model Tests
# ------------------------------------------------------------------------------

def test_devicedata_creation(app):
    """
    Test creating a DeviceData entry, ensuring it correctly links to Device and Patient.
    Also checks time, orientation, and acceleration fields are stored.
    """
    with app.app_context():
        user = User(email="devicedataowner@example.com", password="mypassword")
        db.session.add(user)
        db.session.commit()

        device = Device(
            name="Sensor1",
            type="Acceleration",
            serial_number="SN001",
            user_id=user.id
        )
        db.session.add(device)

        patient = Patient(
            name="Dana Lee",
            date_of_birth=date(1995, 8, 15),
            gender="Female",
            user_id=user.id
        )
        db.session.add(patient)
        db.session.commit()

        data_point = DeviceData(
            device_id=device.id,
            patient_id=patient.id,
            request_timestamp=datetime.utcnow(),
            test_name="Test Jump",
            time=123.45,
            ax1=0.1,
            ay1=0.1,
            az1=0.1,
            ox1=1.0,
            oy1=1.0,
            oz1=1.0,
            ow1=1.0,
            ax2=0.2,
            ay2=0.2,
            az2=0.2,
            ox2=2.0,
            oy2=2.0,
            oz2=2.0,
            ow2=2.0
        )
        db.session.add(data_point)
        db.session.commit()

        saved_data = DeviceData.query.first()
        assert saved_data is not None
        assert saved_data.test_name == "Test Jump"
        assert saved_data.device == device
        assert saved_data.patient == patient
        assert saved_data.time == 123.45
        assert saved_data.ax1 == 0.1
        assert saved_data.ox2 == 2.0

        # Confirm relationships
        assert len(device.data_points) == 1
        assert len(patient.data_points) == 1


def test_devicedata_unique_session_id(app):
    """
    Test that two DeviceData records cannot have the same session_id if set.
    session_id is unique, so an IntegrityError should be raised.
    """
    with app.app_context():
        user = User(email="device2@example.com", password="pwd")
        db.session.add(user)
        db.session.commit()

        device = Device(
            name="TestDevice2",
            type="Acceleration",
            serial_number="SN002",
            user_id=user.id
        )
        db.session.add(device)
        db.session.commit()

        # First record with a session_id of 100
        d1 = DeviceData(
            device_id=device.id,
            request_timestamp=datetime.utcnow(),
            session_id=100,
            time=0.0  # required
        )
        db.session.add(d1)
        db.session.commit()

        # Second record with the same session_id=100
        d2 = DeviceData(
            device_id=device.id,
            request_timestamp=datetime.utcnow(),
            session_id=100,
            time=1.0
        )
        db.session.add(d2)
        with pytest.raises(IntegrityError):
            db.session.commit()
