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
import socket

from Classes.Exceptions import PopupError, PrematureExit, PopupNotExist
from Classes.States import States
from Classes.Timer import Timer
from Classes.Popups import WarningPopup, Question
from Classes.EventHandler import EventHandler
from utils import threaded, Setup, make_functions
from Classes.AutomationController import AutomationController
from Classes.SocketHandler import SocketHandler
from Classes.MessageHandler import handle_message
from Classes.StreamEvents import StreamEvents as SE
from Classes.SubScenes import SubScenes as SS

import logging

logger = logging.getLogger("Main." + __name__)


class MasterController:
    OPTIONS_FILE_PATH = pathlib.Path(".").parent / "extras" / "options.json"
    settings = None

    def __init__(self):
        opts, args = getopt.getopt(argv[1:], "t")
        self.in_debug_mode = False
        for opt, val in opts:
            if opt in ["-t"]:
                self.in_debug_mode = True
                logger.warning("\nIn Debugging mode!!! Certain behavior disabled!!!\n")

        self.socket_handler = SocketHandler(socket.gethostbyname(socket.gethostname()), 5000)

        self.update_settings()
        self.States = States(stream_running=False,
                             stream_is_setup=False,
                             stream_title="",
                             stream_is_muted=False,
                             change_with_clicker=True,
                             augmented=False,
                             auto_change_to_camera=True,
                             current_scene=SE.CAMERA_SCENE,
                             current_camera_sub_scene=SS.Camera.CAMERA_NONE,
                             current_screen_sub_scene=SS.Screen.SCREEN_NONE,
                             timer_text="0.0",
                             timer_length=self.settings["general"]["default_timer_length"],
                             timer_not_running=False,
                             timer_kill=threading.Event(),
                             sound_on=self.settings['general']["music_default_state-on"],
                             callback=self.on_update,
                             )
        atexit.register(self.States.timer_kill.set)
        atexit.register(self.socket_handler.close)
        ahk_files_path = pathlib.Path(".").parent / "ahk_scripts"
        assert ahk_files_path.exists(), f"There is an error! expected {str(ahk_files_path)} does not exist!"

        self.auto_contro = AutomationController(self, debug=self.in_debug_mode)
        if not self.in_debug_mode:
            # Dark grey magic. Phoosh! Be amazed!
            for name, value in self.settings['startup'].items():
                if name[:4] == "open" and value:
                    program = name[5:]
                    logger.debug(f"Setup program trying to open is {program}")
                    program_path = self.settings['startup'][str(program) + "_path"]
                    subprocess.call([str(ahk_files_path / "program_opener.exe"),
                                     f".*{program}.*", program_path])
            self.auto_contro.start_hotkeys()
        self.Timer = Timer(self.States.timer_length)
        self.register_timer_events()
        self.event_handler = EventHandler(self)
        self.socket_handler.register_message_handler(partial(handle_message,
                                                             message_handler=self.event_handler.handle_state_change))

    def stop(self):
        self.socket_handler.close()
        self.Timer.kill_timer()

    def update_settings(self):
        tmp_settings = None
        if self.settings is not None:
            tmp_settings = copy.deepcopy(self.settings)
        try:
            with open(str(self.OPTIONS_FILE_PATH)) as f:
                json_file = json.load(f)

            settings_dictionary = json_file

            path = self.OPTIONS_FILE_PATH.parent / "options" / str(settings_dictionary['streaming_service'] + ".json")

            with open(path) as f:
                json_file_2 = json.load(f)

            settings_dictionary["setup_" +
                                settings_dictionary['streaming_service']] = json_file_2

            self.settings = settings_dictionary

            logger.info("Successfully updated settings from file")
        except json.JSONDecodeError as e:
            logger.warning("Loading settings from file failed")
            logger.error(e)
            if tmp_settings is not None:
                self.settings = tmp_settings
            else:
                logger.error("loading the settings has failed")
                raise e

    @threaded
    def on_update(self, var_name, value):
        if var_name != "timer_text":
            logger.info(f"{var_name} was changed")
        if var_name == "change_with_clicker":
            # only legit use?
            self.check_auto()
        if var_name != "callback":
            self.socket_handler.send_all(json.dumps({"states": [var_name, value]}))

    @threaded
    def update_all(self):
        send_on_update = [
            # "stream_running",
            # "stream_is_setup",
            # "stream_title",
            "stream_is_muted",
            "change_with_clicker",
            "augmented",
            "auto_change_to_camera",
            "current_scene",
            "current_camera_sub_scene",
            "current_screen_sub_scene",
            "timer_text",
            "timer_not_running",
            "sound_on",
            "timer_length",
        ]
        for i in send_on_update:
            self.socket_handler.send_all(json.dumps({"states": [i, self.States.__getattribute__(i)]}))

    def set_scene_camera(self, change_sub_scene=False):
        if self.States.current_scene == SE.AUGMENTED_SCENE:
            self.States.change_with_clicker = True

        logger.info(f"changing scene to camera")
        if not self.in_debug_mode:
            self.auto_contro.obs_send(self.States.current_camera_sub_scene)

        # If we are not only changing the sub scene, ensure these are correct
        if not change_sub_scene:
            self.States.current_scene = SE.CAMERA_SCENE
            self.Timer.stop_timer()

    def set_scene_screen(self, change_sub_scene=False):
        if self.States.current_scene == SE.AUGMENTED_SCENE:
            self.States.change_with_clicker = True

        logger.info(f"changing scene to screen")
        if not self.in_debug_mode:
            self.auto_contro.obs_send(self.States.current_screen_sub_scene)

        # I know this could be a redundant call, but it is only one extra update
        # sent across the server, but I don't think it is redundant
        self.States.current_scene = SE.SCREEN_SCENE

        self.check_auto()

    def set_scene_augmented(self, *args):
        if self.States.current_scene != SS.AUGMENTED:
            logger.info(f"changing scene to augmented")
            self.States.change_with_clicker = False
            self.check_auto()
            self.States.current_scene = SS.AUGMENTED
            if not self.in_debug_mode:
                self.auto_contro.obs_send(SS.AUGMENTED)

    # This function is meant to be sporadically called by other updates
    # to ensure that the timer is behaving correctly
    # TODO check if this function an be safely removed
    def check_auto(self, *args):
        logger.info(f"check_auto called with automatic enable = {self.States.change_with_clicker} and" +
                    f" auto_change_to_camera = {self.States.auto_change_to_camera}")
        if not self.States.auto_change_to_camera or self.States.current_scene == SS.AUGMENTED:
            logger.info(f"pausing timer")
            self.Timer.stop_timer()
        else:
            if self.States.current_scene == SE.SCREEN_SCENE:
                logger.info(f"check_auto restarting timer")
                self.Timer.reset_timer()

    def register_timer_events(self):

        def on_timer_text_update(text: str):
            self.States.timer_text = text

        self.Timer.add_timer_callback(Timer.TimerEvents.TIMER_TEXT_UPDATE, on_timer_text_update)

        def on_timer_run_out():
            self.States.timer_not_running = True
            self.event_handler.handle_state_change(SE.CAMERA_SCENE)

        self.Timer.add_timer_callback(Timer.TimerEvents.TIMER_RUN_OUT, on_timer_run_out)

        def on_timer_start():
            self.States.timer_not_running = False

        self.Timer.add_timer_callback(Timer.TimerEvents.TIMER_START, on_timer_start)

    def setup_stream(self):
        try:
            self.States.timer_text = "unavailable"
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
            self.auto_contro.give_window_focus(self.auto_contro.Windows.PROPRESENTER)
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
            self.States.timer_text = "0.0"
