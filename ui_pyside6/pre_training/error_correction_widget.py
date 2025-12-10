from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QLabel,
    QStackedWidget,
    QSizePolicy,
)
from PySide6.QtCore import Signal

class ErrorCorrectionWidget(QWidget):
    configuration_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("error_correction")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        # --- Create the two different UI modes ---
        self.standard_widget = self._create_standard_ui()
        self.dynamic_plane_widget = self._create_dynamic_plane_ui()

        self.stack.addWidget(self.standard_widget)
        self.stack.addWidget(self.dynamic_plane_widget)

        self.layout.addStretch()

    def _create_standard_ui(self):
        container = QWidget()
        container.setObjectName("error_correction.standard")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Early Stopping Parameters")
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.addWidget(group)
        
        grid_layout = QGridLayout(group)

        self.loss_function_combo = QComboBox()
        self.loss_function_combo.setObjectName("error_correction.standard.loss_function")
        self.loss_function_combo.addItems(["Mean Squared Error (MSE)", "Mean Absolute Error (MAE)"])
        self._add_grid_row(grid_layout, 0, "Loss Function:", self.loss_function_combo)

        self.patience_spinbox = QSpinBox()
        self.patience_spinbox.setObjectName("error_correction.standard.patience")
        self.patience_spinbox.setRange(1, 1000)
        self.patience_spinbox.setValue(10)
        self.patience_spinbox.setSuffix(" epochs")
        self._add_grid_row(grid_layout, 1, "Patience:", self.patience_spinbox)
        
        return container

    def _create_dynamic_plane_ui(self):
        container = QWidget()
        container.setObjectName("error_correction.dynamic_plane")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Dynamic Plane Correction Parameters")
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.addWidget(group)
        
        grid_layout = QGridLayout(group)

        self.drift_threshold_spinbox = QDoubleSpinBox()
        self.drift_threshold_spinbox.setObjectName("error_correction.dynamic_plane.drift_threshold")
        self.drift_threshold_spinbox.setRange(0.0, 1.0)
        self.drift_threshold_spinbox.setSingleStep(0.01)
        self.drift_threshold_spinbox.setValue(0.05)
        self._add_grid_row(grid_layout, 0, "Drift Threshold:", self.drift_threshold_spinbox)

        self.healing_decay_rate_spinbox = QDoubleSpinBox()
        self.healing_decay_rate_spinbox.setObjectName("error_correction.dynamic_plane.healing_decay_rate")
        self.healing_decay_rate_spinbox.setRange(0.0, 1.0)
        self.healing_decay_rate_spinbox.setSingleStep(0.01)
        self.healing_decay_rate_spinbox.setValue(0.1)
        self._add_grid_row(grid_layout, 1, "Healing Decay Rate:", self.healing_decay_rate_spinbox)

        return container

    def _add_grid_row(self, layout, row, label_text, widget):
        label = QLabel(label_text)
        label.setBuddy(widget)
        layout.addWidget(label, row, 0)
        layout.addWidget(widget, row, 1)

    def connect_signals(self):
        # Standard UI signals
        self.loss_function_combo.currentIndexChanged.connect(self.configuration_changed)
        self.patience_spinbox.valueChanged.connect(self.configuration_changed)
        # Dynamic Plane UI signals
        self.drift_threshold_spinbox.valueChanged.connect(self.configuration_changed)
        self.healing_decay_rate_spinbox.valueChanged.connect(self.configuration_changed)

    def set_dynamic_plane_mode(self, enabled: bool):
        """Switches the UI between standard and dynamic plane modes."""
        if enabled:
            self.stack.setCurrentWidget(self.dynamic_plane_widget)
        else:
            self.stack.setCurrentWidget(self.standard_widget)
        self.configuration_changed.emit()

    def get_parameters(self):
        """Returns parameters based on the currently active UI."""
        if self.stack.currentWidget() == self.standard_widget:
            return {
                "error_correction_mode": "standard",
                "loss_function": self.loss_function_combo.currentText(),
                "patience": self.patience_spinbox.value(),
            }
        else: # Dynamic Plane Widget
            return {
                "error_correction_mode": "dynamic_plane",
                "drift_threshold": self.drift_threshold_spinbox.value(),
                "healing_decay_rate": self.healing_decay_rate_spinbox.value(),
            }