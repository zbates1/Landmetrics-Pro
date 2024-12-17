from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import event, UniqueConstraint
from werkzeug.security import generate_password_hash
from datetime import date

class User(db.Model, UserMixin): # Note: This is a User class for Healthcare Providers, but renaming to Provider was too confusing
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    
    devices = db.relationship('Device', backref='owner', lazy=True)
    patients = db.relationship('Patient', backref='provider', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)  # Date of birth
    gender = db.Column(db.String(50), nullable=False)    # e.g. 'Male', 'Female', 'Other'
    injury = db.Column(db.String(255), nullable=True)    # Description of injury
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_patient_user'),
        nullable=False
    )
    
    # DeviceData references Patient
    data_points = db.relationship('DeviceData', backref='patient', lazy=True)

    def __repr__(self):
        return f'<Patient {self.name} (ID: {self.id})>'

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    type = db.Column(db.String(150))
    serial_number = db.Column(db.String(150), unique=True)
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('user.id', name='fk_device_user'), 
        nullable=False
    )

    data_points = db.relationship('DeviceData', backref='device', lazy=True)

    def __repr__(self):
        return f'<Device {self.name}>'

class DeviceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, 
        db.ForeignKey('device.id', name='fk_device_data_device'), 
        nullable=False
    )
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('patient.id', name='fk_devicedata_patient'),
        nullable=True
    )

    request_timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    session_id = db.Column(db.Integer, nullable=True, unique=True)
    test_name = db.Column(db.String(255), nullable=True) # e.g. "depth jump", etc
    time = db.Column(db.Float, nullable=False)

    # Accelerometer and orientation data for two sets of readings
    ax1 = db.Column(db.Float, nullable=True)
    ay1 = db.Column(db.Float, nullable=True)
    az1 = db.Column(db.Float, nullable=True)
    ox1 = db.Column(db.Float, nullable=True)
    oy1 = db.Column(db.Float, nullable=True)
    oz1 = db.Column(db.Float, nullable=True)
    ow1 = db.Column(db.Float, nullable=True)

    ax2 = db.Column(db.Float, nullable=True)
    ay2 = db.Column(db.Float, nullable=True)
    az2 = db.Column(db.Float, nullable=True)
    ox2 = db.Column(db.Float, nullable=True)
    oy2 = db.Column(db.Float, nullable=True)
    oz2 = db.Column(db.Float, nullable=True)
    ow2 = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<DeviceData {self.id} - Device {self.device_id} - Patient {self.patient_id}>'

@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value, method='pbkdf2:sha256')
    return value
