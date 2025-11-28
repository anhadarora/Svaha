from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QSlider,
    QCheckBox,
    QLineEdit,
)
from PySide6.QtCore import Qt


class PredictionTargetWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Prediction Target (Label) Parameters")
        self.layout.addWidget(group)

        form_layout = QFormLayout(group)

        self.prediction_target_type = QComboBox()
        self.prediction_target_type.addItems(
            [
                "Vectorial Movement (in Dynamic Plane)",
                "Image-to-Image (Next Dynamic Plane)",
                "Scalar Return (Regression)",
                "Signal Class (Buy/Sell/Hold)",
            ]
        )
        form_layout.addRow("Prediction Target Type:", self.prediction_target_type)

        self.prediction_horizon = QSlider(Qt.Horizontal)
        self.prediction_horizon.setRange(1, 10)
        form_layout.addRow("Prediction Horizon (H):", self.prediction_horizon)

        self.vector_type = QComboBox()
        self.vector_type.addItems(["Single-Step Vector (ΔX', ΔY')", "Full Trajectory (H steps)"])
        form_layout.addRow("Vector Type (if Vectorial):", self.vector_type)

        self.buy_threshold = QLineEdit("+1.0")
        form_layout.addRow("Buy Threshold (%) (if Class):", self.buy_threshold)

        self.sell_threshold = QLineEdit("-1.0")
        form_layout.addRow("Sell Threshold (%) (if Class):", self.sell_threshold)

        self.predict_rally_time = QCheckBox()
        form_layout.addRow("Predict Rally Time:", self.predict_rally_time)
