import keyboard
import pathlib
import logging
import mouse
import os
import subprocess
import time
import threading

from utils import threaded, open_program

logger = logging.getLogger(__name__)


class AutomationController:
    def __init__(self, MasterApp, default_browser="CHROME", debug=False):
        if debug:
            self.__getattribute__ = self.defanged
        else:
            self.ahk_files_path = pathlib.Path(".").parent / "ahk_scripts"
            self.MasterApp = MasterApp
            self.sett = self.MasterApp.settings
            self.platform_settings = self.sett[f"setup_" +
                                               f"{self.sett.streaming_service}"]
            self.toggle_sound(not self.sett.general["music_default_state-on"])
            assert os.path.exists(str(self.ahk_files_path / "window_activator.exe")), "missing required file: " \
                                                                                      "window_activator.exe "
            assert os.path.exists(str(self.ahk_files_path / "music_toggle.exe")), "missing required file: " \
                                                                                  "music_toggle.exe "

    def defanged(self):
        return True

    def give_window_focus(self, window_to_focus):
        if window_to_focus.lower() == "propresenter":
            logger.debug("WindowController: Changing active" +
                         " window to ProPresenter")
            subprocess.call([str(self.ahk_files_path / "window_activator.exe"),
                             self.sett.windows.propresenter_re])
            time.sleep(.1)
        elif window_to_focus.lower() == "obs":
            logger.debug("WindowController: Changing active window to OBS")
            subprocess.call([str(self.ahk_files_path / "window_activator.exe"),
                             self.sett.windows.obs_re])
            time.sleep(.1)
        elif window_to_focus.lower() == "chrome":
            logger.debug("WindowController: Changing active window to Chrome")
            subprocess.call([str(self.ahk_files_path / "window_activator.exe"),
                             self.sett.windows.chrome_re])
            time.sleep(.1)

    @threaded
    def toggle_sound(self, turn_up=True):
        if turn_up:
            # the second argument (1 or 0) determines whether the volume is going up or down.
            # 1 is up, 0 is down
            subprocess.call([str(self.ahk_files_path / "music_toggle.exe"),
                             '1', f"{self.sett.general.music_fade_time}"])
        else:
            subprocess.call([str(self.ahk_files_path / "music_toggle.exe"),
                             '0', f"{self.sett.general.music_fade_time}"])
                
    @threaded
    def toggle_media_pause_play_global(self):
        logger.debug("trying to toggle media in dopamine")
        subprocess.call([str(self.ahk_files_path / "pause_play_global.exe")])
        time.sleep(.1)
        self.give_window_focus("propresenter")


    def obs_send(self, scene: str):
        """Change the current obs scene

        Arguments:
            scene {str} -- specify which scene to switch to \n one of "camera", "screen", and "augmented"
            or "start" or "stop" or "mute" or "unmute"
        """
        logger.debug(f"Sending {scene}'s hotkey to obs")

        self.give_window_focus("obs")
        time.sleep(.4)

        hotkey_dict = {
            "start": self.sett.hotkeys.obs.start_stream,
            "stop": self.sett.hotkeys.obs.stop_stream,
            "Camera_None": self.sett.hotkeys.obs.camera_scene_hotkey,
            "Screen_None": self.sett.hotkeys.obs.screen_scene_hotkey,
            "camera_scene_augmented": self.sett.hotkeys.obs.camera_scene_augmented,
            "mute": self.sett.hotkeys.obs.mute_stream,
            "unmute": self.sett.hotkeys.obs.unmute_stream,
            "Camera_Top_Right": self.sett.hotkeys.obs.Camera_Top_Right,
            "Camera_Bottom_Right": self.sett.hotkeys.obs.Camera_Bottom_Right,
            "Camera_Bottom_Left": self.sett.hotkeys.obs.Camera_Bottom_Left,
            "Screen_Top_Right": self.sett.hotkeys.obs.Screen_Top_Right,
            "Screen_Bottom_Right": self.sett.hotkeys.obs.Screen_Bottom_Right,
        }

        hotkey = hotkey_dict.get(scene, "Failure")

        if hotkey == "Failure":
            logger.debug(f"Unable to find hotkey for: '{scene}'")
            return

        logger.debug(f"Sending to obs: '{hotkey}'")
        keyboard.send(hotkey)
        self.give_window_focus("propresenter")

    def propre_send(self, hotkey):
        self.give_window_focus("propresenter")

        if hotkey.lower() == "next":
            hotkey = self.sett.hotkeys.general.clicker_forward
        elif hotkey.lower() == "prev":
            hotkey = self.sett.hotkeys.general.clicker_backward

        logger.debug(f"Sending {hotkey} to ProPresenter")
        keyboard.send(hotkey)
        time.sleep(.2)

    @threaded
    def go_live(self):
        logger.debug("Going Live")
        self.give_window_focus("chrome")
        time.sleep(1)
        mouse_pos = self.sett["go_live"]
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()
        time.sleep(.5)
        self.give_window_focus("propresenter")

    @threaded
    def end_stream(self):
        self.obs_send("stop")
        logger.debug("stopping the stream")
