import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QSizePolicy,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ui_pyside6.backtester_screen import BacktesterScreen
from ui_pyside6.downloader_screen import DownloaderScreen
from ui_pyside6.trainer_screen import TrainerScreen


class MainScreen(QMainWindow):
    def __init__(self, session_manager):
        super().__init__()
        self.setWindowTitle("Svaha - PySide6")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create the top toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        # Add a spacer to push the action to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)

        # Add user account action
        self.user_action = QAction("User", self)
        self.toolbar.addAction(self.user_action)

        # Create the tab widget for bottom navigation
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.South)
        layout.addWidget(self.tab_widget)

        # Create the screens (as simple widgets for now)
        self.downloader_screen = DownloaderScreen(
            session_manager=session_manager)
        self.trainer_screen = TrainerScreen(session_manager=session_manager)
        self.backtester_screen = BacktesterScreen()

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.downloader_screen, "Downloader")
        self.tab_widget.addTab(self.trainer_screen, "Trainer")
        self.tab_widget.addTab(self.backtester_screen, "Backtester")

    def update_user_icon(self, logged_in):
        if logged_in:
            self.user_action.setText("Logged In")
        else:
            self.user_action.setText("User")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_screen = MainScreen()
    main_screen.show()
    sys.exit(app.exec())
