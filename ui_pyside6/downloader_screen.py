import os
import sys
import threading
from datetime import datetime

import pandas as pd
from PySide6.QtCore import QDate, QObject, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QAbstractItemView,
)

from lib.downloader.download_worker import DownloadWorker
from lib.logger import UILogger


class Communicate(QObject):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    finish_signal = Signal()
    data_loaded_signal = Signal()


class DownloaderScreen(QWidget):
    def __init__(self, session_manager):
        super().__init__()

        self.session_manager = session_manager

        # Replicate Kivy properties
        self.logs = []
        self.is_resume_mode = False
        self.master_df = None
        self.available_symbols = []
        self.selected_symbols = []
        self.selected_count_text = "Selected: 0"

        # Communication signals for worker thread
        self.comm = Communicate()
        self.comm.log_signal.connect(self.add_log_entry)
        self.comm.progress_signal.connect(self.update_progress_bar)
        self.comm.finish_signal.connect(self.on_download_finished)
        self.comm.data_loaded_signal.connect(self.setup_ui_with_data)

        self.init_ui()
        self.connect_signals()

        # Load master data in a separate thread
        self.search_filter.setDisabled(True)
        self.sector_filter.setDisabled(True)
        self.index_filter.setDisabled(True)
        self.add_log_entry("Loading master data...")
        threading.Thread(target=self.load_master_data, daemon=True).start()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Section 1: Symbol Selection ---
        self.symbol_selection_group = QGroupBox("Symbol Selection")
        symbol_layout = QHBoxLayout()
        self.symbol_selection_group.setLayout(symbol_layout)
        main_layout.addWidget(self.symbol_selection_group)

        # Left Pane: Browser
        browser_layout = QVBoxLayout()
        symbol_layout.addLayout(browser_layout)

        browser_label = QLabel("Symbol Browser")
        browser_layout.addWidget(browser_label)

        filter_layout = QHBoxLayout()
        browser_layout.addLayout(filter_layout)

        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Search Symbol")
        filter_layout.addWidget(self.search_filter)

        self.sector_filter = QComboBox()
        self.sector_filter.addItem("All Sectors")
        filter_layout.addWidget(self.sector_filter)

        self.index_filter = QComboBox()
        self.index_filter.addItem("All Indices")
        filter_layout.addWidget(self.index_filter)

        self.available_symbols_list = QListWidget()
        self.available_symbols_list.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        browser_layout.addWidget(self.available_symbols_list)

        selection_buttons_layout = QHBoxLayout()
        browser_layout.addLayout(selection_buttons_layout)

        self.select_all_button = QPushButton("Select All")
        selection_buttons_layout.addWidget(self.select_all_button)

        self.deselect_all_button = QPushButton("Deselect All")
        selection_buttons_layout.addWidget(self.deselect_all_button)

        # Middle Pane: Action Buttons
        action_buttons_layout = QVBoxLayout()
        symbol_layout.addLayout(action_buttons_layout)

        self.add_selected_button = QPushButton(">>")
        action_buttons_layout.addWidget(self.add_selected_button)

        self.remove_selected_button = QPushButton("<<")
        action_buttons_layout.addWidget(self.remove_selected_button)

        # Right Pane: Queue
        queue_layout = QVBoxLayout()
        symbol_layout.addLayout(queue_layout)

        self.selected_count_label = QLabel("Selected: 0")
        queue_layout.addWidget(self.selected_count_label)

        self.selected_symbols_list = QListWidget()
        self.selected_symbols_list.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        queue_layout.addWidget(self.selected_symbols_list)

        # --- Section 2: Time & Interval ---
        time_interval_group = QGroupBox("Time & Interval")
        time_layout = QHBoxLayout()
        time_interval_group.setLayout(time_layout)
        main_layout.addWidget(time_interval_group)

        self.start_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        time_layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        time_layout.addWidget(self.end_date_edit)

        self.interval_combo = QComboBox()
        self.interval_combo.addItems(
            [
                "minute",
                "3minute",
                "5minute",
                "10minute",
                "15minute",
                "30minute",
                "60minute",
                "day",
            ]
        )
        time_layout.addWidget(self.interval_combo)

        # --- Section 3: Storage & Sharding ---
        storage_sharding_group = QGroupBox("Storage & Sharding")
        storage_layout = QHBoxLayout()
        storage_sharding_group.setLayout(storage_layout)
        main_layout.addWidget(storage_sharding_group)

        self.output_dir_edit = QLineEdit()
        self.output_dir_button = QPushButton("...")
        storage_layout.addWidget(self.output_dir_edit)
        storage_layout.addWidget(self.output_dir_button)

        self.save_csv_check = QCheckBox("CSV")
        self.save_csv_check.setChecked(True)
        storage_layout.addWidget(self.save_csv_check)

        self.save_parquet_check = QCheckBox("Parquet")
        storage_layout.addWidget(self.save_parquet_check)

        self.sharding_combo = QComboBox()
        self.sharding_combo.addItems(
            ["None", "By Day", "By Week", "By Month", "By Quarter", "By Year"]
        )
        storage_layout.addWidget(self.sharding_combo)

        # --- Section 4: Execution & Logs ---
        execution_logs_group = QGroupBox("Execution & Logs")
        logs_layout = QVBoxLayout()
        execution_logs_group.setLayout(logs_layout)
        main_layout.addWidget(execution_logs_group)

        self.progress_bar = QProgressBar()
        logs_layout.addWidget(self.progress_bar)

        self.log_view = QListWidget()
        logs_layout.addWidget(self.log_view)

        # --- Bottom controls ---
        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout)

        self.resume_check = QCheckBox("Resume Mode")
        bottom_layout.addWidget(self.resume_check)

        self.manifest_file_edit = QLineEdit()
        self.manifest_file_edit.setPlaceholderText("Select manifest.json")
        self.manifest_file_edit.setEnabled(False)
        bottom_layout.addWidget(self.manifest_file_edit)

        self.manifest_file_button = QPushButton("...")
        self.manifest_file_button.setEnabled(False)
        bottom_layout.addWidget(self.manifest_file_button)

        self.start_button = QPushButton("START DOWNLOAD")
        bottom_layout.addWidget(self.start_button)

    def connect_signals(self):
        # Connect filter signals
        self.search_filter.textChanged.connect(self.filter_symbols)
        self.sector_filter.currentIndexChanged.connect(self.filter_symbols)
        self.index_filter.currentIndexChanged.connect(self.filter_symbols)

        # Connect symbol list signals
        self.available_symbols_list.itemDoubleClicked.connect(
            self.add_single_symbol_to_queue
        )
        self.selected_symbols_list.itemDoubleClicked.connect(
            self.remove_single_symbol_from_queue
        )

        # Connect button signals
        self.select_all_button.clicked.connect(self.select_all)
        self.deselect_all_button.clicked.connect(self.deselect_all)
        self.add_selected_button.clicked.connect(self.add_selected_to_queue)
        self.remove_selected_button.clicked.connect(
            self.remove_selected_from_queue)

        # Connect file dialog signals
        self.output_dir_button.clicked.connect(self.trigger_output_dir_chooser)
        self.manifest_file_button.clicked.connect(
            self.trigger_manifest_file_chooser)

        # Connect resume mode
        self.resume_check.stateChanged.connect(self.toggle_resume_mode)

        # Connect start button
        self.start_button.clicked.connect(self.start_download)

    def add_log_entry(self, message):
        """Adds a message to the log view."""
        self.log_view.addItem(message)
        self.log_view.scrollToBottom()

    def update_progress_bar(self, value):
        """Updates the progress bar value."""
        self.progress_bar.setValue(value)

    def on_download_finished(self):
        """Called when the download worker is finished."""
        self.start_button.setDisabled(False)
        self.add_log_entry("Download finished.")

    def load_master_data(self):
        """Loads the master instrument catalog in a background thread."""
        try:
            # Correctly locate the assets folder relative to the project root
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..")
            )
            master_file_path = os.path.join(
                project_root, "source_data", "master_catalog_enriched.csv"
            )
            self.master_df = pd.read_csv(master_file_path)
            self.comm.data_loaded_signal.emit()
        except Exception as e:
            self.comm.log_signal.emit(f"Error loading master data: {e}")

    def setup_ui_with_data(self):
        """
        Sets up UI elements that depend on the master data being loaded.
        """
        self.search_filter.setDisabled(False)
        self.sector_filter.setDisabled(False)
        self.index_filter.setDisabled(False)

        # Populate sector filter
        unique_sectors = ["All Sectors"] + sorted(
            self.master_df["Industry"].dropna().unique().tolist()
        )
        self.sector_filter.addItems(unique_sectors)

        # Populate index filter
        all_indices = (
            self.master_df["Indices"]
            .dropna()
            .apply(lambda x: [idx.strip() for idx in x.split(",")])
            .explode()
            .unique()
            .tolist()
        )
        unique_indices = ["All Indices"] + sorted(all_indices)
        self.index_filter.addItems(unique_indices)

        # Populate initial available symbols
        self.available_symbols = self.master_df["Symbol"].tolist()
        self.filter_symbols()
        self.add_log_entry("UI elements updated with master data.")

    def filter_symbols(self):
        """Filters the available symbols based on UI controls."""
        if self.master_df is None:
            return

        df = self.master_df.copy()
        search_term = self.search_filter.text().upper()
        sector = self.sector_filter.currentText()
        index = self.index_filter.currentText()

        if search_term:
            df = df[df["Symbol"].str.contains(search_term, na=False)]
        if sector and sector != "All Sectors":
            df = df[df["Industry"] == sector]
        if index and index != "All Indices":
            df = df[df["Indices"].str.contains(index, na=False)]

        self.available_symbols = df["Symbol"].tolist()
        self.available_symbols_list.clear()
        self.available_symbols_list.addItems(self.available_symbols)

    def add_single_symbol_to_queue(self, item):
        """Adds a single symbol to the selection queue."""
        self.add_to_queue([item.text()])

    def remove_single_symbol_from_queue(self, item):
        """Removes a single symbol from the selection queue."""
        self.remove_from_queue([item.text()])

    def select_all(self):
        """Selects all items in the available symbols list."""
        self.available_symbols_list.selectAll()

    def deselect_all(self):
        """Deselects all items in the available symbols list."""
        self.available_symbols_list.clearSelection()

    def add_selected_to_queue(self):
        """Adds selected symbols to the queue."""
        selected_items = self.available_symbols_list.selectedItems()
        symbols_to_add = [item.text() for item in selected_items]
        self.add_to_queue(symbols_to_add)

    def remove_selected_from_queue(self):
        """Removes selected symbols from the queue."""
        selected_items = self.selected_symbols_list.selectedItems()
        symbols_to_remove = [item.text() for item in selected_items]
        self.remove_from_queue(symbols_to_remove)

    def add_to_queue(self, symbols):
        """Adds a list of symbols to the selection queue."""
        for symbol in symbols:
            if symbol not in self.selected_symbols:
                self.selected_symbols.append(symbol)
        self.selected_symbols.sort()
        self.selected_symbols_list.clear()
        self.selected_symbols_list.addItems(self.selected_symbols)
        self.update_selected_count()

    def remove_from_queue(self, symbols):
        """Removes a list of symbols from the selection queue."""
        for symbol in symbols:
            if symbol in self.selected_symbols:
                self.selected_symbols.remove(symbol)
        self.selected_symbols_list.clear()
        self.selected_symbols_list.addItems(self.selected_symbols)
        self.update_selected_count()

    def update_selected_count(self):
        self.selected_count_text = f"Selected: {len(self.selected_symbols)}"
        self.selected_count_label.setText(self.selected_count_text)

    def start_download(self):
        """Validates UI parameters and starts the DownloadWorker thread."""
        params = {}
        try:
            params["resume_mode"] = self.is_resume_mode
            if self.is_resume_mode:
                params["manifest_path"] = self.manifest_file_edit.text()
                if not os.path.exists(params["manifest_path"]):
                    raise ValueError("Manifest file not found.")
            else:
                params["symbols"] = self.selected_symbols[:]
                if not params["symbols"]:
                    raise ValueError("No symbols selected in the queue.")

            params["start_date"] = self.start_date_edit.date().toPython()
            params["end_date"] = self.end_date_edit.date().toPython()
            params["interval"] = self.interval_combo.currentText()

            params["output_dir"] = self.output_dir_edit.text()
            if not os.path.isdir(params["output_dir"]):
                raise ValueError("Output directory is not valid.")

            params["save_csv"] = self.save_csv_check.isChecked()
            params["save_parquet"] = self.save_parquet_check.isChecked()
            params["sharding"] = self.sharding_combo.currentText()

            if not params["save_csv"] and not params["save_parquet"]:
                raise ValueError(
                    "Select at least one save format (CSV or Parquet).")

            self.log_view.clear()
            self.progress_bar.setValue(0)
            self.start_button.setDisabled(True)

            kite = self.session_manager.get_kite()
            if not kite:
                raise ConnectionError(
                    "Kite session not available. Please log in.")

            # Pass the authenticated session to the worker
            worker = DownloadWorker(params, self, kite_session=kite)
            worker.start()

        except Exception as e:
            self.add_log_entry(f"Configuration Error: {e}")
            self.start_button.setDisabled(False)

    def trigger_output_dir_chooser(self):
        """Opens a dialog to select an output directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory")
        if directory:
            self.output_dir_edit.setText(directory)

    def trigger_manifest_file_chooser(self):
        """Opens a dialog to select a manifest file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Manifest File", "", "JSON Files (*.json)"
        )
        if file_path:
            self.manifest_file_edit.setText(file_path)

    def toggle_resume_mode(self, state):
        """Enables or disables resume mode UI elements."""
        self.is_resume_mode = bool(state)
        self.manifest_file_edit.setEnabled(self.is_resume_mode)
        self.manifest_file_button.setEnabled(self.is_resume_mode)
        self.symbol_selection_group.setHidden(self.is_resume_mode)