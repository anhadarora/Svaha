from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDIconButton
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from ui.downloader.downloader_screen import DownloaderScreen
from ui.trainer_screen import TrainerScreen
from ui.backtester_screen import BacktesterScreen


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.name = "main"

        self.layout = MDBoxLayout(orientation='vertical')

        self.toolbar = MDTopAppBar(title="Svaha")
        self.toolbar.right_action_items = [
            ["account-outline", lambda x: self.open_user_screen()]]
        self.layout.add_widget(self.toolbar)

        self.screen_manager = ScreenManager()

        downloader_item = MDBottomNavigationItem(
            name='downloader',
            text='Downloader',
            icon='database-arrow-down',
        )
        # Give the DownloaderScreen an ID so we can access it from the app
        self.downloader_screen = DownloaderScreen()
        downloader_item.add_widget(self.downloader_screen)

        trainer_item = MDBottomNavigationItem(
            name='trainer',
            text='Trainer',
            icon='robot',
        )
        trainer_item.add_widget(TrainerScreen())

        backtester_item = MDBottomNavigationItem(
            name='backtester',
            text='Backtester',
            icon='test-tube',
        )
        backtester_item.add_widget(BacktesterScreen())

        self.bottom_nav = MDBottomNavigation()
        self.bottom_nav.add_widget(downloader_item)
        self.bottom_nav.add_widget(trainer_item)
        self.bottom_nav.add_widget(backtester_item)

        self.layout.add_widget(self.bottom_nav)
        self.add_widget(self.layout)

        # Add the downloader screen to the ids dictionary for easy access
        self.ids['downloader_screen'] = self.downloader_screen

    def open_user_screen(self):
        self.manager.current = "user"

    def update_user_icon(self, logged_in):
        if logged_in:
            self.toolbar.right_action_items = [
                ["account-check", lambda x: self.open_user_screen()]]
        else:
            self.toolbar.right_action_items = [
                ["account-outline", lambda x: self.open_user_screen()]]
