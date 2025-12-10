from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QLabel,
)
from PySide6.QtCore import Signal


class PredictionTargetWidget(QWidget):
    """A widget to configure how the ground-truth labels are calculated."""

    configuration_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("pred_target")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        # --- 1. Regression Logic ---
        regression_group = QGroupBox("Regression Logic")
        regression_group.setObjectName("pred_target.regression")
        self.layout.addWidget(regression_group)
        regression_layout = QGridLayout(regression_group)

        self.return_calculation = QComboBox()
        self.return_calculation.setObjectName("pred_target.regression.return_calculation")
        self.return_calculation.addItems([
            "Thesis (Next Open to Future Close)",
            "Standard (Close to Close)",
            "Intraday (Open to Close)",
        ])
        self._add_grid_row(regression_layout, 0, "Return Calculation:", self.return_calculation)

        self.label_scaling = QComboBox()
        self.label_scaling.setObjectName("pred_target.regression.label_scaling")
        self.label_scaling.addItems(["Percent", "Decimal", "Log Return", "Basis Points"])
        self.label_scaling.setCurrentText("Percent")
        self._add_grid_row(regression_layout, 1, "Label Scaling:", self.label_scaling)

        # --- 2. Classification Settings (Conditional) ---
        self.classification_group = QGroupBox("Classification Settings")
        self.classification_group.setObjectName("pred_target.classification")
        self.layout.addWidget(self.classification_group)
        classification_layout = QGridLayout(self.classification_group)

        self.class_logic = QComboBox()
        self.class_logic.setObjectName("pred_target.classification.class_logic")
        self.class_logic.addItems(["Ternary (Buy/Sell/Hold)", "Binary (Up/Down)"])
        self._add_grid_row(classification_layout, 0, "Class Logic:", self.class_logic)

        self.buy_threshold = QDoubleSpinBox()
        self.buy_threshold.setObjectName("pred_target.classification.buy_threshold")
        self.buy_threshold.setSuffix(" %")
        self.buy_threshold.setRange(0.01, 100.0)
        self.buy_threshold.setValue(1.0)
        self._add_grid_row(classification_layout, 1, "Buy Threshold:", self.buy_threshold)

        self.sell_threshold = QDoubleSpinBox()
        self.sell_threshold.setObjectName("pred_target.classification.sell_threshold")
        self.sell_threshold.setSuffix(" %")
        self.sell_threshold.setRange(-100.0, -0.01)
        self.sell_threshold.setValue(-1.0)
        self._add_grid_row(classification_layout, 2, "Sell Threshold:", self.sell_threshold)

        # --- 3. Rally Time Settings (Conditional) ---
        self.rally_time_group = QGroupBox("Rally Time Settings")
        self.rally_time_group.setObjectName("pred_target.rally_time")
        self.layout.addWidget(self.rally_time_group)
        rally_layout = QGridLayout(self.rally_time_group)

        self.target_magnitude = QDoubleSpinBox()
        self.target_magnitude.setObjectName("pred_target.rally_time.target_magnitude")
        self.target_magnitude.setSuffix(" %")
        self.target_magnitude.setRange(0.1, 1000.0)
        self.target_magnitude.setValue(2.0)
        self._add_grid_row(rally_layout, 0, "Target Magnitude:", self.target_magnitude)

        self.max_horizon = QSpinBox()
        self.max_horizon.setObjectName("pred_target.rally_time.max_horizon")
        self.max_horizon.setSuffix(" candles")
        self.max_horizon.setRange(1, 1000)
        self.max_horizon.setValue(50)
        self._add_grid_row(rally_layout, 1, "Max Horizon:", self.max_horizon)

        # --- 4. Frame Reference (Conditional) ---
        self.frame_reference_group = QGroupBox("Frame of Reference")
        self.frame_reference_group.setObjectName("pred_target.frame_of_reference")
        self.layout.addWidget(self.frame_reference_group)
        frame_layout = QGridLayout(self.frame_reference_group)

        self.target_frame = QComboBox()
        self.target_frame.setObjectName("pred_target.frame_of_reference.target_frame")
        self.target_frame.addItems(["Global (Absolute Return)", "Local (Dynamic Vector)"])
        self._add_grid_row(frame_layout, 0, "Target Frame:", self.target_frame)

        self.layout.addStretch()

        # Set initial visibility
        self.classification_group.setVisible(False)
        self.rally_time_group.setVisible(False)
        self.frame_reference_group.setVisible(False)

    def _add_grid_row(self, layout, row, label_text, widget):
        label = QLabel(label_text)
        label.setBuddy(widget)
        layout.addWidget(label, row, 0)
        layout.addWidget(widget, row, 1)

    def connect_signals(self):
        self.return_calculation.currentIndexChanged.connect(self.configuration_changed)
        self.label_scaling.currentIndexChanged.connect(self.configuration_changed)
        self.class_logic.currentIndexChanged.connect(self.configuration_changed)
        self.buy_threshold.valueChanged.connect(self.configuration_changed)
        self.sell_threshold.valueChanged.connect(self.configuration_changed)
        self.target_magnitude.valueChanged.connect(self.configuration_changed)
        self.max_horizon.valueChanged.connect(self.configuration_changed)
        self.target_frame.currentIndexChanged.connect(self.configuration_changed)

    def get_parameters(self):
        params = {
            "regression_logic": {
                "return_calculation": self.return_calculation.currentText(),
                "label_scaling": self.label_scaling.currentText(),
            }
        }
        if self.classification_group.isVisible():
            params["classification_settings"] = {
                "class_logic": self.class_logic.currentText(),
                "buy_threshold": self.buy_threshold.value(),
                "sell_threshold": self.sell_threshold.value(),
            }
        if self.rally_time_group.isVisible():
            params["rally_time_settings"] = {
                "target_magnitude": self.target_magnitude.value(),
                "max_horizon": self.max_horizon.value(),
            }
        if self.frame_reference_group.isVisible():
            params["frame_reference"] = {
                "target_frame": self.target_frame.currentText(),
            }
        return params

    def update_visibility(self, heads_state: dict):
        """Updates visibility of conditional sections based on head selections."""
        is_classification_head = "Classification" in heads_state.get("primary", "")
        is_directional_confidence_head = heads_state.get("directional_confidence", False)
        self.classification_group.setVisible(is_classification_head or is_directional_confidence_head)

        is_rally_time_head = heads_state.get("rally_time", False)
        self.rally_time_group.setVisible(is_rally_time_head)

    def set_frame_reference_visibility(self, visible: bool):
        """Updates visibility of the frame reference section."""
        self.frame_reference_group.setVisible(visible)