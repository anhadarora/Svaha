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
from PySide6.QtCore import Qt, Signal


class ErrorCorrectionWidget(QWidget):
    configuration_changed = Signal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Dynamic Error Correction & Healing Parameters")
        self.layout.addWidget(group)

        form_layout = QFormLayout(group)

        self.enable_dynamic_correction = QCheckBox()
        form_layout.addRow("Enable Dynamic Correction:", self.enable_dynamic_correction)

        self.gamma_1 = QSlider(Qt.Horizontal)
        self.gamma_1.setRange(0, 100)
        form_layout.addRow("gamma_1 (Vector Deviation Weight):", self.gamma_1)

        self.gamma_2 = QSlider(Qt.Horizontal)
        self.gamma_2.setRange(0, 100)
        form_layout.addRow("gamma_2 (Frame Shift Weight):", self.gamma_2)

        self.alpha_1 = QSlider(Qt.Horizontal)
        self.alpha_1.setRange(0, 100)
        form_layout.addRow("alpha_1 (Vector Distance Weight):", self.alpha_1)

        self.alpha_2 = QSlider(Qt.Horizontal)
        self.alpha_2.setRange(0, 100)
        form_layout.addRow("alpha_2 (Vector Angle Weight):", self.alpha_2)

        self.beta_1 = QSlider(Qt.Horizontal)
        self.beta_1.setRange(0, 100)
        form_layout.addRow("beta_1 (PCA1 Angle Weight):", self.beta_1)

        self.beta_2 = QSlider(Qt.Horizontal)
        self.beta_2.setRange(0, 100)
        form_layout.addRow("beta_2 (PCA2 Angle Weight):", self.beta_2)

        self.error_buffer_size = QLineEdit("20")
        form_layout.addRow("Error Buffer Size:", self.error_buffer_size)

        self.wound_threshold_multiplier = QLineEdit("2.5")
        form_layout.addRow("Wound Threshold Multiplier (k):", self.wound_threshold_multiplier)

        self.correction_step = QLineEdit("0.1")
        form_layout.addRow("Correction Step:", self.correction_step)

        self.max_correction_factor = QLineEdit("1.0")
        form_layout.addRow("Max Correction Factor:", self.max_correction_factor)

        self.correctness_buffer_size = QLineEdit("20")
        form_layout.addRow("Correctness Buffer Size:", self.correctness_buffer_size)

        self.prediction_accuracy_method = QComboBox()
        self.prediction_accuracy_method.addItems(["Vector Cosine Similarity", "Directional Accuracy"])
        form_layout.addRow("Prediction Accuracy Method:", self.prediction_accuracy_method)

        self.healing_threshold = QSlider(Qt.Horizontal)
        self.healing_threshold.setRange(0, 100)
        form_layout.addRow("Healing Threshold:", self.healing_threshold)

        self.healing_rate_function = QComboBox()
        self.healing_rate_function.addItems(["Proportional", "Linear Step"])
        form_layout.addRow("Healing Rate Function:", self.healing_rate_function)

    def connect_signals(self):
        self.enable_dynamic_correction.toggled.connect(self.configuration_changed)
        self.gamma_1.valueChanged.connect(self.configuration_changed)
        self.gamma_2.valueChanged.connect(self.configuration_changed)
        self.alpha_1.valueChanged.connect(self.configuration_changed)
        self.alpha_2.valueChanged.connect(self.configuration_changed)
        self.beta_1.valueChanged.connect(self.configuration_changed)
        self.beta_2.valueChanged.connect(self.configuration_changed)
        self.error_buffer_size.textChanged.connect(self.configuration_changed)
        self.wound_threshold_multiplier.textChanged.connect(self.configuration_changed)
        self.correction_step.textChanged.connect(self.configuration_changed)
        self.max_correction_factor.textChanged.connect(self.configuration_changed)
        self.correctness_buffer_size.textChanged.connect(self.configuration_changed)
        self.prediction_accuracy_method.currentIndexChanged.connect(self.configuration_changed)
        self.healing_threshold.valueChanged.connect(self.configuration_changed)
        self.healing_rate_function.currentIndexChanged.connect(self.configuration_changed)

    def get_parameters(self):
        return {
            "enable_dynamic_correction": self.enable_dynamic_correction.isChecked(),
            "gamma_1": self.gamma_1.value() / 100.0,
            "gamma_2": self.gamma_2.value() / 100.0,
            "alpha_1": self.alpha_1.value() / 100.0,
            "alpha_2": self.alpha_2.value() / 100.0,
            "beta_1": self.beta_1.value() / 100.0,
            "beta_2": self.beta_2.value() / 100.0,
            "error_buffer_size": self.error_buffer_size.text(),
            "wound_threshold_multiplier": self.wound_threshold_multiplier.text(),
            "correction_step": self.correction_step.text(),
            "max_correction_factor": self.max_correction_factor.text(),
            "correctness_buffer_size": self.correctness_buffer_size.text(),
            "prediction_accuracy_method": self.prediction_accuracy_method.currentText(),
            "healing_threshold": self.healing_threshold.value() / 100.0,
            "healing_rate_function": self.healing_rate_function.currentText(),
        }