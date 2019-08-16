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
    
from utils import Settings
from dialogs import WarningPopup
if True == False:
    from kivy_based.utils import Settings
    from kivy_based.dialogs import WarningPopup

def threaded(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def with_popup(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.popup == False:
            return
    return wrapper

class Setup:
        
    def __init__(self, popup:WarningPopup, stream_title:str, *args, **kwargs):
        self.popup = popup
        self.stream_title = stream_title
        self.settings = Settings()
        self.platform_settings = self.settings[f"setup_{settings['streaming_service']}"]

    def del_popup(self):
        self.popup = False

    def set_popup(self, popup):
        self.popup = popup

    def open_url(self, url, timer_time):
        self.popup.set_task("Opening Browser", timer_time)
        webbrowser.open(url)
 
    @with_popup
    @threaded
    def sleep(self, time_to_sleep):
        time.sleep(time_to_sleep)

    @with_popup
    @threaded
    def mouse_click(self, mouse_pos:tuple, timer_time):
        self.popup.set_task("Moving & Clicking Mouse", timer_time)
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click

    @with_popup
    @threaded
    def write(self, text:str, timer_time):
        self.popup.set_task("Entering Text", timer_time)
        keyboard.write(text)
    
    @threaded
    def go_live(self):
        mouse_pos = self.settings[f"setup_{settings['streaming_service']}"].go_live
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()

if __name__ == "__main__":
    setup_facebook("it'sa supera coolera")