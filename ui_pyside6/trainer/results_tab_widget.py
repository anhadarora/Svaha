from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QScrollArea
from ..post_training.experiment_summary_widget import ExperimentSummaryWidget
from ..post_training.parameter_configuration_widget import ParameterConfigurationWidget
from ..post_training.kpi_widget import KpiWidget
from ..post_training.trade_statistics_widget import TradeStatisticsWidget
from ..post_training.plots.loss_vs_epoch_plot_widget import LossVsEpochPlotWidget
from ..post_training.plots.correctness_vs_epoch_plot_widget import (
    CorrectnessVsEpochPlotWidget,
)
from ..post_training.plots.equity_curve_plot_widget import EquityCurvePlotWidget
from ..post_training.plots.correction_factor_history_plot_widget import (
    CorrectionFactorHistoryPlotWidget,
)
from ..post_training.plots.error_component_histogram_widget import (
    ErrorComponentHistogramWidget,
)
from ..post_training.plots.frame_shift_stability_histogram_widget import (
    FrameShiftStabilityHistogramWidget,
)


class ResultsTabWidget(QWidget):
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

        # Top Row: Summary and Parameters
        main_grid.addWidget(ExperimentSummaryWidget(), 0, 0, 1, 2)
        main_grid.addWidget(ParameterConfigurationWidget(), 0, 2, 1, 2)

        # Second Row: KPIs and Trade Statistics
        main_grid.addWidget(KpiWidget(), 1, 0, 1, 2)
        main_grid.addWidget(TradeStatisticsWidget(), 1, 2, 1, 2)

        # Plot Grid
        main_grid.addWidget(LossVsEpochPlotWidget(), 2, 0)
        main_grid.addWidget(CorrectnessVsEpochPlotWidget(), 2, 1)
        main_grid.addWidget(EquityCurvePlotWidget(), 2, 2)
        main_grid.addWidget(CorrectionFactorHistoryPlotWidget(), 3, 0)
        main_grid.addWidget(ErrorComponentHistogramWidget(), 3, 1)
        main_grid.addWidget(FrameShiftStabilityHistogramWidget(), 3, 2)
