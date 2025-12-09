from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QListWidget,
    QStackedWidget,
    QListWidgetItem,
    QSizePolicy,
    QScrollArea,
)
from PySide6.QtCore import Signal, Qt, QTimer, QSize

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
        self.visited_pages = set()
        self.steps = [
            ("1. Data Source", DataSourceWidget),
            ("2. Input Parameters", ModelInputParametersWidget),
            ("3. Model Architecture", ModelArchitectureWidget),
            ("4. Prediction Target", PredictionTargetWidget),
            ("5. Error Correction", ErrorCorrectionWidget),
            ("6. File Saving", FileSavingWidget),
            ("7. Run & Output", RunOutputWidget),
        ]
        self.widgets = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        main_layout = QHBoxLayout()
        self.layout.addLayout(main_layout, 1)

        # --- Sidebar ---
        self.nav_list = QListWidget()
        self.nav_list.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.nav_list.setFixedWidth(200)
        self.nav_list.setIconSize(QSize(16, 16))
        main_layout.addWidget(self.nav_list)

        # --- Main Content Area (Scrollable) ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area, 1)

        content_container = QWidget()
        scroll_area.setWidget(content_container)
        
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(10, 10, 10, 10)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)

        # --- Navigation Buttons for Stack ---
        nav_button_layout = QHBoxLayout()
        nav_button_layout.addStretch()
        self.back_button = QPushButton("< Back")
        self.next_button = QPushButton("Next >")
        nav_button_layout.addWidget(self.back_button)
        nav_button_layout.addWidget(self.next_button)
        content_layout.addLayout(nav_button_layout)


        # --- Instantiate and Layout Widgets ---
        self._setup_wizard_pages()

        # --- Control Buttons ---
        control_button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_and_run_button = QPushButton("Apply & Run")
        self.apply_and_run_button.setStyleSheet("""
            background-color: #0d6efd; 
            color: white; 
            font-weight: bold; 
            padding: 10px;
        """)
        control_button_layout.addStretch()
        control_button_layout.addWidget(self.apply_button)
        control_button_layout.addWidget(self.apply_and_run_button)
        self.layout.addLayout(control_button_layout)

        # --- Finalize setup after event loop starts ---
        QTimer.singleShot(0, self.finalize_setup)

    def _setup_wizard_pages(self):
        for name, widget_class in self.steps:
            widget = widget_class()
            self.widgets.append(widget)
            self.stack.addWidget(widget)

            item = QListWidgetItem(f"○ {name}")
            self.nav_list.addItem(item)

        # Assign widgets to instance variables for later access
        (
            self.data_source_widget,
            self.model_input_parameters_widget,
            self.model_architecture_widget,
            self.prediction_target_widget,
            self.error_correction_widget,
            self.file_saving_widget,
            self.run_output_widget,
        ) = self.widgets

    def finalize_setup(self):
        """Connects all signals and sets initial states after UI is constructed."""
        self._connect_signals()
        self.on_data_source_selected(False)
        self.update_experiment_id()
        
        # Emit initial states for connected widgets
        self._on_chart_type_changed(self.model_input_parameters_widget.chart_type_combo.currentText())
        self.model_input_parameters_widget._emit_resolution()
        self.model_input_parameters_widget.window_size_changed.emit(
            self.model_input_parameters_widget.input_window_size_n_spinbox.value()
        )
        self.model_architecture_widget._emit_prediction_heads_changed()

        self.nav_list.setCurrentRow(0)
        self._update_nav_buttons(0)
        self._update_visited_status(0)
        self.is_fully_initialized = True

    def _connect_signals(self):
        self.widgets_to_toggle = self.widgets[1:] + [
            self.apply_button,
            self.apply_and_run_button,
        ]

        # Wizard navigation
        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.stack.currentChanged.connect(self._update_nav_buttons)
        self.stack.currentChanged.connect(self._update_visited_status)
        self.next_button.clicked.connect(self.go_to_next_page)
        self.back_button.clicked.connect(self.go_to_previous_page)

        # Core logic
        self.data_source_widget.data_source_selected.connect(
            self.on_data_source_selected
        )
        self.run_output_widget.regeneration_requested.connect(
            self.update_experiment_id
        )

        # Connect signals from children now that they are all constructed
        for widget in self.widgets:
            if hasattr(widget, "connect_signals"):
                widget.connect_signals()

        # Connect the configuration changed signals to the parent slot
        for widget in self.widgets:
            if hasattr(widget, "configuration_changed"):
                widget.configuration_changed.connect(
                    self._on_parameter_changed, Qt.QueuedConnection
                )

        # Inter-widget communication
        self.model_input_parameters_widget.resolution_changed.connect(
            self.model_architecture_widget.set_target_resolution
        )
        self.model_input_parameters_widget.window_size_changed.connect(
            self.model_architecture_widget.set_sequence_modeling_visibility
        )
        self.model_input_parameters_widget.chart_type_combo.currentTextChanged.connect(
            self._on_chart_type_changed
        )
        self.model_architecture_widget.prediction_heads_changed.connect(
            self.prediction_target_widget.update_visibility
        )

        self.apply_button.clicked.connect(self._on_apply)
        self.apply_and_run_button.clicked.connect(self._on_apply_and_run)

    def go_to_next_page(self):
        current_index = self.stack.currentIndex()
        if current_index < self.stack.count() - 1:
            self.stack.setCurrentIndex(current_index + 1)

    def go_to_previous_page(self):
        current_index = self.stack.currentIndex()
        if current_index > 0:
            self.stack.setCurrentIndex(current_index - 1)

    def _update_nav_buttons(self, index):
        self.back_button.setEnabled(index > 0)
        self.next_button.setEnabled(index < self.stack.count() - 1)
        # Sync list widget selection without re-emitting the signal
        if self.nav_list.currentRow() != index:
            self.nav_list.setCurrentRow(index)

    def _update_visited_status(self, index):
        if index not in self.visited_pages:
            self.visited_pages.add(index)
            item = self.nav_list.item(index)
            if item:
                # Update text to show checkmark, preserving the original name
                original_text = item.text().lstrip("○ ").lstrip("✔ ")
                item.setText(f"✔ {original_text}")

    def on_data_source_selected(self, is_selected):
        for widget in self.widgets_to_toggle:
            widget.setEnabled(is_selected)
        
        # Also enable the navigation list beyond the first item
        for i in range(1, self.nav_list.count()):
            item = self.nav_list.item(i)
            if item:
                item.setFlags(item.flags() | Qt.ItemIsEnabled if is_selected else item.flags() & ~Qt.ItemIsEnabled)


    def _on_parameter_changed(self):
        if not self.is_fully_initialized:
            return
        if not self.run_output_widget.is_manually_edited:
            self.update_experiment_id()

    def _on_chart_type_changed(self, chart_type_text):
        is_dynamic = chart_type_text == "Dynamic 2D Plane"
        self.run_output_widget.set_dynamic_plane_diagnostics_visibility(is_dynamic)
        self.prediction_target_widget.set_frame_reference_visibility(is_dynamic)

    def get_configuration(self):
        config = {}
        for widget in self.widgets:
            if hasattr(widget, "get_parameters"):
                config.update(widget.get_parameters())
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
            msg_box.setInformativeText(
                f"Ready to run experiment: {config['experiment_name']}\n\n"
                "You can now switch to the Monitor tab to begin the experiment."
            )
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{e}")

    def _on_apply_and_run(self):
        self._on_apply()
        self.start_training_requested.emit()
