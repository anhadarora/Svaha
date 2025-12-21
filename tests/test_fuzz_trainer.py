import time
import random
import json
import os
from unittest.mock import patch
from PySide6.QtCore import Qt

from tests.ui_fuzzer import TrainerWalker

def test_trainer_scenarios(main_window, qtbot):
    """
    Tests the TrainerScreen setup wizard by running a series of automated scenarios.
    This test runs the REAL TrainingWorker to verify the end-to-end process.
    """
    # Ensure the Trainer screen is the active tab
    qtbot.mouseClick(main_window.btn_trainer, Qt.LeftButton)
    qtbot.wait(100) # Allow time for the tab to become visible

    seed_value = time.time()
    random.seed(seed_value)
    print(f"Fuzz test running with seed: {seed_value}")

    # Wait for any initial data loading
    qtbot.wait(500) 

    # --- Execution ---
    walker = TrainerWalker(main_window, qtbot)
    walker.history.append(f"Seed for this run: {seed_value}")

    try:
        # We only patch QMessageBox.exec to prevent the success dialog 
        # from blocking the test run. The TrainingWorker will be real.
        with patch('PySide6.QtWidgets.QMessageBox.exec', return_value=None):
            walker.run_scenarios()
    
    finally:
        # --- Reporting ---
        report_path = os.path.abspath("./fuzz_history_trainer.json")
        print(f"Writing fuzz history to {report_path}")
        try:
            with open(report_path, "w") as f:
                json.dump(walker.history, f, indent=4)
        except Exception as e:
            print(f"Error writing fuzz history file: {e}")

    # --- Assertion ---
    assert walker.all_scenarios_passed, \
        f"One or more trainer fuzzing scenarios failed. " \
        f"Check {os.path.basename(report_path)} with seed {seed_value} for details."
