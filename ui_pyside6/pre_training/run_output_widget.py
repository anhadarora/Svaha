from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QCheckBox,
    QLineEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import Signal
import json
import hashlib
import re

class RunOutputWidget(QWidget):
    regeneration_requested = Signal()
    configuration_changed = Signal()

    def __init__(self):
        super().__init__()
        self.all_checkboxes = []
        self.is_manually_edited = False
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Run & Output Parameters")
        self.layout.addWidget(group)

        layout = QVBoxLayout(group)

        exp_name_group = QGroupBox("Experiment Name")
        exp_name_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        exp_name_layout = QVBoxLayout(exp_name_group)
        
        name_layout = QHBoxLayout()
        self.experiment_name = QLineEdit()
        name_layout.addWidget(self.experiment_name)
        self.revert_button = QPushButton("Revert to ID")
        self.revert_button.setVisible(False)
        name_layout.addWidget(self.revert_button)
        exp_name_layout.addLayout(name_layout)
        layout.addWidget(exp_name_group)

        metrics_group = QGroupBox("Output Metrics")
        metrics_layout = QVBoxLayout(metrics_group)
        layout.addWidget(metrics_group)

        self.loss_curve_check = self._add_checkbox(metrics_layout, "Loss Curve")
        self.accuracy_curve_check = self._add_checkbox(metrics_layout, "Accuracy Curve")
        
        financial_group = QGroupBox("Financial Metrics")
        financial_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        financial_layout = QVBoxLayout(financial_group)
        self.sharpe_ratio_check = self._add_checkbox(financial_layout, "Sharpe Ratio")
        self.alpha_beta_check = self._add_checkbox(financial_layout, "Alpha & Beta")
        self.cum_return_check = self._add_checkbox(financial_layout, "Cumulative Return vs. Benchmark")
        self.max_drawdown_check = self._add_checkbox(financial_layout, "Max Drawdown")
        metrics_layout.addWidget(financial_group)

        self.dyn_plane_group = QGroupBox("Dynamic Plane Diagnostics")
        self.dyn_plane_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        dyn_plane_layout = QVBoxLayout(self.dyn_plane_group)
        self.vector_dev_log_check = self._add_checkbox(dyn_plane_layout, "Vector Deviation Log")
        self.correction_factor_trace_check = self._add_checkbox(dyn_plane_layout, "Correction Factor Trace")
        self.input_snapshots_check = self._add_checkbox(dyn_plane_layout, "Input Snapshots (Sample)")
        metrics_layout.addWidget(self.dyn_plane_group)

        for checkbox in self.all_checkboxes:
            checkbox.setChecked(True)

    def connect_signals(self):
        self.experiment_name.textEdited.connect(self._on_name_manually_edited)
        self.revert_button.clicked.connect(self.on_revert_clicked)
        for checkbox in self.all_checkboxes:
            checkbox.toggled.connect(self.configuration_changed)

    def set_dynamic_plane_diagnostics_visibility(self, visible):
        self.dyn_plane_group.setVisible(visible)

    def _add_checkbox(self, layout, text):
        checkbox = QCheckBox(text)
        self.all_checkboxes.append(checkbox)
        layout.addWidget(checkbox)
        return checkbox

    def _on_name_manually_edited(self):
        self.is_manually_edited = True
        self.revert_button.setVisible(True)
        self.configuration_changed.emit()

    def on_revert_clicked(self):
        self.is_manually_edited = False
        self.regeneration_requested.emit()
        self.revert_button.setVisible(False)

    def get_parameters(self):
        return {
            "output_metrics": {cb.text(): cb.isChecked() for cb in self.all_checkboxes}
        }

    def get_sanitized_name(self):
        name = self.experiment_name.text()
        sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '', name.replace(' ', '_'))
        return sanitized_name.lower()

    def update_experiment_name(self, config_dict):
        if not isinstance(config_dict, dict):
            return
        config_string = json.dumps(config_dict, sort_keys=True)
        hasher = hashlib.sha1(config_string.encode('utf-8'))
        short_id = hasher.hexdigest()[:12]
        
        self.experiment_name.blockSignals(True)
        self.experiment_name.setText(short_id)
        self.experiment_name.blockSignals(False)
        
        self.revert_button.setVisible(False)
        self.is_manually_edited = False