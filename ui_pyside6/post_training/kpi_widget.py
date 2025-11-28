from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QGroupBox


class KpiWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        kpi_group = QGroupBox("Key Performance Indicators (KPIs)")
        self.layout.addWidget(kpi_group)
        kpi_layout = QFormLayout(kpi_group)

        self.total_return = QLabel("N/A")
        kpi_layout.addRow("Total Return (%):", self.total_return)

        self.sharpe_ratio = QLabel("N/A")
        kpi_layout.addRow("Sharpe Ratio:", self.sharpe_ratio)

        self.sortino_ratio = QLabel("N/A")
        kpi_layout.addRow("Sortino Ratio:", self.sortino_ratio)

        self.calmar_ratio = QLabel("N/A")
        kpi_layout.addRow("Calmar Ratio:", self.calmar_ratio)

        self.max_drawdown = QLabel("N/A")
        kpi_layout.addRow("Maximum Drawdown (%):", self.max_drawdown)
