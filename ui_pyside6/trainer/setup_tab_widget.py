from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from ..pre_training.data_source_widget import DataSourceWidget
from ..pre_training.dynamic_plane_widget import DynamicPlaneWidget
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

        # Left Column
        left_column.addWidget(DataSourceWidget())
        left_column.addWidget(DynamicPlaneWidget())
        left_column.addStretch()

        # Right Column
        right_column.addWidget(ModelArchitectureWidget())
        right_column.addWidget(PredictionTargetWidget())
        right_column.addWidget(ErrorCorrectionWidget())
        right_column.addWidget(RunOutputWidget())
        right_column.addStretch()
