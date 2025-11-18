from kivymd.app import MDApp
from ui.dashboard import Dashboard


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "A700"
        self.theme_cls.theme_style = "Dark"
        return Dashboard()


if __name__ == "__main__":
    MainApp().run()
