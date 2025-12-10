import sys
import os
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Signal
from .trainer.setup_tab_widget import SetupTabWidget
from .trainer.monitor_tab_widget import MonitorTabWidget
from .trainer.results_tab_widget import ResultsTabWidget
from .history.history_widget import HistoryWidget


class TrainerScreen(QWidget):
    history_updated = Signal()

    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.setup_tab = SetupTabWidget()
        self.monitor_tab = MonitorTabWidget()
        self.results_tab = ResultsTabWidget()
        self.history_tab = HistoryWidget()

        self.tab_widget.addTab(self.setup_tab, "Setup")
        self.tab_widget.addTab(self.monitor_tab, "Monitor")
        self.tab_widget.addTab(self.results_tab, "Results")
        self.tab_widget.addTab(self.history_tab, "History")

        # Connect signals between tabs
        self.setup_tab.start_training_requested.connect(self._on_start_training_requested)
        self.monitor_tab.training_run_completed.connect(self._on_training_completed)
        self.history_updated.connect(self.history_tab.load_history)

    def _on_start_training_requested(self):
        """Switches to the monitor tab and starts the training process."""
        self.tab_widget.setCurrentWidget(self.monitor_tab)
        self.monitor_tab.begin_training()

    def _on_training_completed(self, summary_data):
        """
        Receives the results, saves them to the history database,
        and populates the results tab.
        """
        if not summary_data:
            return

        self._save_run_to_history(summary_data)
        
        self.results_tab.load_results(summary_data)
        self.tab_widget.setCurrentWidget(self.results_tab)
        self.history_updated.emit()

    def _save_run_to_history(self, summary_data):
        """Merges config with summary and appends it to the history file."""
        try:
            config_path = os.path.abspath("./build/last_applied_config.json")
            history_path = os.path.abspath("./build/history.json")

            if not os.path.exists(config_path):
                print("Could not save to history: last_applied_config.json not found.")
                return

            with open(config_path, "r") as f:
                config_data = json.load(f)
            
            # Create a complete record
            full_record = {**config_data, **summary_data}

            history = []
            if os.path.exists(history_path):
                with open(history_path, "r") as f:
                    try:
                        history = json.load(f)
                        if not isinstance(history, list):
                            history = []
                    except json.JSONDecodeError:
                        history = []
            
            history.insert(0, full_record) # Prepend to show newest first

            with open(history_path, "w") as f:
                json.dump(history, f, indent=4)

        except Exception as e:
            print(f"Error saving run to history: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrainerScreen(None)
    window.show()
    sys.exit(app.exec())