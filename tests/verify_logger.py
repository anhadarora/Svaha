
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.logger import setup_run_logger

def verify_logger():
    print("Setting up logger...")
    setup_run_logger()
    
    logger = logging.getLogger(__name__)
    
    test_message = "Chaos Monkey Verification Log Entry"
    logger.info(test_message)
    
    # Check if log file exists and contains the message
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    
    # Find the most recent log file
    log_files = [f for f in os.listdir(log_dir) if f.startswith("scova_run_") and f.endswith(".log")]
    if not log_files:
        print("FAIL: No log files found.")
        return

    latest_log = max([os.path.join(log_dir, f) for f in log_files], key=os.path.getctime)
    print(f"Checking latest log file: {latest_log}")
    
    with open(latest_log, 'r') as f:
        content = f.read()
        if test_message in content:
            print("SUCCESS: Log entry found in file.")
        else:
            print("FAIL: Log entry NOT found in file.")

if __name__ == "__main__":
    verify_logger()
