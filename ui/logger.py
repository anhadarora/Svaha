import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, f"svaha_ui_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

def log_to_file(message):
    """Writes a message to the log file."""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{message}\n")

class UILogger:
    @staticmethod
    def add_log_entry(logs_list, message):
        """Adds a timestamped message to the logs list and writes it to a file."""
        log_message = f"{datetime.now().strftime('%H:%M:%S')} - {message}"
        logs_list.insert(0, {'text': log_message})
        log_to_file(log_message)
