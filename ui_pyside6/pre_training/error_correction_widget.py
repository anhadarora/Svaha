from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QCheckBox,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QLabel,
)
from PySide6.QtCore import Signal


class ErrorCorrectionWidget(QWidget):
    configuration_changed = Signal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        # --- Dynamic Error Correction Group ---
        error_group = QGroupBox("Dynamic Error Correction")
        self.layout.addWidget(error_group)
        error_layout = QGridLayout(error_group)

        self.enable_dynamic_correction = QCheckBox("Enable Dynamic Correction")
        error_layout.addWidget(self.enable_dynamic_correction, 0, 0, 1, 4)

        self.error_buffer_size = QSpinBox()
        self.error_buffer_size.setRange(1, 200)
        self.error_buffer_size.setValue(20)
        self._add_grid_row(error_layout, 1, "Error Buffer Size:", self.error_buffer_size)

        self.wound_threshold_multiplier = QDoubleSpinBox()
        self.wound_threshold_multiplier.setRange(0.1, 10.0)
        self.wound_threshold_multiplier.setValue(2.5)
        self._add_grid_row(error_layout, 2, "Wound Threshold (StdDev Mult):", self.wound_threshold_multiplier)

        self.correction_step = QDoubleSpinBox()
        self.correction_step.setRange(0.01, 1.0)
        self.correction_step.setValue(0.1)
        self._add_grid_row(error_layout, 3, "Correction Step:", self.correction_step)

        self.max_correction_factor = QDoubleSpinBox()
        self.max_correction_factor.setRange(0.1, 10.0)
        self.max_correction_factor.setValue(1.0)
        self._add_grid_row(error_layout, 4, "Max Correction Factor:", self.max_correction_factor)

        # --- Healing Phase Group ---
        healing_group = QGroupBox("Healing Phase (Correction Recovery)")
        self.layout.addWidget(healing_group)
        healing_layout = QGridLayout(healing_group)

        # Healing Trigger
        self.healing_metric = QComboBox()
        self.healing_metric.addItems(["Prediction Correctness (Hit Rate)", "Low Total Error"])
        self._add_grid_row(healing_layout, 0, "Healing Trigger Metric:", self.healing_metric)

        self.healing_threshold = QDoubleSpinBox()
        self.healing_threshold.setSuffix(" %")
        self.healing_threshold.setRange(0.0, 100.0)
        self.healing_threshold.setValue(80.0)
        self._add_grid_row(healing_layout, 1, "Healing Threshold:", self.healing_threshold)

        self.success_window = QSpinBox()
        self.success_window.setSuffix(" steps")
        self.success_window.setRange(1, 200)
        self.success_window.setValue(10)
        self._add_grid_row(healing_layout, 2, "Success Window:", self.success_window)

        # Decay Dynamics
        self.decay_strategy = QComboBox()
        self.decay_strategy.addItems(["Performance-Proportional", "Linear Step", "Exponential"])
        self._add_grid_row(healing_layout, 3, "Decay Strategy:", self.decay_strategy)

        self.base_decay_rate = QDoubleSpinBox()
        self.base_decay_rate.setRange(0.0, 1.0)
        self.base_decay_rate.setSingleStep(0.01)
        self.base_decay_rate.setValue(0.05)
        self._add_grid_row(healing_layout, 4, "Base Decay / Scaling Factor:", self.base_decay_rate)

        # Safety Limits
        self.min_correction = QDoubleSpinBox()
        self.min_correction.setRange(0.0, 1.0)
        self.min_correction.setValue(0.0)
        self._add_grid_row(healing_layout, 5, "Min Correction:", self.min_correction)

        self.hysteresis = QSpinBox()
        self.hysteresis.setSuffix(" steps")
        self.hysteresis.setRange(0, 100)
        self.hysteresis.setValue(5)
        self._add_grid_row(healing_layout, 6, "Hysteresis (Cool-down):", self.hysteresis)

        self.layout.addStretch()

    def _add_grid_row(self, layout, row, label_text, widget, tooltip=None, column=0):
        label = QLabel(label_text)
        label.setBuddy(widget)
        if tooltip:
            widget.setToolTip(tooltip)
        layout.addWidget(label, row, column)
        layout.addWidget(widget, row, column + 1)

    def connect_signals(self):
        self.enable_dynamic_correction.toggled.connect(self.configuration_changed)
        self.error_buffer_size.valueChanged.connect(self.configuration_changed)
        self.wound_threshold_multiplier.valueChanged.connect(self.configuration_changed)
        self.correction_step.valueChanged.connect(self.configuration_changed)
        self.max_correction_factor.valueChanged.connect(self.configuration_changed)
        
        self.healing_metric.currentIndexChanged.connect(self.configuration_changed)
        self.healing_threshold.valueChanged.connect(self.configuration_changed)
        self.success_window.valueChanged.connect(self.configuration_changed)
        self.decay_strategy.currentIndexChanged.connect(self.configuration_changed)
        self.base_decay_rate.valueChanged.connect(self.configuration_changed)
        self.min_correction.valueChanged.connect(self.configuration_changed)
        self.hysteresis.valueChanged.connect(self.configuration_changed)

    def get_parameters(self):
        return {
            "error_correction": {
                "enabled": self.enable_dynamic_correction.isChecked(),
                "error_buffer_size": self.error_buffer_size.value(),
                "wound_threshold_multiplier": self.wound_threshold_multiplier.value(),
                "correction_step": self.correction_step.value(),
                "max_correction_factor": self.max_correction_factor.value(),
            },
            "healing_phase": {
                "trigger_metric": self.healing_metric.currentText(),
                "success_threshold": self.healing_threshold.value(),
                "evaluation_window": self.success_window.value(),
                "decay_strategy": self.decay_strategy.currentText(),
                "base_decay_rate": self.base_decay_rate.value(),
                "min_correction_floor": self.min_correction.value(),
                "hysteresis_cooldown": self.hysteresis.value(),
            }
        }