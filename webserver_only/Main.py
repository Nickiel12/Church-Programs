import atexit
import copy
import keyboard
import json
import pathlib
import logging
import engineio.async_drivers.gevent
from gevent import monkey
import flask
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from flask_socketio import SocketIO
from functools import partial
import subprocess
import time
import threading

from Classes.Forms import SetupStreamForm, GoLiveForm
from Classes.Exceptions import PopupError, PrematureExit, PopupNotExist
from Classes.States import States
from Classes.Timer import Timer
from Classes.Popups import WarningPopup, Question
from utils import DotDict, threaded, Setup, make_functions
from Classes.AutomationController import AutomationController

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
#datefmt='%m/%d/%Y %H:%M:%S'
logger = logging.getLogger("Main")
web_logger = logging.getLogger("Main.webserver")


class MasterController:

    OPTIONS_FILE_PATH = pathlib.Path(".").parent/"extras"/"options.json"
    settings = None

    def __init__(self, socketio):
        self.socketio = socketio
        self.update_settings()
        self.States = States(stream_running=False,
                             stream_is_setup=False,
                             stream_title="",
                             stream_is_muted=False,
                             automatic_enabled=True,
                             current_scene="camera",
                             current_camera_sub_scene="Camera_None",
                             current_screen_sub_scene="Screen_None",
                             timer_text="0.0",
                             timer_paused=False,
                             timer_kill=threading.Event(),
                             sound_on=not(self.settings.general["music_default_state-on"]),
                             callback=self.on_update,
                             )
        atexit.register(self.States.timer_kill.set)
        ahk_files_path = pathlib.Path(".").parent/"ahk_scripts"

        for name, value in self.settings.startup.items():
            if name[:4] == "open" and value == True:
                program = name[5:]
                logger.debug(f"Setup program trying to open is {program}")
                program_path = self.settings.startup[str(program)+"_path"]
                subprocess.call([str(ahk_files_path/"program_opener.exe"),
                                 f".*{program}.*", program_path])
        self.start_hotkeys()
        self.auto_contro = AutomationController(self)
        self.Timer = Timer(self)

    def start(self):
        logging.getLogger('socketio').setLevel(logging.ERROR)
        logging.getLogger('engineio').setLevel(logging.ERROR)
        self.socketio.run(app, "0.0.0.0", debug=False)

    def update_settings(self):
        have_backup = False
        if self.settings != None:
            tmp_settings = copy.deepcopy(self.settings)
            have_backup = True
        try:
            with open(self.OPTIONS_FILE_PATH) as f:
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
        self.socketio.emit("update", {"data": "None",
                                 "states": [var_name, value]})

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
            self.socketio.emit("update", {"states":[i, self.States[i]]})

    def set_scene_camera(self, *args):
        if self.States.current_scene == "augmented":
            self.States.automatic_enabled = True

        if self.States.current_scene != "camera":
            logger.debug(f"changing scene to camera")
            if self.States.current_camera_sub_scene != "Camera_None":
                self.auto_contro.obs_send(self.States.current_camera_sub_scene)
            else:
                self.auto_contro.obs_send("camera")
            self.States.current_scene = "camera"
            self.Timer.pause_timer()

    def set_scene_screen(self, *args):
        if self.States.current_scene == "augmented":
            self.States.automatic_enabled = True
        if self.States.current_scene != "screen":
            logger.debug(f"changing scene to screen")
            if self.States.current_screen_sub_scene != "Screen_None":
                self.auto_contro.obs_send(self.States.current_screen_sub_scene)
            else:
                self.auto_contro.obs_send("screen")
            self.States.current_scene = "screen"
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
        if self.States.automatic_enabled == False:
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

    def handle_state_change(self, hotkey):
        sett = self.settings
        logger.debug(f"hotkey {hotkey} caught")
        if hotkey == "camera":
            self.set_scene_camera()
        elif hotkey == "screen":
            self.set_scene_screen()
        elif hotkey == "auto_lock":
            state = self.States.automatic_enabled
            self.States.automatic_enabled = not state
        elif hotkey == "clicker_next":
            self.auto_contro.propre_send("next")
            time.sleep(.2)
            if sett.general.clicker_change_scene_without_automatic:
                self.set_scene_screen()
            else:
                if self.States.automatic_enabled:
                    self.set_scene_screen()
        elif hotkey == "clicker_prev":
            self.auto_contro.propre_send("prev")
            time.sleep(.2)
            if sett.general.clicker_change_scene_without_automatic:
                self.set_scene_screen()
            else:
                if self.States.automatic_enabled:
                    self.set_scene_screen()
        elif hotkey == "toggle_camera_scene_augmented":
            if not (self.States.current_scene == "augmented"):
                self.set_scene_augmented()
            else:
                self.States.automatic_enabled = True
                self.set_scene_camera()
        elif hotkey == "muted":
            if self.States.stream_is_muted:
                self.auto_contro.obs_send("unmute")
                self.States.stream_is_muted = False
            else:
                self.auto_contro.obs_send("mute")
                self.States.stream_is_muted = True
        elif hotkey.startswith("Camera"):
            self.States.current_camera_sub_scene = hotkey
            self.set_scene_camera()
        elif hotkey.startswith("Screen"):
            self.States.current_screen_sub_scene = hotkey
            self.set_scene_screen(hotkey)
 

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


