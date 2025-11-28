from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QSlider,
    QCheckBox,
    QLabel,
)
from PySide6.QtCore import Qt


class DynamicPlaneWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Dynamic Plane Transformation Parameters")
        self.layout.addWidget(group)

        form_layout = QFormLayout(group)

        self.enable_dynamic_plane = QCheckBox()
        form_layout.addRow("Enable Dynamic Plane:", self.enable_dynamic_plane)

        self.window_size = QSlider(Qt.Horizontal)
        self.window_size.setRange(5, 50)
        form_layout.addRow("Window Size (N):", self.window_size)

        self.time_norm_method = QComboBox()
        self.time_norm_method.addItems(["Fractional Elapsed Time", "Linear Index"])
        form_layout.addRow("Time Normalization Method:", self.time_norm_method)

        self.time_norm_range = QComboBox()
        self.time_norm_range.addItems(["[0, 1]", "[-1, 1]"])
        form_layout.addRow("Time Normalization Range:", self.time_norm_range)

        self.price_norm_method = QComboBox()
        self.price_norm_method.addItems(["Log Return", "Percent Return"])
        form_layout.addRow("Price Normalization Method:", self.price_norm_method)

        self.price_clipping = QComboBox()
        self.price_clipping.addItems(["None", "5th/95th Percentile", "1st/99th Percentile"])
        form_layout.addRow("Price Clipping Threshold:", self.price_clipping)

        self.price_norm_range = QComboBox()
        self.price_norm_range.addItems(["[-1, 1]", "Raw Scaled"])
        form_layout.addRow("Price Normalization Range:", self.price_norm_range)

        self.volume_norm_method = QComboBox()
        self.volume_norm_method.addItems(
            ["Log-Transform + Robust Scaling (IQR)", "Log-Transform + Standard Scaling (Z-score)"]
        )
        form_layout.addRow("Volume Normalization Method:", self.volume_norm_method)

        self.volume_clipping = QComboBox()
        self.volume_clipping.addItems(["None", "5th/95th Percentile"])
        form_layout.addRow("Volume Clipping Threshold:", self.volume_clipping)

        self.volume_norm_range = QComboBox()
        self.volume_norm_range.addItems(["[-1, 1]", "Raw Scaled"])
        form_layout.addRow("Volume Normalization Range:", self.volume_norm_range)

        self.basis_method = QComboBox()
        self.basis_method.addItems(["PCA", "ICA", "Raw Normalized"])
        form_layout.addRow("Basis Method:", self.basis_method)
