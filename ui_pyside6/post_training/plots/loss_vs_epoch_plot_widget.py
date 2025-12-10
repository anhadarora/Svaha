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
        
        self.train_curve = self.plot.plot(pen='g', name="Training Loss")
        self.val_curve = self.plot.plot(pen='r', name="Validation Loss")

    def update_data(self, plot_data: dict):
        """Populates the plot with the full history of training and validation loss."""
        all_epochs_data = plot_data.get("all_epochs", [])
        if not all_epochs_data:
            return

        train_loss = [epoch.get("train_loss", 0) for epoch in all_epochs_data]
        val_loss = [epoch.get("val_loss", 0) for epoch in all_epochs_data]
        x_data = [epoch.get("epoch") for epoch in all_epochs_data]
        
        self.train_curve.setData(x_data, train_loss)
        self.val_curve.setData(x_data, val_loss)