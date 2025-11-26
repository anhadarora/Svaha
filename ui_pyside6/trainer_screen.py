import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

class TrainerScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Trainer Screen")
        layout.addWidget(label)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    trainer_screen = TrainerScreen()
    trainer_screen.show()
    sys.exit(app.exec())
