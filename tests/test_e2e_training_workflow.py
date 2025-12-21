import json
import os
import shutil
from unittest.mock import patch, MagicMock

import pytest
from PySide6.QtCore import Qt


# File paths for cleanup
HISTORY_FILE = os.path.abspath("./build/history.json")
CONFIG_FILE = os.path.abspath("./build/last_applied_config.json")


@pytest.fixture
def history_backup():
    """Fixture to handle backup and restoration of the history file."""
    # --- Setup ---
    history_backup_path = ""
    if os.path.exists(HISTORY_FILE):
        history_backup_path = HISTORY_FILE + ".bak"
        shutil.copy(HISTORY_FILE, history_backup_path)

    yield  # The test runs here

    # --- Teardown ---
    # Restore the original history file
    if os.path.exists(history_backup_path):
        shutil.move(history_backup_path, HISTORY_FILE)
    # Or if no original existed, remove the one created by the test
    elif os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    
    # Clean up the config file created by the test
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)


def test_e2e_training_workflow(main_window, qtbot, history_backup):
    """
    Tests the full end-to-end training workflow:
    1. Configure a run in the Setup tab.
    2. Start the run.
    3. Mock the training process in the Monitor tab.
    4. Verify the UI moves to the Results tab and displays data.
    5. Verify the run is saved in the History tab.
    """
    trainer_screen = main_window.trainer_screen
    setup_widget = trainer_screen.setup_tab
    
    # --- 1. Configure the Run ---
    main_window.tab_widget.setCurrentWidget(trainer_screen)
    qtbot.wait(500) # Allow data to load

    # Select a data source to enable the UI
    assert setup_widget.data_source_widget.available_instruments_list.count() > 0
    item = setup_widget.data_source_widget.available_instruments_list.item(0)
    item_rect = setup_widget.data_source_widget.available_instruments_list.visualItemRect(item)
    qtbot.mouseDClick(
        setup_widget.data_source_widget.available_instruments_list.viewport(),
        Qt.LeftButton,
        pos=item_rect.center()
    )
    qtbot.wait(100)

    # --- 2. Mock the Training Worker ---
    
    dummy_results = {"final_loss": 0.123, "accuracy": 0.95, "experiment_name": "e2e_test_run"}
    mock_comm = MagicMock()
    mock_worker_instance = MagicMock()
    mock_worker_instance.comm = mock_comm
    mock_worker_instance.start.side_effect = lambda: mock_comm.training_finished.emit(dummy_results)

    # --- 3. Start the Run & Verify ---

    # Patch the worker and, critically, the exec method of QMessageBox to prevent blocking
    with patch('analysis.training_worker.TrainingWorker', return_value=mock_worker_instance), \
         patch('PySide6.QtWidgets.QMessageBox.exec', return_value=None):
        
        qtbot.mouseClick(setup_widget.apply_and_run_button, Qt.LeftButton)

        # Wait until the tab has switched to the Monitor tab
        qtbot.waitUntil(
            lambda: trainer_screen.tab_widget.currentWidget() == trainer_screen.monitor_tab,
            timeout=5000
        )

        # Wait until the training_run_completed signal is emitted from the TrainerScreen
        with qtbot.waitSignal(trainer_screen.training_run_completed, timeout=5000) as blocker:
            pass
        
        assert blocker.args[0] == dummy_results

    # --- 4. Verify Results Tab ---
    # Wait until the tab has switched to the Results tab
    qtbot.waitUntil(
        lambda: trainer_screen.tab_widget.currentWidget() == trainer_screen.results_tab,
        timeout=5000
    )
    
    summary_text = trainer_screen.results_tab.experiment_summary_widget.toPlainText()
    assert "e2e_test_run" in summary_text
    assert "0.123" in summary_text
    assert "0.95" in summary_text

    # --- 5. Verify History Tab ---
    trainer_screen.tab_widget.setCurrentWidget(trainer_screen.history_tab)
    qtbot.wait(200)

    history_widget = trainer_screen.history_tab
    assert history_widget.history_list.count() > 0
    first_item = history_widget.history_list.item(0)
    assert "e2e_test_run" in first_item.text()

    print("\nEnd-to-end test completed successfully.")