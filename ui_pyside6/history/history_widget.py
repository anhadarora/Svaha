from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QAbstractItemView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from .historical_run_dialog import HistoricalRunDialog


class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.history_table = QTableView()
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.history_table)
        self.history_table.doubleClicked.connect(self.show_historical_run)

        self.model = QStandardItemModel()
        self.history_table.setModel(self.model)

        self.model.setHorizontalHeaderLabels(
            [
                "Experiment Name",
                "Final Status",
                "Total Training Time",
                "Total Return (%)",
                "Sharpe Ratio",
            ]
        )

        # Add dummy data
        self.add_history_item(
            "Run_10m_HeikenAshi_ViT_Heal_v2",
            "COMPLETED",
            "04:38:52",
            "15.2",
            "1.2",
        )
        self.add_history_item(
            "Run_5m_Candle_CNN_NoHeal", "ERROR", "00:10:00", "-5.1", "-0.5"
        )

    def add_history_item(
        self, name, status, time, total_return, sharpe_ratio
    ):
        row = [
            QStandardItem(name),
            QStandardItem(status),
            QStandardItem(time),
            QStandardItem(total_return),
            QStandardItem(sharpe_ratio),
        ]
        self.model.appendRow(row)

    def show_historical_run(self, index):
        row = index.row()
        history_data = {
            "name": self.model.item(row, 0).text(),
            "status": self.model.item(row, 1).text(),
            "time": self.model.item(row, 2).text(),
            "return": self.model.item(row, 3).text(),
            "sharpe": self.model.item(row, 4).text(),
        }
        dialog = HistoricalRunDialog(history_data, self)
        dialog.show()
