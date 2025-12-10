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

    def update_data(self, data: dict):
        """
        Updates the widget with sample prediction data.
        NOTE: This requires specific sample data not included in the main summary.
        """
        print(f"SamplePredictionAnalysisWidget: update_data called. Data: {data}")
        self.sample_grid_label.setText("Sample prediction data received (not displayed).")