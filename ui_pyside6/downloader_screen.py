import os
import sys
import threading
from datetime import datetime, timedelta

import pandas as pd
from PySide6.QtCore import QDate, QObject, Signal, Qt
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
    QTabWidget,
    QTextEdit,
)

from lib.downloader.download_worker import DownloadWorker


class Communicate(QObject):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    finish_signal = Signal()
    data_loaded_signal = Signal()


class DownloaderScreen(QWidget):
    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.master_df = None

        self.comm = Communicate()
        self.comm.log_signal.connect(self.add_log_entry)
        self.comm.progress_signal.connect(self.update_progress_bar)
        self.comm.finish_signal.connect(self.on_download_finished)
        self.comm.data_loaded_signal.connect(self.on_data_loaded)

        self.init_ui()
        self.connect_signals()

        self.add_log_entry("Loading master data...")
        threading.Thread(target=self.load_master_data, daemon=True).start()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # --- Tab 1: New Job ---
        new_job_widget = QWidget()
        new_job_layout = QVBoxLayout(new_job_widget)
        new_job_layout.setContentsMargins(0, 0, 0, 0)
        new_job_layout.setSpacing(15)
        self.tab_widget.addTab(new_job_widget, "New Download Job")

        # Tickers
        tickers_group = QGroupBox("1. Select Tickers")
        new_job_layout.addWidget(tickers_group)
        tickers_layout = QHBoxLayout(tickers_group)
        
        self.available_symbols_list = QListWidget()
        self.selected_symbols_list = QListWidget()
        
        tickers_layout.addWidget(self.create_symbol_browser())
        tickers_layout.addWidget(self.selected_symbols_list)

        # Date Range
        date_group = QGroupBox("2. Select Date Range")
        new_job_layout.addWidget(date_group)
        date_layout = QHBoxLayout(date_group)
        self.start_date_edit = QDateEdit(QDate.currentDate().addYears(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        date_layout.addWidget(QLabel("Start Date:"))
        date_layout.addWidget(self.start_date_edit)
        date_layout.addStretch()
        date_layout.addWidget(QLabel("End Date:"))
        date_layout.addWidget(self.end_date_edit)

        # Intervals & Storage
        interval_group = QGroupBox("3. Select Intervals & Storage")
        new_job_layout.addWidget(interval_group)
        interval_layout = QVBoxLayout(interval_group)
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["minute", "3minute", "5minute", "10minute", "15minute", "30minute", "60minute", "day"])
        interval_layout.addWidget(self.interval_combo)
        
        storage_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit("./generated_data")
        self.output_dir_button = QPushButton("...")
        storage_layout.addWidget(QLabel("Output Directory:"))
        storage_layout.addWidget(self.output_dir_edit)
        storage_layout.addWidget(self.output_dir_button)
        interval_layout.addLayout(storage_layout)

        # --- Tab 2: Resume Job ---
        resume_job_widget = QWidget()
        resume_job_layout = QVBoxLayout(resume_job_widget)
        self.tab_widget.addTab(resume_job_widget, "Resume Download Job")
        
        manifest_group = QGroupBox("Select Manifest File")
        resume_job_layout.addWidget(manifest_group)
        manifest_layout = QHBoxLayout(manifest_group)
        self.manifest_file_edit = QLineEdit()
        self.manifest_file_edit.setPlaceholderText("Select a manifest.json file to resume a download")
        self.manifest_file_button = QPushButton("...")
        manifest_layout.addWidget(self.manifest_file_edit)
        manifest_layout.addWidget(self.manifest_file_button)
        resume_job_layout.addStretch()

        # --- Shared Section: Execution & Logs ---
        execution_group = QGroupBox("Execution & Logs")
        main_layout.addWidget(execution_group)
        execution_layout = QVBoxLayout(execution_group)
        self.progress_bar = QProgressBar()
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        execution_layout.addWidget(self.progress_bar)
        execution_layout.addWidget(self.log_view)

        # --- Shared Action Button ---
        self.start_button = QPushButton("START DOWNLOAD")
        self.start_button.setObjectName("primary_button") # For styling
        self.start_button.setMinimumHeight(40)
        main_layout.addWidget(self.start_button, 0, Qt.AlignRight)

    def create_symbol_browser(self):
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        
        filter_layout = QHBoxLayout()
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Search available symbols...")
        self.sector_filter = QComboBox()
        filter_layout.addWidget(self.search_filter)
        filter_layout.addWidget(self.sector_filter)
        
        browser_layout.addLayout(filter_layout)
        browser_layout.addWidget(self.available_symbols_list)
        
        return browser_widget

    def connect_signals(self):
        self.search_filter.textChanged.connect(self.filter_symbols)
        self.sector_filter.currentIndexChanged.connect(self.filter_symbols)
        self.available_symbols_list.itemDoubleClicked.connect(lambda item: self.add_to_queue([item.text()]))
        self.selected_symbols_list.itemDoubleClicked.connect(lambda item: self.remove_from_queue([item.text()]))
        self.output_dir_button.clicked.connect(self.trigger_output_dir_chooser)
        self.manifest_file_button.clicked.connect(self.trigger_manifest_file_chooser)
        self.start_button.clicked.connect(self.start_download)

    def add_log_entry(self, message):
        self.log_view.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def on_download_finished(self):
        self.start_button.setDisabled(False)
        self.add_log_entry("Download finished.")

    def load_master_data(self):
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            master_file_path = os.path.join(project_root, "source_data", "master_catalog_enriched.csv")
            self.master_df = pd.read_csv(master_file_path)
            self.comm.data_loaded_signal.emit()
        except Exception as e:
            self.comm.log_signal.emit(f"Error loading master data: {e}")

    def on_data_loaded(self):
        self.search_filter.setDisabled(False)
        self.sector_filter.setDisabled(False)
        unique_sectors = ["All Sectors"] + sorted(self.master_df["Industry"].dropna().unique().tolist())
        self.sector_filter.addItems(unique_sectors)
        self.filter_symbols()
        self.add_log_entry("Master data loaded.")

    def filter_symbols(self):
        if self.master_df is None: return
        df = self.master_df.copy()
        search_term = self.search_filter.text().upper()
        sector = self.sector_filter.currentText()
        if search_term:
            df = df[df["Symbol"].str.contains(search_term, na=False)]
        if sector and sector != "All Sectors":
            df = df[df["Industry"] == sector]
        self.available_symbols_list.clear()
        self.available_symbols_list.addItems(df["Symbol"].tolist())

    def add_to_queue(self, symbols):
        current_items = {self.selected_symbols_list.item(i).text() for i in range(self.selected_symbols_list.count())}
        for symbol in symbols:
            if symbol and symbol not in current_items:
                self.selected_symbols_list.addItem(symbol)

    def remove_from_queue(self, symbols):
        for symbol in symbols:
            items = self.selected_symbols_list.findItems(symbol, Qt.MatchExactly)
            for item in items:
                self.selected_symbols_list.takeItem(self.selected_symbols_list.row(item))

    def start_download(self):
        params = {}
        try:
            # Check which tab is active
            if self.tab_widget.currentIndex() == 0: # New Job
                params["resume_mode"] = False
                params["symbols"] = [self.selected_symbols_list.item(i).text() for i in range(self.selected_symbols_list.count())]
                if not params["symbols"]:
                    raise ValueError("No symbols in the download queue.")
                params["start_date"] = self.start_date_edit.date().toPython()
                params["end_date"] = self.end_date_edit.date().toPython()
                params["interval"] = self.interval_combo.currentText()
                params["output_dir"] = self.output_dir_edit.text()
            
            elif self.tab_widget.currentIndex() == 1: # Resume Job
                params["resume_mode"] = True
                params["manifest_path"] = self.manifest_file_edit.text()
                if not os.path.exists(params["manifest_path"]):
                    raise ValueError("Manifest file for resume not found.")

            # Hardcoded params for simplicity, can be re-added to UI
            params["save_csv"] = True
            params["save_parquet"] = True
            params["sharding"] = "None"

            self.log_view.clear()
            self.progress_bar.setValue(0)
            self.start_button.setDisabled(True)

            kite = self.session_manager.get_kite()
            if not kite:
                raise ConnectionError("Kite session not available. Please log in.")

            worker = DownloadWorker(params, self, kite_session=kite)
            worker.start()

        except Exception as e:
            self.add_log_entry(f"Configuration Error: {e}")
            self.start_button.setDisabled(False)

    def trigger_output_dir_chooser(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_edit.setText(directory)

    def trigger_manifest_file_chooser(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Manifest File", "", "JSON Files (*.json)")
        if file_path:
            self.manifest_file_edit.setText(file_path)
