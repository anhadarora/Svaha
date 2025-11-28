from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class CorrectnessVsEpochPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Prediction Correctness vs. Epoch (Train & Validation)")
        self.plot.setLabel('bottom', 'Epoch')
        self.plot.setLabel('left', 'Correctness')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)
