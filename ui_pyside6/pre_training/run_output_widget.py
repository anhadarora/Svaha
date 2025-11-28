from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QCheckBox,
    QLineEdit,
)


class RunOutputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Run & Output Parameters")
        self.layout.addWidget(group)

        form_layout = QFormLayout(group)

        self.experiment_name = QLineEdit()
        form_layout.addRow("Experiment Name:", self.experiment_name)

        self.save_model = QCheckBox()
        form_layout.addRow("Save Model:", self.save_model)

        self.output_metrics = QWidget()
        output_metrics_layout = QVBoxLayout(self.output_metrics)
        self.loss_curve_check = QCheckBox("Loss Curve")
        self.accuracy_curve_check = QCheckBox("Accuracy Curve")
        self.sharpe_ratio_check = QCheckBox("Sharpe Ratio")
        self.frame_drift_log_check = QCheckBox("Frame Drift Log")
        output_metrics_layout.addWidget(self.loss_curve_check)
        output_metrics_layout.addWidget(self.accuracy_curve_check)
        output_metrics_layout.addWidget(self.sharpe_ratio_check)
        output_metrics_layout.addWidget(self.frame_drift_log_check)
        form_layout.addRow("Output Metrics:", self.output_metrics)
