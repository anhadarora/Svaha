from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Signal
import json
import os

from analysis.training_worker import TrainingWorker
from ..training.run_status_widget import RunStatusWidget
from ..training.progress_indicators_widget import ProgressIndicatorsWidget
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
    training_run_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.training_worker = None
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        container = QWidget()
        scroll_area.setWidget(container)
        main_grid = QGridLayout(container)

        # --- Top Bar ---
        top_bar = QHBoxLayout()
        self.begin_button = QPushButton("Begin Experiment")
        self.begin_button.clicked.connect(self._on_begin_clicked)
        top_bar.addWidget(self.begin_button)
        top_bar.addStretch()
        self.run_status_widget = RunStatusWidget()
        self.progress_indicators_widget = ProgressIndicatorsWidget()
        top_bar.addWidget(self.run_status_widget)
        top_bar.addWidget(self.progress_indicators_widget)
        main_grid.addLayout(top_bar, 0, 0, 1, 3)

        # --- Plot Grid ---
        self.training_loss_plot = TrainingLossPlotWidget()
        self.validation_loss_plot = ValidationLossPlotWidget()
        self.prediction_correctness_plot = PredictionCorrectnessPlotWidget()
        self.frame_shift_error_plot = FrameShiftErrorPlotWidget()
        self.correction_healing_plot = CorrectionHealingPlotWidget()
        self.error_component_plot = ErrorComponentPlotWidget()

        self.dynamic_plane_plots = [
            self.frame_shift_error_plot,
            self.correction_healing_plot,
            self.error_component_plot,
        ]

        main_grid.addWidget(self.training_loss_plot, 1, 0)
        main_grid.addWidget(self.validation_loss_plot, 1, 1)
        main_grid.addWidget(self.prediction_correctness_plot, 1, 2)
        main_grid.addWidget(self.frame_shift_error_plot, 2, 0)
        main_grid.addWidget(self.correction_healing_plot, 2, 1)
        main_grid.addWidget(self.error_component_plot, 2, 2)

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
            
            is_dynamic_plane = config.get("chart_type") == "Dynamic 2D Plane"
            for plot in self.dynamic_plane_plots:
                plot.setVisible(is_dynamic_plane)

            self.begin_button.setEnabled(False)
            self.begin_button.setText("Experiment Running...")
            
            # Setup and start the worker
            self.training_worker = TrainingWorker(config)
            self.training_worker.comm.log_message.connect(self._update_log)
            self.training_worker.comm.epoch_completed.connect(self._update_plots)
            self.training_worker.comm.training_finished.connect(self._on_training_finished)
            self.training_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load or parse configuration file:\n{e}")
            self.begin_button.setEnabled(True)
            self.begin_button.setText("Begin Experiment")

    def _update_log(self, message):
        print(f"LOG: {message}")

    def _update_plots(self, metrics):
        self.training_loss_plot.update_data(metrics)
        self.validation_loss_plot.update_data(metrics)
        self.prediction_correctness_plot.update_data(metrics)
        
        if self.frame_shift_error_plot.isVisible():
            self.frame_shift_error_plot.update_data(metrics)
        if self.correction_healing_plot.isVisible():
            self.correction_healing_plot.update_data(metrics)
        if self.error_component_plot.isVisible():
            self.error_component_plot.update_data(metrics)

    def _on_training_finished(self, final_results):
        self.begin_button.setEnabled(True)
        self.begin_button.setText("Begin Experiment")
        QMessageBox.information(self, "Training Complete", "The training process has finished.")
        self.training_run_completed.emit(final_results)