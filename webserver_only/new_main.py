import copy
import pathlib
import json
import logging
import flask
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from flask_socketio import SocketIO
from functools import partial
import time
import eventlet

#from utils import threaded
from forms import SetupStreamForm, GoLiveForm
from Classes.States import States
from utils import DotDict, threaded

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
#datefmt='%m/%d/%Y %H:%M:%S'
logger = logging.getLogger("Main")
web_logger = logging.getLogger("Main.webserver")


class MasterController:

    OPTIONS_FILE_PATH = pathlib.Path(".").parent/"extras"/"options.json"
    settings = None

    def __init__(self):
        self.States = States(stream_running = False,
                             stream_setup   = False,
                             stream_title   = "",
                             callback = self.on_update,
                             )
        self.update_settings()

    def update_settings(self):
        if self.settings != None:
            tmp_settings = copy.deepcopy(self.settings)
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
            self.settings = tmp_settings

    def on_update(self, key):
        logger.debug(f"{key} was changed")

    def _stop_timer(self, *args):
        print("timer stopped")
        self.timer_run.set()

    def zero_timer(self, *args):
        self.pause_timer()
        self.ids.TimerLabel.text = "0.0"

    def pause_timer(self, *args):
        self._timer_paused = True

    def start_timer(self, *args):
        self._timer_paused = False

    def reset_timer(self):
        self.timer_start_time = time.time()
        self.start_timer()

    def timer_unavailable(self):
        self.timer_text = "Unvailable"

    def timer_available(self):
        self.timer_text = None
        self.zero_timer()

    @threaded
    def _timer(self):
        while not self.timer_run.is_set():
            if self.timer_text is None:
                try:
                    if self._timer_paused is False:
                        end_time = self.timer_start_time + self.timer_length
                        self.timer_left = round(end_time - time.time(), 1)
                        if self.timer_left >= 0:
                            self.ids.TimerLabel.text = str(self.timer_left)
                        else:
                            self.timer_run_out()
                    else:
                        time.sleep(.3)
                except KeyboardInterrupt:
                    return
            else:
                self.ids.TimerLabel.text = self.timer_text
                time.sleep(.3)
            time.sleep(.1)

    def timer_run_out(self):
        self._timer_paused = True
        self.on_hotkey("camera")

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

        # Automatic Checkbox Hotkey
        keyboard.add_hotkey(kivy_settings.scene_lock,
                            lambda x: self.on_hotkey("scene_lock", x),
                            suppress=True)
        logger.info(f"binding hotkey {kivy_settings.scene_lock}")

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
        sett = self.app.settings
        event = hotkey[-1]
        print(f"The hotkey event was: {event}")
        hotkey = "".join(hotkey[:-1])
        logger.debug(f"hotkey {hotkey} caught")
        if hotkey == "camera" or event == "camera":
            self._do_fake_press_camera()
        elif hotkey == "center" or event == "center":
            self._do_fake_press_center()
        elif hotkey == "scene_lock" or event == "scene_lock":
            self.ids.SCQAutomatic.ids.cb._do_press()
        elif hotkey == "clicker_next" or event == "clicker_next":
            self.app.auto_contro.propre_send("next")
            time.sleep(.2)
            if sett.general.clicker_change_scene_without_automatic:
                self._do_fake_press_center()
            else:
                if self.auto_state:
                    self._do_fake_press_center()
        elif hotkey == "clicker_prev" or event == "clicker_prev":
            self.app.auto_contro.propre_send("prev")
            time.sleep(.2)
            if sett.general.clicker_change_scene_without_automatic:
                self._do_fake_press_center()
            else:
                if self.auto_state:
                    self._do_fake_press_center()
        elif hotkey == "toggle_center_augmented" or event == "toggle_center_augmented":
            print("toggleing center augmented")
            if (self.is_center_augmented == False):
                self.ids.center_screen.ids.cb.active = False
                self.ids.live_camera.ids.cb.active = False
                self.ids.SCQAutomatic.ids.cb.active = False
                self.on_auto()
                self.app.auto_contro.obs_send("center_augmented")
                self.current_scene = "augmented"
                self.is_center_augmented = True
            else:
                self.ids.SCQAutomatic.ids.cb.active = True
                self.ids.live_camera.ids.cb.active = True
                self._do_fake_press_camera()
                self.is_center_augmented = False


MasterApp = MasterController()

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '$hor!K#y'
socketio = SocketIO(app)
Mobility(app)


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
            if __name__ != "__main__":
                MasterApp.go_live()
        return flask.redirect(flask.url_for('index'))
    if __name__ == "__main__":
        return flask.render_template("go_live.html", form=form, state=True)
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
    MasterApp.on_hotkey("scene_lock")


@socketio.on("slide_next")
def on_slide_next(event):
    MasterApp.on_hotkey("clicker_next")


@socketio.on("slide_prev")
def on_slide_prev(event):
    MasterApp.on_hotkey("clicker_prev")


@socketio.on("volume")
def toggle_volume(event):
    global master_app
    master_app.auto_contro.toggle_sound()


@socketio.on("center_toggle")
def on_toggle_center(event):
    MasterApp.on_hotkey("toggle_center_augmented")


def start_web_server():
    # loop()
    socketio.run(app, "0.0.0.0")


if __name__ == "__main__":
    MasterApp.States.stream_running = True
    pass
