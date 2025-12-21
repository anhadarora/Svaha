
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QScrollArea
from ..post_training.experiment_summary_widget import ExperimentSummaryWidget
from ..post_training.parameter_configuration_widget import ParameterConfigurationWidget
from ..post_training.plots.sample_prediction_plot_widget import SamplePredictionPlotWidget
from ..post_training.plots.confusion_matrix_widget import ConfusionMatrixWidget

class ResultsTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dynamic_widgets = []
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        container = QWidget()
        scroll_area.setWidget(container)
        self.main_grid = QGridLayout(container)

        # --- Static Widgets ---
        self.summary_widget = ExperimentSummaryWidget()
        self.params_widget = ParameterConfigurationWidget()
        
        self.main_grid.addWidget(self.summary_widget, 0, 0)
        self.main_grid.addWidget(self.params_widget, 0, 1)

    def load_results(self, summary_data: dict):
        """
        Public slot to receive the final results dictionary and dynamically populate the tab.
        """
        self._clear_dynamic_widgets()
        
        if not summary_data:
            print("Results tab received empty summary data.")
            return

        # --- Update Static Widgets ---
        self.summary_widget.update_data(summary_data.get("experiment_summary", {}))
        self.params_widget.update_data(summary_data.get("parameter_configuration", {}))

        # --- Dynamically Create and Populate Inference Widgets ---
        inference_results = summary_data.get("inference_results", {})
        if not inference_results:
            return
            
        row = 1 # Start placing dynamic widgets below the static ones
        
        for head_name, results in inference_results.items():
            # Determine if the head is classification or regression
            is_classification = 'classification' in head_name or 'confidence' in head_name
            
            # 1. Create Sample Prediction Plot
            mode = 'classification' if is_classification else 'regression'
            pred_plot = SamplePredictionPlotWidget(title=f"Sample Predictions: {head_name}", mode=mode)
            pred_plot.update_data(results.get('true_sample', []), results.get('pred_sample', []))
            self.main_grid.addWidget(pred_plot, row, 0)
            self.dynamic_widgets.append(pred_plot)
            
            # 2. Create Confusion Matrix if available
            if 'confusion_matrix' in results:
                cm_widget = ConfusionMatrixWidget(title=f"Confusion Matrix: {head_name}")
                cm_widget.update_data(results.get('confusion_matrix', []))
                self.main_grid.addWidget(cm_widget, row, 1)
                self.dynamic_widgets.append(cm_widget)
            
            row += 1 # Move to the next row for the next head

    def _clear_dynamic_widgets(self):
        for widget in self.dynamic_widgets:
            self.main_grid.removeWidget(widget)
            widget.deleteLater()
        self.dynamic_widgets.clear()
