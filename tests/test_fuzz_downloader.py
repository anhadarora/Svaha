import time
import random
import json
import os
from unittest.mock import patch, MagicMock
from PySide6.QtCore import Qt
from datetime import datetime

from tests.ui_fuzzer import DownloaderWalker

def test_fuzz_downloader_scenarios(main_window, qtbot):
    """
    Tests the DownloaderScreen by running a series of automated scenarios.
    """
    # Ensure the Downloader screen is the active tab
    qtbot.mouseClick(main_window.btn_downloader, Qt.LeftButton)
    qtbot.wait(100) # Allow time for the tab to become visible

    # --- Test Setup ---
    seed_value = time.time()
    random.seed(seed_value)
    print(f"Fuzz test running with seed: {seed_value}")

    # Wait for the downloader's internal data to load
    # This is crucial as it populates the symbol lists.
    qtbot.wait(1000) 

    # --- Mocking ---
    # We will let the real DownloadWorker run, but mock the Kite API calls it makes.
    mock_kite = MagicMock()
    
    # Mock historical_data to return some fake data for the success scenario
    mock_kite.historical_data.return_value = [
        {'date': datetime.now(), 'open': 100, 'high': 110, 'low': 90, 'close': 105, 'volume': 1000}
    ]
    
    # Mock instruments to provide the symbols we'll use in the tests
    mock_kite.instruments.return_value = [
        {'instrument_token': 123, 'tradingsymbol': 'AIAENG', 'instrument_type': 'EQ'},
        {'instrument_token': 456, 'tradingsymbol': 'ACC', 'instrument_type': 'EQ'},
        {'instrument_token': 789, 'tradingsymbol': 'RELIANCE', 'instrument_type': 'EQ'},
    ]

    # --- Execution ---
    walker = DownloaderWalker(main_window, qtbot)
    walker.history.append(f"Seed for this run: {seed_value}")

    try:
        # We only need to patch the get_kite method to return our mock object.
        # The DownloadWorker will be instantiated and run, but its API calls will be mocked.
        with patch.object(main_window.session_manager, 'get_kite', return_value=mock_kite):
            walker.run_scenarios()
    
    finally:
        # --- Reporting ---
        report_path = os.path.abspath("./fuzz_history_downloader.json")
        print(f"Writing fuzz history to {report_path}")
        try:
            with open(report_path, "w") as f:
                json.dump(walker.history, f, indent=4)
        except Exception as e:
            print(f"Error writing fuzz history file: {e}")

    # --- Assertion ---
    # The assertion will be based on the scenarios' success, recorded by the walker.
    assert walker.all_scenarios_passed, \
        f"One or more downloader fuzzing scenarios failed. " \
        f"Check fuzz_history_downloader.json with seed {seed_value} for details."