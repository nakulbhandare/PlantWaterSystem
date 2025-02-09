from flask import Flask, jsonify, request
import sqlite3
import requests
from datetime import datetime, timedelta
import schedule
import time
import threading
import os

app = Flask(__name__)

# Configuration
DB_NAME = "plant_sensor_data.db"
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "https://backend.example.com/receive-data")
RETRY_ATTEMPTS = 3


def fetch_recent_data():
    """Fetch all sensor readings from the last 12 hours."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Get the current timestamp and 12 hours back
        twelve_hours_ago = datetime.now() - timedelta(hours=12)

        # Query for data within the last 12 hours
        cursor.execute("""
            SELECT id, timestamp, sensor_id, moisture_level, digital_status
            FROM moisture_data
            WHERE timestamp >= ?
        """, (twelve_hours_ago.strftime("%Y-%m-%d %H:%M:%S"),))

        data = cursor.fetchall()
        conn.close()

        # Convert data to a list of dictionaries
        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "sensor_id": row[2],
                "moisture_level": row[3],
                "digital_status": row[4]
            }
            for row in data
        ]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def send_data_to_backend():
    """Send sensor data to the backend with retry logic."""
    data = fetch_recent_data()

    if not data:
        print("No data to send.")
        return

    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(BACKEND_API_URL, json={"sensor_data": data})

            if response.status_code == 200:
                print("Data sent successfully")
                return
            else:
                print(f"Attempt {attempt + 1}: Failed to send data ({response.status_code}) - {response.text}")
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1}: Error sending data - {e}")

    print("All retry attempts failed.")


@app.route("/send-data", methods=["POST"])
def send_data():
    """Trigger data sending via an API request."""
    send_data_to_backend()
    return jsonify({"message": "Data sending initiated"}), 200


def schedule_data_sending():
    """Schedule data sending to occur at 12:00 AM and 12:00 PM daily."""
    schedule.every().day.at("00:00").do(send_data_to_backend)
    schedule.every().day.at("12:00").do(send_data_to_backend)

    while True:
        schedule.run_pending()
        time.sleep(1)


def run_schedule_in_thread():
    """Run the scheduler in a separate thread."""
    thread = threading.Thread(target=schedule_data_sending)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    run_schedule_in_thread()
    app.run(host="0.0.0.0", port=5000)
