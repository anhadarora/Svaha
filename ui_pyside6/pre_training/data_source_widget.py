from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QComboBox,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QDateEdit,
    QLabel,
    QAbstractItemView,
    QSizePolicy,
    QStackedWidget,
    QSpinBox,
    QLineEdit,
)
from PySide6.QtCore import Signal, QDate
import json
import os
from datetime import datetime
import pandas as pd

class DataSourceWidget(QWidget):
    data_source_selected = Signal(bool)

    def __init__(self):
        super().__init__()
        self._metadata = []
        self.master_df = None
        self.selected_symbols = []
        
        self.init_ui()
        self.connect_signals()
        self.load_data()
        self._update_ui_state()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Data Source & Timeframe Parameters")
        self.layout.addWidget(group)

        main_form_layout = QVBoxLayout(group)

        # --- 1. Interval Selection ---
        main_form_layout.addWidget(QLabel("Time Interval:"))
        self.time_interval_combo = QComboBox()
        self.time_interval_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_form_layout.addWidget(self.time_interval_combo)

        # --- 2. Instrument Selection ---
        instrument_group = QGroupBox("Instrument Selection")
        instrument_group_layout = QVBoxLayout(instrument_group)
        
        # Filters
        filter_layout = QHBoxLayout()
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Search Symbol...")
        self.sector_filter = QComboBox()
        self.index_filter = QComboBox()
        filter_layout.addWidget(self.search_filter)
        filter_layout.addWidget(self.sector_filter)
        filter_layout.addWidget(self.index_filter)
        instrument_group_layout.addLayout(filter_layout)

        # Selection lists
        instrument_selection_layout = self.create_instrument_selection_ui()
        instrument_group_layout.addWidget(instrument_selection_layout)
        main_form_layout.addWidget(instrument_group)
        
        # --- 3. Date Range Guidance & Master Selection ---
        self.overlapping_dates_label = QLabel("Selected Instruments Overlap: N/A")
        main_form_layout.addWidget(self.overlapping_dates_label)
        
        master_date_group = QGroupBox("Master Data Range")
        master_date_layout = QHBoxLayout(master_date_group)
        master_date_layout.addWidget(QLabel("Use data from:"))
        self.master_start_date = QDateEdit()
        self.master_start_date.setCalendarPopup(True)
        self.master_start_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        master_date_layout.addWidget(self.master_start_date)
        master_date_layout.addWidget(QLabel("to"))
        self.master_end_date = QDateEdit()
        self.master_end_date.setCalendarPopup(True)
        self.master_end_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        master_date_layout.addWidget(self.master_end_date)
        main_form_layout.addWidget(master_date_group)

        # --- 4. Validation Method ---
        validation_group = QGroupBox("Validation Method")
        validation_layout = QVBoxLayout(validation_group)
        self.split_method_combo = QComboBox()
        self.split_method_combo.addItems(["Date Range", "Percentage Split", "Time-Series K-Fold"])
        self.split_method_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        validation_layout.addWidget(self.split_method_combo)
        
        self.split_options_stack = QStackedWidget()
        self.date_range_widget = self.create_date_range_widget()
        self.percent_split_widget = self.create_percent_split_widget()
        self.kfold_widget = self.create_kfold_widget()
        self.split_options_stack.addWidget(self.date_range_widget)
        self.split_options_stack.addWidget(self.percent_split_widget)
        self.split_options_stack.addWidget(self.kfold_widget)
        validation_layout.addWidget(self.split_options_stack)
        main_form_layout.addWidget(validation_group)

    def create_instrument_selection_ui(self):
        # ... (same as before)
        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0,0,0,0)

        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("Available"))
        self.available_instruments_list = QListWidget()
        self.available_instruments_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        available_layout.addWidget(self.available_instruments_list)
        main_layout.addLayout(available_layout)

        buttons_layout = QVBoxLayout()
        self.add_button = QPushButton(">>")
        self.remove_button = QPushButton("<<")
        self.add_all_button = QPushButton("All >>")
        self.remove_all_button = QPushButton("<< All")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.add_all_button)
        buttons_layout.addWidget(self.remove_all_button)
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        selected_layout = QVBoxLayout()
        self.selected_count_label = QLabel("Selected: 0")
        selected_layout.addWidget(self.selected_count_label)
        self.selected_instruments_list = QListWidget()
        self.selected_instruments_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        selected_layout.addWidget(self.selected_instruments_list)
        main_layout.addLayout(selected_layout)
        
        return container

    def create_date_range_widget(self):
        # ... (same as before, but now uses master date range)
        container = QWidget()
        top_level_layout = QVBoxLayout(container)
        top_level_layout.setContentsMargins(0,0,0,0)
        
        date_ranges_layout = QHBoxLayout()

        training_date_layout = QVBoxLayout()
        training_date_layout.addWidget(QLabel("Training Date Range:"))
        training_date_container = QHBoxLayout()
        self.training_start_date = QDateEdit()
        self.training_start_date.setCalendarPopup(True)
        self.training_start_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.training_end_date = QDateEdit()
        self.training_end_date.setCalendarPopup(True)
        self.training_end_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        training_date_container.addWidget(self.training_start_date)
        training_date_container.addWidget(QLabel("to"))
        training_date_container.addWidget(self.training_end_date)
        training_date_layout.addLayout(training_date_container)
        date_ranges_layout.addLayout(training_date_layout)

        validation_date_layout = QVBoxLayout()
        validation_date_layout.addWidget(QLabel("Validation Date Range:"))
        validation_date_container = QHBoxLayout()
        self.validation_start_date = QDateEdit()
        self.validation_start_date.setCalendarPopup(True)
        self.validation_start_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.validation_end_date = QDateEdit()
        self.validation_end_date.setCalendarPopup(True)
        self.validation_end_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        validation_date_container.addWidget(self.validation_start_date)
        validation_date_container.addWidget(QLabel("to"))
        validation_date_container.addWidget(self.validation_end_date)
        validation_date_layout.addLayout(validation_date_container)
        date_ranges_layout.addLayout(validation_date_layout)
        
        top_level_layout.addLayout(date_ranges_layout)
        
        self.date_error_label = QLabel("")
        self.date_error_label.setStyleSheet("color: red")
        top_level_layout.addWidget(self.date_error_label)

        return container

    def create_percent_split_widget(self):
        # ... (same as before)
        container = QWidget()
        layout = QVBoxLayout(container)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Validation Percentage:"))
        self.validation_percent_spinbox = QSpinBox()
        self.validation_percent_spinbox.setRange(1, 99)
        self.validation_percent_spinbox.setValue(20)
        self.validation_percent_spinbox.setSuffix("%")
        self.validation_percent_spinbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.validation_percent_spinbox)
        layout.addLayout(input_layout)

        self.percent_split_label = QLabel("")
        layout.addWidget(self.percent_split_label)
        self._update_percent_label()

        return container

    def create_kfold_widget(self):
        # ... (same as before)
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(QLabel("Number of Folds (K):"))
        self.k_folds_spinbox = QSpinBox()
        self.k_folds_spinbox.setRange(2, 20)
        self.k_folds_spinbox.setValue(5)
        self.k_folds_spinbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.k_folds_spinbox)
        return container

    def connect_signals(self):
        # Instrument selection
        self.add_button.clicked.connect(self.add_selected)
        self.remove_button.clicked.connect(self.remove_selected)
        self.add_all_button.clicked.connect(self.add_all)
        self.remove_all_button.clicked.connect(self.remove_all)
        self.available_instruments_list.itemDoubleClicked.connect(lambda item: self.add_to_queue([item.text()]))
        self.selected_instruments_list.itemDoubleClicked.connect(lambda item: self.remove_from_queue([item.text()]))
        self.selected_instruments_list.model().rowsInserted.connect(self._update_date_guidance)
        self.selected_instruments_list.model().rowsRemoved.connect(self._update_date_guidance)

        # Filters
        self.time_interval_combo.currentIndexChanged.connect(self._filter_available_instruments)
        self.search_filter.textChanged.connect(self._filter_available_instruments)
        self.sector_filter.currentIndexChanged.connect(self._filter_available_instruments)
        self.index_filter.currentIndexChanged.connect(self._filter_available_instruments)

        # Master date range affects validation date pickers
        self.master_start_date.dateChanged.connect(self._update_validation_ranges)
        self.master_end_date.dateChanged.connect(self._update_validation_ranges)

        # Validation
        self.split_method_combo.currentIndexChanged.connect(self.split_options_stack.setCurrentIndex)
        self.validation_percent_spinbox.valueChanged.connect(self._update_percent_label)
        self.training_start_date.dateChanged.connect(self.validate_date_ranges)
        self.training_end_date.dateChanged.connect(self.validate_date_ranges)
        self.validation_start_date.dateChanged.connect(self.validate_date_ranges)
        self.validation_end_date.dateChanged.connect(self.validate_date_ranges)

    def load_data(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        try:
            metadata_path = os.path.join(project_root, "generated_data", "metadata.json")
            with open(metadata_path, "r") as f:
                self._metadata = json.load(f)
            all_intervals = ["All Intervals"] + sorted(list(set(item['interval'] for item in self._metadata)))
            self.time_interval_combo.addItems(all_intervals)
        except Exception as e:
            print(f"Error loading metadata.json: {e}")

        try:
            master_catalog_path = os.path.join(project_root, "source_data", "master_catalog_enriched.csv")
            self.master_df = pd.read_csv(master_catalog_path)
            self._populate_filters()
        except Exception as e:
            print(f"Error loading master_catalog_enriched.csv: {e}")
        
        self._filter_available_instruments()

    def _populate_filters(self):
        if self.master_df is None: return
        unique_sectors = ["All Sectors"] + sorted(self.master_df["Industry"].dropna().unique().tolist())
        self.sector_filter.addItems(unique_sectors)
        
        all_indices = self.master_df["Indices"].dropna().apply(lambda x: [idx.strip() for idx in x.split(',')]).explode().unique().tolist()
        unique_indices = ["All Indices"] + sorted(all_indices)
        self.index_filter.addItems(unique_indices)

    def _filter_available_instruments(self):
        if self.master_df is None or not self._metadata:
            return

        # 1. Filter symbols by selected interval
        selected_interval = self.time_interval_combo.currentText()
        interval_symbols = {item['symbol'] for item in self._metadata if selected_interval == "All Intervals" or item['interval'] == selected_interval}

        # 2. Filter by sector, index, and search term using master_df
        df = self.master_df.copy()
        search_term = self.search_filter.text().upper()
        sector = self.sector_filter.currentText()
        index = self.index_filter.currentText()

        if search_term:
            df = df[df["Symbol"].str.contains(search_term, na=False)]
        if sector != "All Sectors":
            df = df[df["Industry"] == sector]
        if index != "All Indices":
            df = df[df["Indices"].str.contains(index, na=False)]
        
        catalog_symbols = set(df["Symbol"].tolist())

        # 3. Find intersection and update list
        final_symbols = sorted(list(interval_symbols.intersection(catalog_symbols)))
        
        self.available_instruments_list.clear()
        self.available_instruments_list.addItems([s for s in final_symbols if s not in self.selected_symbols])

    def _update_date_guidance(self):
        if not self.selected_symbols:
            self.overlapping_dates_label.setText("Selected Instruments Overlap: N/A")
            self._update_ui_state()
            return

        max_start, min_end = self.get_date_intersection()
        
        if max_start and min_end and max_start <= min_end:
            self.overlapping_dates_label.setText(f"Selected Instruments Overlap: {max_start.isoformat()} to {min_end.isoformat()}")
            q_max_start = QDate(max_start.year, max_start.month, max_start.day)
            q_min_end = QDate(min_end.year, min_end.month, min_end.day)
            
            self.master_start_date.setMinimumDate(q_max_start)
            self.master_start_date.setMaximumDate(q_min_end)
            self.master_start_date.setDate(q_max_start)
            
            self.master_end_date.setMinimumDate(q_max_start)
            self.master_end_date.setMaximumDate(q_min_end)
            self.master_end_date.setDate(q_min_end)
        else:
            self.overlapping_dates_label.setText("Selected Instruments Have No Overlapping Dates")

        self._update_ui_state()
        self._update_validation_ranges()

    def _update_validation_ranges(self):
        # Validation ranges are now based on the master range
        start_date = self.master_start_date.date()
        end_date = self.master_end_date.date()
        
        for date_edit in [self.training_start_date, self.training_end_date, self.validation_start_date, self.validation_end_date]:
            date_edit.setMinimumDate(start_date)
            date_edit.setMaximumDate(end_date)
        
        self.training_start_date.setDate(start_date)
        self.training_end_date.setDate(end_date)
        self.validation_start_date.setDate(start_date)
        self.validation_end_date.setDate(end_date)
        self.validate_date_ranges()

    def _update_ui_state(self):
        has_selection = bool(self.selected_symbols)
        self.master_start_date.setEnabled(has_selection)
        self.master_end_date.setEnabled(has_selection)
        self.split_method_combo.setEnabled(has_selection)
        self.split_options_stack.setEnabled(has_selection)
        self.data_source_selected.emit(has_selection)

    def get_date_intersection(self):
        # ... (same as before)
        if not self.selected_symbols: return None, None
        max_start, min_end, date_format = None, None, "%Y-%m-%d"
        selected_interval = self.time_interval_combo.currentText()

        for symbol in self.selected_symbols:
            for item in self._metadata:
                if item['symbol'] == symbol and (selected_interval == "All Intervals" or item['interval'] == selected_interval):
                    start_date = datetime.strptime(item['start_date'], date_format).date()
                    end_date = datetime.strptime(item['end_date'], date_format).date()
                    if max_start is None or start_date > max_start: max_start = start_date
                    if min_end is None or end_date < min_end: min_end = end_date
        return max_start, min_end

    def add_selected(self):
        symbols = [item.text() for item in self.available_instruments_list.selectedItems()]
        self.add_to_queue(symbols)

    def remove_selected(self):
        symbols = [item.text() for item in self.selected_instruments_list.selectedItems()]
        self.remove_from_queue(symbols)

    def add_all(self):
        all_symbols = [self.available_instruments_list.item(i).text() for i in range(self.available_instruments_list.count())]
        self.add_to_queue(all_symbols)

    def remove_all(self):
        self.selected_symbols.clear()
        self.refresh_lists()

    def add_to_queue(self, symbols):
        for symbol in symbols:
            if symbol not in self.selected_symbols:
                self.selected_symbols.append(symbol)
        self.refresh_lists()

    def remove_from_queue(self, symbols):
        for symbol in symbols:
            if symbol in self.selected_symbols:
                self.selected_symbols.remove(symbol)
        self.refresh_lists()

    def refresh_lists(self):
        self.selected_symbols.sort()
        self.selected_instruments_list.clear()
        self.selected_instruments_list.addItems(self.selected_symbols)
        self.selected_count_label.setText(f"Selected: {len(self.selected_symbols)}")
        self._filter_available_instruments()
        self._update_date_guidance()

    def _update_percent_label(self):
        # ... (same as before)
        valid_pct = self.validation_percent_spinbox.value()
        train_pct = 100 - valid_pct
        self.percent_split_label.setText(f"Train: {train_pct}%, Validate: {valid_pct}%")

    def validate_date_ranges(self):
        # ... (same as before)
        if self.training_end_date.date() >= self.validation_start_date.date():
            self.date_error_label.setText("Error: Training range must end before validation range begins.")
        else:
            self.date_error_label.setText("")
