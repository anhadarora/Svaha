from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class TrainingLossPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Training Loss (per Batch)")
        self.plot.setLabel('bottom', 'Batch Number (Step)')
        self.plot.setLabel('left', 'Loss Value')
        self.layout.addWidget(self.plot)
