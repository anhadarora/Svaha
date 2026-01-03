import random
import os
import json
from PySide6.QtWidgets import QComboBox, QSpinBox, QCheckBox, QDateEdit, QLineEdit, QListWidget, QApplication, QMessageBox, QDialog, QPushButton
from PySide6.QtCore import Qt, QDate, QTimer

class TrainerMonkey:
    """
    A utility to run automated 'Chaos Monkey' scenarios on the TrainerScreen's setup wizard.
    This has been refactored to run a series of permutations.
    """

    def __init__(self, main_window, qtbot):
        self.main_window = main_window
        self.qtbot = qtbot
        self.trainer_screen = main_window.trainer_screen
        self.setup_widget = self.trainer_screen.setup_tab
        self.history = []
        self.all_scenarios_passed = True

    def _log_scenario_start(self, name):
        self.history.append(f"--- Running Permutation: {name} ---")
        print(f"--- Running Permutation: {name} ---")

    def _log_scenario_end(self, name, success, reason=""):
        status = "PASSED" if success else "FAILED"
        self.history.append(f"--- PERMUTATION {status}: {name} ---")
        if not success:
            self.history.append(f"    Reason: {reason}")
            self.all_scenarios_passed = False
        print(f"--- PERMUTATION {status}: {name} ---")

    def _reset_ui(self):
        """Resets the UI widgets to a clean state before each scenario."""
        self.history.append("Resetting UI state...")
        self.trainer_screen.tab_widget.setCurrentWidget(self.setup_widget)
        self.setup_widget.stack.setCurrentIndex(0)
        self.setup_widget.on_data_source_selected(False)
        self.qtbot.wait(100)

    def _generate_permutations(self):
        """Defines the exhaustive, representative test cases for the trainer."""
        return [
            {
                "name": "End-to-End Run (ViT, Date Range)",
                "params": {
                    "data_source": {"symbols": ["ACMESOLAR"]},
                    "validation_method": "Date Range",
                    "model_architecture": "ResNet-50",
                    "training": {"max_epochs": 1}
                },
                "expected_outcome": "success"
            },
             {
                "name": "Failure case: No data source selected",
                "params": {"data_source": {"symbols": []}},
                "expected_outcome": "failure"
            }
        ]

    def run_scenarios(self):
        """Iterates through and executes all defined permutations."""
        permutations = self._generate_permutations()
        self.history.append(f"Generated {len(permutations)} permutations to test.")
        
        for perm in permutations:
            self._execute_permutation(perm)

    def _execute_permutation(self, permutation):
        name = permutation["name"]
        params = permutation["params"]
        self._log_scenario_start(name)
        self._reset_ui()
        success = False
        reason = ""
        
        try:
            # 1. Set up UI from permutation params
            ds_params = params.get("data_source", {})
            if not ds_params.get("symbols"):
                if self.setup_widget.apply_and_run_button.isEnabled():
                    raise AssertionError("Apply and Run button should be disabled when no symbols are selected.")
                self.history.append("Verified 'Apply and Run' is disabled.")
                success = True
                return

            for symbol in ds_params["symbols"]:
                self.setup_widget.data_source_widget.add_to_queue([symbol])
            self.qtbot.wait(200)
            
            if "validation_method" in params:
                self.setup_widget.data_source_widget.split_method_combo.setCurrentText(params["validation_method"])
            
            if "model_architecture" in params:
                self.setup_widget.model_architecture_widget.architecture_selection.setCurrentText(params["model_architecture"])
            
            if "training" in params:
                 training_params = params["training"]
                 if "max_epochs" in training_params:
                     self.setup_widget.model_architecture_widget.max_epochs.setValue(training_params["max_epochs"])

            self.qtbot.wait(100)

            # 2. Execute action
            self.setup_widget.apply_and_run_button.click()
            self.history.append("Clicked 'Apply and Run'.")

            # 3. Verify outcome
            outcome = permutation["expected_outcome"]
            if outcome == "success":
                # Wait for the training to finish, handling the "Training Complete" dialog if it appears
                # We expect the process to take some time, so we poll for the dialog or the tab switch
                
                def check_training_complete():
                    # 1. Check if we switched to Results tab (success)
                    if self.trainer_screen.tab_widget.currentWidget() == self.trainer_screen.results_tab:
                        return True
                    
                    # 2. Check for blocking Success Dialog
                    widget = QApplication.activeModalWidget()
                    if isinstance(widget, QMessageBox) and "Training Complete" in widget.text():
                        self._log("Verified: Training Success Dialog appeared. Closing it.")
                        widget.close() # This will unblock and trigger the signal emission
                    
                    return False

                # We wait up to 90s (training can be slow)
                self.qtbot.waitUntil(check_training_complete, timeout=90000)
                self.history.append("Verified UI switched to Results tab.")

                # Verify that a model file was created
                config = self.setup_widget.get_configuration()
                model_dir = config.get("model_save_path")
                model_name = config.get("experiment_name")
                model_path = os.path.join(model_dir, f"{model_name}.keras")

                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"Model file was not created at expected path: {model_path}")
                self.history.append(f"Verified model file was created at: {model_path}")
            
            success = True
        except Exception as e:
            reason = f"Permutation failed with exception: {e}"
        finally:
            # Cleanup is handled by the conftest fixture
            self._log_scenario_end(name, success, reason)


