from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel

class TrainerScreen(MDScreen):
    def __init__(self, **kwargs):
        super(TrainerScreen, self).__init__(**kwargs)
        self.name = "trainer"
        self.add_widget(MDLabel(text="Trainer Screen", halign="center"))
