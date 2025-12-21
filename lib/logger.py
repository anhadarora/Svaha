import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_run_logger():
    """
    Configures a unique, timestamped logger for an application run.
    This should be called once when the application starts.
    """
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(log_dir, f"svaha_run_{timestamp}.log")

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove any existing handlers to avoid duplication
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # --- Console Handler ---
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    
    # --- File Handler ---
    # Use a standard FileHandler since the file is already unique per run.
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.INFO)

    # --- Formatter ---
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # --- Add Handlers ---
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.info(f"Logging initialized. Log file: {log_file}")

# Do not automatically configure. The main application will call the setup function.
