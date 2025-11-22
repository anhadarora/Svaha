from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel

class BacktesterScreen(MDScreen):
    def __init__(self, **kwargs):
        super(BacktesterScreen, self).__init__(**kwargs)
        self.name = "backtester"
        self.add_widget(MDLabel(text="Backtester Screen", halign="center"))
