from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QDateEdit,
    QFileDialog,
    QLabel,
)
import json
import os


class DataSourceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Data Source & Timeframe Parameters")
        self.layout.addWidget(group)

        form_layout = QFormLayout(group)

        self.market_segment = QComboBox()
        form_layout.addRow("Market Segment:", self.market_segment)

        instrument_layout = QHBoxLayout()
        self.instrument_list = QListWidget()
        self.instrument_list.setSelectionMode(QListWidget.MultiSelection)
        instrument_layout.addWidget(self.instrument_list)
        self.load_instruments_button = QPushButton("Load from File")
        instrument_layout.addWidget(self.load_instruments_button)
        form_layout.addRow("Instrument List:", instrument_layout)

        self.time_interval = QComboBox()
        form_layout.addRow("Time Interval:", self.time_interval)

        self.chart_type = QComboBox()
        self.chart_type.addItems(["Candlestick", "Heiken-Ashi"])
        form_layout.addRow("Chart Type:", self.chart_type)

        training_date_layout = QHBoxLayout()
        self.training_start_date = QDateEdit()
        self.training_end_date = QDateEdit()
        training_date_layout.addWidget(self.training_start_date)
        training_date_layout.addWidget(QLabel("to"))
        training_date_layout.addWidget(self.training_end_date)
        form_layout.addRow("Training Date Range:", training_date_layout)

        validation_date_layout = QHBoxLayout()
        self.validation_start_date = QDateEdit()
        self.validation_end_date = QDateEdit()
        validation_date_layout.addWidget(self.validation_start_date)
        validation_date_layout.addWidget(QLabel("to"))
        validation_date_layout.addWidget(self.validation_end_date)
        form_layout.addRow("Validation Date Range:", validation_date_layout)

        self.load_instruments_button.clicked.connect(self.load_instruments)
        self.populate_dropdowns()

    def populate_dropdowns(self):
        # For now, we'll use dummy data.
        # This will be replaced with data from metadata.json.
        self.market_segment.addItems(["NSE Equities", "NFO", "MCX"])
        self.time_interval.addItems(["10-minute", "5-minute", "1-minute", "1-hour"])

    def load_instruments(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Instrument List", "", "CSV Files (*.csv)"
        )
        if file_path:
            with open(file_path, "r") as f:
                instruments = [line.strip() for line in f.readlines()]
                self.instrument_list.addItems(instruments)