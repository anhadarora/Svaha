from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton, QMessageBox
from PySide6.QtCore import Signal, Qt, QTimer

import json
import os

from ..pre_training.data_source_widget import DataSourceWidget
from ..pre_training.model_input_parameters_widget import ModelInputParametersWidget
from ..pre_training.model_architecture_widget import ModelArchitectureWidget
from ..pre_training.prediction_target_widget import PredictionTargetWidget
from ..pre_training.error_correction_widget import ErrorCorrectionWidget
from ..pre_training.run_output_widget import RunOutputWidget
from ..pre_training.file_saving_widget import FileSavingWidget


class SetupTabWidget(QWidget):
    start_training_requested = Signal()

    def __init__(self):
        super().__init__()
        self.is_fully_initialized = False
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        container = QWidget()
        scroll_area.setWidget(container)
        main_layout = QHBoxLayout(container)

        left_column = QVBoxLayout()
        right_column = QVBoxLayout()

        main_layout.addLayout(left_column, 1)
        main_layout.addLayout(right_column, 1)

        # --- Instantiate Widgets ---
        self.data_source_widget = DataSourceWidget()
        self.model_input_parameters_widget = ModelInputParametersWidget()
        self.model_architecture_widget = ModelArchitectureWidget()
        self.prediction_target_widget = PredictionTargetWidget()
        self.error_correction_widget = ErrorCorrectionWidget()
        self.run_output_widget = RunOutputWidget()
        self.file_saving_widget = FileSavingWidget()

        # --- Layout Widgets ---
        left_column.addWidget(self.data_source_widget)
        left_column.addWidget(self.model_input_parameters_widget)
        left_column.addStretch()

        right_column.addWidget(self.model_architecture_widget)
        right_column.addWidget(self.prediction_target_widget)
        right_column.addWidget(self.error_correction_widget)
        right_column.addWidget(self.run_output_widget)
        right_column.addWidget(self.file_saving_widget)
        right_column.addStretch()

        # --- Control Buttons ---
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_and_run_button = QPushButton("Apply & Run")
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.apply_and_run_button)
        self.layout.addLayout(button_layout)

        # --- Finalize setup after event loop starts ---
        QTimer.singleShot(0, self.finalize_setup)

    def finalize_setup(self):
        """Connects all signals and sets initial states after UI is constructed."""
        self._connect_signals()
        self.on_data_source_selected(False)
        self.update_experiment_id()
        self._on_chart_type_changed(self.model_input_parameters_widget.chart_type_combo.currentText())
        self.is_fully_initialized = True

    def _connect_signals(self):
        self.widgets_to_toggle = [
            self.model_input_parameters_widget,
            self.model_architecture_widget,
            self.prediction_target_widget,
            self.error_correction_widget,
            self.run_output_widget,
            self.file_saving_widget,
            self.apply_button,
            self.apply_and_run_button,
        ]
        
        self.data_source_widget.data_source_selected.connect(self.on_data_source_selected)
        self.run_output_widget.regeneration_requested.connect(self.update_experiment_id)
        
        # Connect signals from children now that they are all constructed
        self.data_source_widget.connect_signals()
        self.model_input_parameters_widget.connect_signals()
        self.model_architecture_widget.connect_signals()
        self.prediction_target_widget.connect_signals()
        self.error_correction_widget.connect_signals()
        self.file_saving_widget.connect_signals()
        self.run_output_widget.connect_signals()

        # Connect the configuration changed signals to the parent slot
        self.data_source_widget.configuration_changed.connect(self._on_parameter_changed, Qt.QueuedConnection)
        self.model_input_parameters_widget.configuration_changed.connect(self._on_parameter_changed, Qt.QueuedConnection)
        self.model_architecture_widget.configuration_changed.connect(self._on_parameter_changed, Qt.QueuedConnection)
        self.prediction_target_widget.configuration_changed.connect(self._on_parameter_changed, Qt.QueuedConnection)
        self.error_correction_widget.configuration_changed.connect(self._on_parameter_changed, Qt.QueuedConnection)
        self.file_saving_widget.configuration_changed.connect(self._on_parameter_changed, Qt.QueuedConnection)
        self.run_output_widget.configuration_changed.connect(self._on_parameter_changed, Qt.QueuedConnection)

        self.model_input_parameters_widget.chart_type_combo.currentTextChanged.connect(self._on_chart_type_changed)

        self.apply_button.clicked.connect(self._on_apply)
        self.apply_and_run_button.clicked.connect(self._on_apply_and_run)

    def on_data_source_selected(self, is_selected):
        for widget in self.widgets_to_toggle:
            widget.setEnabled(is_selected)

    def _on_parameter_changed(self):
        if not self.is_fully_initialized:
            return
        if not self.run_output_widget.is_manually_edited:
            self.update_experiment_id()

    def _on_chart_type_changed(self, chart_type_text):
        is_dynamic = (chart_type_text == "Dynamic 2D Plane")
        self.run_output_widget.set_dynamic_plane_diagnostics_visibility(is_dynamic)

    def get_configuration(self):
        config = {}
        config.update(self.data_source_widget.get_parameters())
        config.update(self.model_input_parameters_widget.get_parameters())
        config.update(self.model_architecture_widget.get_parameters())
        config.update(self.prediction_target_widget.get_parameters())
        config.update(self.error_correction_widget.get_parameters())
        config.update(self.file_saving_widget.get_parameters())
        config.update(self.run_output_widget.get_parameters())
        config["experiment_name"] = self.run_output_widget.get_sanitized_name()
        return config

    def update_experiment_id(self):
        config_for_hash = self.get_configuration()
        config_for_hash.pop("output_metrics", None)
        config_for_hash.pop("experiment_name", None)
        self.run_output_widget.update_experiment_name(config_for_hash)

    def _on_apply(self):
        config = self.get_configuration()
        
        build_dir = os.path.abspath("./build")
        os.makedirs(build_dir, exist_ok=True)
        
        save_path = os.path.join(build_dir, "last_applied_config.json")
        
        try:
            with open(save_path, "w") as f:
                json.dump(config, f, indent=4)
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Success")
            msg_box.setText("Configuration has been applied successfully.")
            msg_box.setInformativeText(f"Ready to run experiment: {config['experiment_name']}\n\nYou can now switch to the Monitor tab to begin the experiment.")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{e}")

    def _on_apply_and_run(self):
        self._on_apply()
        self.start_training_requested.emit()