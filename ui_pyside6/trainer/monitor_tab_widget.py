from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
)
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

        # Snapshot visualization can be added here if desired
        # main_grid.addWidget(SnapshotVisualizationWidget(), 3, 0, 1, 3)
