from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
)


class RunStatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Run Status & Controls")
        self.layout.addWidget(group)

        form_layout = QFormLayout(group)

        self.experiment_name = QLabel("Not running")
        form_layout.addRow("Experiment Name:", self.experiment_name)

        self.current_status = QLabel("IDLE")
        form_layout.addRow("Current Status:", self.current_status)

        self.elapsed_time = QLabel("00:00:00")
        form_layout.addRow("Elapsed Time:", self.elapsed_time)

        button_layout = QHBoxLayout()
        self.pause_button = QPushButton("PAUSE")
        self.stop_button = QPushButton("STOP TRAINING")
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        form_layout.addRow(button_layout)
