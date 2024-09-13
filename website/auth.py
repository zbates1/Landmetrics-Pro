from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, Device
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import json
from flask import jsonify

from flask_wtf.csrf import generate_csrf # used to generate csrf token as seen in return statement for below function

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user, csrf=generate_csrf())


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user) # user=current_user was here in the template repo, but I actually don't think it needs to be there

# from flask_wtf.csrf import generate_csrf # used to generate csrf token as seen in return statement for below function
@auth.route('/devices', methods=['GET', 'POST'])
@login_required
def register_device():
    print('Running register_device, current_user.id:', current_user.id)
    if request.method == 'POST':
        print('Running POST in register_device')
        data = request.get_json()
        name = data.get('name')
        type = data.get('type')
        serial_number = data.get('serial_number')

        # Check if device already exists
        device = Device.query.filter_by(serial_number=serial_number).first()
        if device:
            print('Device with this serial number already exists.')
            return jsonify({'error': 'Device with this serial number already exists.'}), 400
        else:
            print('Adding device:', name, type, serial_number)
            new_device = Device(name=name, type=type, serial_number=serial_number, user_id=current_user.id)
            db.session.add(new_device)
            db.session.commit()
            return jsonify({'success': 'Device registered successfully!'})

    # This part is unnecessary for POST request, should be handled differently
    devices = Device.query.filter_by(user_id=current_user.id).all()
    return render_template("devices.html", user=current_user, devices=devices, csrf_token=generate_csrf())

@auth.route('/get-devices')
@login_required
def get_devices():
    devices = Device.query.filter_by(user_id=current_user.id).all()
    devices_list = [{'name': device.name, 'type': device.type, 'serial_number': device.serial_number, 'id': device.id} for device in devices]
    return jsonify(devices_list)


@auth.route('/delete-device', methods=['POST'])
@login_required
def delete_device():
    data = request.get_json()
    device_id = data['deviceId']
    device = Device.query.get(device_id)

    if device and device.user_id == current_user.id:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'success': 'Device deleted'})
    else:
        return jsonify({'error': 'Device not found or unauthorized'}), 404


@auth.route('/edit-device', methods=['POST'])
@login_required
def edit_device():
    data = request.get_json()
    device = Device.query.get(data['id'])
    if device and device.user_id == current_user.id:
        device.name = data['name']
        device.type = data['type']
        device.serial_number = data['serial_number']
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Unauthorized or invalid data'}), 400
