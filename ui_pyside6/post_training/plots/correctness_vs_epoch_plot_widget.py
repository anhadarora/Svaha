from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class CorrectnessVsEpochPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Prediction Correctness vs. Epoch")
        self.plot.setLabel('bottom', 'Epoch')
        self.plot.setLabel('left', 'Correctness Score')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)
        self.curve = self.plot.plot(pen='b', name="Correctness")

    def update_data(self, plot_data: dict):
        """Populates the plot with the full history of prediction correctness."""
        all_epochs_data = plot_data.get("all_epochs", [])
        if not all_epochs_data:
            return

        y_data = [epoch.get("prediction_correctness", 0) for epoch in all_epochs_data]
        x_data = [epoch.get("epoch") for epoch in all_epochs_data]
        
        self.curve.setData(x_data, y_data)