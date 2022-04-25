from kivy.app import App
from kivy.uix.gridlayout import GridLayout

from kivy.config import Config
Config.set('graphics', 'width', '1600')
Config.set('graphics', 'height', '900')


class MainLayout(GridLayout):
    pass

class MainApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    MainApp().run()