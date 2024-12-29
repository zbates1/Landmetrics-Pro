# db_utils.py

try:
    from .models import User, Device, DeviceData, Patient  # Relative import for package context
except ImportError:
    from website.models import User, Device, DeviceData, Patient  # Absolute import for script execution

from werkzeug.security import generate_password_hash

try:
    from . import db  # Relative import for package context
except ImportError:
    from website import db, create_app  # Absolute import for direct script execution
    from website.config import DevelopmentConfig

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


# tag: Outdated -> needs patient_id to be included
def add_device_data(
    serial_number,
    time,
    ax1, ay1, az1, ox1, oy1, oz1, ow1,
    ax2, ay2, az2, ox2, oy2, oz2, ow2,
    test_name=None
):
    """
    Add a new DeviceData entry for a specific device identified by 'serial_number'.
    
    :param serial_number: The device's unique serial_number in the Device table.
    :param time: The 'time' value from the sensor data (float).
    :param ax1, ay1, az1, ox1, oy1, oz1, ow1: First set of sensor readings.
    :param ax2, ay2, az2, ox2, oy2, oz2, ow2: Second set of sensor readings.
    :param test_name: Optional test name, e.g. "depth jump".
    """
    device = Device.query.filter_by(serial_number=serial_number).first()
    if device:
        new_data = DeviceData(
            device_id=device.id,
            time=time,  
            request_timestamp=datetime.utcnow(),  # or func.now() if you prefer
            test_name=test_name,
            
            ax1=ax1, ay1=ay1, az1=az1,
            ox1=ox1, oy1=oy1, oz1=oz1, ow1=ow1,
            
            ax2=ax2, ay2=ay2, az2=az2,
            ox2=ox2, oy2=oy2, oz2=oz2, ow2=ow2
        )
        db.session.add(new_data)
        db.session.commit()
        print(f"Data for Device {serial_number} added successfully!")
    else:
        print(f"Device with serial number {serial_number} does not exist.")


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

def find_patient_by_id(patient_id):
    """
    Finds a patient by their ID and prints the patient's name and associated provider.
    """
    patient = Patient.query.get(patient_id)
    if patient:
        provider_email = patient.provider.email if patient.provider else "No provider"
        print(f"Patient found: {patient.name} (ID: {patient.id}, Provider: {provider_email})")
    else:
        print(f"No patient found with ID {patient_id}.")

def find_patient_by_name(name):
    """
    Finds patients matching the provided name (case-insensitive).
    Prints out their ID, name, and associated provider.
    """
    # Case-insensitive search
    patients = Patient.query.filter(Patient.name.ilike(f"%{name}%")).all()
    if patients:
        print(f"Patients matching '{name}':")
        for p in patients:
            provider_email = p.provider.email if p.provider else "No provider"
            print(f" - ID: {p.id}, Name: {p.name}, Provider: {provider_email}")
    else:
        print(f"No patients found with name containing '{name}'.")

def find_tests_by_patient_id(patient_id):
    """
    Finds all test-related data_points (DeviceData) for the given patient ID,
    printing out each test_name, ID, and related info.
    """
    patient = Patient.query.get(patient_id)
    if patient:
        # All DeviceData rows for this patient
        tests = patient.data_points
        if tests:
            print(f"Tests for patient {patient.name} (ID: {patient.id}):")
            for t in tests:
                # 't' is a DeviceData row
                # If you only want DeviceData rows that have a non-empty test_name, you can check:
                if t.test_name:
                    print(f" - DeviceData ID: {t.id}, Test Name: {t.test_name}, Device ID: {t.device_id}")
                else:
                    print(f" - DeviceData ID: {t.id}, No test_name set")
        else:
            print(f"No data points (tests) found for patient {patient.name}.")
    else:
        print(f"No patient found with ID {patient_id}.")

def find_data_by_patient_id(patient_id): # tag: Outdated -> it looks like this has the same functionality as the above function
    patient = Patient.query.get(patient_id)
    if patient:
        # All DeviceData rows for this patient
        tests = patient.data_points
        if tests:
            print(f"Data points for patient {patient.name} (ID: {patient.id}):")
            for t in tests:
                # 't' is a DeviceData row
                print(f" - DeviceData ID: {t.id}, Request Timestamp: {t.request_timestamp}")
        
            return tests # this returns the DeviceData rows
        else:
            print(f"No data points found for patient {patient.name}.")
    else:
        print(f"No patient found with ID {patient_id}.")


def find_unique_request_timestamps_by_patient_id(patient_id):
    """
    Finds all unique request_timestamp values for the given patient ID.
    Prints out how many unique timestamps there are and lists them.
    """
    patient = Patient.query.get(patient_id)
    if not patient:
        print(f"No patient found with ID {patient_id}.")
        return
    
    # Extract all request_timestamps from the patient's DeviceData
    timestamps = [dp.request_timestamp for dp in patient.data_points]
    if not timestamps:
        print(f"No data points found for patient {patient.name} (ID: {patient.id}).")
        return
    
    # Convert to a set to get unique values
    unique_timestamps = set(timestamps)
    
    print(f"Unique request timestamps for patient {patient.name} (ID: {patient.id}):")
    print(f"Found {len(unique_timestamps)} unique timestamp(s).")
    for ts in sorted(unique_timestamps):
        print(f" - {ts}")

