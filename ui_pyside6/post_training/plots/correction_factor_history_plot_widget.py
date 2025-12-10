from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class CorrectionFactorHistoryPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Correction Factor History")
        self.plot.setLabel('bottom', 'Epoch')
        self.plot.setLabel('left', 'Correction Factor')
        self.layout.addWidget(self.plot)
        self.curve = self.plot.plot(pen='y')

    def update_data(self, plot_data: dict):
        """Populates the plot with the full history of the correction factor."""
        all_epochs_data = plot_data.get("all_epochs", [])
        if not all_epochs_data:
            return

        # This assumes the live plot widget's key was 'correction_factor'
        # The summary data from the worker doesn't have this key, so we'll use 'correction_healing' as a placeholder
        y_data = [epoch.get("correction_healing", 0) for epoch in all_epochs_data]
        x_data = [epoch.get("epoch") for epoch in all_epochs_data]
        
        self.curve.setData(x_data, y_data)