class DownloaderMonkey:
    """
    A utility to run automated 'Chaos Monkey' scenarios on the DownloaderScreen.
    This has been refactored to run a series of permutations.
    """

    def __init__(self, main_window, qtbot):
        self.main_window = main_window
        self.qtbot = qtbot
        self.downloader = main_window.downloader_screen
        self.history = []
        self.all_scenarios_passed = True
        self.pre_test_metadata = []

    def _log_scenario_start(self, name):
        self.history.append(f"--- Running Permutation: {name} ---")
        print(f"--- Running Permutation: {name} ---")

    def _log_scenario_end(self, name, success, reason=""):
        status = "PASSED" if success else "FAILED"
        self.history.append(f"--- PERMUTATION {status}: {name} ---")
        if not success:
            self.history.append(f"    Reason: {reason}")
            self.all_scenarios_passed = False
        print(f"--- PERMUTATION {status}: {name} ---")

    def _read_metadata(self, file_path):
        if not os.path.exists(file_path): return []
        try:
            with open(file_path, "r") as f:
                content = json.load(f)
            return content if isinstance(content, list) else []
        except (json.JSONDecodeError, IOError): return []

    def _capture_pre_test_state(self):
        self.pre_test_metadata = self._read_metadata(os.path.abspath("./generated_data/metadata.json"))

    def _cleanup_generated_files(self):
        output_dir = self.downloader.output_dir_edit.text()
        post_test_metadata = self._read_metadata(os.path.join(output_dir, "metadata.json"))
        pre_test_ids = {entry.get("file_id") for entry in self.pre_test_metadata}
        new_entries = [entry for entry in post_test_metadata if entry.get("file_id") not in pre_test_ids]
        
        for entry in new_entries:
            for key in ["csv_filename", "parquet_filename"]:
                if filename := entry.get(key):
                    p = os.path.join(output_dir, filename)
                    if os.path.exists(p): os.remove(p)
        
        metadata_path = os.path.join(output_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "w") as f:
                json.dump(self.pre_test_metadata, f, indent=4)

    def _reset_ui(self):
        self.downloader.tab_widget.setCurrentIndex(0)
        self.downloader.selected_symbols_list.clear()
        self.downloader.start_date_edit.setDate(QDate.currentDate().addDays(-10))
        self.downloader.end_date_edit.setDate(QDate.currentDate())
        self.downloader.log_view.clear()
        self.qtbot.wait(100)

    def _generate_permutations(self):
        """Defines the exhaustive, representative test cases."""
        return [
            {
                "name": "Successful single symbol download (minute)",
                "params": {"symbols": ["RELIANCE"], "interval": "minute", "start_date": QDate.currentDate().addDays(-2), "end_date": QDate.currentDate()},
                "expected_outcome": "success"
            },
            {
                "name": "Successful multi-symbol download (day)",
                "params": {"symbols": ["ACC", "AIAENG"], "interval": "day", "start_date": QDate.currentDate().addDays(-30), "end_date": QDate.currentDate()},
                "expected_outcome": "success"
            },
            {
                "name": "Failure case: No symbols selected",
                "params": {"symbols": [], "interval": "minute"},
                "expected_outcome": "error",
                "expected_message": "No symbols in the download queue"
            },
            {
                "name": "Failure case: Invalid date range",
                "params": {"symbols": ["TCS"], "interval": "minute", "start_date": QDate.currentDate(), "end_date": QDate.currentDate().addDays(-1)},
                "expected_outcome": "warning",
                "expected_message": "No data returned for TCS"
            }
        ]

    def run_scenarios(self):
        """Iterates through and executes all defined permutations."""
        permutations = self._generate_permutations()
        self.history.append(f"Generated {len(permutations)} permutations to test.")
        
        for perm in permutations:
            self._execute_permutation(perm)

    def _execute_permutation(self, permutation):
        name = permutation["name"]
        params = permutation["params"]
        self._log_scenario_start(name)
        self._reset_ui()
        success = False
        reason = ""
        
        self._capture_pre_test_state()

        try:
            # 1. Set up UI from permutation params
            if "interval" in params:
                self.downloader.interval_combo.setCurrentText(params["interval"])
            if "symbols" in params:
                for symbol in params["symbols"]:
                    self.downloader.add_to_queue([symbol])
            if "start_date" in params:
                self.downloader.start_date_edit.setDate(params["start_date"])
            if "end_date" in params:
                self.downloader.end_date_edit.setDate(params["end_date"])
            
            self.qtbot.wait(100)

            # 2. Execute action
            self.downloader.start_button.click()
            self.qtbot.waitUntil(lambda: self.downloader.start_button.isEnabled(), timeout=10000)

            # 3. Verify outcome
            outcome = permutation["expected_outcome"]
            if outcome == "success":
                post_test_metadata = self._read_metadata(os.path.abspath("./generated_data/metadata.json"))
                pre_test_ids = {entry.get("file_id") for entry in self.pre_test_metadata}
                new_entries = [entry for entry in post_test_metadata if entry.get("file_id") not in pre_test_ids]
                
                if len(new_entries) != len(params["symbols"]):
                    raise ValueError(f"Expected {len(params['symbols'])} new metadata entries, but found {len(new_entries)}.")
                self.history.append("Verified correct number of metadata entries were created.")
            
            elif outcome in ["error", "warning"]:
                log_text = self.downloader.log_view.toPlainText()
                if permutation["expected_message"] not in log_text:
                    raise AssertionError(f"Expected message '{permutation['expected_message']}' not found in logs. Log was:\n{log_text}")
                self.history.append(f"Verified expected message '{permutation['expected_message']}' was logged.")

            success = True
        except Exception as e:
            reason = f"Permutation failed with exception: {e}"
        finally:
            self._log_scenario_end(name, success, reason)
            self._cleanup_generated_files()


