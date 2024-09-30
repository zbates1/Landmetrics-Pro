from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import event
from werkzeug.security import generate_password_hash

## Tag: Database updates.
# If you need to update the database schema, you can do so by updating this file, models.py, then making corresponding changes in the files that utilize these models, such as db_utils.py,
# user_data.py, views.py, and then the html files must be adapted to match the new schema.

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
    serial_number = db.Column(db.String(150), unique=True)  # Use serial_number as device identifier
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_points = db.relationship('DeviceData', backref='device', lazy=True)

    def __repr__(self):
        return f'<Device {self.name}>'

class DeviceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())  # Timestamp of data creation in the DB
    # request_timestamp = db.Column(db.DateTime(timezone=True))  # When the HTTP request was sent
    # new request_timestamp without DateTime, it throws an error
    request_timestamp = db.Column(db.String(150), nullable=False)

    time = db.Column(db.Float, nullable=False)  # This represents the time value from the data
    
    # Accelerometer and gyroscope data for three sets of readings
    ax1 = db.Column(db.Float, nullable=False)
    ay1 = db.Column(db.Float, nullable=False)
    az1 = db.Column(db.Float, nullable=False)
    gx1 = db.Column(db.Float, nullable=False)
    gy1 = db.Column(db.Float, nullable=False)
    gz1 = db.Column(db.Float, nullable=False)

    ax2 = db.Column(db.Float, nullable=False)
    ay2 = db.Column(db.Float, nullable=False)
    az2 = db.Column(db.Float, nullable=False)
    gx2 = db.Column(db.Float, nullable=False)
    gy2 = db.Column(db.Float, nullable=False)
    gz2 = db.Column(db.Float, nullable=False)

    ax3 = db.Column(db.Float, nullable=False)
    ay3 = db.Column(db.Float, nullable=False)
    az3 = db.Column(db.Float, nullable=False)
    gx3 = db.Column(db.Float, nullable=False)
    gy3 = db.Column(db.Float, nullable=False)
    gz3 = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<DeviceData {self.id} for Device {self.device_id}>'



@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value, method='pbkdf2:sha256')
    return value