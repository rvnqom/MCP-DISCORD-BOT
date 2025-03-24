import requests

LOG_SERVER_URL = "http://127.0.0.1:5000/logs"  # Flask server for logging

def log_to_backend(category, message, sender="System"):
    
    try:
        log_entry = f"[{category}] {sender}: {message}"
        requests.post(LOG_SERVER_URL, json={"log": log_entry})
    except requests.exceptions.RequestException:
        pass  # Avoid crashing if backend is unavailable
