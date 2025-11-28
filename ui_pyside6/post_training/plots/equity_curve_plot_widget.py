from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class EquityCurvePlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Equity Curve")
        self.plot.setLabel('bottom', 'Date')
        self.plot.setLabel('left', 'Portfolio Value')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)
