import sys
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QTabWidget,
    QWidget,
)

from ..trainer.setup_tab_widget import SetupTabWidget
from ..trainer.monitor_tab_widget import MonitorTabWidget
from ..trainer.results_tab_widget import ResultsTabWidget


class HistoricalRunDialog(QDialog):
    def __init__(self, history_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Historical Run: {history_data.get('name', 'N/A')}")
        self.setMinimumSize(1200, 800)

        self.layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.setup_tab = SetupTabWidget()
        self.monitor_tab = MonitorTabWidget()
        self.results_tab = ResultsTabWidget()

        self.tab_widget.addTab(self.setup_tab, "Setup")
        self.tab_widget.addTab(self.monitor_tab, "Monitor")
        self.tab_widget.addTab(self.results_tab, "Results")

        # TODO: Populate widgets with history_data
        # This will involve iterating through the widgets in each tab
        # and setting their values from the history_data object.
        # For now, the widgets will be in their default state.
        # self.set_read_only(True)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        self.export_button = self.button_box.addButton(
            "Export Report", QDialogButtonBox.ButtonRole.ActionRole
        )
        self.reload_button = self.button_box.addButton(
            "Reload Parameters", QDialogButtonBox.ButtonRole.ActionRole
        )

        self.layout.addWidget(self.button_box)

        self.button_box.rejected.connect(self.reject)
        self.export_button.clicked.connect(self.export_report)
        self.reload_button.clicked.connect(self.reload_parameters)

    def set_read_only(self, read_only):
        # Recursively set all child widgets to be read-only
        for widget in self.findChildren(QWidget):
            if hasattr(widget, "setReadOnly"):
                widget.setReadOnly(read_only)
            # For widgets that don't have setReadOnly, we might need to disable them
            elif hasattr(widget, "setEnabled"):
                # Don't disable container widgets, only controls
                if not isinstance(widget, (QTabWidget, QDialog)):
                    widget.setEnabled(not read_only)

    def export_report(self):
        # TODO: Implement export functionality
        print("Exporting report...")

    def reload_parameters(self):
        # TODO: Implement reload functionality
        print("Reloading parameters...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Dummy data for testing
    dummy_data = {
        "name": "Test Run",
    }
    dialog = HistoricalRunDialog(dummy_data)
    dialog.exec()
    sys.exit(app.exec())
