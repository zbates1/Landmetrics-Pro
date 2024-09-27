# db_utils.py
from .models import User, Device, DeviceData
from werkzeug.security import generate_password_hash
from . import db
from sqlalchemy import func
from datetime import datetime


# Add a new user
def add_user(email, password, first_name):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256') # tag: hardcoded encryption
    new_user = User(email=email, password=hashed_password, first_name=first_name)
    db.session.add(new_user)
    db.session.commit()
    print(f'User {email} added successfully!')

# Add a new device for a specific user
def add_device(name, device_type, serial_number, user_id):
    user = User.query.get(user_id)
    if user:
        new_device = Device(name=name, type=device_type, serial_number=serial_number, user_id=user.id)
        db.session.add(new_device)
        db.session.commit()
        print(f'Device {name} added successfully for User {user.email}!')
    else:
        print(f'User with id {user_id} does not exist.')

# Updated add_device_data function
def add_device_data(serial_number, time, ax1, ay1, az1, gx1, gy1, gz1, ax2, ay2, az2, gx2, gy2, gz2, ax3, ay3, az3, gx3, gy3, gz3):
    device = Device.query.filter_by(serial_number=serial_number).first()  # Query by serial_number
    if device:
        new_data = DeviceData(
            device_id=device.id,
            time=time,  # Time from the Arduino data
            request_timestamp=datetime.utcnow(),  # Timestamp of when the request was received
            ax1=ax1, ay1=ay1, az1=az1, gx1=gx1, gy1=gy1, gz1=gz1,
            ax2=ax2, ay2=ay2, az2=az2, gx2=gx2, gy2=gy2, gz2=gz2,
            ax3=ax3, ay3=ay3, az3=az3, gx3=gx3, gy3=gy3, gz3=gz3
        )
        db.session.add(new_data)
        db.session.commit()
        print(f'Data for Device {serial_number} added successfully!')
    else:
        print(f'Device with serial number {serial_number} does not exist.')

def list_users():
    users = User.query.all()
    if users:
        print(f"{'ID':<5} {'Email':<25} {'First Name':<15}")
        print("="*45)
        for user in users:
            print(f"{user.id:<5} {user.email:<25} {user.first_name:<15}")
    else:
        print("No users found in the database.")

def list_devices_for_user(user_id):
    user = User.query.get(user_id)
    if user:
        if user.devices:
            print(f"Devices for {user.first_name} ({user.email}):")
            print(f"{'Device ID':<10} {'Device Name':<25} {'Device Type':<25} {'Serial Number':<20}")
            print("="*80)
            for device in user.devices:
                print(f"{device.id:<10} {device.name:<25} {device.type:<25} {device.serial_number:<20}")
        else:
            print(f"{user.first_name} has no registered devices.")
    else:
        print(f"User with ID {user_id} not found.")

def list_all_devices():
    devices = Device.query.all()
    if devices:
        print(f"{'Device ID':<10} {'Device Name':<25} {'Device Type':<25} {'Owner Email':<30}")
        print("=" * 90)
        for device in devices:
            owner_email = device.owner.email if device.owner else "No owner"
            print(f"{device.id:<10} {device.name:<25} {device.type:<25} {owner_email:<30}")
    else:
        print("No devices found in the database.")


# Updated list_device_data function
# Updated list_device_data function
def list_device_data(serial_number):
    device = Device.query.filter_by(serial_number=serial_number).first()
    if device:
        if device.data_points:
            print(f"Data points for {device.name} (Serial: {device.serial_number}):")
            print(f"{'Data ID':<10} {'Timestamp':<25} {'Time':<10} {'Ax1':<10} {'Ay1':<10} {'Az1':<10} {'Gx1':<10} "
                  f"{'Gy1':<10} {'Gz1':<10} {'Ax2':<10} {'Ay2':<10} {'Az2':<10} {'Gx2':<10} {'Gy2':<10} {'Gz2':<10} "
                  f"{'Ax3':<10} {'Ay3':<10} {'Az3':<10} {'Gx3':<10} {'Gy3':<10} {'Gz3':<10}")
            print("=" * 200)
            for data in device.data_points:
                print(f"{data.id:<10} {data.timestamp.strftime('%Y-%m-%d %H:%M:%S'):<25} {data.time:<10.2f} "
                      f"{data.ax1:<10.2f} {data.ay1:<10.2f} {data.az1:<10.2f} {data.gx1:<10.2f} {data.gy1:<10.2f} {data.gz1:<10.2f} "
                      f"{data.ax2:<10.2f} {data.ay2:<10.2f} {data.az2:<10.2f} {data.gx2:<10.2f} {data.gy2:<10.2f} {data.gz2:<10.2f} "
                      f"{data.ax3:<10.2f} {data.ay3:<10.2f} {data.az3:<10.2f} {data.gx3:<10.2f} {data.gy3:<10.2f} {data.gz3:<10.2f}")
        else:
            print(f"No data points found for device {device.name}.")
    else:
        print(f"Device with serial number {serial_number} not found.")

def find_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if user:
        print(f"User found: {user.first_name} (ID: {user.id}, Email: {user.email})")
    else:
        print(f"No user found with email {email}.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="CLI Tools for Interacting with the Database")
    
    parser.add_argument('--list-users', action='store_true', help="List all users")
    parser.add_argument('--list-devices-for-user', type=int, help="List devices for a specific user by user ID")
    parser.add_argument('--list-all-devices', action='store_true', help="List all devices")
    parser.add_argument('--list-device-data', type=str, help="List data points for a specific device by serial number")
    parser.add_argument('--find-user-by-email', type=str, help="Find a user by their email")
    
    args = parser.parse_args()
    
    if args.list_users:
        list_users()
    elif args.list_devices_for_user:
        list_devices_for_user(args.list_devices_for_user)
    elif args.list_all_devices:
        list_all_devices()
    elif args.list_device_data:
        list_device_data(args.list_device_data)
    elif args.find_user_by_email:
        find_user_by_email(args.find_user_by_email)



## Usage

# cmd prmpt (in root): flask --app website shell 
# this allows you to utilize the functions above to manually add db entries

## Example Usage: 
# 1.
# from website.db_utils import add_user
# add_user(email="test@example.com", password="password123", first_name="Test")

# 2.
# from website.db_utils import add_device
# Example command to add a device for a user with user_id=1 -> NOTE: for this to work, you will need to utilize the list_users() function to find the user_id
# add_device(name="Knee Tracker", device_type="Physical Therapy Device", serial_number="SN123456", user_id=1)

# 3.
# from website.db_utils import add_device_data
# Example command to add data for a device with serial number 'SN123456'
# add_device_data(
#     serial_number='SN123456',
#     time=2138,  # Time sent from the Arduino
#     ax1=0.01, ay1=0.02, az1=0.98, gx1=1.5, gy1=-0.5, gz1=0.0,
#     ax2=0.03, ay2=0.04, az2=1.02, gx2=1.2, gy2=-0.3, gz2=0.1,
#     ax3=0.05, ay3=0.06, az3=1.05, gx3=1.0, gy3=-0.2, gz3=0.2
# )



## Example CLI Commands

# List all users:
# python db_utils.py --list-users

# List devices for a user with ID 1:
# python db_utils.py --list-devices-for-user 1

# List all devices:
# python db_utils.py --list-all-devices

# List data points for a device with ID 2:
# python db_utils.py --list-device-data 2

# Find user by email:
# python db_utils.py --find-user-by-email 'user@example.com'