def list_all_patients():
    """
    Lists all patients in the database with their ID, name, and provider's email.
    """
    patients = Patient.query.all()
    if patients:
        print(f"{'Patient ID':<10} {'Patient Name':<25} {'DOB':<12} {'Gender':<10} {'Provider Email':<30}")
        print("=" * 90)
        for p in patients:
            provider_email = p.provider.email if p.provider else "No provider"
            dob_str = p.date_of_birth.isoformat() if p.date_of_birth else "N/A"
            print(f"{p.id:<10} {p.name:<25} {dob_str:<12} {p.gender:<10} {provider_email:<30}")
    else:
        print("No patients found in the database.")



if __name__ == '__main__':
    import argparse
    # from website import create_app
    # from website.models import User, Device, DeviceData, Patient
    # from website.db_utils import (
    #     list_users,
    #     list_devices_for_user,
    #     list_all_devices,
    #     list_device_data,
    #     find_user_by_email,
    #     find_patient_by_id,
    #     find_patient_by_name,
    #     list_all_patients,
    #     find_tests_by_patient_id,
    #     find_data_by_patient_id,
    #     find_unique_request_timestamps_by_patient_id
    # )

    # Initialize argument parser
    parser = argparse.ArgumentParser(description="CLI Tools for Interacting with the Database")
    parser.add_argument('--list-users', action='store_true', help="List all users")
    parser.add_argument('--list-devices-for-user', type=int, help="List devices for a specific user by user ID")
    parser.add_argument('--list-all-devices', action='store_true', help="List all devices")
    parser.add_argument('--list-device-data', type=str, help="List data points for a specific device by serial number")
    parser.add_argument('--find-user-by-email', type=str, help="Find a user by their email")
    parser.add_argument('--find-patient-by-id', type=int, help="Find a patient by their ID")
    parser.add_argument('--find-patient-by-name', type=str, help="Find a patient by name")
    parser.add_argument('--list-all-patients', action='store_true', help="List all patients")
    parser.add_argument('--find-tests-by-patient-id', type=int, help="Find tests by patient ID")
    parser.add_argument('--find-unique-request-timestamps-by-patient-id', type=int, help="Find unique request timestamps by patient ID")
    parser.add_argument('--find-data-by-patient-id', type=int, help="Find data by patient ID")

    # Parse arguments
    args = parser.parse_args()

    # Create Flask app
    app = create_app(DevelopmentConfig)  # Adjust if `DevelopmentConfig` is needed: `create_app(DevelopmentConfig)`

    # Push app context to handle database operations
    with app.app_context():
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
        elif args.find_patient_by_id:
            find_patient_by_id(args.find_patient_by_id)
        elif args.find_patient_by_name:
            find_patient_by_name(args.find_patient_by_name)
        elif args.list_all_patients:
            list_all_patients()
        elif args.find_tests_by_patient_id:
            find_tests_by_patient_id(args.find_tests_by_patient_id)
        elif args.find_unique_request_timestamps_by_patient_id:
            find_unique_request_timestamps_by_patient_id(args.find_unique_request_timestamps_by_patient_id)
        elif args.find_data_by_patient_id:
            find_data_by_patient_id(args.find_data_by_patient_id)
        else:
            parser.print_help()
# ======================================
# Usage Guide for `website` Module
# ======================================

# Command Prompt (In Project Root):
# To interact with the database via Flask shell:
# flask --app website shell
# This allows you to use the following functions to manually add or query database entries.

# Example Usage in Flask Shell:

# 1. Add a User
# from website.db_utils import add_user
# add_user(email="test@example.com", password="password123", first_name="Test")

# 2. Add a Device
# First, find the `user_id` using the `list_users()` function.
# Then:
# from website.db_utils import add_device
# add_device(name="Knee Tracker", device_type="Physical Therapy Device", serial_number="SN123456", user_id=1)

# 3. Add Device Data
# This example assumes you have a device with `serial_number='SN123456'`:
# from website.db_utils import add_device_data
# add_device_data(
#     serial_number='SN123456',
#     time=2138,  # Time sent from the Arduino
#     ax1=0.01, ay1=0.02, az1=0.98, gx1=1.5, gy1=-0.5, gz1=0.0,
#     ax2=0.03, ay2=0.04, az2=1.02, gx2=1.2, gy2=-0.3, gz2=0.1,
#     ax3=0.05, ay3=0.06, az3=1.05, gx3=1.0, gy3=-0.2, gz3=0.2
# )

# 4. Find a Patient by ID
# from website.db_utils import find_patient_by_id
# find_patient_by_id(5)  # Replace 5 with the desired patient ID.

# 5. Find a Patient by Name
# from website.db_utils import find_patient_by_name
# find_patient_by_name("John")  # Lists all patients whose name includes "John".

# ======================================
# Example CLI Commands
# ======================================

# List all users:
# python website/db_utils.py --list-users

# List devices for a user with ID 1:
# python website/db_utils.py --list-devices-for-user 1

# List all devices:
# python website/db_utils.py --list-all-devices

# List data points for a device with ID 2:
# python website/db_utils.py --list-device-data 2

# Find user by email:
# python website/db_utils.py --find-user-by-email 'user@example.com'
