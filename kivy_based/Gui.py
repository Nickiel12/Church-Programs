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

from exceptions import PopupError, PopupNotExist, PopupClosed, PrematureExit
from dialogs import Question, WarningPopup
if True == False:
    from kivy_based.exceptions import PopupError, PopupNotExist, PopupClosed, PrematureExit
    from kivy_based.utils import WarningPopup
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

def sleep_check(time_to_sleep, event_to_check:threading.Event):
    last_time = 0
    end_time = time.time() + time_to_sleep
    while True:
        try:
            if event_to_check.is_set():
                raise PrematureExit("Timer caught event set")
            time_left = end_time - time.time()
            #debug(f"time_left is {time_left}")
            #debug(f"end_time is {end_time}")
            if time_left != last_time:
                last_time = time_left
                if time_left <= 0:
                    break
            time.sleep(.1)
        except KeyboardInterrupt:
            raise PrematureExit("Keyboard Inturrupt caught in sleep_check")

def redo_startup():
    App.get_running_app().root.current = "StartupScreen"

def _run_startup(stream_name, *args):
    try:
        popup = WarningPopup()
        popup.open()
        
        popup.set_task("Task One", 20)
        sleep_check(20, popup.timer_event)
        popup.set_task("Task Two", 10)
        sleep_check(10, popup.timer_event)
    except KeyboardInterrupt:
        if popup.timer_thread and popup.timer_thread.isAlive():
            popup.timer_event.set()
    except (PopupNotExist, PrematureExit):
        debug("Popup was closed unexpectedly")
        if Question("Setup was canceled before it was finished\n"+
            "Would you like to restart the program?", "Python"):
            try:
                popup.close()
            except PopupClosed:
                pass
            redo_startup()
        else:
            print("the user said no to the question")
        print("done with the question")
    finally:
        try:
            popup.close()
        except PopupClosed:
            if Question("Setup was canceled before it was finished\n"+
                "Would you like to restart the program?", "Python"):
                debug("yes")
                redo_startup()
            else:
                debug("no")    

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