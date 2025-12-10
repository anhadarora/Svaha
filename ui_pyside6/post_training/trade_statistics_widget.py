from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QGroupBox, QVBoxLayout


class TradeStatisticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        stats_group = QGroupBox("Trade Statistics")
        self.layout.addWidget(stats_group)
        stats_layout = QFormLayout(stats_group)

        self.total_trades = QLabel("N/A")
        stats_layout.addRow("Total Trades:", self.total_trades)

        self.win_rate = QLabel("N/A")
        stats_layout.addRow("Win Rate:", self.win_rate)

        self.profit_factor = QLabel("N/A")
        stats_layout.addRow("Profit Factor:", self.profit_factor)

        self.avg_win = QLabel("N/A")
        stats_layout.addRow("Average Win:", self.avg_win)

        self.avg_loss = QLabel("N/A")
        stats_layout.addRow("Average Loss:", self.avg_loss)

    def update_data(self, data: dict):
        """Populates the trade statistics fields."""
        self.total_trades.setText(str(data.get("Total Trades", "N/A")))
        self.win_rate.setText(str(data.get("Win Rate", "N/A")))
        self.profit_factor.setText(str(data.get("Profit Factor", "N/A")))
        self.avg_win.setText(str(data.get("Average Win", "N/A")))
        self.avg_loss.setText(str(data.get("Average Loss", "N/A")))