from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QGroupBox


class TradeStatisticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        stats_group = QGroupBox("Trade Statistics")
        self.layout.addWidget(stats_group)
        stats_layout = QFormLayout(stats_group)

        self.total_trades = QLabel("N/A")
        stats_layout.addRow("Total Trades:", self.total_trades)

        self.win_rate = QLabel("N/A")
        stats_layout.addRow("Win Rate (%):", self.win_rate)

        self.loss_rate = QLabel("N/A")
        stats_layout.addRow("Loss Rate (%):", self.loss_rate)

        self.profit_factor = QLabel("N/A")
        stats_layout.addRow("Profit Factor:", self.profit_factor)

        self.avg_win = QLabel("N/A")
        stats_layout.addRow("Average Win ($/Pts):", self.avg_win)

        self.avg_loss = QLabel("N/A")
        stats_layout.addRow("Average Loss ($/Pts):", self.avg_loss)
