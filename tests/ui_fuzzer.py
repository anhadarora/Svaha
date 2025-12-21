import random
import os
import json
from PySide6.QtWidgets import QComboBox, QSpinBox, QCheckBox, QDateEdit, QLineEdit, QListWidget
from PySide6.QtCore import Qt, QDate

class TrainerWalker:
    """
    A utility to run automated test scenarios on the TrainerScreen's setup wizard.
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
                    "data_source": {"symbols": ["RELIANCE"]},
                    "validation_method": "Date Range",
                    "model_architecture": "ViT-Base-Patch16",
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

            self.qtbot.wait(100)

            # 2. Execute action
            self.setup_widget.apply_and_run_button.click()
            self.history.append("Clicked 'Apply and Run'.")

            # 3. Verify outcome
            outcome = permutation["expected_outcome"]
            if outcome == "success":
                # Wait for the training to finish and the UI to switch to the results tab
                self.qtbot.waitUntil(lambda: self.trainer_screen.tab_widget.currentWidget() == self.trainer_screen.results_tab, timeout=90000)
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


class DownloaderWalker:
    """
    A utility to run automated test scenarios on the DownloaderScreen.
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


class UserWalker:
    """
    A utility to run automated test scenarios on the UserScreen.
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
