# This MUST be the first import to ensure color definitions are updated
# before any other KivyMD modules are loaded.
import ui.theming_init
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, WipeTransition
from ui.main_screen import MainScreen
from ui.downloader.downloader_screen import DownloaderScreen
from ui.user_screen import UserScreen


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.accent_palette = "Amber"
        self.title = "Svaha"

        sm = ScreenManager()
        sm.transition = WipeTransition()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(UserScreen(name='user'))
        # The DownloaderScreen is defined within the MainScreen's KV file,
        # so we do not need to add it here. Navigation to 'downloader'
        # will be handled by the ScreenManager inside MainScreen.

        return sm


if __name__ == "__main__":
    MainApp().run()
