from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class ValidationLossPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Validation Loss (per Epoch)")
        self.plot.setLabel('bottom', 'Epoch Number')
        self.plot.setLabel('left', 'Loss Value')
        self.layout.addWidget(self.plot)
