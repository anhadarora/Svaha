from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class CorrectionHealingPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Correction & Healing (Live)")
        self.plot.setLabel('bottom', 'Batch Number (Step)')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)
