import sys
from lib import logger # Import the logger module
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui_pyside6.main_screen import MainScreen
from ui_pyside6.session_manager import SessionManager
from api.kite.client import kite_api
from ui_pyside6.user_screen import UserScreen
from ui_pyside6.widgets.tooltip_system import TooltipManager, TooltipEventFilter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scova")

        # ADD THIS LINE: Set a reasonable default size (Width, Height)
        self.resize(1280, 800)

        self.session_manager = SessionManager(kite_api=kite_api)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_screen = MainScreen(session_manager=self.session_manager)
        self.user_screen = UserScreen(
            session_manager=self.session_manager, kite_api=kite_api
        )

        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.user_screen)

        # CHANGE 1: Connect to the button's 'clicked' signal instead of action's 'triggered'
        self.main_screen.user_button.clicked.connect(self.show_user_screen)

        self.user_screen.back_requested.connect(self.show_main_screen)

        # This line remains the same (assuming you updated update_user_icon in MainScreen)
        self.user_screen.comm.logged_in_signal.connect(
            self.main_screen.update_user_icon
        )

        self.show_main_screen()

    def show_main_screen(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)

    def show_user_screen(self):
        self.stacked_widget.setCurrentWidget(self.user_screen)


if __name__ == "__main__":
    # Initialize logging as the first step
    logger.setup_run_logger()

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)


    # --- Tooltip System Setup ---
    tooltip_manager = TooltipManager()
    tooltip_manager.load_tooltips()
    tooltip_event_filter = TooltipEventFilter(tooltip_manager)
    app.installEventFilter(tooltip_event_filter)
    # --------------------------

    # Load and apply stylesheet
    import os
    project_root = os.path.dirname(os.path.abspath(__file__))
    theme_path = os.path.join(project_root, "ui_pyside6", "theme.qss")
    try:
        with open(theme_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Stylesheet not found at {theme_path}, using default styles.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())