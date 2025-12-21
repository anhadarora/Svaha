
from PySide6.QtWidgets import QWidget, QVBoxLayout
from pyqtgraph import PlotWidget, mkPen, LegendItem

class CombinedMetricPlotWidget(QWidget):
    def __init__(self, title: str, train_metric_key: str, val_metric_key: str, y_label: str = "Value"):
        super().__init__()
        self.train_metric_key = train_metric_key
        self.val_metric_key = val_metric_key

        self.layout = QVBoxLayout(self)
        self.plot_widget = PlotWidget()
        self.layout.addWidget(self.plot_widget)

        self.plot_widget.setTitle(title)
        self.plot_widget.setLabel('bottom', 'Epoch')
        self.plot_widget.setLabel('left', y_label)
        self.plot_widget.showGrid(x=True, y=True)
        
        # Add legend
        self.legend = self.plot_widget.addLegend()

        self.train_curve = self.plot_widget.plot(pen=mkPen('c', width=2), name=f"Train {y_label}") # Cyan for training
        self.val_curve = self.plot_widget.plot(pen=mkPen('m', width=2), name=f"Validation {y_label}") # Magenta for validation

        self.train_data_x = []
        self.train_data_y = []
        self.val_data_x = []
        self.val_data_y = []

    def update_data(self, metrics: dict):
        epoch = metrics.get('epoch')
        train_value = metrics.get(self.train_metric_key)
        val_value = metrics.get(self.val_metric_key)

        if epoch is None:
            return

        if train_value is not None:
            self.train_data_x.append(epoch)
            self.train_data_y.append(train_value)
            self.train_curve.setData(self.train_data_x, self.train_data_y)

        if val_value is not None:
            self.val_data_x.append(epoch)
            self.val_data_y.append(val_value)
            self.val_curve.setData(self.val_data_x, self.val_data_y)

    def clear_plot(self):
        self.train_data_x.clear()
        self.train_data_y.clear()
        self.val_data_x.clear()
        self.val_data_y.clear()
        self.train_curve.clear()
        self.val_curve.clear()
