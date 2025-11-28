from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLabel,
    QProgressBar,
)


class ProgressIndicatorsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Progress Indicators")
        self.layout.addWidget(group)

        form_layout = QFormLayout(group)

        self.epoch_progress = QProgressBar()
        form_layout.addRow("Epoch Progress:", self.epoch_progress)

        self.batch_progress = QProgressBar()
        form_layout.addRow("Batch Progress:", self.batch_progress)

        self.data_throughput = QLabel("0 samples/sec")
        form_layout.addRow("Data Throughput:", self.data_throughput)

        self.etr = QLabel("00:00:00")
        form_layout.addRow("Estimated Time Remaining (ETR):", self.etr)
