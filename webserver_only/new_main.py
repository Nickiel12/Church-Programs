import atexit
import copy
import eventlet
import keyboard
import json
import pathlib
import logging
import flask
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from flask_socketio import SocketIO
from functools import partial
import subprocess
import time
import threading

from forms import SetupStreamForm, GoLiveForm
from Classes.States import States
from Classes.Timer import Timer
from utils import DotDict, threaded
from automation_controller import AutomationController

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
                             stream_setup=False,
                             stream_title="",
                             automatic_enabled=False,
                             current_scene="",
                             timer_text="0.0",
                             timer_paused=False,
                             timer_kill=threading.Event(),
                             sound_on=not(self.settings.general["music_default_state-on"]),
                             callback=self.on_update,
                             )
        self.Timer = Timer(self)
        ahk_files_path = pathlib.Path(".").parent/"ahk_scripts"

        for name, value in self.settings.startup.items():
            if name[:4] == "open" and value == True:
                program = name[5:]
                logger.debug(f"Setup program trying to open is {program}")
                program_path = self.settings.startup[str(program)+"_path"]
                subprocess.call([str(ahk_files_path/"program_opener.exe"),
                                 f".*{program}.*", program_path])

        self.auto_contro = AutomationController(self)

    def start(self):
        self.socketio.run(app, "0.0.0.0", debug=False)

    def update_settings(self):
        have_backup = False
        if self.settings != None:
            tmp_settings = copy.deepcopy(self.settings)
            have_backup = True
        try:
            with open(self.OPTIONS_FILE_PATH) as file:
                json_file = json.load(file)
            dot_dict = DotDict(json_file)
            path = self.OPTIONS_FILE_PATH.parent / "options" / \
                str(dot_dict.streaming_service + ".json")
            with open(path) as file:
                json_file_2 = json.load(file)
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

    def on_update(self, var_name, value):
        logger.debug(f"{var_name} was changed")
        if var_name == "automatic_enabled":
            self.check_auto()
        self.socketio.emit("update", {"data": "None",
                                 "states": [var_name, value]})

    def set_scene_camera(self, *args):
        if self.States.current_scene != "camera":
            logger.debug(f"changing scene to camera")
            self.States.current_scene = "camera"
            self.auto_contro.obs_send("camera")
            self.Timer.zero_timer()

    def set_scene_center(self, *args):
        if self.States.current_scene != "center":
            logger.debug(f"changing scene to center")
            self.States.current_scene = "center"
            self.auto_contro.obs_send("center")
        self.check_auto()

    def set_scene_augmented(self, *args):
        if self.States.current_scene != "augmented":
            logger.debug(f"changing scene to augmented")
            self.States.automatic_enabled = False
            self.check_auto()
            self.States.current_scene = "augmented"
            self.auto_contro.obs_send("center_augmented")

    def check_auto(self, *args):
        if self.States.automatic_enabled is False:
            logger.info(f"chech_auto called while automatic_enabled is false")
            self.Timer.zero_timer()
        else:
            logger.info(f"check_auto called while automatic_enabled is true")
            if self.States.current_scene == "center":
                logger.info(f"check_auto reseting timer")
                self.Timer.reset_timer()

    def start_hotkeys(self):
        obs_settings = self.app.settings.hotkeys.obs
        kivy_settings = self.app.settings.hotkeys.kivy
        general_settings = self.app.settings.hotkeys.general

        # Camera Hotkey
        keyboard.hook_key(obs_settings.camera_scene_hotkey[0],
                          lambda x: self.on_hotkey("camera", x), suppress=True)
        logger.info("binding hotkey " +
                    f"{obs_settings.camera_scene_hotkey[0]}")

        # Center Scene Hotkey
        keyboard.hook_key(obs_settings.center_screen_hotkey[0],
                          lambda x: self.on_hotkey("center", x), suppress=True)
        logger.info("binding hotkey" +
                    f" {obs_settings.center_screen_hotkey[0]}")

        """
        # Automatic Checkbox Hotkey
        keyboard.add_hotkey(kivy_settings.automatic_toggle,
                            lambda x: self.on_hotkey("automatic_toggle", x),
                            suppress=True)
        logger.info(f"binding hotkey {kivy_settings.automatic_toggle}")
        """

        # Next Button for the clicker
        keyboard.on_release_key(general_settings.clicker_forward,
                                lambda x: self.on_hotkey("clicker_next", x),
                                suppress=True)
        logger.info(f"binding hotkey {general_settings.clicker_forward}")

        # Previous Button for the clicker
        keyboard.on_release_key(general_settings.clicker_backward,
                                lambda x: self.on_hotkey("clicker_prev", x),
                                suppress=True)
        logger.info("binding hotkey " +
                    f"{general_settings.clicker_backward}")

    def on_hotkey(self, *hotkey):
        sett = self.settings
        event = hotkey[-1]
        hotkey = "".join(hotkey[:-1])
        logger.debug(f"hotkey {hotkey} caught")
        logger.debug(f"The hotkey event was: {event}")
        if hotkey == "camera" or event == "camera":
            self.set_scene_camera()
        elif hotkey == "center" or event == "center":
            self.set_scene_center()
        elif hotkey == "auto_lock" or event == "auto_lock":
            self.States.automatic_enabled = False
        elif hotkey == "clicker_next" or event == "clicker_next":
            self.auto_contro.propre_send("next")
            time.sleep(.2)
            if sett.general.clicker_change_scene_without_automatic:
                self.set_scene_center()
            else:
                if self.States.automatic_enabled:
                    self.set_scene_center()
        elif hotkey == "clicker_prev" or event == "clicker_prev":
            self.auto_contro.propre_send("prev")
            time.sleep(.2)
            if sett.general.clicker_change_scene_without_automatic:
                self.set_scene_center()
            else:
                if self.States.automatic_enabled:
                    self.set_scene_center()
        elif hotkey == "toggle_center_augmented" or event == "toggle_center_augmented":
            logger.debug("toggling center augmented")
            if not (self.States.current_scene == "augmented"):
                self.set_scene_augmented()
            else:
                self.States.automatic_enabled = True
                self.set_scene_camera()



