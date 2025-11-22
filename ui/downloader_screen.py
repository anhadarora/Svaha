from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel

class DownloaderScreen(MDScreen):
    def __init__(self, **kwargs):
        super(DownloaderScreen, self).__init__(**kwargs)
        self.name = "downloader"
        self.add_widget(MDLabel(text="Downloader Screen", halign="center"))
