from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)
import json
import os

from ..training.run_status_widget import RunStatusWidget
from ..training.progress_indicators_widget import ProgressIndicatorsWidget
from ..training.snapshot_visualization_widget import SnapshotVisualizationWidget
from ..training.plots.training_loss_plot_widget import TrainingLossPlotWidget
from ..training.plots.validation_loss_plot_widget import ValidationLossPlotWidget
from ..training.plots.prediction_correctness_plot_widget import (
    PredictionCorrectnessPlotWidget,
)
from ..training.plots.frame_shift_error_plot_widget import FrameShiftErrorPlotWidget
from ..training.plots.correction_healing_plot_widget import (
    CorrectionHealingPlotWidget,
)
from ..training.plots.error_component_plot_widget import ErrorComponentPlotWidget


class MonitorTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        container = QWidget()
        scroll_area.setWidget(container)
        main_grid = QGridLayout(container)

        # Top Bar
        top_bar = QHBoxLayout()
        self.begin_button = QPushButton("Begin Experiment")
        self.begin_button.clicked.connect(self._on_begin_clicked)
        top_bar.addWidget(self.begin_button)
        top_bar.addStretch()
        top_bar.addWidget(RunStatusWidget())
        top_bar.addWidget(ProgressIndicatorsWidget())
        main_grid.addLayout(top_bar, 0, 0, 1, 3)  # Span 3 columns

        # Plot Grid
        main_grid.addWidget(TrainingLossPlotWidget(), 1, 0)
        main_grid.addWidget(ValidationLossPlotWidget(), 1, 1)
        main_grid.addWidget(PredictionCorrectnessPlotWidget(), 1, 2)
        main_grid.addWidget(FrameShiftErrorPlotWidget(), 2, 0)
        main_grid.addWidget(CorrectionHealingPlotWidget(), 2, 1)
        main_grid.addWidget(ErrorComponentPlotWidget(), 2, 2)

    def begin_training(self):
        """Public method to programmatically start the training."""
        self.begin_button.click()

    def _on_begin_clicked(self):
        """Loads the last applied config and starts the training process."""
        config_path = os.path.abspath("./build/last_applied_config.json")
        
        if not os.path.exists(config_path):
            QMessageBox.critical(self, "Error", "No configuration applied. Please go to the Setup tab and click 'Apply' first.")
            return

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            
            print("--- Starting Experiment ---")
            print(f"Experiment Name: {config.get('experiment_name', 'N/A')}")
            # In a real scenario, you would pass this config to a training worker thread.
            print("Configuration loaded. Training process would start now.")
            
            self.begin_button.setEnabled(False)
            self.begin_button.setText("Experiment Running...")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load or parse configuration file:\n{e}")