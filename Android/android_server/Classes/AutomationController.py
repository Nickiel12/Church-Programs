import enum
import keyboard
import pathlib
import logging
import mouse
import os
import subprocess
import time

from win32gui import GetWindowText, GetForegroundWindow
from utils import threaded

from Classes.StreamEvents import StreamEvents as SE
from Classes.SubScenes import SubScenes as SS

logger = logging.getLogger("Main." + __name__)


class AutomationController:
    class Windows(enum.Enum):
        PROPRESENTER = enum.auto()
        OBS = enum.auto()
        CHROME = enum.auto()

    SCREEN_SWITCH_DELAY_LENGTH = 0
    OBS_SWITCH_DELAY_LENGTH = 0

    def __init__(self, MasterApp, default_browser=Windows.CHROME, debug=False):
        if debug:
            self.__getattribute__ = self.defanged
        else:
            self.ahk_files_path = pathlib.Path(".").parent / "ahk_scripts"
            self.MasterApp = MasterApp
            self.sett = self.MasterApp.settings

            self.SCREEN_SWITCH_DELAY_LENGTH = self.sett["general"]["windows_change_delay_length"]
            self.OBS_SWITCH_DELAY_LENGTH = self.sett["general"]["obs_screen_switch_delay_length"]
            self.PROPRESENTER_SEND_DELAY = self.sett["general"]["propresenter_send_delay"]

            self.platform_settings = self.sett[f"setup_" +
                                               f"{self.sett['streaming_service']}"]
            self.toggle_sound(SE.MEDIA_VOLUME_UP if self.MasterApp.States.sound_on else SE.MEDIA_VOLUME_DOWN)
            assert os.path.exists(str(self.ahk_files_path / "window_activator.exe")), "missing required file: " \
                                                                                      "window_activator.exe "
            assert os.path.exists(str(self.ahk_files_path / "music_toggle.exe")), "missing required file: " \
                                                                                  "music_toggle.exe "

    def defanged(self):
        return True

    def give_window_focus(self, window_to_focus):
        if window_to_focus == self.Windows.PROPRESENTER:
            logger.debug("WindowController: Changing active" +
                         " window to ProPresenter")
            subprocess.call([str(self.ahk_files_path / "window_activator.exe"),
                             self.sett['windows']['propresenter_re']])
        elif window_to_focus == self.Windows.OBS:
            logger.debug("WindowController: Changing active window to OBS")
            subprocess.call([str(self.ahk_files_path / "window_activator.exe"),
                             self.sett['windows']['obs_re']])
        elif window_to_focus == self.Windows.CHROME:
            logger.debug("WindowController: Changing active window to Chrome")
            subprocess.call([str(self.ahk_files_path / "window_activator.exe"),
                             self.sett['windows']['chrome_re']])
        else:
            logger.warning(f"AutomationController.give_window_focus received an unknown windows_to_focus: {window_to_focus}")
            return
        time.sleep(self.SCREEN_SWITCH_DELAY_LENGTH)

    @threaded
    def toggle_sound(self, turn_up=SE.MEDIA_VOLUME_UP):
        logger.info(f"toggle sound with {turn_up}")
        if turn_up == SE.MEDIA_VOLUME_UP:
            # the second argument (1 or 0) determines whether the volume is going up or down.
            # 1 is up, 0 is down
            subprocess.call([str(self.ahk_files_path / "music_toggle.exe"),
                             '1', f"{self.sett['general']['music_fade_time']}"])
        elif turn_up == SE.MEDIA_VOLUME_DOWN:
            subprocess.call([str(self.ahk_files_path / "music_toggle.exe"),
                             '0', f"{self.sett['general']['music_fade_time']}"])
        else:
            logger.critical(f"Toggle Sound received a non-flag argument!")

    @threaded
    def toggle_media_pause_play_global(self):
        logger.info("trying to toggle media in dopamine")
        subprocess.call([str(self.ahk_files_path / "pause_play_global.exe")])
        time.sleep(.05)
        self.give_window_focus(self.Windows.PROPRESENTER)

    def obs_send(self, scene):
        """Change the current obs scene

        Arguments:
            scene {str} -- specify which scene to switch to \n one of "camera", "screen", and "augmented"
            or "start" or "stop" or "mute" or "unmute"
        """
        logger.debug(f"Sending {scene}'s hotkey to obs")

        self.give_window_focus(self.Windows.OBS)
        time.sleep(self.OBS_SWITCH_DELAY_LENGTH)

        hotkey_dict = {
            SE.START_STREAM: self.sett["hotkeys"]["obs"]["start_stream"],
            SE.STOP_STREAM: self.sett["hotkeys"]["obs"]["stop_stream"],
            SS.Camera.CAMERA_NONE: self.sett["hotkeys"]["obs"]["camera_scene_hotkey"],
            SS.Camera.CAMERA_TOP_RIGHT: self.sett["hotkeys"]["obs"]["Camera_Top_Right"],
            SS.Camera.CAMERA_BOTTOM_RIGHT: self.sett["hotkeys"]["obs"]["Camera_Bottom_Right"],
            SS.Camera.CAMERA_BOTTOM_LEFT: self.sett["hotkeys"]["obs"]["Camera_Bottom_Left"],
            SS.Screen.SCREEN_NONE: self.sett["hotkeys"]["obs"]["screen_scene_hotkey"],
            SS.Screen.SCREEN_TOP_RIGHT: self.sett["hotkeys"]["obs"]["Screen_Top_Right"],
            SS.Screen.SCREEN_BOTTOM_RIGHT: self.sett["hotkeys"]["obs"]["Screen_Bottom_Right"],
            SS.AUGMENTED: self.sett["hotkeys"]["obs"]["camera_scene_augmented"],
            SE.OBS_MUTE: self.sett["hotkeys"]["obs"]["mute_stream"],
            SE.OBS_UNMUTE: self.sett["hotkeys"]["obs"]["unmute_stream"],
        }

        hotkey = hotkey_dict.get(scene, "Failure")

        if hotkey == "Failure":
            logger.critical(f"Unable to find hotkey for: '{scene}'")
            return

        logger.debug(f"Sending to obs: '{hotkey}'")
        keyboard.send(hotkey)
        self.give_window_focus(self.Windows.PROPRESENTER)

    def propre_send(self, hotkey):
        if self.sett['windows']['propresenter_re'] not in GetWindowText(GetForegroundWindow()):
            self.give_window_focus(self.Windows.PROPRESENTER)

            if hotkey == SE.NEXT_SLIDE:
                hotkey = self.sett["hotkeys"]["general"]["clicker_forward"]
            elif hotkey == SE.PREV_SLIDE:
                hotkey = self.sett["hotkeys"]["general"]["clicker_backward"]

            logger.debug(f"Sending {hotkey} to ProPresenter")
            keyboard.send(hotkey)
        time.sleep(self.PROPRESENTER_SEND_DELAY)

    def start_hotkeys(self):
        obs_settings = self.sett["hotkeys"]["obs"]
        general_settings = self.sett["hotkeys"]["general"]
        """ 
        # Camera Hotkey
        keyboard.hook_key(obs_settings.camera_scene_hotkey[0],
                          lambda x: self.handle_state_change("camera"), suppress=True)
        logger.info("binding hotkey " +
                    f"{obs_settings.camera_scene_hotkey[0]}")

        # screen Scene Hotkey
        keyboard.hook_key(obs_settings.screen_scene_hotkey[0],
                          lambda x: self.handle_state_change("screen"), suppress=True)
        logger.info("binding hotkey" +
                    f" {obs_settings.screen_scene_hotkey[0]}")
        """
        # Next Button for the clicker
        keyboard.on_release_key(general_settings["clicker_forward"],
                                lambda x: self.MasterApp.event_handler.handle_state_change(SE.NEXT_SLIDE),
                                suppress=True)
        logger.info(f"binding hotkey {general_settings['clicker_forward']}")
        # Previous Button for the clicker
        keyboard.on_release_key(general_settings["clicker_backward"],
                                lambda x: self.MasterApp.event_handler.handle_state_change(SE.PREV_SLIDE),
                                suppress=True)
        logger.info("binding hotkey " +
                    f"{general_settings['clicker_backward']}")

    @threaded
    def go_live(self):
        logger.info("Going Live")
        self.give_window_focus(self.Windows.CHROME)
        time.sleep(1)
        mouse_pos = self.sett["go_live"]
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()
        time.sleep(.5)
        self.give_window_focus(self.Windows.PROPRESENTER)

    @threaded
    def end_stream(self):
        self.obs_send(SE.STOP_STREAM)
        logger.info("stopping the stream")
