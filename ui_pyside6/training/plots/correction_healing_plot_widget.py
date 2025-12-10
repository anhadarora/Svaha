from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class CorrectionHealingPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Correction & Healing (Live)")
        self.plot.setLabel('bottom', 'Epoch')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)
        
        self.correction_data = []
        self.healing_data = []
        self.correction_curve = self.plot.plot(pen='r', name="Correction Factor")
        self.healing_curve = self.plot.plot(pen='g', name="Healing Factor")

    def update_data(self, metrics: dict):
        """Public slot to receive new data from the training worker."""
        epoch = metrics.get("epoch")
        correction = metrics.get("correction_factor") # This key will need to be in the emitted dict
        healing = metrics.get("correction_healing")
        
        if epoch is None or correction is None or healing is None:
            return
            
        self.correction_data.append(correction)
        self.healing_data.append(healing)
        
        # For simplicity, x-axis is just the count of data points
        x_axis = list(range(len(self.correction_data)))
        
        self.correction_curve.setData(x_axis, self.correction_data)
        self.healing_curve.setData(x_axis, self.healing_data)