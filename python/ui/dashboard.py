import threading
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivy.metrics import dp
from api.kite_api import kite_api
from api.auth_server import AuthServer

class Tab(MDBoxLayout, MDTabsBase):
    '''Class implementing content for a tab.'''

class Dashboard(MDScreen):
    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)
        self.name = "dashboard"
        
        self.layout = MDBoxLayout(orientation='vertical')
        
        self.toolbar = MDTopAppBar(title="Svaha")
        self.layout.add_widget(self.toolbar)

        self.scroll_view = ScrollView()
        self.content_layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), adaptive_height=True)
        
        # Login Card
        self.login_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            size_hint_y=None,
            height=dp(200)
        )
        self.login_label = MDLabel(
            text="Please login to continue",
            halign="center",
            theme_text_color="Secondary"
        )
        self.login_button = MDFillRoundFlatIconButton(
            text="Login with Kite",
            icon="login",
            on_release=self.login_with_kite,
            pos_hint={'center_x': 0.5}
        )
        self.login_card.add_widget(self.login_label)
        self.login_card.add_widget(self.login_button)
        self.content_layout.add_widget(self.login_card)

        # Data Layout (initially empty)
        self.data_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing=dp(20))
        self.content_layout.add_widget(self.data_layout)

        self.scroll_view.add_widget(self.content_layout)
        self.layout.add_widget(self.scroll_view)

        # Action Buttons
        self.action_buttons_layout = MDBoxLayout(orientation='horizontal', spacing=dp(10), adaptive_height=True, size_hint_y=None, height=dp(50), padding=dp(10))
        self.data_button = MDFillRoundFlatIconButton(text="Fetch", icon="database-arrow-down", on_release=self.fetch_data, disabled=True)
        self.train_button = MDFillRoundFlatIconButton(text="Train", icon="robot", on_release=self.train_models, disabled=True)
        self.test_button = MDFillRoundFlatIconButton(text="Test", icon="test-tube", on_release=self.test_models, disabled=True)
        self.report_button = MDFillRoundFlatIconButton(text="Report", icon="chart-bar", on_release=self.generate_report, disabled=True)
        
        self.action_buttons_layout.add_widget(self.data_button)
        self.action_buttons_layout.add_widget(self.train_button)
        self.action_buttons_layout.add_widget(self.test_button)
        self.action_buttons_layout.add_widget(self.report_button)
        self.layout.add_widget(self.action_buttons_layout)

        self.add_widget(self.layout)

        self.try_auto_login()


    def try_auto_login(self):
        print("Attempting to auto-login...")
        session_data = kite_api.load_session()
        if session_data:
            print("Session found, checking validity...")
            if kite_api.is_session_valid():
                print("Session valid, updating dashboard.")
                self.login_card.height = 0
                self.login_card.clear_widgets()
                margins = kite_api.get_margins()
                positions = kite_api.get_positions()
                holdings = kite_api.get_holdings()
                Clock.schedule_once(lambda dt: self.update_status("Logged in from saved session", True, margins, positions, holdings))
            else:
                print("Session invalid, manual login required.")
        else:
            print("No saved session found.")

    def login_with_kite(self, *args):
        self.login_label.text = "Status: Logging in..."
        self.data_layout.clear_widgets()
        auth_thread = threading.Thread(target=self.run_auth_flow)
        auth_thread.start()

    def run_auth_flow(self):
        auth_server = AuthServer()
        login_url = kite_api.get_login_url()
        auth_server.start(login_url)
        
        if auth_server.request_token:
            data = kite_api.generate_session(auth_server.request_token)
            if data:
                margins = kite_api.get_margins()
                positions = kite_api.get_positions()
                holdings = kite_api.get_holdings()
                Clock.schedule_once(lambda dt: self.update_status("Login successful", True, margins, positions, holdings))
            else:
                Clock.schedule_once(lambda dt: self.update_status("Status: Login failed", success=False))
        else:
            Clock.schedule_once(lambda dt: self.update_text("Status: Login failed", success=False))

    def update_status(self, message, success, margins=None, positions=None, holdings=None):
        if success:
            self.content_layout.remove_widget(self.login_card)
            self.enable_buttons()
            self.update_dashboard(margins, positions, holdings)
        else:
            self.login_label.text = message

    def update_dashboard(self, margins, positions, holdings):
        self.data_layout.clear_widgets()

        # Funds Card
        if margins:
            funds_card = MDCard(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(100))
            funds_card.add_widget(MDLabel(text="Funds", halign='center', theme_text_color="Primary", font_style="H6"))
            funds_card.add_widget(MDLabel(text=f"Available: ₹{margins['equity']['available']['live_balance']:.2f}", halign='center'))
            self.data_layout.add_widget(funds_card)

        # Tabs for Positions and Holdings
        tab_layout = MDTabs()
        tab_layout.size_hint_y = None
        tab_layout.height = dp(500)
        
        # Positions Tab
        positions_tab = Tab(title="Positions")
        if positions and (positions['net'] or positions['day']):
            positions_data = positions['net'] + positions['day']
            position_rows = [
                (p['tradingsymbol'], str(p['quantity']), f"₹{p['average_price']:.2f}", f"₹{p['pnl']:.2f}", f"₹{p['m2m']:.2f}")
                for p in positions_data
            ]
            table_layout = MDBoxLayout()
            positions_table = MDDataTable(
                column_data=[
                    ("Symbol", dp(30)), ("Qty", dp(20)), ("Avg.", dp(20)), ("P&L", dp(20)), ("M2M", dp(20))
                ],
                row_data=position_rows,
                use_pagination=True,
                rows_num=10
            )
            table_layout.add_widget(positions_table)
            positions_tab.add_widget(table_layout)
        tab_layout.add_widget(positions_tab)

        # Holdings Tab
        holdings_tab = Tab(title="Holdings")
        if holdings:
            holding_rows = [
                (h['tradingsymbol'], str(h['quantity']), f"₹{h['average_price']:.2f}", f"₹{h['last_price']:.2f}", f"₹{h['pnl']:.2f}")
                for h in holdings
            ]
            table_layout = MDBoxLayout()
            holdings_table = MDDataTable(
                column_data=[
                    ("Symbol", dp(30)), ("Qty", dp(20)), ("Avg.", dp(20)), ("LTP", dp(20)), ("P&L", dp(20))
                ],
                row_data=holding_rows,
                use_pagination=True,
                rows_num=10
            )
            table_layout.add_widget(holdings_table)
            holdings_tab.add_widget(table_layout)
        tab_layout.add_widget(holdings_tab)
        
        self.data_layout.add_widget(tab_layout)


    def enable_buttons(self):
        self.data_button.disabled = False
        self.train_button.disabled = False
        self.test_button.disabled = False
        self.report_button.disabled = False

    def fetch_data(self, *args):
        print("Fetching data...")

    def train_models(self, *args):
        print("Training models...")

    def test_models(self, *args):
        print("Testing models...")

    def generate_report(self, *args):
        print("Generating report...")