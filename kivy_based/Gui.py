from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.core.window import Window

Window.size = (300, 400)

class StreamController(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class SceneController(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Controller(FloatLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class GuiApp(App):
    def build(self):
        return Controller()

if __name__ == "__main__":
    app = GuiApp()
    app.run()