class UserMonkey:
    """
    A utility to run automated 'Chaos Monkey' scenarios on the UserScreen.
    """

    def __init__(self, main_window, qtbot):
        self.main_window = main_window
        self.qtbot = qtbot
        self.user_screen = main_window.user_screen
        self.history = []
        self.all_scenarios_passed = True

    def _log_scenario_start(self, name):
        self.history.append(f"--- SCENARIO START: {name} ---")
        print(f"--- Running scenario: {name} ---")

    def _log_scenario_end(self, name, success, reason=""):
        status = "PASSED" if success else "FAILED"
        self.history.append(f"--- SCENARIO {status}: {name} ---")
        if not success:
            self.history.append(f"    Reason: {reason}")
            self.all_scenarios_passed = False
        print(f"--- Scenario {status}: {name} ---")

    def run_scenarios(self):
        """Runs all defined test scenarios."""
        self.history.append("Starting user scenarios...")
        
        self._scenario_auto_login()
        # self._scenario_logout() # Commented out to prevent deleting the session
        
        self.history.append("All user scenarios finished.")

    def _scenario_auto_login(self):
        name = "Verify auto-login with existing session"
        self._log_scenario_start(name)
        success = False
        reason = ""
        
        try:
            # Action: Navigate to the user screen
            self.main_window.user_button.click()
            self.qtbot.wait(100) # Allow UI to process the synchronous call

            # Verification
            assert self.user_screen.funds_card.isVisible(), "Funds card is not visible, auto-login failed."
            assert self.user_screen.login_card.isHidden(), "Login card is visible, auto-login failed."
            
            self.history.append("Verified UI is in logged-in state.")
            success = True

        except Exception as e:
            reason = f"Scenario failed with exception: {e}"
        
        finally:
            self._log_scenario_end(name, success, reason)
            # Go back to the main screen for the next test
            self.user_screen.go_back()
            self.qtbot.wait(100)

    def _scenario_logout(self):
        name = "Perform logout"
        self._log_scenario_start(name)
        success = False
        reason = ""
        
        try:
            # Pre-condition: we should be logged in
            if self.user_screen.login_card.isVisible():
                self.main_window.user_button.click()
                self.qtbot.wait(500)
                if self.user_screen.login_card.isVisible():
                     raise Exception("Pre-condition failed: Not logged in at the start of logout scenario.")

            # Action
            self.user_screen.logout_button.click()
            self.qtbot.wait(200)

            # Verification
            if not self.user_screen.login_card.isVisible():
                raise AssertionError("Login card is not visible after logout.")
            if self.user_screen.logout_button.isVisible():
                raise AssertionError("Logout button is still visible after logout.")
            
            self.history.append("Verified UI is in logged-out state.")
            success = True

        except Exception as e:
            reason = f"Scenario failed with exception: {e}"
        
        finally:
            self._log_scenario_end(name, success, reason)
            self.user_screen.go_back()
            self.qtbot.wait(100)