app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '$hor!K#y'
socketio = SocketIO(app, async_mode='eventlet')
eventlet.monkey_patch()
Mobility(app)

MasterApp = MasterController(socketio=socketio)


"""
@threaded
def loop():
    time.sleep(3)
    try:
        if __name__ != "__main__":
            print("starting webserver")
            global SceneController
            global master_app
            master_app = App.get_running_app()
            SceneController = master_app.root.ids.MainScreen.ids.ScenePanel
            while True:
                socketio.emit("update", {"data": "None",
                                         "states": [
                                             SceneController.current_scene == "camera",
                                             SceneController.current_scene == "center",
                                             SceneController.ids.SCQAutomatic.ids.cb.active,
                                             SceneController.ids.TimerLabel.text,
                                             master_app.auto_contro.get_sound_state(),
                                             SceneController.is_center_augmented
                                         ]})
                time.sleep(.2)
        else:
            print("starting test webserver")
            while True:
                socketio.emit("update", {"data": "None",
                                         "states": [
                                             True,
                                             False,
                                             True,
                                             "Test",
                                             True,
                                             False
                                         ]})
                time.sleep(1)
    except KeyboardInterrupt:
        return
"""


@app.route("/")
def send_to_index():
    if MasterApp.States.stream_setup or MasterApp.States.stream_running:
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
        state = MasterApp.States.stream_running.value
        return flask.render_template("go_live.html", form=form, state=state)


@socketio.on("scene_camera")
def on_scene_camera(event):
    MasterApp.on_hotkey("camera")


@socketio.on("scene_center")
def on_scene_center(event):
    MasterApp.on_hotkey("center")


@socketio.on("automatic_change")
def on_auto_change(event):
    MasterApp.on_hotkey("auto_lock")


@socketio.on("slide_next")
def on_slide_next(event):
    MasterApp.on_hotkey("clicker_next")


@socketio.on("slide_prev")
def on_slide_prev(event):
    MasterApp.on_hotkey("clicker_prev")


@socketio.on("volume")
def toggle_volume(event):
    MasterApp.auto_contro.toggle_sound()


@socketio.on("center_toggle")
def on_toggle_center(event):
    MasterApp.on_hotkey("toggle_center_augmented")


if __name__ == "__main__":
    MasterApp.start()
