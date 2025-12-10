from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np


class FrameShiftStabilityHistogramWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Frame Shift Stability Histogram")
        self.plot.setLabel('bottom', 'Frame Shift Error')
        self.plot.setLabel('left', 'Frequency')
        self.layout.addWidget(self.plot)
        self.hist = None

    def update_data(self, plot_data: dict):
        """
        Populates the plot with a histogram of frame shift errors.
        """
        all_epochs_data = plot_data.get("all_epochs", [])
        if not all_epochs_data:
            return

        errors = [epoch.get("frame_shift_error", 0) for epoch in all_epochs_data]
        
        if not errors:
            return

        y, x = np.histogram(errors, bins=20)
        
        if self.hist:
            self.plot.removeItem(self.hist)
            
        self.hist = pg.BarGraphItem(x=x, height=y, width=0.6, brush='b')
        self.plot.addItem(self.hist)