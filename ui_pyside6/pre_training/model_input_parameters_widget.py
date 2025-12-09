from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QComboBox,
    QLabel,
    QSizePolicy,
    QSpinBox,
    QHBoxLayout,
    QPushButton,
    QColorDialog,
    QCheckBox,
    QStackedWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from ..widgets.accordion import Accordion

class ModelInputParametersWidget(QWidget):
    configuration_changed = Signal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Model Input Parameters")
        self.layout.addWidget(group)

        layout = QVBoxLayout(group)

        data_processing_layout = QHBoxLayout()
        data_processing_layout.addLayout(self._create_spinbox_layout("Resampling Factor:", 1, 1000, 1, "e.g., set to 60 to construct 1-hour candles from 1-minute source data."))
        data_processing_layout.addLayout(self._create_spinbox_layout("Input Window Size (N):", 3, 15, 5, "Number of candles in a single training sample."))
        data_processing_layout.addLayout(self._create_spinbox_layout("Prediction Horizon (k):", 1, 100, 1, "How many steps into the future the label represents."))
        layout.addLayout(data_processing_layout)
        
        layout.addWidget(QLabel("Chart Type:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Candlestick", "Heikin-Ashi", "Line", "OHLC Bar", 
            "Hollow Candlestick", "Renko", "Point & Figure", "Dynamic 2D Plane"
        ])
        self.chart_type_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.chart_type_combo)

        self.settings_stack = QStackedWidget()
        layout.addWidget(self.settings_stack)

        self.style_accordion = Accordion()
        style_settings_content = self._create_style_settings_widget()
        self.style_accordion.add_item("Style Settings", style_settings_content)
        self.settings_stack.addWidget(self.style_accordion)

        self.dynamic_plane_widget = self._create_dynamic_plane_widget()
        self.settings_stack.addWidget(self.dynamic_plane_widget)

        layout.addWidget(QLabel("Tensor Channel Depth:"))
        self.channel_depth_combo = QComboBox()
        self.channel_depth_combo.addItems(["Grayscale (1ch)", "RGB (3ch)", "RGB + Delta"])
        self.channel_depth_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.channel_depth_combo)

        layout.addStretch()

    def connect_signals(self):
        self.resampling_factor_spinbox.valueChanged.connect(self.configuration_changed)
        self.input_window_size_n_spinbox.valueChanged.connect(self.configuration_changed)
        self.prediction_horizon_k_spinbox.valueChanged.connect(self.configuration_changed)
        self.chart_type_combo.currentTextChanged.connect(self.configuration_changed)
        self.channel_depth_combo.currentIndexChanged.connect(self.configuration_changed)
        self.target_height_spinbox.valueChanged.connect(self.configuration_changed)
        self.target_width_spinbox.valueChanged.connect(self.configuration_changed)
        self.bar_width_px_spinbox.valueChanged.connect(self.configuration_changed)
        self.border_thickness_px_spinbox.valueChanged.connect(self.configuration_changed)
        self.line_width_px_spinbox.valueChanged.connect(self.configuration_changed)
        self.scaling_mode_combo.currentIndexChanged.connect(self.configuration_changed)
        self.volume_display_combo.currentIndexChanged.connect(self.configuration_changed)
        self.ma_checkbox.toggled.connect(self.configuration_changed)
        self.ma_period_spinbox.valueChanged.connect(self.configuration_changed)
        self.time_basis_check.toggled.connect(self.configuration_changed)
        self.price_basis_check.toggled.connect(self.configuration_changed)
        self.volume_basis_check.toggled.connect(self.configuration_changed)
        self.norm_strategy_combo.currentIndexChanged.connect(self.configuration_changed)
        self.rotation_logic_combo.currentIndexChanged.connect(self.configuration_changed)
        self.drift_error_check.toggled.connect(self.configuration_changed)
        self.chart_type_combo.currentTextChanged.connect(self._on_chart_type_changed)

    def get_parameters(self):
        params = {
            "resampling_factor": self.resampling_factor_spinbox.value(),
            "input_window_size": self.input_window_size_n_spinbox.value(),
            "prediction_horizon": self.prediction_horizon_k_spinbox.value(),
            "chart_type": self.chart_type_combo.currentText(),
            "channel_depth": self.channel_depth_combo.currentText(),
        }
        if params["chart_type"] == "Dynamic 2D Plane":
            params["dynamic_plane_settings"] = {
                "basis_vectors": {
                    "time": self.time_basis_check.isChecked(),
                    "price": self.price_basis_check.isChecked(),
                    "volume": self.volume_basis_check.isChecked(),
                },
                "normalization_strategy": self.norm_strategy_combo.currentText(),
                "rotation_logic": self.rotation_logic_combo.currentText(),
                "include_drift_error": self.drift_error_check.isChecked(),
            }
        else:
            params["style_settings"] = {
                "target_height": self.target_height_spinbox.value(),
                "target_width": self.target_width_spinbox.value(),
                "bar_width": self.bar_width_px_spinbox.value(),
                "border_thickness": self.border_thickness_px_spinbox.value(),
                "line_width": self.line_width_px_spinbox.value(),
                "scaling_mode": self.scaling_mode_combo.currentText(),
                "volume_display": self.volume_display_combo.currentText(),
                "overlays": {
                    "moving_average": {
                        "enabled": self.ma_checkbox.isChecked(),
                        "period": self.ma_period_spinbox.value(),
                    }
                }
            }
        return params

    def _on_chart_type_changed(self, chart_type):
        if chart_type == "Dynamic 2D Plane":
            self.settings_stack.setCurrentWidget(self.dynamic_plane_widget)
        else:
            self.settings_stack.setCurrentWidget(self.style_accordion)

    def _create_spinbox_layout(self, label, min_val, max_val, default_val, tooltip):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default_val)
        spinbox.setToolTip(tooltip)
        spinbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(spinbox)
        attr_name = label.lower().replace(" ", "_").replace(":", "").replace("(n)", "n").replace("(k)", "k").replace("(px)","px")
        setattr(self, f"{attr_name}_spinbox", spinbox)
        return layout

    def _create_style_settings_widget(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Image Resolution (H x W):"))
        self.target_height_spinbox = QSpinBox()
        self.target_height_spinbox.setRange(32, 1024)
        self.target_height_spinbox.setValue(64)
        resolution_layout.addWidget(self.target_height_spinbox)
        self.target_width_spinbox = QSpinBox()
        self.target_width_spinbox.setRange(32, 1024)
        self.target_width_spinbox.setValue(128)
        resolution_layout.addWidget(self.target_width_spinbox)
        layout.addLayout(resolution_layout)
        bar_line_layout = QHBoxLayout()
        bar_line_layout.addLayout(self._create_spinbox_layout("Bar Width (px):", 1, 20, 5, ""))
        bar_line_layout.addLayout(self._create_spinbox_layout("Border Thickness (px):", 0, 5, 1, ""))
        bar_line_layout.addLayout(self._create_spinbox_layout("Line Width (px):", 1, 10, 2, ""))
        layout.addLayout(bar_line_layout)
        color_layout = QHBoxLayout()
        self.up_color_button = QPushButton("Up Color")
        self.down_color_button = QPushButton("Down Color")
        self.bg_color_button = QPushButton("Background Color")
        color_layout.addWidget(self.up_color_button)
        color_layout.addWidget(self.down_color_button)
        color_layout.addWidget(self.bg_color_button)
        self.up_color_button.clicked.connect(lambda: self._open_color_dialog(self.up_color_button))
        self.down_color_button.clicked.connect(lambda: self._open_color_dialog(self.down_color_button))
        self.bg_color_button.clicked.connect(lambda: self._open_color_dialog(self.bg_color_button, is_bg=True))
        layout.addLayout(color_layout)
        scaling_volume_layout = QHBoxLayout()
        scaling_layout = QVBoxLayout()
        scaling_layout.addWidget(QLabel("Scaling Mode:"))
        self.scaling_mode_combo = QComboBox()
        self.scaling_mode_combo.addItems(["Local Min-Max", "Global Min-Max", "Logarithmic"])
        scaling_layout.addWidget(self.scaling_mode_combo)
        scaling_volume_layout.addLayout(scaling_layout)
        volume_layout = QVBoxLayout()
        volume_layout.addWidget(QLabel("Volume Display:"))
        self.volume_display_combo = QComboBox()
        self.volume_display_combo.addItems(["None", "Overlay", "Bottom Subplot", "Color-Coded"])
        volume_layout.addWidget(self.volume_display_combo)
        scaling_volume_layout.addLayout(volume_layout)
        layout.addLayout(scaling_volume_layout)
        overlays_group = QGroupBox("Technical Overlays")
        overlays_layout = QHBoxLayout(overlays_group)
        self.ma_checkbox = QCheckBox("Moving Average")
        self.ma_period_spinbox = QSpinBox()
        self.ma_period_spinbox.setRange(2, 200)
        self.ma_period_spinbox.setValue(20)
        self.ma_period_spinbox.setEnabled(False)
        self.ma_checkbox.toggled.connect(self.ma_period_spinbox.setEnabled)
        overlays_layout.addWidget(self.ma_checkbox)
        overlays_layout.addWidget(QLabel("Period:"))
        overlays_layout.addWidget(self.ma_period_spinbox)
        overlays_layout.addStretch()
        layout.addWidget(overlays_group)
        return container

    def _create_dynamic_plane_widget(self):
        container = QGroupBox("Dynamic Plane Configuration")
        layout = QVBoxLayout(container)
        basis_group = QGroupBox("Basis Vectors")
        basis_layout = QHBoxLayout(basis_group)
        self.time_basis_check = QCheckBox("Time")
        self.price_basis_check = QCheckBox("Price")
        self.volume_basis_check = QCheckBox("Volume")
        self.time_basis_check.setChecked(True)
        self.price_basis_check.setChecked(True)
        basis_layout.addWidget(self.time_basis_check)
        basis_layout.addWidget(self.price_basis_check)
        basis_layout.addWidget(self.volume_basis_check)
        layout.addWidget(basis_group)
        layout.addWidget(QLabel("Normalization Strategy:"))
        self.norm_strategy_combo = QComboBox()
        self.norm_strategy_combo.addItems(["Standard Z-Score", "Robust Relational"])
        layout.addWidget(self.norm_strategy_combo)
        layout.addWidget(QLabel("Rotation Logic:"))
        self.rotation_logic_combo = QComboBox()
        self.rotation_logic_combo.addItems(["Dynamic", "Freeze & Correct"])
        layout.addWidget(self.rotation_logic_combo)
        self.drift_error_check = QCheckBox("Include Frame Drift Error")
        layout.addWidget(self.drift_error_check)
        return container

    def _open_color_dialog(self, button, is_bg=False):
        color = QColorDialog.getColor()
        if color.isValid():
            text_color = "black" if (color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114) > 186 else "white"
            style = f"background-color: {color.name()}; color: {text_color};"
            button.setStyleSheet(style)
