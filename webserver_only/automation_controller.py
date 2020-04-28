import keyboard
import pathlib
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
from utils import threaded, open_program




class AutomationController:
    def __init__(self, settings, default_browser="CHROME"):
        self.ahk_files_path = pathlib.Path(os.path.abspath(__file__)
                                           ).parent/"ahk_scripts"
        self.app = App.get_running_app()
        self.sett = self.app.settings
        self.platform_settings = self.sett[f"setup_" +
                                           f"{self.sett.streaming_service}"]
        self.sound_on = not self.sett.general["music_default_state-on"]
        self.toggle_sound()

    def give_window_focus(self, window_to_focus):
        if window_to_focus.lower() == "propresenter":
            Logger.debug("WindowController: Changing active" +
                         " window to ProPresenter")
            subprocess.call([str(self.ahk_files_path/"window_activator.exe"),
                             self.sett.windows.propresenter_re])
            time.sleep(.1)
        elif window_to_focus.lower() == "obs":
            Logger.debug("WindowController: Changing active window to OBS")
            subprocess.call([str(self.ahk_files_path/"window_activator.exe"),
                             self.sett.windows.obs_re])
            time.sleep(.1)
        elif window_to_focus.lower() == "chrome":
            Logger.debug("WindowController: Changing active window to Chrome")
            subprocess.call([str(self.ahk_files_path/"window_activator.exe"),
                             self.sett.windows.chrome_re])
            time.sleep(.1)

    @threaded
    def toggle_sound(self):
        self.sound_on = not self.sound_on
        if self.sound_on:
            # False is for the endpoint of the toggle.
            subprocess.call([str(self.ahk_files_path/"music_toggle.exe"),
                             '1', f"{self.sett.general.music_fade_time}"])
        else:
            subprocess.call([str(self.ahk_files_path/"music_toggle.exe"),
                             '0', f"{self.sett.general.music_fade_time}"])

    def get_sound_state(self) -> bool:
        return self.sound_on

    def obs_send(self, scene):
        """Change the current obs scene

        Arguments:
            scene {str} -- specify which scene to switch to \n either "camera" or "center" \n or "start" or "stop"
        """
        Logger.debug(f"Sending {scene}'s hotkey to obs")
        if scene == "camera":
            self.give_window_focus("obs")
            time.sleep(.5)
            keyboard.send(self.sett.hotkeys.obs.camera_scene_hotkey[1])
            Logger.debug(f"Sending to obs: " +
                         f"{self.sett.hotkeys.obs.camera_scene_hotkey[1]}")
        elif scene == "center":
            self.give_window_focus("obs")
            time.sleep(.5)
            keyboard.send(self.sett.hotkeys.obs.center_screen_hotkey[1])
            Logger.debug(f"Sending to obs: " +
                         f"{self.sett.hotkeys.obs.center_screen_hotkey[1]}")
        elif scene == "start":
            self.give_window_focus("obs")
            time.sleep(.5)
            keyboard.send(self.sett.hotkeys.obs.start_stream)
            Logger.debug(f"Sending to obs: " +
                         f"{self.sett.hotkeys.obs.start_stream}")
        elif scene == "stop":
            self.give_window_focus("obs")
            time.sleep(.5)
            keyboard.send(self.sett.hotkeys.obs.stop_stream)
            Logger.debug(f"Sending to obs: " +
                         f"{self.sett.hotkeys.obs.stop_stream}")
        elif scene == "center_augmented":
            self.give_window_focus("obs")
            time.sleep(.5)
            keyboard.send(self.sett.hotkeys.obs.center_augmented[1])
            Logger.debug
            print(f"Sending to obs: " +
                  f"{self.sett.hotkeys.obs.center_augmented[1]}")
        self.give_window_focus("propresenter")

    def propre_send(self, hotkey):
        print(str(self.sett.hotkeys.general.clicker_forward))
        if hotkey.lower() == "next":
            self.give_window_focus("propresenter")
            keyboard.send(self.sett.hotkeys.general.clicker_forward)
            Logger.debug(f"Sending to propresenter: " +
                         f"{self.sett.hotkeys.general.clicker_forward}")
            time.sleep(.2)
        elif hotkey.lower() == "prev":
            self.give_window_focus("propresenter")
            keyboard.send(self.sett.hotkeys.general.clicker_backward)
            Logger.debug(f"Sending to propresenter: " +
                         f"{self.sett.hotkeys.general.clicker_backward}")
            time.sleep(.2)

    @threaded
    def go_live(self):
        self.give_window_focus("chrome")
        time.sleep(1)
        print(self.platform_settings)
        mouse_pos = self.sett["go_live"]
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()
        Logger.debug("clicking the facebook go_live button in chrome")
        time.sleep(.5)
        self.give_window_focus("propresenter")

    @threaded
    def end_stream(self):
        self.give_window_focus("chrome")
        time.sleep(.2)
        mouse_pos = self.platform_settings["go_live"]
        time.sleep(.1)
        mouse.move(mouse_pos[0], mouse_pos[1])
        time.sleep(.5)
        mouse.click()
        time.sleep(.2)
        self.obs_send("stop")
        Logger.debug("stopping the stream")


if __name__ == "__main__":
    auto_contro = AutomationController(Settings())
    keyboard.wait("esc")
    auto_contro.give_window_focus("obs")
