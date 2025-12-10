from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class FrameShiftErrorPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Frame Shift Error (Live)")
        self.plot.setLabel('bottom', 'Epoch')
        self.plot.setLabel('left', 'Error Value')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)

        self.data = []
        self.curve = self.plot.plot(pen='y', name="Frame Shift Error")

    def update_data(self, metrics: dict):
        """Public slot to receive new data from the training worker."""
        epoch = metrics.get("epoch")
        error = metrics.get("frame_shift_error")

        if epoch is None or error is None:
            return

        self.data.append(error)
        x_axis = list(range(len(self.data)))
        self.curve.setData(x_axis, self.data)