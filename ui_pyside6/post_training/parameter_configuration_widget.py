from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel


class ParameterConfigurationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Parameter Configuration (Recap)")
        self.layout.addWidget(group)

        self.parameters_label = QLabel("Parameters will be displayed here.")
        layout = QVBoxLayout(group)
        layout.addWidget(self.parameters_label)
