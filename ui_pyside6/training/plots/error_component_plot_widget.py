from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class ErrorComponentPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(
            title="Error Component Contribution (Live)"
        )
        self.plot.setLabel('bottom', 'Epoch')
        self.plot.setLabel('left', 'Error Value')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)

        self.component_a_data = []
        self.component_b_data = []
        self.component_a_curve = self.plot.plot(pen='c', name="Component A")
        self.component_b_curve = self.plot.plot(pen='m', name="Component B")

    def update_data(self, metrics: dict):
        """Public slot to receive new data from the training worker."""
        epoch = metrics.get("epoch")
        comp_a = metrics.get("error_component_A")
        comp_b = metrics.get("error_component_B")

        if epoch is None or comp_a is None or comp_b is None:
            return

        self.component_a_data.append(comp_a)
        self.component_b_data.append(comp_b)
        
        x_axis = list(range(len(self.component_a_data)))

        self.component_a_curve.setData(x_axis, self.component_a_data)
        self.component_b_curve.setData(x_axis, self.component_b_data)