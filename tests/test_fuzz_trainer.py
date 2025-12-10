import time
import random
import json
import os

from tests.ui_fuzzer import WizardWalker

def test_fuzz_wizard_completion(main_window, qtbot):
    """
    Tests the SetupTabWidget wizard by running an automated 'monkey test'.

    - Sets a random seed for reproducibility.
    - Uses WizardWalker to interact with the UI.
    - Logs all actions to a JSON file.
    - Fails if the wizard gets stuck before reaching the last page.
    """
    # Ensure the Trainer screen is the active tab
    main_window.tab_widget.setCurrentWidget(main_window.trainer_screen)
    qtbot.wait(100) # Allow time for the tab to become visible

    # 1. Seeding
    seed_value = time.time()
    random.seed(seed_value)
    print(f"Fuzz test running with seed: {seed_value}")

    # 2. Execution
    walker = WizardWalker(main_window, qtbot)
    walker.history.append(f"Seed for this run: {seed_value}")

    try:
        walker.walk_wizard()
    
    finally:
        # 3. Reporting
        report_path = os.path.abspath("./fuzz_history.json")
        print(f"Writing fuzz history to {report_path}")
        try:
            with open(report_path, "w") as f:
                json.dump(walker.history, f, indent=4)
        except Exception as e:
            print(f"Error writing fuzz history file: {e}")

    # 4. Assertion
    final_index = walker.setup_widget.stack.currentIndex()
    last_page_index = walker.setup_widget.stack.count() - 1
    
    assert final_index == last_page_index, \
        f"Wizard walk failed to complete. Stuck on page {final_index}/{last_page_index}. " \
        f"Check fuzz_history.json with seed {seed_value} for details."

