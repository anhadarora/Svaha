from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class FrameShiftStabilityHistogramWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Frame Shift Stability Histogram")
        self.plot.setLabel('bottom', 'Frame Shift Error')
        self.plot.setLabel('left', 'Frequency')
        self.layout.addWidget(self.plot)
