import sys

from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class BacktesterScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Backtester Screen")
        layout.addWidget(label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    backtester_screen = BacktesterScreen()
    backtester_screen.show()
    sys.exit(app.exec())
