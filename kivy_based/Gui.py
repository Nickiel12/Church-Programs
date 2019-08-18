import atexit
import kivy
import keyboard
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty
import sys
from tkinter import messagebox
import time
import threading

from automation_controller import Setup, AutomationController
from exceptions import PopupError, PopupNotExist, PrematureExit
from dialogs import Question, WarningPopup
from utils import make_functions, Settings, threaded

if True == False:
    from kivy_based.automation_controller import Setup, AutomationController
    from kivy_based.exceptions import PopupError, PopupNotExist, PrematureExit
    from kivy_based.utils import make_functions, Settings, threaded
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
                if popup.timer_event.is_set():
                    raise PrematureExit("Timer caught event set")
                print(f"current function: {i[0]}")
                i[0]()
                print(f"sleeping for {i[1]} seconds")
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
    
    on = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_run = threading.Event()
        self._startup()
        
    @threaded
    def _startup(self):
        time.sleep(2)
        self.auto_contro = AutomationController(Settings())
        App.get_running_app().bind(on_stop=self._stop_timer)
        self.start_hotkeys()
        self.timer_start_time = time.time()
        self.timer_length = 30
        self._timer_paused = True
        self.automatic = True
        self._timer()
        self.ids.live_camera.ids.cb.bind(active=self.on_camera)
        self.ids.center_screen.ids.cb.bind(active=self.on_center_screen)
        self.ids.SCQAutomatic.ids.cb.bind(active=self.on_auto)
    
    def _stop_timer(self, *args):
        print("timer stopped")
        self.timer_run.set()

    def zero_timer(self, *args):
        self.pause_timer()
        self.ids.TimerLabel.text = "0.0"

    def pause_timer(self, *args):
        self._timer_paused = True
    
    def start_timer(self, *args):
        self._timer_paused = False

    def reset_timer(self):
        self.timer_start_time = time.time()
        self.start_timer()
        
    @threaded
    def _timer(self):
        while not self.timer_run.is_set():
            try:
                if self._timer_paused == False:
                    end_time = self.timer_start_time + self.timer_length
                    timer_left = round(end_time - time.time(), 1)
                    if timer_left >= 0:
                        self.ids.TimerLabel.text = str(timer_left)
                    else:
                        self.timer_run_out()
                else:
                    time.sleep(.3)
            except KeyboardInterrupt:
                return
            time.sleep(.1)

    def timer_run_out(self):
        self.on_camera(None)
        self.ids.live_camera.ids.cb.active = True

    def start_hotkeys(self):
        sett = Settings()
        keyboard.add_hotkey(sett.hotkeys.obs.camera_scene_hotkey[0], 
            self.on_hotkey, args=("camera"))
        keyboard.add_hotkey(sett.hotkeys.obs.center_screen_hotkey[0],
            self.on_hotkey, args=("center"))

    def on_hotkey(self, *hotkey):
        
        hotkey = "".join(hotkey)
        print(f"hotkey {hotkey} caught")
        if hotkey == "camera":
            self.ids.live_camera.ids.cb._do_press()
        elif hotkey == "center":
            self.ids.center_screen.ids.cb._do_press()

        elif hotkey == "shift_down":
            self.shift = True
        elif hotkey == "shift_up":
            self.shift = False

    def on_camera(self, *args):
        self.auto_contro.obs_scene("camera")
        self.pause_timer()
        self.zero_timer()

    def on_center_screen(self, *args):
        self.auto_contro.obs_scene("center")
        self.on_auto()

    def on_auto(self, *args):
        state = self.ids.SCQAutomatic.ids.cb.active
        if state == False:
            self.zero_timer()
        else:
            if self.ids.center_screen.ids.cb.active == True:
                self.reset_timer()

class GuiApp(App):
    def build(self):
        return Controller()

if __name__ == "__main__":
    app = GuiApp()
    app.run()