from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class TrainingLossPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Training Loss (per Epoch)")
        self.plot.setLabel('bottom', 'Epoch')
        self.plot.setLabel('left', 'Loss Value')
        self.layout.addWidget(self.plot)

        self.data = []
        self.curve = self.plot.plot(pen='g', name="Training Loss")

    def update_data(self, metrics: dict):
        """Public slot to receive new data from the training worker."""
        epoch = metrics.get("epoch")
        loss = metrics.get("train_loss")

        if epoch is None or loss is None:
            return

        self.data.append(loss)
        x_axis = list(range(len(self.data)))
        self.curve.setData(x_axis, self.data)