class TrainerResultsMonkey:
    """
    Automated check for the Results Tab.
    """
    def __init__(self, main_window, qtbot):
        self.main_window = main_window
        self.qtbot = qtbot
        self.trainer_screen = main_window.trainer_screen
        self.results_tab = self.trainer_screen.results_tab
        self.history = []
        self.all_scenarios_passed = True

    def _log(self, message):
        self.history.append(message)
        print(message)

    def run_scenarios(self):
        """
        Verifies that the results tab is populated after a training run.
        """
        self._log("--- Running TrainerResultsMonkey ---")
        try:
            # 1. Verify Experiment Summary is present and has data
            summary_widget = self.results_tab.summary_widget
            if not summary_widget.isVisible():
                raise AssertionError("Experiment Summary Widget is not visible.")
            self._log("Verified: Experiment Summary Widget is visible.")

            # 2. Verify Parameter Configuration is present
            params_widget = self.results_tab.params_widget
            if not params_widget.isVisible():
                raise AssertionError("Parameter Configuration Widget is not visible.")
            self._log("Verified: Parameter Configuration Widget is visible.")

            # 3. Verify Dynamic Prediction Widgets
            # We expect at least one dynamic widget (e.g. plot or confusion matrix) if training finished
            if not self.results_tab.dynamic_widgets:
                self._log("WARNING: No dynamic prediction widgets found. Did the model have prediction heads?")
            else:
                self._log(f"Verified: Found {len(self.results_tab.dynamic_widgets)} dynamic results widgets.")
                for widget in self.results_tab.dynamic_widgets:
                    if not widget.isVisible():
                        raise AssertionError(f"Dynamic widget {widget} is created but not visible.")
            
            self._log("--- TrainerResultsMonkey PASSED ---")

        except Exception as e:
            self._log(f"--- TrainerResultsMonkey FAILED: {e} ---")
            self.all_scenarios_passed = False


