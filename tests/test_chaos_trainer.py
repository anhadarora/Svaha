import time
import random
import json
import os
# from unittest.mock import patch # REMOVED: No mocking allowed
from PySide6.QtCore import Qt

from tests.chaos_monkey import TrainerMonkey, TrainerResultsMonkey, TrainerHistoryMonkey

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
    print(f"Chaos Monkey running with seed: {seed_value}")

    # Wait for any initial data loading
    qtbot.wait(500) 

    # --- Execution ---
    walker = TrainerMonkey(main_window, qtbot)
    walker.history.append(f"Seed for this run: {seed_value}")

    try:
        # NO MOCKS: Running with full system integration
        walker.run_scenarios()
        
        # If the trainer run was successful, we should now be reachable for Results verification
        results_monkey = TrainerResultsMonkey(main_window, qtbot)
        results_monkey.run_scenarios()
        walker.history.extend(results_monkey.history) # augment main history
        if not results_monkey.all_scenarios_passed:
            walker.all_scenarios_passed = False

        # Now test History Tab interactions
        history_monkey = TrainerHistoryMonkey(main_window, qtbot)
        history_monkey.run_scenarios()
        walker.history.extend(history_monkey.history) # augment main history
        if not history_monkey.all_scenarios_passed:
            walker.all_scenarios_passed = False
    
    finally:
        # --- Reporting ---
        report_path = os.path.abspath("./chaos_history_trainer.json")
        print(f"Writing chaos history to {report_path}")
        try:
            with open(report_path, "w") as f:
                json.dump(walker.history, f, indent=4)
        except Exception as e:
            print(f"Error writing chaos history file: {e}")

    # --- Assertion ---
    assert walker.all_scenarios_passed, \
        f"One or more trainer chaos scenarios failed. " \
        f"Check {os.path.basename(report_path)} with seed {seed_value} for details."
