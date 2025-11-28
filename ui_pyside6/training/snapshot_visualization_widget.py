from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel
import pyqtgraph as pg


class SnapshotVisualizationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Live Snapshot Visualization")
        self.layout.addWidget(group)

        plot_layout = QVBoxLayout(group)

        self.last_input_snapshot = pg.ImageView()
        plot_layout.addWidget(self.last_input_snapshot)

        self.static_chart = pg.ImageView()
        plot_layout.addWidget(self.static_chart)

        self.predicted_output = pg.ImageView()
        plot_layout.addWidget(self.predicted_output)
