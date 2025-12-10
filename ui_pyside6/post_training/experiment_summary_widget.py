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

        self.completed_on = QLabel("N/A")
        form_layout.addRow("Completed On:", self.completed_on)

        self.total_epochs = QLabel("N/A")
        form_layout.addRow("Total Epochs:", self.total_epochs)

        self.best_val_loss = QLabel("N/A")
        form_layout.addRow("Best Validation Loss:", self.best_val_loss)

    def update_data(self, data: dict):
        """Populates the summary fields with data from the completed run."""
        self.experiment_name.setText(data.get("Experiment Name", "N/A"))
        self.completed_on.setText(data.get("Completed On", "N/A"))
        self.total_epochs.setText(str(data.get("Total Epochs", "N/A")))
        self.best_val_loss.setText(str(data.get("Best Validation Loss", "N/A")))