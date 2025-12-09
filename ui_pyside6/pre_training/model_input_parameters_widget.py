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
    QGridLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class ModelInputParametersWidget(QWidget):
    configuration_changed = Signal()
    resolution_changed = Signal(str)
    window_size_changed = Signal(int)

    def __init__(self):
        super().__init__()
        # --- Color State ---
        self.up_color = QColor("#26a69a")
        self.down_color = QColor("#ef5350")
        self.bg_color = QColor("#2d2d2d")
        self.line_color = QColor("#f0f0f0")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        # --- Main Group ---
        group = QGroupBox("Model Input Parameters")
        self.layout.addWidget(group)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # --- Data Processing Group ---
        processing_group = QGroupBox("Data Processing")
        layout.addWidget(processing_group)
        processing_layout = QGridLayout(processing_group)
        
        self.resampling_factor_spinbox = self._create_spinbox(1, 1000, 1)
        self._add_grid_row(processing_layout, 0, "Resampling Factor:", self.resampling_factor_spinbox, "e.g., set to 60 to construct 1-hour candles from 1-minute source data.")
        
        self.input_window_size_n_spinbox = self._create_spinbox(1, 15, 5)
        self._add_grid_row(processing_layout, 1, "Input Window Size (N):", self.input_window_size_n_spinbox, "Number of candles in a single training sample.")

        self.prediction_horizon_k_spinbox = self._create_spinbox(1, 100, 1)
        self._add_grid_row(processing_layout, 2, "Prediction Horizon (k):", self.prediction_horizon_k_spinbox, "How many steps into the future the label represents.")

        # --- Chart & Tensor Group ---
        chart_group = QGroupBox("Chart & Tensor Settings")
        layout.addWidget(chart_group)
        chart_layout = QGridLayout(chart_group)

        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Candlestick", "Heikin-Ashi", "Line", "OHLC Bar", 
            "Hollow Candlestick", "Renko", "Point & Figure", "Dynamic 2D Plane"
        ])
        self._add_grid_row(chart_layout, 0, "Chart Type:", self.chart_type_combo)

        self.channel_depth_combo = QComboBox()
        self.channel_depth_combo.addItems(["Grayscale (1ch)", "RGB (3ch)", "RGB + Delta"])
        self._add_grid_row(chart_layout, 1, "Tensor Channel Depth:", self.channel_depth_combo)

        # --- Conditional Settings Stack ---
        self.settings_stack = QStackedWidget()
        layout.addWidget(self.settings_stack)

        self.style_settings_widget = self._create_style_settings_widget()
        self.settings_stack.addWidget(self.style_settings_widget)

        self.dynamic_plane_widget = self._create_dynamic_plane_widget()
        self.settings_stack.addWidget(self.dynamic_plane_widget)

        layout.addStretch()

    def _add_grid_row(self, layout, row, label_text, widget, tooltip=None, column=0):
        label = QLabel(label_text)
        label.setBuddy(widget)
        if tooltip:
            widget.setToolTip(tooltip)
        layout.addWidget(label, row, column)
        layout.addWidget(widget, row, column + 1)

    def _create_spinbox(self, min_val, max_val, default_val):
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default_val)
        return spinbox

    def connect_signals(self):
        self.resampling_factor_spinbox.valueChanged.connect(self.configuration_changed)
        self.input_window_size_n_spinbox.valueChanged.connect(self.configuration_changed)
        self.input_window_size_n_spinbox.valueChanged.connect(self.window_size_changed)
        self.prediction_horizon_k_spinbox.valueChanged.connect(self.configuration_changed)
        self.chart_type_combo.currentTextChanged.connect(self.configuration_changed)
        self.channel_depth_combo.currentIndexChanged.connect(self.configuration_changed)
        
        self.target_height_spinbox.valueChanged.connect(self.configuration_changed)
        self.target_width_spinbox.valueChanged.connect(self.configuration_changed)
        self.target_height_spinbox.valueChanged.connect(self._emit_resolution)
        self.target_width_spinbox.valueChanged.connect(self._emit_resolution)

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
                "up_color": self.up_color.name(),
                "down_color": self.down_color.name(),
                "bg_color": self.bg_color.name(),
                "line_color": self.line_color.name(),
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

    def _emit_resolution(self):
        res_text = f"{self.target_height_spinbox.value()} x {self.target_width_spinbox.value()}"
        self.resolution_changed.emit(res_text)

    def _on_chart_type_changed(self, chart_type):
        if chart_type == "Dynamic 2D Plane":
            self.settings_stack.setCurrentWidget(self.dynamic_plane_widget)
        else:
            self.settings_stack.setCurrentWidget(self.style_settings_widget)

    def _create_style_settings_widget(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        # --- Resolution & Sizing ---
        res_group = QGroupBox("Resolution & Sizing")
        layout.addWidget(res_group)
        res_layout = QGridLayout(res_group)
        
        self.target_height_spinbox = self._create_spinbox(32, 1024, 64)
        self._add_grid_row(res_layout, 0, "Target Height (px):", self.target_height_spinbox)
        
        self.target_width_spinbox = self._create_spinbox(32, 1024, 128)
        self._add_grid_row(res_layout, 1, "Target Width (px):", self.target_width_spinbox)

        self.bar_width_px_spinbox = self._create_spinbox(1, 20, 5)
        self._add_grid_row(res_layout, 0, "Bar Width (px):", self.bar_width_px_spinbox, column=2)

        self.border_thickness_px_spinbox = self._create_spinbox(0, 5, 1)
        self._add_grid_row(res_layout, 1, "Border Thickness (px):", self.border_thickness_px_spinbox, column=2)

        self.line_width_px_spinbox = self._create_spinbox(1, 10, 2)
        self._add_grid_row(res_layout, 2, "Line Width (px):", self.line_width_px_spinbox, column=2)

        # --- Color & Display ---
        display_group = QGroupBox("Color & Display")
        layout.addWidget(display_group)
        display_layout = QGridLayout(display_group)

        self.up_color_button = QPushButton("Up Color")
        self.down_color_button = QPushButton("Down Color")
        self.bg_color_button = QPushButton("Background Color")
        self.line_color_button = QPushButton("Line Color")
        
        self._update_button_style(self.up_color_button, self.up_color)
        self._update_button_style(self.down_color_button, self.down_color)
        self._update_button_style(self.bg_color_button, self.bg_color, is_bg=True)
        self._update_button_style(self.line_color_button, self.line_color)

        display_layout.addWidget(self.up_color_button, 0, 0)
        display_layout.addWidget(self.down_color_button, 0, 1)
        display_layout.addWidget(self.bg_color_button, 0, 2)
        display_layout.addWidget(self.line_color_button, 0, 3)

        self.up_color_button.clicked.connect(lambda: self._pick_color(self.up_color_button, 'up_color'))
        self.down_color_button.clicked.connect(lambda: self._pick_color(self.down_color_button, 'down_color'))
        self.bg_color_button.clicked.connect(lambda: self._pick_color(self.bg_color_button, 'bg_color', is_bg=True))
        self.line_color_button.clicked.connect(lambda: self._pick_color(self.line_color_button, 'line_color'))

        self.scaling_mode_combo = QComboBox()
        self.scaling_mode_combo.addItems(["Local Min-Max", "Global Min-Max", "Logarithmic"])
        self._add_grid_row(display_layout, 1, "Scaling Mode:", self.scaling_mode_combo)

        self.volume_display_combo = QComboBox()
        self.volume_display_combo.addItems(["None", "Overlay", "Bottom Subplot", "Color-Coded"])
        self._add_grid_row(display_layout, 2, "Volume Display:", self.volume_display_combo)

        # --- Overlays ---
        overlays_group = QGroupBox("Technical Overlays")
        layout.addWidget(overlays_group)
        overlays_layout = QGridLayout(overlays_group)
        self.ma_checkbox = QCheckBox("Moving Average")
        self.ma_period_spinbox = self._create_spinbox(2, 200, 20)
        self.ma_period_spinbox.setEnabled(False)
        self.ma_checkbox.toggled.connect(self.ma_period_spinbox.setEnabled)
        overlays_layout.addWidget(self.ma_checkbox, 0, 0)
        overlays_layout.addWidget(QLabel("Period:"), 0, 1)
        overlays_layout.addWidget(self.ma_period_spinbox, 0, 2)
        
        return container

    def _create_dynamic_plane_widget(self):
        container = QGroupBox("Dynamic Plane Configuration")
        layout = QGridLayout(container)
        
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
        layout.addWidget(basis_group, 0, 0, 1, 2)

        self.norm_strategy_combo = QComboBox()
        self.norm_strategy_combo.addItems(["Standard Z-Score", "Robust Relational"])
        self._add_grid_row(layout, 1, "Normalization Strategy:", self.norm_strategy_combo)

        self.rotation_logic_combo = QComboBox()
        self.rotation_logic_combo.addItems(["Dynamic", "Freeze & Correct"])
        self._add_grid_row(layout, 2, "Rotation Logic:", self.rotation_logic_combo)
        
        self.drift_error_check = QCheckBox("Include Frame Drift Error")
        layout.addWidget(self.drift_error_check, 3, 0, 1, 2)

        return container

    def _pick_color(self, button, color_attr, is_bg=False):
        initial_color = getattr(self, color_attr)
        color = QColorDialog.getColor(initial_color, self, "Select Color")
        if color.isValid():
            setattr(self, color_attr, color)
            self._update_button_style(button, color, is_bg)
            self.configuration_changed.emit()

    def _update_button_style(self, button, color, is_bg=False):
        text_color = "black" if (color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114) > 186 else "white"
        if is_bg:
            text_color = "white" # Keep text white for background color button
        style = f"background-color: {color.name()}; color: {text_color};"
        button.setStyleSheet(style)
    
    def _add_grid_row(self, layout, row, label_text, widget, tooltip=None, column=0):
        label = QLabel(label_text)
        label.setBuddy(widget)
        if tooltip:
            widget.setToolTip(tooltip)
        layout.addWidget(label, row, column)
        layout.addWidget(widget, row, column + 1)