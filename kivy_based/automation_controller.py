import keyboard
from kivy.app import App
from kivy.logger import Logger
import pathlib2
import mouse
import os
import subprocess
import time
import threading
import webbrowser
from functools import wraps
from win32.win32gui import GetWindowText, GetForegroundWindow
    
from exceptions import PopupNotExist 
from dialogs import WarningPopup, Question
from utils import Settings, threaded, open_program
if True == False:
    from kivy_based.utils import Settings, threaded, open_program
    from kivy_based.dialogs import WarningPopup, Question
    from kivy_based.exceptions import PopupNotExist

def with_popup(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.popup == False:
            raise PopupNotExist
        func(self, *args, **kwargs)
    return wrapper

class AutomationController:
    def __init__(self, settings, default_browser="CHROME"):
        self.ahk_files_path = pathlib2.Path(os.path.abspath(__file__)).parent/"ahk_scripts"
        self.app = App.get_running_app()
        self.sett = self.app.settings
        self.platform_settings = self.sett[f"setup_{self.sett.streaming_service}"]
        self.sound_on = False
        self.toggle_sound()
# TODO
    def give_window_focus(self, window_to_focus):
        if window_to_focus.lower() == "propresenter":
            Logger.debug("WindowController: Changing active window to ProPresenter")
            subprocess.call([str(self.ahk_files_path/"window_opener.exe"), self.sett.windows.propresenter_re])
            time.sleep(.1)
        elif window_to_focus.lower() == "obs":
            Logger.debug("WindowController: Changing active window to OBS")
            subprocess.call([str(self.ahk_files_path/"window_opener.exe"), self.sett.windows.obs_re])
            time.sleep(.1)
        elif window_to_focus.lower() == "chrome":
            Logger.debug("WindowController: Changing active window to Chrome")
            subprocess.call([str(self.ahk_files_path/"window_opener.exe"), self.sett.windows.chrome_re])
            time.sleep(.1)

    @threaded
    def toggle_sound(self):
        if self.sound_on:
            # False is for the endpoint of the toggle.
            subprocess.call([str(self.ahk_files_path/"music_toggle.exe"), True, self.sett.general.music_fade_time])
        else:
            subprocess.call([str(self.ahk_files_path/"music_toggle.exe"), False, self.sett.general.music_fade_time])
    
    def get_sound_state(self) -> bool:
        return self.sound_on

    #@threaded
    def obs_send(self, scene):
        """Change the current obs scene
        
        Arguments:
            scene {str} -- specify which scene to switch to \n either "camera" or "center" \n or "start" or "stop"
        """
        Logger.debug(f"Sending {scene}'s hotkey to obs")
        if scene == "camera":
            self.give_window_focus("obs")
            time.sleep(.3)
            keyboard.send(self.sett.hotkeys.obs.camera_scene_hotkey[1])
            Logger.debug(f"Sending to obs: {self.sett.hotkeys.obs.camera_scene_hotkey[1]}")
        elif scene == "center":
            self.give_window_focus("obs")
            time.sleep(.3)
            keyboard.send(self.sett.hotkeys.obs.center_screen_hotkey[1])
            Logger.debug(f"Sending to obs: {self.sett.hotkeys.obs.center_screen_hotkey[1]}")
        elif scene == "start":
            self.give_window_focus("obs")
            time.sleep(.3)
            keyboard.send(self.sett.hotkeys.obs.start_stream)
            Logger.debug(f"Sending to obs: {self.sett.hotkeys.obs.start_stream}")
        elif scene == "stop":
            self.give_window_focus("obs")
            time.sleep(.3)
            keyboard.send(self.sett.hotkeys.obs.stop_stream)
            Logger.debug(f"Sending to obs: {self.sett.hotkeys.obs.stop_stream}")
        self.give_window_focus("propresenter")
    
    def propre_send(self, hotkey):
        print(str(self.sett.hotkeys.general.clicker_forward))
        if hotkey.lower() == "next":
            self.give_window_focus("propresenter")
            keyboard.send(self.sett.hotkeys.general.clicker_forward)
            Logger.debug(f"Sending to propresenter: {self.sett.hotkeys.general.clicker_forward}")
            time.sleep(.2)
        elif hotkey.lower() == "prev":
            self.give_window_focus("propresenter")
            keyboard.send(self.sett.hotkeys.general.clicker_backward)
            Logger.debug(f"Sending to propresenter: {self.sett.hotkeys.general.clicker_backward}")
            time.sleep(.2)

    @threaded
    def go_live(self):
        self.give_window_focus("chrome")
        time.sleep(.2)
        mouse_pos = self.platform_settings["go_live"]
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()
        Logger.debug("clicking the facebook go_live button in chrome")

    @threaded
    def end_stream(self):
        self.give_window_focus("chrome")
        time.sleep(.2)
        mouse_pos = self.platform_settings["go_live"]
        time.sleep(.1)
        mouse.click()
        time.sleep(.2)
        self.obs_send("stop")
        Logger.debug("stopping the stream")

class Setup:
    def __init__(self, popup:WarningPopup, stream_title:str, auto_contro:AutomationController
        , *args, **kwargs):
        self.auto_contro = auto_contro
        self.popup = popup
        self.stream_title = stream_title
        self.settings = Settings()
        self.platform_settings = self.settings[f"setup_{self.settings['streaming_service']}"]

    def del_popup(self):
        self.popup = False

    def set_popup(self, popup):
        self.popup = popup

    def open_url(self, url, timer_time):
        Logger.info(f"Opening {url}")
        self.popup.set_task("Opening Browser", timer_time)
        webbrowser.open(url)
 
    @with_popup
    @threaded
    def sleep(self, time_to_sleep):
        Logger.info(f"setup is sleeping for {time_to_sleep}")
        self.popup.set_task("Next Task In", time_to_sleep)
        time.sleep(time_to_sleep)

    @with_popup
    @threaded
    def mouse_click(self, mouse_pos:tuple, timer_time):
        self.popup.set_task("Moving & Clicking Mouse", timer_time)
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()

    @with_popup
    @threaded
    def write(self, text:str, timer_time):
        self.popup.set_task("Entering Text", timer_time)
        keyboard.write(text)
        self.auto_contro.obs_send("start")

if __name__ == "__main__":
    auto_contro = AutomationController(Settings())
    keyboard.wait("esc")
    auto_contro.give_window_focus("obs")