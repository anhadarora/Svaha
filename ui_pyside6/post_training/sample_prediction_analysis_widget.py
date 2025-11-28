from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel


class SamplePredictionAnalysisWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Sample Prediction Analysis (Test Set)")
        self.layout.addWidget(group)

        self.sample_grid_label = QLabel("Sample prediction grid will be displayed here.")
        layout = QVBoxLayout(group)
        layout.addWidget(self.sample_grid_label)
