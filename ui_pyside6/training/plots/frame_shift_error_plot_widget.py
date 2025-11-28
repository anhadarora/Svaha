from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class FrameShiftErrorPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Frame Shift Error (Live)")
        self.plot.setLabel('bottom', 'Batch Number (Step)')
        self.plot.setLabel('left', 'Angle (Degrees or Radians)')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)
