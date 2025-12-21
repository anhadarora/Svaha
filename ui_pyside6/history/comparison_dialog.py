
import pandas as pd
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QDialogButtonBox,
)
from PySide6.QtGui import QColor

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

class ComparisonDialog(QDialog):
    def __init__(self, runs_data: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compare Runs")
        self.setMinimumSize(1200, 800)

        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)

        self.populate_table(runs_data)

    def populate_table(self, runs_data):
        if not runs_data:
            return

        # --- Data Preparation ---
        # Flatten the parameter config for each run
        flat_configs = [flatten_dict(run.get("parameter_configuration", {})) for run in runs_data]
        
        # Get experiment names for headers
        experiment_names = [run.get("experiment_summary", {}).get("Experiment Name", f"Run {i+1}") for i, run in enumerate(runs_data)]

        # Create a DataFrame for easy comparison
        df = pd.DataFrame(flat_configs).T
        df.columns = experiment_names
        
        # Find rows where not all values are the same
        diff_rows = df.apply(lambda x: x.nunique() > 1, axis=1)

        # --- Table Population ---
        self.table.setColumnCount(len(experiment_names))
        self.table.setHorizontalHeaderLabels(experiment_names)
        
        self.table.setRowCount(len(df))
        self.table.setVerticalHeaderLabels(df.index)

        for row_idx, (param, data) in enumerate(df.iterrows()):
            is_different = diff_rows[param]
            for col_idx, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                if is_different:
                    item.setBackground(QColor(60, 60, 30)) # Dark yellow background for diffs
                self.table.setItem(row_idx, col_idx, item)
        
        self.table.resizeColumnsToContents()
