from pywinauto.application import WindowSpecification
from pywinauto import Desktop
from pywinauto.findwindows import ElementNotFoundError
import keyboard
from kivy.app import App
import mouse
import time
import threading
import webbrowser
from functools import wraps
import logging
from win32.win32gui import GetWindowText, GetForegroundWindow
from logging import debug
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,
    format= '%(asctime)s - %(levelname)s - %(message)s')
    
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
        self.app = App.get_running_app()
        self.sett = self.app.settings
        self.platform_settings = self.sett[f"setup_{self.sett.streaming_service}"]
        self.obs_dlg = Desktop(backend="uia").window(title_re=self.sett.windows.obs_re)
        self.propre_dlg = Desktop(backend="uia").window(title_re=self.sett.windows.propresenter_re)
        self.chrome_dlg = Desktop(backend="uia").window(title_re=self.sett.windows.chrome_re)
# TODO
    def give_window_focus(self, window_to_focus):
        if isinstance(window_to_focus, WindowSpecification):
            window_to_focus.set_focus()
        elif window_to_focus == None:
            pass
        elif window_to_focus.lower() == "propresenter":
            old_win = Desktop(backend="uia").window(title=GetWindowText(GetForegroundWindow()))
            if not old_win.wrapper_object() == self.propre_dlg.wrapper_object():
                print("top window wasn't propresenter")
                time.sleep(.1)
                self.propre_dlg.set_focus()
                return True
            else: return False
        elif window_to_focus.lower() == "obs":
            #old_win = Desktop(backend="uia").window(title=GetWindowText(GetForegroundWindow()))
            time.sleep(.1)
            self.obs_dlg.set_focus()
        elif window_to_focus.lower() == "chrome":
            self.chrome_dlg.set_focus()
            time.sleep(.1)

    def window_not_found(self, obs=False, propresenter=False):
        if propresenter == True:
            if Question("The ProPresenter 6 window was not found,\n and it is assumed that it is not open\n"+
                    "Would you like to open it?\n(\"No\" if it is already open)", "Program Not Found", tall=True):
                    open_program("propresenter")
        if obs == True:
            if Question("The OBS window was not found,\n and it is assumed that it is not open\n\n"+
                "Would you like to open it?\n(\"No\" if it is already open)", "Program Not Found", tall=True):
                open_program('obs')

    @threaded
    def obs_send(self, scene):
        """Change the current obs scene
        
        Arguments:
            scene {str} -- specify which scene to switch to \n either "camera" or "center" \n or "start" or "stop"
        """
        try:
            if scene == "camera":
                #current = self.give_window_focus("OBS")
                self.give_window_focus("OBS")
                time.sleep(.2)
                keyboard.send(self.sett.hotkeys.obs.camera_scene_hotkey[1])
                #self.give_window_focus(current)
            elif scene == "center":
                self.give_window_focus("OBS")
                #current = self.give_window_focus("OBS")
                time.sleep(.2)
                keyboard.send(self.sett.hotkeys.obs.center_screen_hotkey[1])
                #self.give_window_focus(current)
            elif scene == "start":
                self.give_window_focus("OBS")
                #current = self.give_window_focus("OBS")
                time.sleep(.2)
                keyboard.send(self.sett.hotkeys.obs.start_stream)
                #self.give_window_focus(current)
            elif scene == "stop":
                self.give_window_focus("OBS")
                #current = self.give_window_focus("OBS")
                time.sleep(.2)
                keyboard.send(self.sett.hotkeys.obs.stop_stream)
                #self.give_window_focus(current)
        except ElementNotFoundError:
            self.window_not_found(obs=True)
        try:
            self.give_window_focus("propresenter")
        except ElementNotFoundError:
            self.window_not_found(propresenter=True)

    @threaded
    def propre_send(self, hotkey):
        try:
            if hotkey.lower() == "next":
                if self.give_window_focus("propresenter"):
                    time.sleep(.2)
                    keyboard.send(self.sett.hotkeys.general.clicker_forward)
            elif hotkey.lower() == "prev":
                if self.give_window_focus("propresenter"):
                    time.sleep(.2)
                    keyboard.send(self.sett.hotkeys.general.clicker_backward)
        except ElementNotFoundError:
            self.window_not_found(propresenter=True)
    
    @threaded
    def go_live(self):
        self.give_window_focus("chrome")
        time.sleep(.2)
        mouse_pos = self.platform_settings["go_live"]
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()

    @threaded
    def end_stream(self):
        self.give_window_focus("chrome")
        time.sleep(.2)
        mouse_pos = self.platform_settings["go_live"]
        mouse.click()
        time.sleep(.2)
        self.obs_send("stop")

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
        self.auto_contro.obs_send("start")

if __name__ == "__main__":
    Controller(Settings())
    keyboard.wait("ESC")