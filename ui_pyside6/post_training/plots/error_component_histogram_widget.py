from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class ErrorComponentHistogramWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Error Component Histogram")
        self.plot.setLabel('bottom', 'Error Component')
        self.plot.setLabel('left', 'Frequency')
        self.layout.addWidget(self.plot)
