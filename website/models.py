from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import event, UniqueConstraint
from werkzeug.security import generate_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    devices = db.relationship('Device', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

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
    request_timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    session_id = db.Column(db.Integer, nullable=True, unique=True)
    time = db.Column(db.Float, nullable=False)

    # Accelerometer and orientation data for two sets of readings
    ax1 = db.Column(db.Float, nullable=True)
    ay1 = db.Column(db.Float, nullable=True)
    az1 = db.Column(db.Float, nullable=True)
    ox1 = db.Column(db.Float, nullable=True)
    oy1 = db.Column(db.Float, nullable=True)
    oz1 = db.Column(db.Float, nullable=True)

    ax2 = db.Column(db.Float, nullable=True)
    ay2 = db.Column(db.Float, nullable=True)
    az2 = db.Column(db.Float, nullable=True)
    ox2 = db.Column(db.Float, nullable=True)
    oy2 = db.Column(db.Float, nullable=True)
    oz2 = db.Column(db.Float, nullable=True)

    __table_args__ = (
        # UniqueConstraint('session_id', name='uq_device_data_session_id'),
    )

    def __repr__(self):
        return f'<DeviceData {self.id} for Device {self.device_id}>'

@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value, method='pbkdf2:sha256')
    return value