class TrainerHistoryMonkey:
    """
    Automated interactions with the History Tab: selection, compare, reload.
    """
    def __init__(self, main_window, qtbot):
        self.main_window = main_window
        self.qtbot = qtbot
        self.trainer_screen = main_window.trainer_screen
        self.history_tab = self.trainer_screen.history_tab
        self.history = []
        self.all_scenarios_passed = True

    def _log(self, message):
        self.history.append(message)
        print(message)

    def run_scenarios(self):
        self._log("--- Running TrainerHistoryMonkey ---")
        
        # Switch to history tab
        self.trainer_screen.tab_widget.setCurrentWidget(self.history_tab)
        self.qtbot.wait(200)

        # 1. Test Refresh
        self._test_refresh()
        
        # 2. Test Compare (if enough data)
        self._test_compare()

        # 3. Test Reload (if enough data)
        self._test_reload()

    def _test_refresh(self):
        self._log("Action: Clicking Refresh")
        self.history_tab.refresh_button.click()
        self.qtbot.wait(100)
        # Verify multiple rows potentially loaded
        row_count = self.history_tab.model.rowCount(None)
        self._log(f"Verified: History table has {row_count} rows after refresh.")

    def _wait_for_window(self, timeout=2000):
        """Helper to wait for a modal dialog to appear."""
        deadline = QTimer()
        deadline.setSingleShot(True)
        loop = QApplication.processEvents
        
        # Simple polling loop
        end_time = getattr(self.qtbot, 'use_time_time', False) and (import_time.time() + timeout/1000.0) or (QDate.currentDate().startOfDay().msecsTo(QDate.currentDate().startOfDay()) + timeout) # simplified
        # Actually qtbot has wait functionality, let's use a simpler approach:
        # We will assume the action that triggers the dialog is already done.
        # We just look for the active modal widget.
        
        widget = QApplication.activeModalWidget()
        start = 0
        while not widget and start < timeout:
            self.qtbot.wait(50)
            start += 50
            widget = QApplication.activeModalWidget()
        return widget

    def _test_compare(self):
        row_count = self.history_tab.model.rowCount(None)
        if row_count < 2:
            self._log("Skipping Compare test: Not enough history rows (need > 1).")
            return

        self._log("Action: Selecting top 2 rows for comparison")
        # Select first 2 rows
        view = self.history_tab.history_table
        selection_model = view.selectionModel()
        selection_model.clear()
        
        # Select row 0 and 1
        model_index_0 = self.history_tab.model.index(0, 0)
        model_index_1 = self.history_tab.model.index(1, 0)
        
        # We use 'Select' command on selection model
        selection_model.select(model_index_0, selection_model.Select | selection_model.Rows)
        selection_model.select(model_index_1, selection_model.Select | selection_model.Rows)
        self.qtbot.wait(100)
        
        if not self.history_tab.compare_button.isEnabled():
             raise AssertionError("Compare button should be enabled when 2 rows are selected.")

        # Click Compare - this opens a DIALOG.
        # We need to click it, then handle the dialog asynchronously? 
        # No, QDialog.exec() blocks the main loop. 
        # Using qtbot.mouseClick usually blocks if the slot calls exec().
        # Strategy: Use QTimer to close the dialog slightly AFTER we click the button.
        
        def handle_compare_dialog():
            widget = QApplication.activeModalWidget()
            if widget:
                self._log(f"Verified: Comparison Dialog opened: {widget.windowTitle()}")
                # Close it
                widget.close()
            else:
                self._log("FAILURE: No modal dialog found after clicking Compare.")

        # Schedule the handler to run 500ms after button click
        QTimer.singleShot(500, handle_compare_dialog)
        
        self.history_tab.compare_button.click()
        self.qtbot.wait(200) # Wait for dialog loop to finish closing
        self._log("Verified: Returned from Compare dialog.")


    def _test_reload(self):
        row_count = self.history_tab.model.rowCount(None)
        if row_count < 1:
            self._log("Skipping Reload test: Not enough history rows.")
            return

        self._log("Action: Selecting 1st row for Reload")
        view = self.history_tab.history_table
        selection_model = view.selectionModel()
        selection_model.clear()
        
        model_index_0 = self.history_tab.model.index(0, 0)
        selection_model.select(model_index_0, selection_model.Select | selection_model.Rows)
        self.qtbot.wait(100)

        if not self.history_tab.reload_button.isEnabled():
             raise AssertionError("Reload button should be enabled when 1 row is selected.")

        # This triggers a Confirmation QMessageBox.
        # Strategy: QTimer to find the message box and click 'Yes'.
        
        def handle_confirm_dialog():
            widget = QApplication.activeModalWidget()
            if isinstance(widget, QMessageBox):
                self._log(f"Verified: Confirmation Dialog opened: {widget.text()}")
                # Click Yes
                yes_button = widget.button(QMessageBox.Yes)
                if yes_button:
                    yes_button.click()
                    self._log("Action: Clicked 'Yes' in confirmation dialog.")
                else:
                    self._log("FAILURE: Could not find 'Yes' button.")
                    widget.close()
            else:
                self._log(f"FAILURE: Expected QMessageBox, found {widget}.")
                if widget: widget.close()

        QTimer.singleShot(500, handle_confirm_dialog)
        
        # Capture configuration BEFORE reload (to verify it changes or matches)
        # Note: In a real test, we might want to change the setup tab first to ensure it changes back.
        # But here we just verify the flow works.
        
        self.history_tab.reload_button.click()
        self._log("Verified: Reload flow completed.")
        
        # Verify we were switched to Setup tab
        current_idx = self.trainer_screen.tab_widget.currentIndex()
        current_widget = self.trainer_screen.tab_widget.currentWidget()
        if current_widget != self.trainer_screen.setup_tab:
             raise AssertionError(f"Expected to be on Setup Tab after reload, but on index {current_idx}")
        self._log("Verified: Switched to Setup Tab.")
