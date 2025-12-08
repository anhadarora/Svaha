from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from ..pre_training.data_source_widget import DataSourceWidget
from ..pre_training.model_input_parameters_widget import ModelInputParametersWidget
from ..pre_training.model_architecture_widget import ModelArchitectureWidget
from ..pre_training.prediction_target_widget import PredictionTargetWidget
from ..pre_training.error_correction_widget import ErrorCorrectionWidget
from ..pre_training.run_output_widget import RunOutputWidget


class SetupTabWidget(QWidget):
    def __init__(self):
        super().__init__()
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

        # --- Layout Widgets ---
        # Left Column
        left_column.addWidget(self.data_source_widget)
        left_column.addWidget(self.model_input_parameters_widget)
        left_column.addStretch()

        # Right Column
        right_column.addWidget(self.model_architecture_widget)
        right_column.addWidget(self.prediction_target_widget)
        right_column.addWidget(self.error_correction_widget)
        right_column.addWidget(self.run_output_widget)
        right_column.addStretch()

        # --- Connect Signals and Set Initial State ---
        self.widgets_to_toggle = [
            self.model_input_parameters_widget,
            self.model_architecture_widget,
            self.prediction_target_widget,
            self.error_correction_widget,
            self.run_output_widget,
        ]
        
        self.data_source_widget.data_source_selected.connect(self.on_data_source_selected)
        
        # Disable widgets initially
        self.on_data_source_selected(False)

    def on_data_source_selected(self, is_selected):
        """
        Enables or disables the other setup widgets based on data source selection.
        """
        for widget in self.widgets_to_toggle:
            widget.setEnabled(is_selected)
