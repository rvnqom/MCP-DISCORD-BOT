from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import datetime

app = Flask(__name__)
CORS(app, resources={r"/logs": {"origins": "*"}})  # Allow all origins for /logs

LOG_FILE = "logs.json"
LOG_LIMIT = 500  # Maximum number of logs stored

# Ensure log file exists and is valid JSON
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        json.dump([], file, indent=2)

def read_logs():
    """Reads logs from the file."""
    try:
        with open(LOG_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def write_logs(logs):
    """Writes logs back to the file with a limit."""
    logs = logs[-LOG_LIMIT:]  # Keep only the latest N logs
    with open(LOG_FILE, "w") as file:
        json.dump(logs, file, indent=2)

@app.route("/logs", methods=["GET"])
def get_logs():
    """Retrieves all stored logs."""
    logs = read_logs()
    return jsonify({"logs": logs})

@app.route("/logs", methods=["POST"])
def add_log():
    """Adds a new log entry."""
    try:
        data = request.get_json()
        
        log_type = data.get("log_type", "UNKNOWN")
        message = data.get("message", "").strip()
        sender = data.get("sender", "Unknown User")

        if not message:
            return jsonify({"error": "Log message is required"}), 400

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_log = {
            "timestamp": timestamp,
            "log_type": log_type,
            "message": message,
            "sender": sender
        }

        logs = read_logs()
        logs.append(new_log)
        write_logs(logs)

        print(f"✅ [LOG] {timestamp} | {log_type} | {sender}: {message}")  # Debugging
        return jsonify({"message": "Log added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/logs/clear", methods=["POST"])
def clear_logs():
    """Clears all stored logs."""
    try:
        write_logs([])  # Overwrite logs with an empty list
        print("🗑️ Logs cleared successfully!")  # Debugging
        return jsonify({"message": "Logs cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080 , debug=True)  # Allow external connections
