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
    def __init__(self, MasterApp, default_browser="CHROME"):
        self.ahk_files_path = pathlib.Path(".").parent/"ahk_scripts"
        self.MasterApp = MasterApp
        self.sett = self.MasterApp.settings
        self.platform_settings = self.sett[f"setup_" +
                                           f"{self.sett.streaming_service}"]
        self.sound_on = not self.sett.general["music_default_state-on"]
        self.toggle_sound()
        assert os.path.exists(str(self.ahk_files_path/"window_activator.exe"))
        assert os.path.exists(str(self.ahk_files_path/"music_toggle.exe"))

    def give_window_focus(self, window_to_focus):
        if window_to_focus.lower() == "propresenter":
            logger.debug("WindowController: Changing active" +
                         " window to ProPresenter")
            subprocess.call([str(self.ahk_files_path/"window_activator.exe"),
                             self.sett.windows.propresenter_re])
            time.sleep(.1)
        elif window_to_focus.lower() == "obs":
            logger.debug("WindowController: Changing active window to OBS")
            subprocess.call([str(self.ahk_files_path/"window_activator.exe"),
                             self.sett.windows.obs_re])
            time.sleep(.1)
        elif window_to_focus.lower() == "chrome":
            logger.debug("WindowController: Changing active window to Chrome")
            subprocess.call([str(self.ahk_files_path/"window_activator.exe"),
                             self.sett.windows.chrome_re])
            time.sleep(.1)

    @threaded
    def toggle_sound(self):
        self.sound_on = not self.sound_on
        self.MasterApp.States.sound_on = not self.sound_on
        if self.sound_on:
            # False is for the endpoint of the toggle.
            subprocess.call([str(self.ahk_files_path/"music_toggle.exe"),
                             '1', f"{self.sett.general.music_fade_time}"])
        else:
            subprocess.call([str(self.ahk_files_path/"music_toggle.exe"),
                             '0', f"{self.sett.general.music_fade_time}"])

    def get_sound_state(self) -> bool:
        return self.sound_on

    def obs_send(self, scene:str):
        """Change the current obs scene

        Arguments:
            scene {str} -- specify which scene to switch to \n one of "camera", "center", and "augmented"
            or "start" or "stop" or "mute" or "unmute"
        """
        logger.debug(f"Sending {scene}'s hotkey to obs")

        self.give_window_focus("obs")
        time.sleep(.4)
        if scene == "start":
            hotkey = self.sett.hotkeys.obs.start_stream
        elif scene == "stop":
            hotkey = self.sett.hotkeys.obs.stop_stream
        elif scene == "camera":
            hotkey = self.sett.hotkeys.obs.camera_scene_hotkey
        elif scene == "center":
            hotkey = self.sett.hotkeys.obs.screen_sene_hotkey
        elif scene == "camera_scene_augmented":
            hotkey = self.sett.hotkeys.obs.camera_scene_augmented
        elif scene == "mute":
            hotkey = self.sett.hotkeys.obs.mute_stream
        elif scene == "unmute":
            hotkey = self.sett.hotkeys.obs.unmute_stream
        elif scene.startswith("Camera") or scene.startswith("Screen"):
            try:
                hotkey = self.sett.hotkeys.obs[scene]
            except KeyError as e:
                logger.warn(f"Special Scene Not Found: {hotkey}\n {e}")
        logger.debug(f"Sending to obs: {hotkey}")
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
