import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui_pyside6.main_screen import MainScreen
from ui_pyside6.session_manager import SessionManager
from api.kite.client import kite_api
from ui_pyside6.user_screen import UserScreen
from ui_pyside6.widgets.tooltip_system import TooltipManager, TooltipEventFilter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Svaha - PySide6")

        self.session_manager = SessionManager(kite_api=kite_api)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_screen = MainScreen(session_manager=self.session_manager)
        self.user_screen = UserScreen(
            session_manager=self.session_manager, kite_api=kite_api
        )

        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.user_screen)

        self.main_screen.user_action.triggered.connect(self.show_user_screen)
        self.user_screen.back_requested.connect(self.show_main_screen)
        self.user_screen.comm.logged_in_signal.connect(
            self.main_screen.update_user_icon
        )

        self.show_main_screen()

    def show_main_screen(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)

    def show_user_screen(self):
        self.stacked_widget.setCurrentWidget(self.user_screen)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # --- Tooltip System Setup ---
    tooltip_manager = TooltipManager()
    tooltip_manager.load_tooltips()
    tooltip_event_filter = TooltipEventFilter(tooltip_manager)
    app.installEventFilter(tooltip_event_filter)
    # --------------------------

    # Load and apply stylesheet
    try:
        with open("ui_pyside6/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Stylesheet not found, using default styles.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
