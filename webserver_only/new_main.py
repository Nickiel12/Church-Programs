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
from Classes.Watch_Classes import WatchBool, WatchNumber, WatchStr
from utils import DotDict

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
        States = States(stream_running=WatchBool(False, partial(on_update, "stream_running")),
                        stream_setup=False,
                        stream_title="",
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


MasterApp = MasterController()

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '$hor!K#y'
socketio = SocketIO(app)
Mobility(app)

SceneController = None
master_app = None

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
                master_app.root.ids.MainScreen.ids.StreamPanel.fake_press_go_live()
        return flask.redirect(flask.url_for('index'))
    if __name__ == "__main__":
        return flask.render_template("go_live.html", form=form, state=True)
    else:
        state = master_app.stream_running
        return flask.render_template("go_live.html", form=form, state=state)


@socketio.on("scene_camera")
def on_scene_camera(event):
    SceneController.on_hotkey("camera")


@socketio.on("scene_center")
def on_scene_center(event):
    SceneController.on_hotkey("center")


@socketio.on("automatic_change")
def on_auto_change(event):
    SceneController.on_hotkey("scene_lock")


@socketio.on("slide_next")
def on_slide_next(event):
    SceneController.on_hotkey("clicker_next")


@socketio.on("slide_prev")
def on_slide_prev(event):
    SceneController.on_hotkey("clicker_prev")


@socketio.on("volume")
def toggle_volume(event):
    global master_app
    master_app.auto_contro.toggle_sound()


@socketio.on("center_toggle")
def on_toggle_center(event):
    SceneController.on_hotkey("toggle_center_augmented")


def start_web_server():
    # loop()
    socketio.run(app, "0.0.0.0")


if __name__ == "__main__":
    #MasterApp.update_value("trust", )
    pass
