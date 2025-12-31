import time
import random
import json
import os
from PySide6.QtCore import Qt

from tests.chaos_monkey import UserMonkey

def test_user_scenarios(main_window, qtbot):
    """
    Tests the UserScreen auto-login and logout flows.
    This test relies on a persistent session.json file having been created
    by a real user login.
    """
    # --- Test Setup ---
    seed_value = time.time()
    random.seed(seed_value)
    print(f"Chaos Monkey running with seed: {seed_value}")

    # Wait for the main window to run its auto-login check
    qtbot.wait(500) 

    # --- Execution ---
    walker = UserMonkey(main_window, qtbot)
    walker.history.append(f"Seed for this run: {seed_value}")

    try:
        # No mocking is needed as we are using the real, persistent session
        walker.run_scenarios()
    
    finally:
        # --- Reporting ---
        report_path = os.path.abspath("./chaos_history_user.json")
        print(f"Writing chaos history to {report_path}")
        try:
            with open(report_path, "w") as f:
                json.dump(walker.history, f, indent=4)
        except Exception as e:
            print(f"Error writing chaos history file: {e}")

    # --- Assertion ---
    assert walker.all_scenarios_passed, \
        f"One or more user chaos scenarios failed. " \
        f"Check {os.path.basename(report_path)} with seed {seed_value} for details."