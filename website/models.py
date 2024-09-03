from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

from sqlalchemy import event
from werkzeug.security import generate_password_hash

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note', backref='author', lazy=True)
    devices = db.relationship('Device', backref='owner', lazy=True)  # This allows access to a user's devices

    def __repr__(self):
        return f'<User {self.email}>'

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    type = db.Column(db.String(150))
    serial_number = db.Column(db.String(150), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # ForeignKey to connect each device to a specific user

    def __repr__(self):
        return f'<Device {self.name}>'


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value)
    return value

