from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QSlider,
    QCheckBox,
    QLabel,
    QSizePolicy,
)
from PySide6.QtCore import Qt


class ModelInputParametersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Model Input Parameters")
        self.layout.addWidget(group)

        layout = QVBoxLayout(group)

        # Chart Type
        layout.addWidget(QLabel("Chart Type:"))
        self.chart_type = QComboBox()
        self.chart_type.addItems(["Candlestick", "Heiken-Ashi"])
        self.chart_type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.chart_type)

        # Enable Dynamic Plane
        self.enable_dynamic_plane = QCheckBox("Enable Dynamic Plane")
        layout.addWidget(self.enable_dynamic_plane)

        # Window Size
        layout.addWidget(QLabel("Window Size (N):"))
        self.window_size = QSlider(Qt.Horizontal)
        self.window_size.setRange(5, 50)
        layout.addWidget(self.window_size)

        # Time Normalization Method
        layout.addWidget(QLabel("Time Normalization Method:"))
        self.time_norm_method = QComboBox()
        self.time_norm_method.addItems(["Fractional Elapsed Time", "Linear Index"])
        self.time_norm_method.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.time_norm_method)

        # Time Normalization Range
        layout.addWidget(QLabel("Time Normalization Range:"))
        self.time_norm_range = QComboBox()
        self.time_norm_range.addItems(["[0, 1]", "[-1, 1]"])
        self.time_norm_range.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.time_norm_range)

        # Price Normalization Method
        layout.addWidget(QLabel("Price Normalization Method:"))
        self.price_norm_method = QComboBox()
        self.price_norm_method.addItems(["Log Return", "Percent Return"])
        self.price_norm_method.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.price_norm_method)

        # Price Clipping Threshold
        layout.addWidget(QLabel("Price Clipping Threshold:"))
        self.price_clipping = QComboBox()
        self.price_clipping.addItems(["None", "5th/95th Percentile", "1st/99th Percentile"])
        self.price_clipping.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.price_clipping)

        # Price Normalization Range
        layout.addWidget(QLabel("Price Normalization Range:"))
        self.price_norm_range = QComboBox()
        self.price_norm_range.addItems(["[-1, 1]", "Raw Scaled"])
        self.price_norm_range.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.price_norm_range)

        # Volume Normalization Method
        layout.addWidget(QLabel("Volume Normalization Method:"))
        self.volume_norm_method = QComboBox()
        self.volume_norm_method.addItems(
            ["Log-Transform + Robust Scaling (IQR)", "Log-Transform + Standard Scaling (Z-score)"]
        )
        self.volume_norm_method.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.volume_norm_method)

        # Volume Clipping Threshold
        layout.addWidget(QLabel("Volume Clipping Threshold:"))
        self.volume_clipping = QComboBox()
        self.volume_clipping.addItems(["None", "5th/95th Percentile"])
        self.volume_clipping.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.volume_clipping)

        # Volume Normalization Range
        layout.addWidget(QLabel("Volume Normalization Range:"))
        self.volume_norm_range = QComboBox()
        self.volume_norm_range.addItems(["[-1, 1]", "Raw Scaled"])
        self.volume_norm_range.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.volume_norm_range)

        # Basis Method
        layout.addWidget(QLabel("Basis Method:"))
        self.basis_method = QComboBox()
        self.basis_method.addItems(["PCA", "ICA", "Raw Normalized"])
        self.basis_method.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.basis_method)
        
        layout.addStretch()