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
)
from PySide6.QtCore import Qt
from ..pandas_model import PandasModel


class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.full_history_data = []
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # --- Toolbar ---
        toolbar_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        toolbar_layout.addWidget(self.refresh_button)
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
        splitter.setSizes([700, 300]) # Initial size ratio

        # --- Data Model ---
        self.model = PandasModel(pd.DataFrame())
        self.history_table.setModel(self.model)

        self.connect_signals()
        self.load_history()

    def connect_signals(self):
        self.refresh_button.clicked.connect(self.load_history)
        self.history_table.clicked.connect(self.show_run_details)

    def load_history(self):
        """Loads the history data from the JSON file and populates the table."""
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

            # Create a summary DataFrame for the table view
            display_data = []
            for run in self.full_history_data:
                summary = run.get("experiment_summary", {})
                kpis = run.get("kpis", {})
                display_data.append({
                    "Experiment Name": summary.get("Experiment Name", "N/A"),
                    "Completed On": summary.get("Completed On", "N/A"),
                    "Best Val Loss": summary.get("Best Validation Loss", "N/A"),
                    "Sharpe Ratio": kpis.get("Sharpe Ratio", "N/A"),
                })
            
            df = pd.DataFrame(display_data)
            self.model = PandasModel(df)
            self.history_table.setModel(self.model)
            self.history_table.resizeColumnsToContents()

        except Exception as e:
            self.details_view.setText(f"Error loading history file:\n{e}")
            self.model = PandasModel(pd.DataFrame())
            self.history_table.setModel(self.model)

    def show_run_details(self, index):
        """Displays the full JSON for the selected run."""
        row = index.row()
        if 0 <= row < len(self.full_history_data):
            selected_run_data = self.full_history_data[row]
            formatted_json = json.dumps(selected_run_data, indent=4)
            self.details_view.setText(formatted_json)
