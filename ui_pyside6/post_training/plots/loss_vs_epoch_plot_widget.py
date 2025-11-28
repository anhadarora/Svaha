from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class LossVsEpochPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Loss vs. Epoch (Train & Validation)")
        self.plot.setLabel('bottom', 'Epoch')
        self.plot.setLabel('left', 'Loss')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)
