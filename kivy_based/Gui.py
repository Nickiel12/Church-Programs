from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button

class Controller(RelativeLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class GuiApp(App):
    def build(self):
        return Controller()

if __name__ == "__main__":
    app = GuiApp()
    app.run()