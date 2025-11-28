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
