from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from ui.main_screen import MainScreen
from ui.user_screen import UserScreen

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "A700"
        self.theme_cls.theme_style = "Dark"
        self.title = "Svaha"
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(UserScreen(name='user'))
        
        return sm

if __name__ == "__main__":
    MainApp().run()