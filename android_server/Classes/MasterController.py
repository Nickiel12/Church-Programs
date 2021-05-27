import atexit
import copy
import keyboard
import json
import pathlib
from functools import partial
import getopt
import subprocess
from sys import argv
import time
import threading

from Classes.Exceptions import PopupError, PrematureExit, PopupNotExist
from Classes.States import States
from Classes.Timer import Timer
from Classes.Popups import WarningPopup, Question
from Classes.StateChangeHandeler import EventHandeler
from utils import DotDict, threaded, Setup, make_functions
from Classes.AutomationController import AutomationController
from Classes.SocketHandler import SocketHandler
from Classes.MessageHandler import handle_message

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("MasterController")

class MasterController:

    OPTIONS_FILE_PATH = pathlib.Path(".").parent/"extras"/"options.json"
    settings = None

    def __init__(self, socketio):
        opts, args = getopt.getopt(argv[1:], "t")
        self.in_debug_mode = False
        for opt, val in opts:
            if opt in ["-t"]:
                self.in_debug_mode = True
                logger.warning("\nIn Debugging mode!!! Certain behavior disabled!!!\n")

        self.update_settings()
        self.States = States(stream_running=False,
                             stream_is_setup=False,
                             stream_title="",
                             stream_is_muted=False,
                             automatic_enabled=True,
                             auto_change_to_camera=True,
                             current_scene="camera",
                             current_camera_sub_scene="Camera_None",
                             current_screen_sub_scene="Screen_None",
                             timer_text="0.0",
                             timer_length=15,
                             timer_paused=False,
                             timer_kill=threading.Event(),
                             sound_on=not(self.settings.general["music_default_state-on"]),
                             callback=self.on_update,
                             )
        atexit.register(self.States.timer_kill.set)
        ahk_files_path = pathlib.Path(".").parent/"ahk_scripts"

        if not self.in_debug_mode:
            for name, value in self.settings.startup.items():
                if name[:4] == "open" and value == True:
                    program = name[5:]
                    logger.debug(f"Setup program trying to open is {program}")
                    program_path = self.settings.startup[str(program)+"_path"]
                    subprocess.call([str(ahk_files_path/"program_opener.exe"),
                                    f".*{program}.*", program_path])
        if not self.in_debug_mode:
            self.start_hotkeys()
        self.auto_contro = AutomationController(self, debug = self.in_debug_mode)
        self.Timer = Timer(self)
        self.event_handeler = EventHandeler(self)

    def start(self, app):
        try:
            self.socket_handler = SocketHandler("localhost", 5000)
            self.socket_handler.register_message_handler(handle_message)
        except KeyboardInterrupt:
            self.socket_handler.close()
            self.States.timer_kill.set()

    def update_settings(self):
        have_backup = False
        if self.settings != None:
            tmp_settings = copy.deepcopy(self.settings)
            have_backup = True
        try:
            with open(str(self.OPTIONS_FILE_PATH)) as f:
                json_file = json.load(f)

            dot_dict = DotDict(json_file)

            path = self.OPTIONS_FILE_PATH.parent / "options" / \
                str(dot_dict.streaming_service + ".json")

            with open(path) as f:
                json_file_2 = json.load(f)

            dot_dict["setup_" +
                     dot_dict.streaming_service] = DotDict(json_file_2)

            self.settings = dot_dict

            logger.info("Successfully updated settings from file")
        except (json.JSONDecodeError) as e:
            logger.warning("Loading settings from file failed")
            logger.error(e)
            if have_backup:
                self.settings = tmp_settings
            else:
                logger.error("loading the settings has failed")
                raise e

    @threaded
    def on_update(self, var_name, value):
        if var_name != "timer_text":
            logger.debug(f"{var_name} was changed")
        if var_name == "automatic_enabled":
            self.check_auto()
        self.socket_handler.send_all(json.dumps({"states": [var_name, value]}))

    @threaded
    def update_page(self):
        send_on_update = [
            "automatic_enabled",
            "current_scene",
            "timer_text",
            "sound_on",
            "stream_is_muted",
            "current_camera_sub_scene",
            "current_screen_sub_scene",
        ]
        for i in send_on_update:
            self.socket_handler.send_all(json.dumps({"states":[i, self.States.__getattribute__(i)]}))

    def set_scene_camera(self, change_sub_scene = False):
        if self.States.current_scene == "augmented":
            self.States.automatic_enabled = True

        if self.States.current_scene != "camera":
            logger.debug(f"changing scene to camera")
            self.auto_contro.obs_send(self.States.current_camera_sub_scene)
            self.States.current_scene = "camera"
            self.Timer.pause_timer()
        elif change_sub_scene:
            self.auto_contro.obs_send(self.States.current_camera_sub_scene)

    def set_scene_screen(self, change_sub_scene = False):
        if self.States.current_scene == "augmented":
            self.States.automatic_enabled = True

        if self.States.current_scene != "screen":
            logger.debug(f"changing scene to screen")
            self.auto_contro.obs_send(self.States.current_screen_sub_scene)
            self.States.current_scene = "screen"
        elif change_sub_scene:
            self.auto_contro.obs_send(self.States.current_screen_sub_scene)
        self.check_auto()

    def set_scene_augmented(self, *args):
        if self.States.current_scene != "augmented":
            logger.debug(f"changing scene to augmented")
            self.States.automatic_enabled = False
            self.check_auto()
            self.States.current_scene = "augmented"
            self.auto_contro.obs_send("camera_scene_augmented")

    def check_auto(self, *args):
        logger.info(f"check_auto called with automatic enable = {self.States.automatic_enabled}")
        if (self.States.automatic_enabled == False 
            or self.States.auto_change_to_camera == False):
            logger.info(f"check_auto called while automatic_enabled is false")
            logger.info(f"pausing timer")
            self.Timer.pause_timer()
        else:
            logger.info(f"check_auto called while automatic_enabled is true")
            if self.States.current_scene == "screen":
                logger.info(f"check_auto restarting timer")
                self.Timer.reset_timer()

    def start_hotkeys(self):
        obs_settings = self.settings.hotkeys.obs
        general_settings = self.settings.hotkeys.general
        """ 
        # Camera Hotkey
        keyboard.hook_key(obs_settings.camera_scene_hotkey[0],
                          lambda x: self.handle_state_change("camera"), suppress=True)
        logger.info("binding hotkey " +
                    f"{obs_settings.camera_scene_hotkey[0]}")

        # screen Scene Hotkey
        keyboard.hook_key(obs_settings.screen_sene_hotkey[0],
                          lambda x: self.handle_state_change("screen"), suppress=True)
        logger.info("binding hotkey" +
                    f" {obs_settings.screen_sene_hotkey[0]}")
        """
        # Next Button for the clicker
        keyboard.on_release_key(general_settings.clicker_forward,
                                lambda x: self.handle_state_change("clicker_next"),
                                suppress=True)
        logger.info(f"binding hotkey {general_settings.clicker_forward}")
        # Previous Button for the clicker
        keyboard.on_release_key(general_settings.clicker_backward,
                                lambda x: self.handle_state_change("clicker_prev"),
                                suppress=True)
        logger.info("binding hotkey " +
                    f"{general_settings.clicker_backward}")

    def handle_state_change(self, *args):
        self.event_handeler.handle_state_change(*args)

    def setup_stream(self):
        try:
            self.Timer.timer_unavailable()
            popup = WarningPopup()
            popup.open()
            
            setup = Setup(popup, self)
            settings = make_functions(setup)
            for i in settings:
                try:
                    if popup.timer_event.is_set():
                        raise PrematureExit("Timer caught event set")
                    i[0]()
                    time.sleep(i[1])
                except KeyboardInterrupt:
                    raise PrematureExit("Keyboard Inturrupt caught in sleep_check")
            self.auto_contro.give_window_focus("propresenter")
            setup.del_popup()
            self.States.stream_is_setup = True

        except KeyboardInterrupt:
            if popup.timer_thread and popup.timer_thread.isAlive():
                popup.timer_event.set()
        except (PopupNotExist, PrematureExit):
            logger.debug("Popup was closed unexpectedly")
            if Question("Setup was canceled before it was finished\n" +
                        "Would you like to restart setup?", "Python"):
                popup.close()
                self.setup_stream()
            else:
                logger.debug("the user said no to the question")
        finally:
            popup.close()  
            self.Timer.timer_available()
