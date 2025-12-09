import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget
from .trainer.setup_tab_widget import SetupTabWidget
from .trainer.monitor_tab_widget import MonitorTabWidget
from .trainer.results_tab_widget import ResultsTabWidget
from .history.history_widget import HistoryWidget


class TrainerScreen(QWidget):
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

        # Connect the signal from the setup tab to switch to the monitor tab
        self.setup_tab.start_training_requested.connect(self._on_start_training_requested)

    def _on_start_training_requested(self):
        """Switches to the monitor tab and starts the training process."""
        self.tab_widget.setCurrentWidget(self.monitor_tab)
        self.monitor_tab.begin_training()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrainerScreen(None)
    window.show()
    sys.exit(app.exec())