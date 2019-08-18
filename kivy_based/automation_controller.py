import pyautogui
import keyboard
from kivy.app import App
import mouse
import time
import threading
import webbrowser
from functools import wraps
import logging
from logging import debug
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,
    format= '%(asctime)s - %(levelname)s - %(message)s')
    
from exceptions import PopupNotExist 
from dialogs import WarningPopup
from utils import Settings, threaded
if True == False:
    from kivy_based.utils import Settings, threaded
    from kivy_based.dialogs import WarningPopup
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
        self.sett = settings
        self.app = App.get_running_app()
# TODO
    def give_window_focus(self, window_to_focus):
        pass 
    #pip install pywinauto
    #from pywinauto.findwindows import find_window
    #from pywinauto.win32functions import SetForegroundWindow
    #old = ??Get Foreground Window??
    #if window_to_focues == "OBS":
    #   SetForgroundWindow(find_window(title = #?"taskeng.exe"))
    #   return old
    #elif window_to_focus == "CHROME":
    #   Set for ground...
    #   return old
    #elif window_to_focus == "PROPRESENTER":
    #   Set for ground...
    #   return old
    #else:
    # Set forground(window_to_focus)

    def obs_scene(self, scene):
        """Change the current obs scene
        
        Arguments:
            scene {str} -- specify which scene to switch to \n either "camera" or "center
        """
        if scene == "camera":
            current = self.give_window_focus("OBS")
            time.sleep(.2)
            keyboard.write(self.sett.hotkeys.obs.camera_scene_hotkey[1])
            self.give_window_focus(current)
        elif scene == "center":
            current = self.give_window_focus("OBS")
            time.sleep(.2)
            keyboard.write(self.sett.hotkeys.obs.center_screen_hotkey[1])
            self.give_window_focus(current)

class Setup:
    def __init__(self, popup:WarningPopup, stream_title:str, *args, **kwargs):
        self.popup = popup
        self.stream_title = stream_title
        self.settings = Settings()
        self.platform_settings = self.settings[f"setup_{self.settings['streaming_service']}"]

    def del_popup(self):
        self.popup = False

    def set_popup(self, popup):
        self.popup = popup

    def open_url(self, url, timer_time):
        print(f"Opening {url}")
        self.popup.set_task("Opening Browser", timer_time)
        webbrowser.open(url)
 
    @with_popup
    @threaded
    def sleep(self, time_to_sleep):
        print(f"setup is sleeping for {time_to_sleep}")
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
    
    @threaded
    def go_live(self):
        mouse_pos = self.platform_settings.go_live
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()

if __name__ == "__main__":
    Controller(Settings())
    keyboard.wait("ESC")