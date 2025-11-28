from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel


class ExperimentSummaryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Experiment Summary")
        self.layout.addWidget(group)

        form_layout = QFormLayout(group)

        self.experiment_name = QLabel("N/A")
        form_layout.addRow("Experiment Name:", self.experiment_name)

        self.final_status = QLabel("N/A")
        form_layout.addRow("Final Status:", self.final_status)

        self.total_training_time = QLabel("N/A")
        form_layout.addRow("Total Training Time:", self.total_training_time)

        self.best_model_checkpoint = QLabel("N/A")
        self.best_model_checkpoint.setOpenExternalLinks(True)
        form_layout.addRow("Best Model Checkpoint:", self.best_model_checkpoint)
