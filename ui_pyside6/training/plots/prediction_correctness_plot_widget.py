from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class PredictionCorrectnessPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(
            title="Prediction Correctness (per Epoch, Train vs. Val)"
        )
        self.plot.setLabel('bottom', 'Epoch Number')
        self.plot.setLabel('left', 'Correctness Score')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)
