from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class EquityCurvePlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget(title="Equity Curve")
        self.plot.setLabel('bottom', 'Trade Number')
        self.plot.setLabel('left', 'Portfolio Value')
        self.plot.addLegend()
        self.layout.addWidget(self.plot)
        self.curve = self.plot.plot(pen='g', name="Strategy")

    def update_data(self, plot_data: dict):
        """
        Populates the plot with the equity curve from a backtest.
        NOTE: The current worker does not produce a backtest summary,
              so this will show placeholder data.
        """
        print("EquityCurvePlotWidget: update_data called. Needs real backtest data to plot.")
        # Placeholder data to show something
        self.curve.setData([100, 102, 105, 103, 108, 110])