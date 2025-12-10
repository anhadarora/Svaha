from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QGroupBox, QVBoxLayout


class KpiWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        kpi_group = QGroupBox("Key Performance Indicators (KPIs)")
        self.layout.addWidget(kpi_group)
        kpi_layout = QFormLayout(kpi_group)

        self.final_accuracy = QLabel("N/A")
        kpi_layout.addRow("Final Accuracy:", self.final_accuracy)

        self.sharpe_ratio = QLabel("N/A")
        kpi_layout.addRow("Sharpe Ratio:", self.sharpe_ratio)

        self.max_drawdown = QLabel("N/A")
        kpi_layout.addRow("Maximum Drawdown:", self.max_drawdown)

        self.alpha = QLabel("N/A")
        kpi_layout.addRow("Alpha:", self.alpha)

    def update_data(self, data: dict):
        """Populates the KPI fields with data from the completed run."""
        self.final_accuracy.setText(data.get("Final Accuracy", "N/A"))
        self.sharpe_ratio.setText(data.get("Sharpe Ratio", "N/A"))
        self.max_drawdown.setText(data.get("Max Drawdown", "N/A"))
        self.alpha.setText(data.get("Alpha", "N/A"))