import sys
import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QFontDatabase, QFont, QPixmap, QIcon
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QButtonGroup,
    QFrame
)

from ui_pyside6.backtester_screen import BacktesterScreen
from ui_pyside6.downloader_screen import DownloaderScreen
from ui_pyside6.trainer_screen import TrainerScreen
from ui_pyside6.user_screen import UserScreen


class MainScreen(QMainWindow):
    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.previous_widget_index = 1  # Default to trainer screen
        self.setWindowTitle("Svaha")
        self.setGeometry(100, 100, 1280, 800)

        # --- FONT LOADING ---
        font_path = os.path.join(os.path.dirname(
            __file__), "..", "assets", "fonts", "custom_font.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id != -1:
            self.custom_font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            self.custom_font_family = "Arial"

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ============================================================
        # 1. HEADER (Logo + Title + Nav Buttons + User)
        # ============================================================
        header_container = QWidget()
        header_container.setFixedHeight(70)
        header_container.setObjectName("HeaderContainer")

        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(24, 0, 24, 0)

        # --- A. LOGO ---
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(50, 50)
        self.logo_label.setStyleSheet("border: none; background: transparent;")
        self.logo_label.setScaledContents(True)

        pixmap_path = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "logo_white.png")
        if os.path.exists(pixmap_path):
            pixmap = QPixmap(pixmap_path)
            self.logo_label.setPixmap(pixmap.scaled(
                50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.logo_label.setText("Svaha")
            self.logo_label.setStyleSheet("color: white; font-size: 10px;")

        # --- B. APP NAME ---
        self.app_name_label = QLabel("SVAHA")
        self.app_name_label.setStyleSheet(f"""
            font-family: '{self.custom_font_family}'; 
            font-size: 42px; 
            font-weight: bold; 
            color: #E0E0E0;
            background: transparent;
            border: none;
            margin-right: 20px;
        """)

        # --- C. NAVIGATION BUTTONS (The "Tabs") ---
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_container = QWidget()
        nav_container.setObjectName("NavContainer")
        nav_container.setFixedHeight(40)

        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(4, 4, 4, 4)
        nav_layout.setSpacing(5)

        self.btn_downloader = self.create_nav_button("Downloader", 0)
        self.btn_trainer = self.create_nav_button("Trainer", 1)
        self.btn_backtester = self.create_nav_button("Backtester", 2)

        nav_layout.addWidget(self.btn_downloader)
        nav_layout.addWidget(self.btn_trainer)
        nav_layout.addWidget(self.btn_backtester)

        # --- D. USER BUTTON ---
        self.user_button = QPushButton("User")
        self.user_button.setFixedSize(100, 32)
        self.user_button.setObjectName("UserButton")
        self.user_button.clicked.connect(self.show_user_screen)

        # --- E. ASSEMBLE HEADER ---
        header_layout.addWidget(self.logo_label)
        header_layout.addWidget(self.app_name_label)
        header_layout.addStretch()
        header_layout.addWidget(nav_container)
        header_layout.addSpacing(20)
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("color: #333333;")
        separator.setFixedHeight(20)
        header_layout.addWidget(separator)
        header_layout.addWidget(self.user_button)
        main_layout.addWidget(header_container)

        # ============================================================
        # 2. CONTENT STACK
        # ============================================================
        self.content_stack = QStackedWidget()
        self.content_stack.currentChanged.connect(self._on_tab_changed)

        # Initialize Screens
        self.downloader_screen = DownloaderScreen(session_manager=session_manager)
        self.trainer_screen = TrainerScreen(session_manager=session_manager)
        self.backtester_screen = BacktesterScreen()
        self.user_screen = UserScreen(session_manager=session_manager, kite_api=session_manager._kite_api)
        self.user_screen.back_requested.connect(self.show_previous_screen)
        self.user_screen.comm.logged_in_signal.connect(self.update_user_icon)

        # Add to Stack
        self.content_stack.addWidget(self.downloader_screen)  # Index 0
        self.content_stack.addWidget(self.trainer_screen)    # Index 1
        self.content_stack.addWidget(self.backtester_screen)  # Index 2
        self.content_stack.addWidget(self.user_screen)       # Index 3

        main_layout.addWidget(self.content_stack)

        # --- INITIAL STATE CHECK ---
        # Set initial state of the user button and UI based on session
        self.user_screen.check_session_and_update_ui()

        # Set default tab
        self.btn_trainer.setChecked(True)
        self.content_stack.setCurrentIndex(1)

    def create_nav_button(self, text, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setObjectName("NavButton")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(index))
        self.nav_group.addButton(btn)
        return btn

    def _on_tab_changed(self, index):
        # Don't update the previous index if we are on the user screen
        if index < 3:
            self.previous_widget_index = index

    def show_user_screen(self):
        self.user_screen.check_session_and_update_ui()
        self.content_stack.setCurrentWidget(self.user_screen)

    def show_previous_screen(self):
        self.content_stack.setCurrentIndex(self.previous_widget_index)

    def update_user_icon(self, logged_in):
        if logged_in:
            self.user_button.setText("Logged In")
            self.user_button.setProperty("state", "logged_in")
        else:
            self.user_button.setText("User")
            self.user_button.setProperty("state", "logged_out")
        self.user_button.style().unpolish(self.user_button)
        self.user_button.style().polish(self.user_button)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from api.kite.client import kite_api
    from ui_pyside6.session_manager import SessionManager

    app = QApplication(sys.argv)
    
    session_manager = SessionManager(kite_api=kite_api)

    try:
        with open("ui_pyside6/dark_theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("dark_theme.qss not found")

    main_screen = MainScreen(session_manager=session_manager)
    main_screen.show()
    sys.exit(app.exec())
