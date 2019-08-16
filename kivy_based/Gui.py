import kivy
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty
import sys
from tkinter import messagebox
import time
import threading

from exceptions import PopupError, PopupNotExist, PopupClosed
from dialogs import Question, WarningPopup
if True == False:
    from kivy_based.exceptions import PopupError, PopupNotExist, PopupClosed
    from kivy_based.utils import WarningPopup
    from kivy_based.dialogs import Question, WarningPopup

import logging
from logging import debug
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,
        format= '%(asctime)s - %(levelname)s - %(message)s')

Window.size = (400, 400)

class Controller(ScreenManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StartupScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StartupController(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MainScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StreamController(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_startup(self, *args):
        print(self.ids.go_live_button)

class SceneController(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GuiApp(App):
    def build(self):
        return Controller()

if __name__ == "__main__":
    app = GuiApp()
    app.run()