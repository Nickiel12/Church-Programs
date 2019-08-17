import pyautogui
import keyboard
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
from utils import Settings
if True == False:
    from kivy_based.utils import Settings
    from kivy_based.dialogs import WarningPopup
    from kivy_based.exceptions import PopupNotExist

def threaded(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        print(f"thread with target \"{func}\" has been started")
        return thread
    return wrapper

def with_popup(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.popup == False:
            raise PopupNotExist
        func(self, *args, **kwargs)
    return wrapper

class Controller:
    def __init__(self, settings, default_browser="CHROME"):
        self.sett = settings
        self.register_hotkeys()
# TODO
    def give_window_focus(self, window_to_focus):
        pass 
    #pip install pywinauto
    #from pywinauto.findwindows import find_window
    #from pywinauto.win32functions import SetForegroundWindow
    #SetForgroundWindow(find_window(title = #?"taskeng.exe"))

    def register_hotkeys(self):
        for i in self.sett.hotkeys:
            keyboard.add_hotkey(self.sett.hotkeys[i], self.on_hotkey, args=(i))

    def on_hotkey(self, *args, **kwargs):
        print("".join(args))
        
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