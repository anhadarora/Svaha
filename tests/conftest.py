import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock

# Make sure the application's source code is in the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui_pyside6.main_screen import MainScreen
from ui_pyside6.session_manager import SessionManager

@pytest.fixture
def main_window(qtbot):
    """
    Pytest fixture to create and setup the MainScreen for testing.
    
    - Initializes a QApplication instance.
    - Mocks the SessionManager to avoid network dependencies.
    - Instantiates the MainScreen with the mock.
    - Registers the window with qtbot for UI interaction testing.
    - Returns the MainScreen instance.
    """
    # Ensure a QApplication instance exists.
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Mock the SessionManager
    mock_session_manager = Mock(spec=SessionManager)
    mock_session_manager.is_session_valid.return_value = False # Default mock state

    # Initialize the MainScreen with the mock
    window = MainScreen(session_manager=mock_session_manager)
    
    # Register the widget with qtbot for testing
    qtbot.addWidget(window)
    
    yield window
    
    # Teardown: close the window after the test is done
    window.close()

