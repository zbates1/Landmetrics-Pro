from .models import User, Device, DeviceData
from werkzeug.security import generate_password_hash
from . import db
from sqlalchemy import func

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
def add_device_data(serial_number, ax, ay, az, gx, gy, gz):
    device = Device.query.filter_by(serial_number=serial_number).first()  # Query by serial_number
    if device:
        new_data = DeviceData(
            device_id=device.id,
            ax=ax,
            ay=ay,
            az=az,
            gx=gx,
            gy=gy,
            gz=gz
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
def list_device_data(serial_number):
    device = Device.query.filter_by(serial_number=serial_number).first()
    if device:
        if device.data_points:
            print(f"Data points for {device.name} (Serial: {device.serial_number}):")
            print(f"{'Data ID':<10} {'Timestamp':<25} {'ax':<10} {'ay':<10} {'az':<10} {'gx':<10} {'gy':<10} {'gz':<10}")
            print("=" * 105)
            for data in device.data_points:
                print(f"{data.id:<10} {data.timestamp.strftime('%Y-%m-%d %H:%M:%S'):<25} "
                      f"{data.ax:<10.2f} {data.ay:<10.2f} {data.az:<10.2f} "
                      f"{data.gx:<10.2f} {data.gy:<10.2f} {data.gz:<10.2f}")
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
# Example command to add data for a device with device_id=1
# add_device_data(serial_number='SN123456', ax=0.01, ay=0.02, az=0.98, gx=1.5, gy=-0.5, gz=0.0)



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
