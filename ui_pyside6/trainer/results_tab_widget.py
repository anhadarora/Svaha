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

        # --- Instantiate Widgets ---
        self.summary_widget = ExperimentSummaryWidget()
        self.params_widget = ParameterConfigurationWidget()
        self.kpi_widget = KpiWidget()
        self.trades_widget = TradeStatisticsWidget()
        self.loss_plot = LossVsEpochPlotWidget()
        self.correctness_plot = CorrectnessVsEpochPlotWidget()
        self.equity_curve_plot = EquityCurvePlotWidget()
        self.correction_factor_plot = CorrectionFactorHistoryPlotWidget()
        self.error_hist_plot = ErrorComponentHistogramWidget()
        self.frame_shift_hist_plot = FrameShiftStabilityHistogramWidget()

        self.all_widgets = [
            self.summary_widget, self.params_widget, self.kpi_widget,
            self.trades_widget, self.loss_plot, self.correctness_plot,
            self.equity_curve_plot, self.correction_factor_plot,
            self.error_hist_plot, self.frame_shift_hist_plot
        ]

        # --- Layout Widgets ---
        main_grid.addWidget(self.summary_widget, 0, 0, 1, 2)
        main_grid.addWidget(self.params_widget, 0, 2, 1, 2)
        main_grid.addWidget(self.kpi_widget, 1, 0, 1, 2)
        main_grid.addWidget(self.trades_widget, 1, 2, 1, 2)
        main_grid.addWidget(self.loss_plot, 2, 0)
        main_grid.addWidget(self.correctness_plot, 2, 1)
        main_grid.addWidget(self.equity_curve_plot, 2, 2)
        main_grid.addWidget(self.correction_factor_plot, 3, 0)
        main_grid.addWidget(self.error_hist_plot, 3, 1)
        main_grid.addWidget(self.frame_shift_hist_plot, 3, 2)

    def load_results(self, summary_data: dict):
        """
        Public slot to receive the final results dictionary and populate all child widgets.
        """
        if not summary_data:
            print("Results tab received empty summary data.")
            return

        # Pass the relevant slice of data to each widget
        self.summary_widget.update_data(summary_data.get("experiment_summary", {}))
        self.params_widget.update_data(summary_data.get("parameter_configuration", {}))
        self.kpi_widget.update_data(summary_data.get("kpis", {}))
        self.trades_widget.update_data(summary_data.get("trade_statistics", {}))
        
        # Pass the full plot data to all plot widgets
        plot_data = summary_data.get("plot_data", {})
        if plot_data:
            self.loss_plot.update_data(plot_data)
            self.correctness_plot.update_data(plot_data)
            self.equity_curve_plot.update_data(plot_data)
            self.correction_factor_plot.update_data(plot_data)
            self.error_hist_plot.update_data(plot_data)
            self.frame_shift_hist_plot.update_data(plot_data)