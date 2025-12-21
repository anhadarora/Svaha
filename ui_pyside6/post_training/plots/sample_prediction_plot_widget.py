
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
import numpy as np

class SamplePredictionPlotWidget(QWidget):
    def __init__(self, title="Sample Predictions", mode='regression'):
        super().__init__()
        self.mode = mode
        
        self.layout = QVBoxLayout(self)
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        
        self.plot_widget.setTitle(title)
        self.plot_widget.showGrid(x=True, y=True)

        if self.mode == 'regression':
            self.plot_widget.setLabel('bottom', 'True Values')
            self.plot_widget.setLabel('left', 'Predicted Values')
            self.scatter = pg.ScatterPlotItem(pen=pg.mkPen(None), brush=pg.mkBrush(0, 255, 255, 150), size=7)
            self.plot_widget.addItem(self.scatter)
            # Add a y=x line for reference
            self.line = pg.PlotDataItem(pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))
            self.plot_widget.addItem(self.line)
        else: # classification
            self.plot_widget.setLabel('bottom', 'Sample Index')
            self.plot_widget.setLabel('left', 'Class')
            self.true_line = self.plot_widget.plot(pen=pg.mkPen('w', width=2), name="True Labels")
            self.correct_scatter = pg.ScatterPlotItem(pen=pg.mkPen(None), brush=pg.mkBrush(0, 255, 0, 200), size=10, symbol='o', name="Correct")
            self.incorrect_scatter = pg.ScatterPlotItem(pen=pg.mkPen(None), brush=pg.mkBrush(255, 0, 0, 200), size=10, symbol='x', name="Incorrect")
            self.plot_widget.addItem(self.correct_scatter)
            self.plot_widget.addItem(self.incorrect_scatter)
            self.plot_widget.addLegend()

    def update_data(self, true_sample: list, pred_sample: list):
        if not true_sample or not pred_sample:
            return

        true = np.array(true_sample)
        pred = np.array(pred_sample)

        if self.mode == 'regression':
            self.scatter.setData(x=true, y=pred.flatten())
            # Update reference line to span the data range
            min_val = min(true.min(), pred.min())
            max_val = max(true.max(), pred.max())
            self.line.setData([min_val, max_val], [min_val, max_val])
        else: # classification
            if pred.ndim > 1 and pred.shape[1] > 1: # Softmax output
                pred_classes = np.argmax(pred, axis=1)
            else: # Sigmoid or single class output
                pred_classes = np.round(pred).flatten()
            
            indices = np.arange(len(true))
            correct_mask = (true == pred_classes)
            
            self.true_line.setData(indices, true)
            self.correct_scatter.setData(indices[correct_mask], true[correct_mask])
            self.incorrect_scatter.setData(indices[~correct_mask], true[~correct_mask])

    def clear_plot(self):
        if self.mode == 'regression':
            self.scatter.clear()
            self.line.clear()
        else:
            self.true_line.clear()
            self.correct_scatter.clear()
            self.incorrect_scatter.clear()
