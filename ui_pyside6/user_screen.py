import sys
import os
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGroupBox, QPushButton,
    QTabWidget, QTableView, QToolBar
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal, QObject
import pandas as pd
from .pandas_model import PandasModel

# Assuming these are in the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.kite_api import kite_api
from api.auth_server import AuthServer

class Communicate(QObject):
    update_status_signal = Signal(str, bool, object, object, object)
    logged_in_signal = Signal(bool)

class UserScreen(QWidget):
    back_requested = Signal()

    def __init__(self, session_manager, kite_api):
        super().__init__()
        
        self.session_manager = session_manager
        self.kite_api = kite_api
        
        self.comm = Communicate()
        self.comm.update_status_signal.connect(self.update_status)
        
        self.init_ui()
        
        self.try_auto_login()

    def login_with_kite(self, *args):
        self.login_label.setText("Status: Logging in...")
        self.data_layout.show()
        auth_thread = threading.Thread(target=self.run_auth_flow)
        auth_thread.start()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        self.toolbar = QToolBar("User")
        back_action = QAction("Back", self)
        back_action.triggered.connect(self.go_back)
        self.toolbar.addAction(back_action)
        layout.addWidget(self.toolbar)

        # Main content area
        content_layout = QVBoxLayout()
        layout.addLayout(content_layout)

        # Login Card
        self.login_card = QGroupBox("Login")
        login_layout = QVBoxLayout(self.login_card)
        self.login_label = QLabel("Please login to continue")
        self.login_button = QPushButton("Login with Kite")
        self.login_button.clicked.connect(self.login_with_kite)
        login_layout.addWidget(self.login_label)
        login_layout.addWidget(self.login_button)
        content_layout.addWidget(self.login_card)

        # Data Layout
        self.data_layout = QVBoxLayout()
        content_layout.addLayout(self.data_layout)

        # Funds Card (placeholder)
        self.funds_card = QGroupBox("Funds")
        funds_layout = QVBoxLayout(self.funds_card)
        self.funds_label = QLabel("Available: ₹...")
        funds_layout.addWidget(self.funds_label)
        self.data_layout.addWidget(self.funds_card)
        self.funds_card.hide() # Initially hidden

        # Tabs for Positions and Holdings
        self.tab_widget = QTabWidget()
        self.positions_tab = QWidget()
        self.holdings_tab = QWidget()
        self.tab_widget.addTab(self.positions_tab, "Positions")
        self.tab_widget.addTab(self.holdings_tab, "Holdings")
        self.data_layout.addWidget(self.tab_widget)
        self.tab_widget.hide() # Initially hidden

        # Positions Table
        positions_layout = QVBoxLayout(self.positions_tab)
        self.positions_table = QTableView()
        positions_layout.addWidget(self.positions_table)

        # Holdings Table
        holdings_layout = QVBoxLayout(self.holdings_tab)
        self.holdings_table = QTableView()
        holdings_layout.addWidget(self.holdings_table)

    def go_back(self):
        self.back_requested.emit()

    def go_back(self):
        self.back_requested.emit()

    def try_auto_login(self):
        if self.kite_api.is_session_valid():
            margins = self.session_manager.get_kite().margins()
            positions = self.session_manager.get_kite().positions()
            holdings = self.session_manager.get_kite().holdings()
            self.comm.update_status_signal.emit("Logged in from saved session", True, margins, positions, holdings)

    def run_auth_flow(self):
        auth_server = AuthServer()
        login_url = self.kite_api.get_login_url()
        auth_server.start(login_url)
        
        if auth_server.request_token:
            if self.session_manager.generate_session(auth_server.request_token):
                margins = self.session_manager.get_kite().margins()
                positions = self.session_manager.get_kite().positions()
                holdings = self.session_manager.get_kite().holdings()
                self.comm.update_status_signal.emit("Login successful", True, margins, positions, holdings)
            else:
                self.comm.update_status_signal.emit("Status: Login failed", False, None, None, None)
        else:
            self.comm.update_status_signal.emit("Status: Login failed", False, None, None, None)

    def update_status(self, message, success, margins=None, positions=None, holdings=None):
        if success:
            self.login_card.hide()
            self.funds_card.show()
            self.tab_widget.show()
            self.update_dashboard(margins, positions, holdings)
            self.comm.logged_in_signal.emit(True)
        else:
            self.login_label.setText(message)
            self.comm.logged_in_signal.emit(False)

    def update_dashboard(self, margins, positions, holdings):
        # Funds
        if margins:
            self.funds_label.setText(f"Available: ₹{margins['equity']['available']['live_balance']:.2f}")

        # Positions
        if positions and (positions['net'] or positions['day']):
            positions_data = positions['net'] + positions['day']
            positions_df = pd.DataFrame(positions_data)
            positions_df = positions_df[['tradingsymbol', 'quantity', 'average_price', 'pnl', 'm2m']]
            positions_df.columns = ['Symbol', 'Qty', 'Avg.', 'P&L', 'M2M']
            positions_model = PandasModel(positions_df)
            self.positions_table.setModel(positions_model)

        # Holdings
        if holdings:
            holdings_df = pd.DataFrame(holdings)
            holdings_df = holdings_df[['tradingsymbol', 'quantity', 'average_price', 'last_price', 'pnl']]
            holdings_df.columns = ['Symbol', 'Qty', 'Avg.', 'LTP', 'P&L']
            holdings_model = PandasModel(holdings_df)
            self.holdings_table.setModel(holdings_model)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    user_screen = UserScreen()
    user_screen.show()
    sys.exit(app.exec())
