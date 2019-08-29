import os
os.environ["KCFG_KIVY_LOG_LEVEL"] = "debug"
import atexit
import kivy
import keyboard
from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.logger import Logger
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import pathlib2
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
        
        setup = Setup(popup, stream_name, App.get_running_app().auto_contro)
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
        Logger.debug("Popup was closed unexpectedly")
        if Question("Setup was canceled before it was finished\n"+
            "Would you like to restart the program?", "Python"):
            
            popup.close()
            redo_startup()
        else:
            Logger.debug("the user said no to the question")
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
        self.app = App.get_running_app()

    def on_already(self, *args):
        self.app.stream_running = True

    def on_submit(self, stream_name, *args):
        on_startup_button_submit(stream_name, self)

class MainScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class StreamController(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.app.bind(on_stop=self._stop_timer)
        self.timer_flag = threading.Event()
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)

    def _stop_timer(self, *args):
        self.timer_flag.set()

    def on_toggle_button(self, *args):
        if self.app._modifier_down():
            if self.app.stream_running == True:
                self.app.auto_contro.end_stream()
                self.app.stream_running = False
            else:
                self.app.auto_contro.go_live()
                self.app.stream_running = True

    def on_key_up(self, *args):
        if not self.app._modifier_down():
            self.ids.go_live_button.background_color = [.2, 0, 0, .5]

    def on_key_down(self, *args):
        if self.app.settings.hotkeys.kivy.modifier in args[-1]:
            if self.app.stream_running == True:
                self.ids.go_live_button.background_color = [1, 0, 0, 1]
            else:
                self.ids.go_live_button.background_color = [0, 1, 0, 1]
        else:
            self.ids.go_live_button.background_color = [.2, 0, 0, .5]

class SceneController(AnchorLayout):
    
    on = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_run = threading.Event()
        self.current_scene = "camera"
        if True == False:
            self.app = GuiApp()
        self.app = App.get_running_app()
        self._startup()
        
    @threaded
    def _startup(self):
        time.sleep(2)
        self.auto_contro = AutomationController(self.app.settings)
        self.app.bind(on_stop=self._stop_timer)
        self.start_hotkeys()
        self.timer_start_time = time.time()
        self.timer_length = self.app.settings.kivy.scene_timer_time
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
                    self.timer_left = round(end_time - time.time(), 1)
                    if self.timer_left >= 0:
                        self.ids.TimerLabel.text = str(self.timer_left)
                    else:
                        self.timer_run_out()
                else:
                    time.sleep(.3)
            except KeyboardInterrupt:
                return
            time.sleep(.1)

    def timer_run_out(self):
        self.on_hotkey("camera")

    def start_hotkeys(self):
        # Camera Hotkey
        keyboard.hook_key(self.app.settings.hotkeys.obs.camera_scene_hotkey[0], 
            lambda x:self.on_hotkey("camera", x), suppress=True)
        Logger.info(f"binding hotkey {self.app.settings.hotkeys.obs.camera_scene_hotkey[0]}")
        # Center Scene Hotkey
        keyboard.hook_key(self.app.settings.hotkeys.obs.center_screen_hotkey[0],
            lambda x:self.on_hotkey("center", x), suppress=True)
        Logger.info(f"binding hotkey {self.app.settings.hotkeys.obs.center_screen_hotkey[0]}")
        # Automatic Checkbox Hotkey
        #keyboard.hook_key(self.app.settings.hotkeys.kivy.scene_lock,
        #    lambda x:self.on_hotkey("scene_lock", x), suppress=True)
        Logger.info(f"binding hotkey {self.app.settings.hotkeys.kivy.scene_lock}")
        # Next Button for the clicker
        keyboard.hook_key(self.app.settings.hotkeys.general.clicker_forward,
            lambda x:self.on_hotkey("clicker_next", x), suppress=True)
        Logger.info(f"binding hotkey {self.app.settings.hotkeys.general.clicker_forward}")
        # Previous Button for the clicker
        keyboard.hook_key(self.app.settings.hotkeys.general.clicker_backward,
            lambda x:self.on_hotkey("clicker_prev", x), suppress=True)
        Logger.info(f"binding hotkey {self.app.settings.hotkeys.general.clicker_backward}")

    def on_hotkey(self, *hotkey):    
        event = hotkey[-1]  
        print(f"The hotkey event was: {event}")  
        hotkey = "".join(hotkey[:-1])
        Logger.debug(f"hotkey {hotkey} caught")
        if hotkey == "camera":
            self._do_fake_press_camera()
        elif hotkey == "center":
            self._do_fake_press_center()
        elif hotkey == "scene_lock":
            self.ids.SCQAutomatic.ids.cb._do_press()
        elif hotkey == "clicker_next":
            self.app.auto_contro.propre_send("next")
            time.sleep(.2)
            self._do_fake_press_center()
        elif hotkey == "clicker_prev":
            self.app.auto_contro.propre_send("prev")
            time.sleep(.2)
            self._do_fake_press_center()

    def _do_fake_press_camera(self):
        if self.ids.live_camera.ids.cb.active == True:
            Logger.info(f"doing fake press camera, with button selected")
            self.on_camera()
        else:
            Logger.info(f"doing fake press camera, without button selected")
            self.ids.live_camera.ids.cb._do_press()

    def _do_fake_press_center(self):
        if self.ids.center_screen.ids.cb.active == True:
            Logger.info(f"doing fake press center, with button selected")
            self.on_center_screen()
        else:
            Logger.info(f"doing fake press center, without button selected")
            self.ids.center_screen.ids.cb._do_press()
            
    def on_camera(self, *args):
        if self.current_scene != "camera":
            Logger.info(f"on_camera called with camera not selected")
            self.current_scene = "camera"
            self.auto_contro.obs_send("camera")
            self.zero_timer()

    def on_center_screen(self, *args):
        if self.current_scene != "center":
            Logger.info(f"on_center_screen called with center not selected")
            self.current_scene = "center"
            self.auto_contro.obs_send("center")
        self.on_auto()

    def on_auto(self, *args):
        state = self.ids.SCQAutomatic.ids.cb.active
        if state == False:
            Logger.info(f"on_auto called while inactive")
            self.zero_timer()
        else:
            Logger.info(f"on_auto called while active")
            if self.ids.center_screen.ids.cb.active == True:
                Logger.info(f"on_auto reseting timer")
                self.reset_timer()

class GuiApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Settings()
        self.auto_contro = AutomationController(self.settings)
        self.stream_running = False
    
    def _modifier_down(self):
        return keyboard.is_pressed(self.settings.hotkeys.kivy.modifier)

    def build(self):
        self.icon = str(pathlib2.Path(os.path.abspath(__file__)).parent / "resources"/"gear_icon.ico")
        print(self.icon)
        return Controller()

if __name__ == "__main__":
    app = GuiApp()
    app.run()