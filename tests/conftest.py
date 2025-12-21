import pytest
from PySide6.QtWidgets import QApplication
import os
import shutil

# Make sure the application's source code is in the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui_pyside6.main_screen import MainScreen
from ui_pyside6.session_manager import SessionManager
from api.kite.client import kite_api # Import the real kite_api instance

@pytest.fixture(scope='function', autouse=True)
def manage_test_artifacts():
    """
    A fixture that runs for every test function.
    It cleans up temporary artifacts created during a test run.
    """
    # Define paths to artifacts that might be created
    build_dir = os.path.abspath("./build")
    models_dir = os.path.join(build_dir, "models")
    data_dir = os.path.join(build_dir, "data")
    history_path = os.path.join(build_dir, "history.json")
    config_path = os.path.join(build_dir, "last_applied_config.json")

    # --- SETUP ---
    # Clean up artifacts from previous runs before the test starts
    if os.path.exists(models_dir):
        shutil.rmtree(models_dir)
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    if os.path.exists(history_path):
        os.remove(history_path)
    if os.path.exists(config_path):
        os.remove(config_path)

    yield # Test runs here

    # --- TEARDOWN ---
    # Clean up again after the test runs
    if os.path.exists(models_dir):
        shutil.rmtree(models_dir)
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    if os.path.exists(history_path):
        os.remove(history_path)
    if os.path.exists(config_path):
        os.remove(config_path)


@pytest.fixture
def main_window(qtbot):
    """
    Pytest fixture to create and setup the MainScreen for testing.
    This now uses the REAL SessionManager and KiteAPI to allow for
    testing with a persistent, authenticated session.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Use the real session manager and kite_api instance
    session_manager = SessionManager(kite_api=kite_api)

    window = MainScreen(session_manager=session_manager)
    
    qtbot.addWidget(window)
    
    yield window
    
    window.close()
