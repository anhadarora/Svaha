from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTextEdit
import json


class ParameterConfigurationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Parameter Configuration (Recap)")
        self.layout.addWidget(group)

        self.parameters_view = QTextEdit()
        self.parameters_view.setReadOnly(True)
        self.parameters_view.setText("Configuration data will be displayed here.")
        
        layout = QVBoxLayout(group)
        layout.addWidget(self.parameters_view)

    def update_data(self, data: dict):
        """Populates the text view with the experiment configuration."""
        if not data:
            self.parameters_view.setText("Configuration data not available.")
            return
        
        # Use pretty-printed JSON for display
        formatted_json = json.dumps(data, indent=4)
        self.parameters_view.setText(formatted_json)