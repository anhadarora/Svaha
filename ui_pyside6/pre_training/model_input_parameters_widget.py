from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QComboBox,
    QLabel,
    QSizePolicy,
    QSpinBox,
    QDoubleSpinBox,
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
    calculate_total_size_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("input_params")
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
        processing_group.setObjectName("input_params.data_processing")
        layout.addWidget(processing_group)
        processing_layout = QGridLayout(processing_group)
        
        self.resampling_factor_spinbox = self._create_spinbox(1, 1000, 1)
        self.resampling_factor_spinbox.setObjectName("input_params.data_processing.resampling_factor")
        self._add_grid_row(processing_layout, 0, "Resampling Factor:", self.resampling_factor_spinbox, "e.g., set to 60 to construct 1-hour candles from 1-minute source data.")
        
        self.input_window_size_n_spinbox = self._create_spinbox(1, 15, 5)
        self.input_window_size_n_spinbox.setObjectName("input_params.data_processing.input_window_size")
        self._add_grid_row(processing_layout, 1, "Input Window Size (N):", self.input_window_size_n_spinbox, "Number of candles in a single training sample.")

        self.prediction_horizon_k_spinbox = self._create_spinbox(1, 100, 1)
        self.prediction_horizon_k_spinbox.setObjectName("input_params.data_processing.prediction_horizon")
        self._add_grid_row(processing_layout, 2, "Prediction Horizon (k):", self.prediction_horizon_k_spinbox, "How many steps into the future the label represents.")

        # --- Chart & Tensor Group ---
        chart_group = QGroupBox("Chart & Tensor Settings")
        chart_group.setObjectName("input_params.chart_tensor")
        layout.addWidget(chart_group)
        chart_layout = QGridLayout(chart_group)

        self.chart_type_combo = QComboBox()
        self.chart_type_combo.setObjectName("input_params.chart_tensor.chart_type")
        self.chart_type_combo.addItems([
            "Candlestick", "Heikin-Ashi", "Line", "OHLC Bar", 
            "Hollow Candlestick", "Renko", "Point & Figure", "Dynamic 2D Plane"
        ])
        self._add_grid_row(chart_layout, 0, "Chart Type:", self.chart_type_combo)

        self.channel_depth_combo = QComboBox()
        self.channel_depth_combo.setObjectName("input_params.chart_tensor.channel_depth")
        self.channel_depth_combo.addItems(["Grayscale (1ch)", "RGB (3ch)", "RGB + Delta"])
        self._add_grid_row(chart_layout, 1, "Tensor Channel Depth:", self.channel_depth_combo)

        # --- Conditional Settings Stack ---
        self.settings_stack = QStackedWidget()
        layout.addWidget(self.settings_stack)

        self.style_settings_widget = self._create_style_settings_widget()
        self.settings_stack.addWidget(self.style_settings_widget)

        self.dynamic_plane_widget = self._create_dynamic_plane_widget()
        self.settings_stack.addWidget(self.dynamic_plane_widget)

        # --- Disk Space Estimation ---
        estimation_group = QGroupBox("Disk Space Estimation")
        estimation_group.setObjectName("input_params.disk_space")
        layout.addWidget(estimation_group)
        estimation_layout = QGridLayout(estimation_group)

        self.per_sample_size_label = QLabel("Calculating...")
        self._add_grid_row(estimation_layout, 0, "Approx. Size per Sample:", self.per_sample_size_label)

        self.total_size_label = QLabel("N/A")
        self.total_files_label = QLabel("N/A")
        self.calculate_total_size_button = QPushButton("Calculate Total")
        self.calculate_total_size_button.setObjectName("input_params.disk_space.calculate_button")
        estimation_layout.addWidget(QLabel("Estimated Total:"), 1, 0)
        estimation_layout.addWidget(self.total_size_label, 1, 1)
        estimation_layout.addWidget(self.total_files_label, 1, 2)
        estimation_layout.addWidget(self.calculate_total_size_button, 1, 3)


        self.estimate_expired_label = QLabel("(Estimate outdated, please recalculate)")
        self.estimate_expired_label.setStyleSheet("color: #ffc107;") # Amber color
        self.estimate_expired_label.setVisible(False)
        estimation_layout.addWidget(self.estimate_expired_label, 2, 1, 1, 3)

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
        # Config changes
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
        self.reference_point_strategy.currentIndexChanged.connect(self.configuration_changed)
        self.outlier_clip_percentile.valueChanged.connect(self.configuration_changed)

        # Inter-widget communication
        self.input_window_size_n_spinbox.valueChanged.connect(self.window_size_changed)
        self.target_height_spinbox.valueChanged.connect(self._emit_resolution)
        self.target_width_spinbox.valueChanged.connect(self._emit_resolution)
        self.chart_type_combo.currentTextChanged.connect(self._on_chart_type_changed)

        # Disk space estimation
        self.target_height_spinbox.valueChanged.connect(self._update_per_sample_estimate)
        self.target_width_spinbox.valueChanged.connect(self._update_per_sample_estimate)
        self.channel_depth_combo.currentIndexChanged.connect(self._update_per_sample_estimate)
        self.calculate_total_size_button.clicked.connect(self.calculate_total_size_requested)

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
                "reference_point_strategy": self.reference_point_strategy.currentText(),
                "outlier_clip_percentile": self.outlier_clip_percentile.value(),
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
        self._update_per_sample_estimate()

    def _create_style_settings_widget(self):
        container = QWidget()
        container.setObjectName("input_params.style_settings")
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        res_group = QGroupBox("Resolution & Sizing")
        layout.addWidget(res_group)
        res_layout = QGridLayout(res_group)
        
        self.target_height_spinbox = self._create_spinbox(32, 1024, 64)
        self.target_height_spinbox.setObjectName("input_params.style_settings.target_height")
        self._add_grid_row(res_layout, 0, "Target Height (px):", self.target_height_spinbox)
        
        self.target_width_spinbox = self._create_spinbox(32, 1024, 128)
        self.target_width_spinbox.setObjectName("input_params.style_settings.target_width")
        self._add_grid_row(res_layout, 1, "Target Width (px):", self.target_width_spinbox)

        self.bar_width_px_spinbox = self._create_spinbox(1, 20, 5)
        self.bar_width_px_spinbox.setObjectName("input_params.style_settings.bar_width")
        self._add_grid_row(res_layout, 0, "Bar Width (px):", self.bar_width_px_spinbox, column=2)

        self.border_thickness_px_spinbox = self._create_spinbox(0, 5, 1)
        self.border_thickness_px_spinbox.setObjectName("input_params.style_settings.border_thickness")
        self._add_grid_row(res_layout, 1, "Border Thickness (px):", self.border_thickness_px_spinbox, column=2)

        self.line_width_px_spinbox = self._create_spinbox(1, 10, 2)
        self.line_width_px_spinbox.setObjectName("input_params.style_settings.line_width")
        self._add_grid_row(res_layout, 2, "Line Width (px):", self.line_width_px_spinbox, column=2)

        display_group = QGroupBox("Color & Display")
        layout.addWidget(display_group)
        display_layout = QGridLayout(display_group)

        self.up_color_button = QPushButton("Up Color")
        self.up_color_button.setObjectName("input_params.style_settings.up_color_button")
        self.down_color_button = QPushButton("Down Color")
        self.down_color_button.setObjectName("input_params.style_settings.down_color_button")
        self.bg_color_button = QPushButton("Background Color")
        self.bg_color_button.setObjectName("input_params.style_settings.bg_color_button")
        self.line_color_button = QPushButton("Line Color")
        self.line_color_button.setObjectName("input_params.style_settings.line_color_button")
        
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
        self.scaling_mode_combo.setObjectName("input_params.style_settings.scaling_mode")
        self.scaling_mode_combo.addItems(["Local Min-Max", "Global Min-Max", "Logarithmic"])
        self._add_grid_row(display_layout, 1, "Scaling Mode:", self.scaling_mode_combo)

        self.volume_display_combo = QComboBox()
        self.volume_display_combo.setObjectName("input_params.style_settings.volume_display")
        self.volume_display_combo.addItems(["None", "Overlay", "Bottom Subplot", "Color-Coded"])
        self._add_grid_row(display_layout, 2, "Volume Display:", self.volume_display_combo)

        overlays_group = QGroupBox("Technical Overlays")
        layout.addWidget(overlays_group)
        overlays_layout = QGridLayout(overlays_group)
        self.ma_checkbox = QCheckBox("Moving Average")
        self.ma_checkbox.setObjectName("input_params.style_settings.moving_average_enabled")
        self.ma_period_spinbox = self._create_spinbox(2, 200, 20)
        self.ma_period_spinbox.setObjectName("input_params.style_settings.moving_average_period")
        self.ma_period_spinbox.setEnabled(False)
        self.ma_checkbox.toggled.connect(self.ma_period_spinbox.setEnabled)
        overlays_layout.addWidget(self.ma_checkbox, 0, 0)
        overlays_layout.addWidget(QLabel("Period:"), 0, 1)
        overlays_layout.addWidget(self.ma_period_spinbox, 0, 2)
        
        return container

    def _create_dynamic_plane_widget(self):
        container = QGroupBox("Dynamic Plane Configuration")
        container.setObjectName("input_params.dynamic_plane")
        layout = QGridLayout(container)
        layout.setSpacing(15)
        
        basis_group = QGroupBox("Basis Vectors")
        basis_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        basis_layout = QHBoxLayout(basis_group)
        self.time_basis_check = QCheckBox("Time")
        self.time_basis_check.setObjectName("input_params.dynamic_plane.basis_vector_time")
        self.price_basis_check = QCheckBox("Price")
        self.price_basis_check.setObjectName("input_params.dynamic_plane.basis_vector_price")
        self.volume_basis_check = QCheckBox("Volume")
        self.volume_basis_check.setObjectName("input_params.dynamic_plane.basis_vector_volume")
        self.time_basis_check.setChecked(True)
        self.price_basis_check.setChecked(True)
        basis_layout.addWidget(self.time_basis_check)
        basis_layout.addWidget(self.price_basis_check)
        basis_layout.addWidget(self.volume_basis_check)
        layout.addWidget(basis_group, 0, 0, 1, 2)

        self.norm_strategy_combo = QComboBox()
        self.norm_strategy_combo.setObjectName("input_params.dynamic_plane.normalization_strategy")
        self.norm_strategy_combo.addItems(["Standard Z-Score", "Robust Relational"])
        self._add_grid_row(layout, 1, "Normalization Strategy:", self.norm_strategy_combo)

        self.rotation_logic_combo = QComboBox()
        self.rotation_logic_combo.setObjectName("input_params.dynamic_plane.rotation_logic")
        self.rotation_logic_combo.addItems(["Dynamic", "Freeze & Correct"])
        self._add_grid_row(layout, 2, "Rotation Logic:", self.rotation_logic_combo)
        
        self.reference_point_strategy = QComboBox()
        self.reference_point_strategy.setObjectName("input_params.dynamic_plane.reference_point_strategy")
        self.reference_point_strategy.addItems(['Previous Close', 'Window Mean', 'EMA Trend'])
        self._add_grid_row(layout, 3, "Reference Point Strategy:", self.reference_point_strategy)

        self.outlier_clip_percentile = QDoubleSpinBox()
        self.outlier_clip_percentile.setObjectName("input_params.dynamic_plane.outlier_clip_percentile")
        self.outlier_clip_percentile.setRange(90.0, 100.0)
        self.outlier_clip_percentile.setValue(99.0)
        self.outlier_clip_percentile.setSingleStep(0.1)
        self._add_grid_row(layout, 4, "Outlier Clip Percentile:", self.outlier_clip_percentile)

        self.drift_error_check = QCheckBox("Include Frame Drift Error")
        self.drift_error_check.setObjectName("input_params.dynamic_plane.include_drift_error")
        layout.addWidget(self.drift_error_check, 5, 0, 1, 2)

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
            text_color = "white"
        style = f"background-color: {color.name()}; color: {text_color};"
        button.setStyleSheet(style)

    def _update_per_sample_estimate(self):
        """Calculates and displays the uncompressed size of a single sample."""
        h = self.target_height_spinbox.value()
        w = self.target_width_spinbox.value()
        
        channels_text = self.channel_depth_combo.currentText()
        if "Grayscale" in channels_text:
            c = 1
        elif "RGB + Delta" in channels_text:
            c = 4 # Assuming RGB + 1 delta channel
        else: # RGB
            c = 3
            
        total_bytes = h * w * c
        
        if total_bytes < 1024:
            size_str = f"{total_bytes} B"
        elif total_bytes < 1024**2:
            size_str = f"{total_bytes/1024:.1f} KB"
        else:
            size_str = f"{total_bytes/(1024**2):.1f} MB"
            
        self.per_sample_size_label.setText(f"{size_str} (uncompressed)")
        self.invalidate_total_estimate()

    def invalidate_total_estimate(self):
        """Resets the total size estimate, indicating it's outdated."""
        self.total_size_label.setText("N/A")
        self.total_files_label.setText("N/A")
        self.estimate_expired_label.setVisible(True)
        self.calculate_total_size_button.setEnabled(True)
        self.total_size_label.setStyleSheet("color: #999;")
        self.total_files_label.setStyleSheet("color: #999;")

    def set_total_size_estimate(self, size_str: str, file_count_str: str, status: str):
        """Public slot to update the total size estimate from the parent."""
        if status == "calculating":
            self.total_size_label.setText("Calculating...")
            self.total_files_label.setText("...")
            self.total_size_label.setStyleSheet("")
            self.total_files_label.setStyleSheet("")
            self.estimate_expired_label.setVisible(False)
            self.calculate_total_size_button.setEnabled(False)
        elif status == "done":
            self.total_size_label.setText(size_str)
            self.total_files_label.setText(file_count_str)
            self.total_size_label.setStyleSheet("color: #f0f0f0; font-weight: bold;")
            self.total_files_label.setStyleSheet("color: #f0f0f0; font-weight: bold;")
            self.estimate_expired_label.setVisible(False)
            self.calculate_total_size_button.setEnabled(True)
        else: # Error or invalid
            self.total_size_label.setText("Error")
            self.total_files_label.setText("Error")
            self.total_size_label.setStyleSheet("color: #ef5350;")
            self.total_files_label.setStyleSheet("color: #ef5350;")
            self.estimate_expired_label.setVisible(False)
            self.calculate_total_size_button.setEnabled(True)
