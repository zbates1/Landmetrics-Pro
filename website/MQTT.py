import csv
from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import threading
import queue
import pyscopg2


app = Flask(__name__)

# HiveMQ Cloud broker details
BROKER_URL = "6b53960d5ee44dbf8e50b63d29b4bfa1.s1.eu.hivemq.cloud"
BROKER_PORT = 8883  # Secure TLS port
USERNAME = "Landmetrics"  # Replace with HiveMQ username
PASSWORD = "TestTest1"  # Replace with HiveMQ password
currentDevice = "device1"

# Queue to store incoming MQTT messages
message_queue = queue.Queue()

# Dictionary to store data and statuses for multiple devices
device_data = {}
device_status = {}

# CSV file path
csv_file_path = "device_data.csv"

# PostgreSQL connection details FOR ZANE
db_conn = psycopg2.connect(
    dbname="your_database",
    user="your_username",
    password="your_password",
    host="your_host",
    port="your_port"
)

# Callback when the client connects successfully
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to HiveMQ!")
        client.subscribe("device/"+currentDevice+"/data")  # Subscribe to the desired topic
        print(f"Subscribed to topics")
    else:
        print(f"Failed to connect, return code {rc}")


# MQTT Callback: When a message is received
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        message_queue.put((msg.topic, payload))  # Add to the queue
    except Exception as e:
        print(f"Error processing message: {e}")

def process_message():
    global device_data
    with open(csv_file_path, mode="a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        while True:
            try:
                topic, payload = message_queue.get(timeout=1)
                topic_parts = topic.split('/')
                if len(topic_parts) == 3:
                    device_id = topic_parts[1]
                    message_type = topic_parts[2]

                    if message_type == "data":
                        # Store the latest data for the device
                        device_data[device_id] = payload
                        # Log to CSV
                        csv_writer.writerow([device_id, message_type, payload])
            except queue.Empty:
                continue

# Start the message processing thread
threading.Thread(target=process_messages, daemon=True).start()

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_URL, BROKER_PORT)
client.loop_start()


# Flask Routes
@app.route("/")
def home():
    return render_template("new_test.html")

@app.route("/stream_data")
def stream_data():
    # Return the latest data for the current device
    return jsonify([device_data.get(currentDevice, "No data available")])

@app.route("/get_device_status", methods=["GET"])
def get_device_status():
    # Return the latest status for the current device
    return jsonify(device_status.get(currentDevice, "No status available"))

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    try:
        with open(csv_file_path, mode="r") as csv_file:
            csv_reader = csv.reader(csv_file)
            cursor = db_conn.cursor()
            for row in csv_reader:
                device_id, message_type, payload = row
                cursor.execute(
                    """
                    INSERT INTO device_data (device_id, message_type, payload)
                    VALUES (%s, %s, %s)
                    """,
                    (device_id, message_type, payload)
                )
            db_conn.commit()
            return jsonify({"status": "success", "message": "Data uploaded to PostgreSQL successfully."})
    except Exception as e:
        print(f"Error uploading CSV: {e}")
        return jsonify({"status": "error", "message": "Failed to upload CSV data."})

@app.route("/start_test", methods=["POST"])
def start_test():
    # Publish "start" command to the MQTT control topic
    topic = f"device/{currentDevice}/control"
    client.publish(topic, "start")
    return jsonify({"status": "success", "message": "Start command sent."})

@app.route("/stop_test", methods=["POST"])
def stop_test():
    # Publish "stop" command to the MQTT control topic
    topic = f"device/{currentDevice}/control"
    client.publish(topic, "stop")
    return jsonify({"status": "success", "message": "Stop command sent."})

if __name__ == "__main__":
    app.run(debug=True)