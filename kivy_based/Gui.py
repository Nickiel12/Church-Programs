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

from automation_controller import Setup
from exceptions import PopupError, PopupNotExist, PrematureExit
from dialogs import Question, WarningPopup
from utils import make_functions
if True == False:
    from kivy_based.automation_controller import Setup
    from kivy_based.exceptions import PopupError, PopupNotExist, PrematureExit
    from kivy_based.utils import make_functions
    from kivy_based.dialogs import Question, WarningPopup

import logging
from logging import debug
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,
        format= '%(asctime)s - %(levelname)s - %(message)s')

Window.size = (400, 400)

def on_startup_button_submit(stream_name, startup_controller):
    print(f"stream_name is: {stream_name}")
    thread = threading.Thread(target=_run_startup, args=(stream_name,))
    thread.start()

def redo_startup():
    App.get_running_app().root.current = "StartupScreen"

def _run_startup(stream_name, *args):
    try:
        popup = WarningPopup()
        popup.open()
        
        setup = Setup(popup, stream_name)
        settings = make_functions(setup)
        for i in settings:
            try:
                if popup.timer_thread.is_set():
                    raise PrematureExit("Timer caught event set")
                i[0]()
                time.sleep(i[1])
            except KeyboardInterrupt:
                raise PrematureExit("Keyboard Inturrupt caught in sleep_check")
        setup.del_popup()

    except KeyboardInterrupt:
        if popup.timer_thread and popup.timer_thread.isAlive():
            popup.timer_event.set()
    except (PopupNotExist, PrematureExit):
        debug("Popup was closed unexpectedly")
        if Question("Setup was canceled before it was finished\n"+
            "Would you like to restart the program?", "Python"):
            
            popup.close()
            redo_startup()
        else:
            logging.getLogger().debug("the user said no to the question")
        print("done with the question")
    finally:
        popup.close()  

class Controller(ScreenManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StartupScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StartupController(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_submit(self, stream_name, *args):
        on_startup_button_submit(stream_name, self)
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