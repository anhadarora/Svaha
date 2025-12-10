from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class PredictionCorrectnessPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(
            title="Prediction Correctness (per Epoch)"
        )
        self.plot.setLabel('bottom', 'Epoch')
        self.plot.setLabel('left', 'Correctness Score')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)

        self.data = []
        self.curve = self.plot.plot(pen='b', name="Prediction Correctness")

    def update_data(self, metrics: dict):
        """Public slot to receive new data from the training worker."""
        epoch = metrics.get("epoch")
        correctness = metrics.get("prediction_correctness")

        if epoch is None or correctness is None:
            return

        self.data.append(correctness)
        x_axis = list(range(len(self.data)))
        self.curve.setData(x_axis, self.data)