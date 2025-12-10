from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np


class ErrorComponentHistogramWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Error Component Histogram")
        self.plot.setLabel('bottom', 'Value')
        self.plot.setLabel('left', 'Frequency')
        self.layout.addWidget(self.plot)
        self.hist = None

    def update_data(self, plot_data: dict):
        """
        Populates the plot with a histogram of error components.
        """
        all_epochs_data = plot_data.get("all_epochs", [])
        if not all_epochs_data:
            return

        # Combine all error components into a single list for the histogram
        error_a = [epoch.get("error_component_A", 0) for epoch in all_epochs_data]
        error_b = [epoch.get("error_component_B", 0) for epoch in all_epochs_data]
        all_errors = error_a + error_b
        
        if not all_errors:
            return

        # Create histogram
        y, x = np.histogram(all_errors, bins=20)
        
        if self.hist:
            self.plot.removeItem(self.hist)
            
        self.hist = pg.BarGraphItem(x=x, height=y, width=0.6, brush='r')
        self.plot.addItem(self.hist)