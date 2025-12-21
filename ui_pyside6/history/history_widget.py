import json
import os
import pandas as pd
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableView,
    QAbstractItemView,
    QTextEdit,
    QGroupBox,
    QSplitter,
    QHBoxLayout,
    QPushButton,
    QHeaderView,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from ..pandas_model import PandasModel
from .comparison_dialog import ComparisonDialog

class HistoryWidget(QWidget):
    configuration_reload_requested = Signal(dict)

    def __init__(self):
        super().__init__()
        self.full_history_data = []
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # --- Toolbar ---
        toolbar_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.compare_button = QPushButton("Compare Selected Runs")
        self.reload_button = QPushButton("Reload Configuration")
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addWidget(self.compare_button)
        toolbar_layout.addWidget(self.reload_button)
        toolbar_layout.addStretch()
        self.layout.addLayout(toolbar_layout)

        # --- Main Content Splitter ---
        splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(splitter, 1)

        # --- History Table ---
        table_group = QGroupBox("Training History")
        table_layout = QVBoxLayout(table_group)
        self.history_table = QTableView()
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setSortingEnabled(True)
        table_layout.addWidget(self.history_table)
        
        # --- Details View ---
        details_group = QGroupBox("Run Details")
        details_layout = QVBoxLayout(details_group)
        self.details_view = QTextEdit()
        self.details_view.setReadOnly(True)
        self.details_view.setLineWrapMode(QTextEdit.NoWrap)
        details_layout.addWidget(self.details_view)

        splitter.addWidget(table_group)
        splitter.addWidget(details_group)
        splitter.setSizes([700, 300])

        self.model = PandasModel(pd.DataFrame())
        self.history_table.setModel(self.model)

        self.connect_signals()
        self.load_history()
        self._update_button_states()

    def connect_signals(self):
        self.refresh_button.clicked.connect(self.load_history)
        self.compare_button.clicked.connect(self.compare_runs)
        self.reload_button.clicked.connect(self.reload_config)
        self.history_table.selectionModel().selectionChanged.connect(self._update_button_states)

    def load_history(self):
        history_path = os.path.abspath("./build/history.json")
        self.details_view.setText("Select a run to view its full configuration.")
        
        if not os.path.exists(history_path):
            self.model = PandasModel(pd.DataFrame())
            self.history_table.setModel(self.model)
            self.full_history_data = []
            return

        try:
            with open(history_path, "r") as f:
                self.full_history_data = json.load(f)
            
            if not self.full_history_data:
                self.model = PandasModel(pd.DataFrame())
                self.history_table.setModel(self.model)
                return

            display_data = []
            for run in self.full_history_data:
                summary = run.get("experiment_summary", {})
                display_data.append({
                    "Experiment Name": summary.get("Experiment Name", "N/A"),
                    "Completed On": summary.get("Completed On", "N/A"),
                    "Result": summary.get("Result", "N/A"),
                })
            
            df = pd.DataFrame(display_data)
            self.model = PandasModel(df)
            self.history_table.setModel(self.model)
            self.history_table.resizeColumnsToContents()

        except Exception as e:
            self.details_view.setText(f"Error loading history file:\n{e}")
            self.model = PandasModel(pd.DataFrame())
            self.history_table.setModel(self.model)
        
        self._update_button_states()

    def show_run_details(self):
        indexes = self.history_table.selectionModel().selectedRows()
        if not indexes:
            self.details_view.setText("Select a run to view its full configuration.")
            return
        
        row = indexes[0].row()
        if 0 <= row < len(self.full_history_data):
            selected_run_data = self.full_history_data[row]
            formatted_json = json.dumps(selected_run_data, indent=4)
            self.details_view.setText(formatted_json)

    def _update_button_states(self):
        selected_rows = len(self.history_table.selectionModel().selectedRows())
        self.reload_button.setEnabled(selected_rows == 1)
        self.compare_button.setEnabled(selected_rows > 1)
        if selected_rows > 0:
            self.show_run_details()

    def get_selected_run_configs(self):
        indexes = self.history_table.selectionModel().selectedRows()
        selected_configs = []
        for index in indexes:
            row = index.row()
            if 0 <= row < len(self.full_history_data):
                selected_configs.append(self.full_history_data[row])
        return selected_configs

    def compare_runs(self):
        selected_runs = self.get_selected_run_configs()
        if len(selected_runs) < 2:
            QMessageBox.information(self, "Not Enough Selections", "Please select two or more runs to compare.")
            return
        
        dialog = ComparisonDialog(selected_runs, self)
        dialog.exec()

    def reload_config(self):
        selected_runs = self.get_selected_run_configs()
        if len(selected_runs) != 1:
            QMessageBox.warning(self, "Invalid Selection", "Please select exactly one run to reload its configuration.")
            return
        
        config_to_load = selected_runs[0].get("parameter_configuration")
        if not config_to_load:
            QMessageBox.critical(self, "Error", "The selected run does not contain a valid parameter configuration.")
            return
            
        reply = QMessageBox.question(self, "Confirm Reload", 
                                     "This will overwrite all current settings in the Setup tab. Are you sure you want to proceed?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.configuration_reload_requested.emit(config_to_load)
            QMessageBox.information(self, "Success", "Configuration has been loaded into the Setup tab.")