app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '$hor!K#y'
socketio = SocketIO(app, async_mode='gevent')
monkey.patch_socket()
Mobility(app)

MasterApp = MasterController(socketio=socketio)


@app.route("/")
def send_to_index():
    if MasterApp.States.stream_is_setup or MasterApp.States.stream_running:
        return flask.redirect(flask.url_for("index"))
    else:
        return flask.redirect(flask.url_for('setup_stream'))


@app.route("/index", methods=["GET", "POST"])
def index():
    return flask.render_template("index.html", state=MasterApp.States.stream_running)


@app.route("/setup_stream", methods=['GET', 'POST'])
def setup_stream():
    form = SetupStreamForm()
    if form.validate_on_submit():
        MasterApp.States.stream_title = form.stream_title.data
        MasterApp.setup_stream()
        return flask.redirect(flask.url_for('index'))
    return flask.render_template("setup_stream.html", form=form)


@app.route("/go_live", methods=["GET", "POST"])
def go_live():
    form = GoLiveForm()
    if form.validate_on_submit():
        answer = form.are_you_sure.data
        if answer == "yes":
            MasterApp.go_live()
        return flask.redirect(flask.url_for('index'))
    else:
        state = MasterApp.States.stream_running
        return flask.render_template("go_live.html", form=form, state=state)


@socketio.on("scene_camera")
def on_scene_camera(event):
    MasterApp.handle_state_change("camera")


@socketio.on("scene_screen")
def on_scene_screen(event):
    MasterApp.handle_state_change("screen")


@socketio.on("automatic_change")
def on_auto_change(event):
    MasterApp.handle_state_change("auto_lock")


@socketio.on("slide_next")
def on_slide_next(event):
    MasterApp.handle_state_change("clicker_next")


@socketio.on("slide_prev")
def on_slide_prev(event):
    MasterApp.handle_state_change("clicker_prev")


@socketio.on("volume")
def toggle_volume(event):
    MasterApp.auto_contro.toggle_sound()

@socketio.on("muted")
def toggle_muted(event):
    MasterApp.handle_state_change("muted")

@socketio.on("camera_augmented_toggle")
def on_toggle_screen(event):
    MasterApp.handle_state_change("toggle_camera_scene_augmented")

@socketio.on("special_scene")
def on_special_scene(event):
    MasterApp.handle_state_change(event["data"])

@socketio.on("new_connection")
def refresh_new_page(event):
    MasterApp.update_page()


if __name__ == "__main__":
    MasterApp.start()
